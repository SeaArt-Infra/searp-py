import unittest
from urllib.parse import urlsplit, parse_qs

from searp_sdk import Client, ClientConfig, GroupCardsService, GroupSessionsService, with_header
from searp_sdk.cards import CardsService
from searp_sdk.cinema import CinemaService
from searp_sdk.sessions import SessionsService


class Transport:
    def __init__(self, payload=b'{}'):
        self.payload = payload
        self.calls = []

    def request(self, method, path, body, headers):
        self.calls.append((method, path, body, headers))
        return 200, self.payload

    def request_stream(self, method, path, body, headers):
        self.calls.append((method, path, body, headers))
        names = ['operation', 'segment_start', 'token', 'segment_delta', 'segment_end', 'parser_warning', 'usage', 'done', 'error']
        for name in names:
            yield b'id: evt-2\n'
            yield f'event: {name}\n'.encode()
            if name == 'done':
                yield b'data: s1\n'
                yield b'data:  Hi \n'
            else:
                yield b'data: {}\n'
            yield b'\n'


class ReleaseContractTests(unittest.TestCase):
    def test_group_exports_and_aliases(self):
        client = Client(ClientConfig(api_key='test'))
        self.assertIsInstance(client.group_cards, GroupCardsService)
        self.assertIsInstance(client.group_sessions, GroupSessionsService)
        self.assertIs(client.GroupCards, client.group_cards)
        self.assertIs(client.GroupSessions, client.group_sessions)

    def test_group_roster_localization_and_cas_delete(self):
        transport = Transport()
        g = GroupCardsService(transport)
        caller = with_header('x-request-id', 'req1')
        g.list({'listed': False, 'include_deleted': False, 'offset': 0, 'q': 'harbor & stars'}, caller)
        g.create({'user_id': 'owner', 'title': 'Story'})
        g.get('g/1', {'lang': 'zh'}, caller)
        g.update('g/1', {'title': 'Story 2'})
        g.set_listing('g/1', {'listed': False})
        g.list_versions('g/1')
        g.get_version('g/1', 3, {'lang': 'ja'})
        g.list_members('g/1')
        g.add_member('g/1', {'card_id': 'a'})
        cas = {'user_id': 'owner', 'expected_latest_version': 3, 'status': 'removed'}
        g.update_member('g/1', 'tipsy:a/b', cas)
        g.remove_member('g/1', 'tipsy:a/b', cas)
        g.extract_characters('g/1', {})
        g.preview('g/1', {})
        g.import_cards({'source': {}, 'dry_run': True})
        g.list_translations('g/1', 3)
        g.save_translations('g/1', 3, {'lang': 'zh', 'translations': {'title': '故事'}})
        g.delete('g/1')
        query = parse_qs(urlsplit(transport.calls[0][1]).query)
        self.assertEqual(query, {'listed': ['false'], 'include_deleted': ['false'], 'offset': ['0'], 'q': ['harbor & stars']})
        self.assertEqual(transport.calls[2][1], '/group-cards/g%2F1?lang=zh')
        self.assertEqual(transport.calls[6][1], '/group-cards/g%2F1/versions/3?lang=ja')
        self.assertEqual(transport.calls[10][:3], ('DELETE', '/group-cards/g%2F1/members/tipsy%3Aa%2Fb', cas))
        self.assertEqual(transport.calls[2][3]['x-request-id'], ['req1'])

    def test_group_session_envelope_and_routes(self):
        transport = Transport(b'{"id":"s1","revision":4,"usage":null,"operation":{"id":"t1"},"turn":{"segments":[{"speaker_valid":true}],"parser_warnings":[]}}')
        service = GroupSessionsService(transport)
        out = service.turn('s1', {'content': 'Hi', 'expected_revision': 3}, with_header('Idempotency-Key', 't1'))
        self.assertEqual(out['revision'], 4)
        self.assertIsNone(out['usage'])
        self.assertTrue(out['turn']['segments'][0]['speaker_valid'])
        self.assertEqual(transport.calls[0][1], '/sessions/s1/group/turns')
        self.assertEqual(transport.calls[0][3]['Idempotency-Key'], ['t1'])
        service.create({'group_id': 'g1', 'user_id': 'u1'})
        service.get_turn('s1', 'a/b')
        service.prompt('s1', {'turn_id': 'a/b&c'})
        self.assertEqual(transport.calls[1][1], '/group-sessions')
        self.assertEqual(transport.calls[2][1], '/sessions/s1/group/turns/a%2Fb')
        self.assertEqual(parse_qs(urlsplit(transport.calls[3][1]).query), {'turn_id': ['a/b&c']})

    def test_group_sse_preserves_segments_ids_done_and_errors(self):
        transport = Transport()
        events = list(GroupSessionsService(transport).turn_stream('s1', {'content': 'Hi'}, with_header('Last-Event-ID', 'evt-1')))
        self.assertEqual([e.event for e in events], ['operation', 'segment_start', 'token', 'segment_delta', 'segment_end', 'parser_warning', 'usage', 'done', 'error'])
        self.assertEqual(events[7].data, 's1\n Hi ')
        self.assertTrue(events[7].done)
        self.assertEqual(events[8].id, 'evt-2')
        self.assertEqual(transport.calls[0][3]['Accept'], ['text/event-stream'])
        self.assertEqual(transport.calls[0][3]['Last-Event-ID'], ['evt-1'])

    def test_inspiration_translation_fork_and_cinema_order(self):
        transport = Transport(b'{"replies":[{"style":"positive","text":"Yes"},{"style":"neutral","text":"Maybe"}],"usage":null,"errors":[{"code":"missing_source"}]}')
        out = SessionsService(transport).inspiration('s1')
        self.assertEqual(len(out['replies']), 2)
        self.assertIsNone(out['usage'])
        self.assertEqual(transport.calls[0][:3], ('POST', '/sessions/s1/inspiration', {}))
        cards = CardsService(transport, transport)
        cards.untranslated({'locale': 'zh-CN', 'include_partial': False, 'offset': 0})
        out = cards.fork_translations({'items': [{'card_id': 'c1', 'card_version': 3, 'locales': ['zh']}]})
        self.assertEqual(out['errors'][0]['code'], 'missing_source')
        cards.fork('p/1', {'catalog_ids': ['c1']})
        CinemaService(transport).list_rounds('s1', {'order': 'desc', 'limit': 1, 'offset': 0})
        self.assertEqual(parse_qs(urlsplit(transport.calls[1][1]).query)['include_partial'], ['false'])
        self.assertEqual(transport.calls[3][1], '/projects/p%2F1/cards/fork')
        self.assertEqual(parse_qs(urlsplit(transport.calls[4][1]).query)['order'], ['desc'])
