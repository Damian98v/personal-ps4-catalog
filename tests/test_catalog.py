import copy
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import catalog
import add_games


PKG = bytearray(8192)
PKG[:4] = b'\x7fCNT'
PKG[0x40:0x64] = b'IV0000-TEST00001_00-TESTPACKAGE00000'
struct.pack_into('>Q', PKG, 0x430, len(PKG))


class Handler(BaseHTTPRequestHandler):
    bytes_sent = 0

    def log_message(self, *args):
        pass

    def do_HEAD(self):
        if self.path == '/no-head':
            self.send_error(405)
            return
        self.send_response(200)
        self.send_header('Content-Length', str(len(PKG)))
        self.end_headers()

    def do_GET(self):
        if self.path == '/redirect':
            self.send_response(302)
            self.send_header('Location', '/pkg')
            self.end_headers()
            return
        if self.path == '/loop':
            self.send_response(302)
            self.send_header('Location', '/loop')
            self.end_headers()
            return
        if self.path == '/no-range':
            self.send_response(200)
            self.end_headers()
            return
        start, end = map(int, self.headers['Range'][6:].split('-'))
        content = bytearray(PKG[start:end + 1])
        if self.path == '/bad-magic' and start == 0:
            content[:4] = b'\x7fPKG'  # PS3 must never be accepted as PS4.
        if self.path == '/bad-size' and start == 0:
            struct.pack_into('>Q', content, 0x430, 999999)
        self.send_response(206)
        self.send_header('Content-Type', 'text/html' if self.path == '/html' else 'application/octet-stream')
        self.send_header('Content-Range', f'bytes {start}-{end}/{len(PKG)}' if self.path != '/wrong-range' else 'bytes 1-4096/8192')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)
        Handler.bytes_sent += len(content)


