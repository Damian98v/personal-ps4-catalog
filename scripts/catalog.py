"""Shared catalog, anonymous bounded HTTP probes and reviewed-source discovery."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time
from datetime import datetime, timezone
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'name', 'title_id', 'content_id', 'version', 'region', 'size',
          'min_fw', 'package_type', 'cover_url', 'description', 'release'}


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def write_json(path, value):
    path = Path(path)
    content = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') == content:
        return
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(content, encoding='utf-8')
    tmp.replace(path)


def valid_url(url):
    if not isinstance(url, str) or len(url) >= 2048 or re.search(r'[\s\\\x00-\x1f\x7f]', url):
        raise ValueError('Invalid HTTP(S) URL')
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password or p.fragment:
        raise ValueError('URL must be public HTTP(S), without credentials or fragment')
    return url


class Redirects(urllib.request.HTTPRedirectHandler):
    max_redirections = 5
    max_repeats = 2

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        valid_url(newurl)
        if req.full_url.startswith('https:') and not newurl.startswith('https:'):
            raise ValueError('HTTPS downgrade redirect rejected')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request(url, *, method='GET', headers=None):
    valid_url(url)
    h = {'User-Agent': 'personal-ps4-catalog/1.0', 'Accept-Encoding': 'identity'}
    h.update(headers or {})
    # Never send GitHub API credentials or cookies to package hosts.
    for attempt in range(3):
        try:
            return urllib.request.build_opener(Redirects()).open(
                urllib.request.Request(url, method=method, headers=h), timeout=20)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            retry = exc.headers.get('Retry-After', '')
            if retry.isdigit() and int(retry) > 5:
                raise ValueError('Rate limited; retry later') from exc
            time.sleep(int(retry) if retry.isdigit() else attempt + 1)


def range_bytes(url, start, end):
    if end < start or end - start >= 65536:
        raise ValueError('Probe exceeds 64 KiB request budget')
    with request(url, headers={'Range': f'bytes={start}-{end}'}) as r:
        if r.status != 206:
            raise ValueError(f'Range unconfirmed: expected 206, got {r.status}; body not downloaded')
        m = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', r.headers.get('Content-Range', ''))
        if not m or tuple(map(int, m.groups()[:2])) != (start, end):
            raise ValueError('Incorrect Content-Range')
        if 'html' in r.headers.get('Content-Type', '').lower():
            raise ValueError('HTML instead of PKG')
        if r.headers.get('Content-Encoding', 'identity') != 'identity':
            raise ValueError('Encoded package response')
        data = r.read(end - start + 2)
        if len(data) != end - start + 1:
            raise ValueError('Truncated/oversized range response')
        return data, int(m.group(3)), urllib.parse.urlsplit(r.url).hostname


def parse_sfo(data):
    if len(data) < 20 or data[:4] != b'\x00PSF':
        raise ValueError('Invalid SFO')
    _, keys, values, count = struct.unpack_from('<4I', data, 4)
    if count > 512 or 20 + count * 16 > len(data):
        raise ValueError('Invalid SFO table')
    result = {}
    for i in range(count):
        key, fmt, length, capacity, offset = struct.unpack_from('<HHIII', data, 20 + i * 16)
        key_end = data.find(b'\0', keys + key)
        if key_end < 0 or length > capacity or values + offset + length > len(data):
            raise ValueError('Invalid SFO entry bounds')
        name = data[keys + key:key_end].decode('utf-8')
        raw = data[values + offset:values + offset + length]
        if fmt == 0x0204:
            result[name] = raw.rstrip(b'\0').decode('utf-8')
        elif fmt == 0x0404 and len(raw) == 4:
            result[name] = struct.unpack('<I', raw)[0]
    return result


def probe(url):
    """Read header + tail and at most 128 KiB of optional public SFO metadata."""
    head_size = None
    head_status = None
    try:
        with request(url, method='HEAD') as r:
            head_status = r.status
            if r.status == 200 and r.headers.get('Content-Length', '').isdigit():
                head_size = int(r.headers['Content-Length'])
    except urllib.error.HTTPError as exc:
        if exc.code not in (403, 405, 501):
            raise
        head_status = exc.code
    header, size, host = range_bytes(url, 0, 4095)
    if header[:4] != b'\x7fCNT':
        raise ValueError('Not a PS4 PKG: missing 7f434e54 signature')
    declared = struct.unpack_from('>Q', header, 0x430)[0]
    if declared != size or (head_size is not None and head_size != size):
        raise ValueError('PKG/HTTP file sizes disagree')
    content_id = header[0x40:0x70].split(b'\0', 1)[0].decode('ascii')
    if not re.fullmatch(r'[A-Z0-9]{6}-[A-Z0-9]{9}_\d{2}-[A-Z0-9]{16}', content_id):
        raise ValueError('Invalid PS4 Content ID')
    _, tail_size, _ = range_bytes(url, size - 1, size - 1)
    if tail_size != size:
        raise ValueError('File changed during probe')
    sfo = {}
    # PS4 PKG public entry table: 32-byte records, param.sfo entry id 0x1000.
    count, table_offset = struct.unpack_from('>I', header, 0x10)[0], struct.unpack_from('>I', header, 0x18)[0]
    if 0 < count <= 2048 and table_offset + count * 32 <= size:
        table, total, _ = range_bytes(url, table_offset, table_offset + count * 32 - 1)
        if total != size:
            raise ValueError('File changed during metadata probe')
        for i in range(count):
            entry_id = struct.unpack_from('>I', table, i * 32)[0]
            offset, length = struct.unpack_from('>II', table, i * 32 + 16)
            if entry_id == 0x1000 and 20 <= length <= 65536 and offset + length <= size:
                raw, total, _ = range_bytes(url, offset, offset + length - 1)
                if total != size:
                    raise ValueError('File changed during SFO probe')
                sfo = parse_sfo(raw)
                break
    fw = sfo.get('SYSTEM_VER')
    return {'status': 'verified', 'checked_at': now(), 'size': size,
            'content_id': content_id, 'title_id': content_id[7:16],
            'version': sfo.get('APP_VER'),
            'min_fw': f'{(fw >> 24) & 255:X}.{(fw >> 16) & 255:02X}' if isinstance(fw, int) and fw else None,
            'head_status': head_status, 'range_supported': True, 'resolved_host': host,
            'header_sha256': hashlib.sha256(header).hexdigest(),
            'verification_scope': 'Header, declared size, public SFO (when present), and final byte; not full-file integrity or hardware installation.'}


def api_json(endpoint):
    if shutil.which('gh') and not os.environ.get('GITHUB_ACTIONS'):
        r = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True, encoding='utf-8')
        if r.returncode == 0:
            return json.loads(r.stdout)
    headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com/' + endpoint, headers=headers), timeout=20) as r:
        return json.load(r)


def discover(name):
    query = urllib.parse.quote(name + ' PS4')
    result = api_json('search/repositories?q=' + query + '&per_page=5')
    return [{'repo': x['full_name'], 'url': x['html_url'], 'description': x.get('description')}
            for x in result.get('items', [])]


def approved(source):
    if not source.get('authorization') or not source.get('reviewed_on'):
        raise ValueError('Source needs recorded authorization research')
    valid_url(source['authorization_url'])
    if not source.get('standalone') and not source.get('requirements'):
        raise ValueError('Record required additional files')


def source_allows(source, url):
    approved(source)
    if source.get('repo'):
        return url.startswith('https://github.com/' + source['repo'] + '/releases/download/')
    return url in source.get('allowed_urls', [])


def release_candidates(source):
    approved(source)
    release = api_json('repos/' + source['repo'] + '/releases/latest')
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('Only stable, public releases are selected automatically')
    assets = [a for a in release['assets'] if a['name'].lower().endswith('.pkg')
              and fnmatch.fnmatchcase(a['name'], source['asset_pattern'])]
    if len(assets) != 1:
        raise ValueError(f'Expected one PS4 PKG, found {len(assets)}; refine asset_pattern')
    return release, assets[0]


def validate(root=ROOT, online=False):
    games = read_json(root / 'games.json')
    if set(games) != {'DATA'} or not isinstance(games['DATA'], dict):
        raise ValueError('Catalog requires only a DATA object')
    if len((root / 'games.json').read_bytes()) > 8 * 1024 * 1024 or len(games['DATA']) > 50000:
        raise ValueError('Installer catalog limit exceeded')
    sources = read_json(root / 'sources.json')['sources']
    by_id = {s['id']: s for s in sources}
    if len(sources) != len(by_id):
        raise ValueError('Duplicate source ID')
    for source in sources:
        approved(source)
    research = read_json(root / 'research.json')['packages']
    read_json(root / 'missing.json')
    identities = set()
    results = []
    for url, item in games['DATA'].items():
        valid_url(url)
        if not isinstance(item, dict) or set(item) - FIELDS:
            raise ValueError('Unsupported catalog fields')
        if not isinstance(item.get('name'), str) or not item['name'].strip() or len(item['name'].encode()) >= 600:
            raise ValueError('Invalid name')
        if type(item.get('size')) is not int or not 4096 < item['size'] <= 9007199254740991:
            raise ValueError('Invalid byte size')
        for field in FIELDS - {'size'}:
            if item.get(field) is not None and not isinstance(item[field], str):
                raise ValueError(f'{field} must be string or null')
        if item.get('package_type') not in ('game', 'update', 'dlc'):
            raise ValueError('package_type must be game/update/dlc; homebrew kind lives in research.json')
        if item.get('cover_url'):
            valid_url(item['cover_url'])
        record = research.get(url, {})
        source = by_id.get(record.get('source_id'))
        evidence = record.get('verification', {})
        if not source or not source_allows(source, url) or evidence.get('status') != 'verified':
            raise ValueError('Unreviewed or unverified catalog item')
        if not evidence.get('checked_at') or evidence.get('range_supported') is not True:
            raise ValueError('Missing verification evidence')
        for field in ('title_id', 'content_id', 'size'):
            if item.get(field) != evidence.get(field):
                raise ValueError(f'{field} differs from verified package')
        identity = (item.get('content_id'), item.get('version'), item.get('package_type'))
        if identity in identities:
            raise ValueError('Duplicate package identity')
        identities.add(identity)
        if online:
            try:
                result = probe(url)
                for field in ('size', 'content_id', 'header_sha256'):
                    if result[field] != evidence[field]:
                        raise ValueError(f'Remote {field} changed; research before updating')
                results.append({'name': item['name'], 'url': url, **result})
            except Exception as exc:
                results.append({'name': item['name'], 'url': url, 'status': 'unconfirmed', 'error': str(exc)})
    return results