class Probes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_bounded_probe(self):
        before = Handler.bytes_sent
        result = catalog.probe(self.url + '/pkg')
        self.assertEqual(result['content_id'], 'IV0000-TEST00001_00-TESTPACKAGE00000')
        self.assertEqual(result['size'], len(PKG))
        self.assertLessEqual(Handler.bytes_sent - before, 4097)

    def test_relative_redirect(self):
        self.assertEqual(catalog.probe(self.url + '/redirect')['status'], 'verified')

    def test_head_optional_when_get_confirms(self):
        self.assertEqual(catalog.probe(self.url + '/no-head')['head_status'], 405)

    def test_bad_servers_rejected(self):
        for path in ['/bad-magic', '/bad-size', '/html', '/wrong-range', '/no-range', '/loop']:
            with self.subTest(path=path), self.assertRaises((ValueError, catalog.urllib.error.HTTPError)):
                catalog.probe(self.url + path)

    def test_credential_fragment_and_scheme_rejected(self):
        for url in ['https://user:pass@example.org/a.pkg', 'file:///tmp/a.pkg', 'https://x/a#f', 'https://x/a\nb']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                catalog.valid_url(url)

    def test_downgrade_rejected(self):
        req = catalog.urllib.request.Request('https://example.org/a')
        with self.assertRaises(ValueError):
            catalog.Redirects().redirect_request(req, None, 302, '', {}, 'http://example.org/b')


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # Independent fixtures: removing/adding real games must not break the test suite.
        url = 'https://github.com/example/test/releases/download/v1/fixture.pkg'
        identity = 'IV0000-TEST00001_00-TESTPACKAGE00000'
        source = {'id': 'fixture', 'name': 'Test Homebrew', 'aliases': ['fixture'],
                  'repo': 'example/test', 'standalone': True,
                  'authorization_url': 'https://github.com/example/test',
                  'authorization': 'Synthetic unit-test fixture only', 'reviewed_on': '2026-11-13'}
        item = {'name': 'Test Homebrew', 'size': 8192, 'title_id': 'TEST00001',
                'content_id': identity, 'version': '1.00', 'package_type': 'game'}
        evidence = {'status': 'verified', 'checked_at': catalog.now(), 'range_supported': True,
                    'size': 8192, 'title_id': 'TEST00001', 'content_id': identity}
        for name, value in [('games.json', {'DATA': {url: item}}),
                            ('sources.json', {'sources': [source]}),
                            ('research.json', {'packages': {url: {'source_id': 'fixture', 'verification': evidence}}}),
                            ('missing.json', {'requests': []})]:
            catalog.write_json(self.root / name, value)

    def tearDown(self):
        self.tmp.cleanup()

    def test_real_catalog(self):
        catalog.validate()
        catalog.validate(self.root)

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"DATA": {}, "DATA": {}}', object_pairs_hook=catalog.unique_object)

    def test_unverified_cannot_publish(self):
        r = catalog.read_json(self.root / 'research.json')
        next(iter(r['packages'].values()))['verification']['status'] = 'unconfirmed'
        catalog.write_json(self.root / 'research.json', r)
        with self.assertRaises(ValueError):
            catalog.validate(self.root)

    def test_duplicate_identity_rejected(self):
        g = catalog.read_json(self.root / 'games.json')
        r = catalog.read_json(self.root / 'research.json')
        url, item = next(iter(g['DATA'].items()))
        moved = url.replace('/v1/', '/other/')
        g['DATA'][moved] = copy.deepcopy(item)
        r['packages'][moved] = copy.deepcopy(r['packages'][url])
        catalog.write_json(self.root / 'games.json', g)
        catalog.write_json(self.root / 'research.json', r)
        with self.assertRaisesRegex(ValueError, 'Duplicate package'):
            catalog.validate(self.root)

    def test_unknown_fields_rejected(self):
        g = catalog.read_json(self.root / 'games.json')
        next(iter(g['DATA'].values()))['source'] = 'not supported'
        catalog.write_json(self.root / 'games.json', g)
        with self.assertRaises(ValueError):
            catalog.validate(self.root)

    def test_failed_recheck_preserves_catalog(self):
        before = (self.root / 'games.json').read_bytes()
        with patch.object(catalog, 'probe', side_effect=ValueError('temporary HTTP 503')):
            result = catalog.validate(self.root, online=True)
        self.assertTrue(all(r['status'] == 'unconfirmed' for r in result))
        self.assertEqual(before, (self.root / 'games.json').read_bytes())

    def test_add_idempotent(self):
        before = (self.root / 'games.json').read_bytes()
        url = next(iter(catalog.read_json(self.root / 'games.json')['DATA']))
        with patch.object(add_games, 'ROOT', self.root), patch.object(add_games, 'validate', wraps=lambda root=self.root: catalog.validate(root)), patch.object(add_games, 'release_candidates', return_value=({}, {'browser_download_url': url})):
            self.assertEqual(add_games.add(['fixture']), 0)
        self.assertEqual(before, (self.root / 'games.json').read_bytes())

    def test_unknown_name_recorded_once(self):
        with patch.object(add_games, 'ROOT', self.root), patch.object(add_games, 'validate', wraps=lambda root=self.root: catalog.validate(root)), patch.object(add_games, 'discover', return_value=[]):
            for _ in range(2):
                self.assertEqual(add_games.add(['Unknown commercial game']), 1)
        self.assertEqual(len(catalog.read_json(self.root / 'missing.json')['requests']), 1)
        self.assertEqual(len(catalog.read_json(self.root / 'games.json')['DATA']), 1)

    def test_new_direct_package_is_added_after_probe(self):
        source = {'id': 'direct', 'name': 'Direct Homebrew', 'allowed_urls': ['https://example.org/test.pkg'],
                  'standalone': True, 'authorization_url': 'https://example.org',
                  'authorization': 'Synthetic authorized fixture', 'reviewed_on': '2026-11-13'}
        sources = catalog.read_json(self.root / 'sources.json')
        sources['sources'].append(source)
        catalog.write_json(self.root / 'sources.json', sources)
        evidence = {'status': 'verified', 'checked_at': catalog.now(), 'range_supported': True,
                    'size': 12288, 'title_id': 'TEST00002', 'version': '1.01', 'min_fw': None,
                    'content_id': 'IV0000-TEST00002_00-TESTPACKAGE00000'}
        with patch.object(add_games, 'ROOT', self.root), patch.object(add_games, 'validate', wraps=lambda root=self.root: catalog.validate(root)), patch.object(add_games, 'probe', return_value=evidence) as probe:
            self.assertEqual(add_games.add(['Direct Homebrew'], source_id='direct', direct_url='https://example.org/test.pkg'), 0)
            probe.assert_called_once()
        self.assertEqual(len(catalog.read_json(self.root / 'games.json')['DATA']), 2)
        catalog.validate(self.root)

    def test_source_scope(self):
        source = catalog.read_json(self.root / 'sources.json')['sources'][0]
        self.assertFalse(catalog.source_allows(source, 'https://github.com/unknown/game/releases/download/x/a.pkg'))


if __name__ == '__main__':
    unittest.main()
