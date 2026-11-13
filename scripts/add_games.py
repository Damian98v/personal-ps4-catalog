"""Resolve names against researched sources, probe PKGs, then add/update safely."""
import argparse
from catalog import (ROOT, read_json, write_json, now, discover, release_candidates,
                     source_allows, probe, validate)


def add(names, *, direct_url=None, source_id=None, refresh=False):
    validate()
    games = read_json(ROOT / 'games.json')
    research = read_json(ROOT / 'research.json')
    missing = read_json(ROOT / 'missing.json')
    sources = read_json(ROOT / 'sources.json')['sources']
    failed = 0
    for name in names:
        source = next((s for s in sources if (source_id and s['id'] == source_id) or
                       (not source_id and name.casefold() in [x.casefold() for x in [s['name'], s['id'], *s.get('aliases', [])]])), None)
        try:
            if not source:
                candidates = discover(name)
                raise ValueError('No reviewed authorized PS4 source. Candidates require Codex research: ' +
                                 ', '.join(c['url'] for c in candidates))
            if direct_url:
                url, release, asset = direct_url, {}, {}
            else:
                release, asset = release_candidates(source)
                url = asset['browser_download_url']
            if not source_allows(source, url):
                raise ValueError('URL outside reviewed source scope')
            if url in games['DATA'] and not refresh:
                print('Already present:', name)
                continue
            verified = probe(url)
            if asset and asset['size'] != verified['size']:
                raise ValueError('GitHub asset size differs from package')
            if verified['title_id'] != verified['content_id'][7:16]:
                raise ValueError('Package identity mismatch')
            item = {'name': source['name'], 'title_id': verified['title_id'],
                    'content_id': verified['content_id'], 'size': verified['size'],
                    'version': verified['version'], 'min_fw': verified['min_fw'] or source.get('min_fw'),
                    'region': source.get('region'), 'package_type': source.get('package_type', 'game'),
                    'cover_url': source.get('cover_url'), 'description': source.get('description'),
                    'release': None}
            if release.get('published_at'):
                from datetime import datetime
                item['release'] = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00')).strftime('%m-%d-%Y')
            # Same identity/version is a moved URL, not a second package. New versions stay separate.
            for old_url, old in list(games['DATA'].items()):
                if old_url != url and (old.get('content_id'), old.get('version'), old.get('package_type')) == (
                        item['content_id'], item['version'], item['package_type']):
                    del games['DATA'][old_url]
                    research['packages'].pop(old_url, None)
            games['DATA'][url] = item
            research['packages'][url] = {'source_id': source['id'], 'kind': source.get('kind', 'homebrew'),
                'release_url': release.get('html_url') or source['authorization_url'],
                'release_tag': release.get('tag_name'), 'requirements': source.get('requirements', []),
                'verification': verified}
            missing['requests'] = [r for r in missing['requests'] if r['name'].casefold() != name.casefold()]
            print('Verified:', item['name'], item['version'], item['size'], 'bytes')
        except Exception as exc:
            failed += 1
            existing = next((r for r in missing['requests'] if r['name'].casefold() == name.casefold()), None)
            record = {'name': name, 'status': 'unconfirmed' if source else 'missing',
                      'reason': str(exc), 'last_attempt': now(),
                      'needed': 'A public direct authorized PS4 PKG URL and evidence of authorization; existing entries are retained.'}
            if existing:
                existing.update(record)
            else:
                missing['requests'].append(record)
            print('Not added:', name, str(exc))
    # Validate the complete proposed state in a temporary directory before publishing any data.
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp)
        for filename, data in [('games.json', games), ('research.json', research),
                               ('missing.json', missing), ('sources.json', {'sources': sources})]:
            write_json(target / filename, data)
        validate(target)
    write_json(ROOT / 'games.json', games)
    write_json(ROOT / 'research.json', research)
    write_json(ROOT / 'missing.json', missing)
    return 1 if failed else 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('names', nargs='+')
    p.add_argument('--url', help='User-authorized direct PKG; requires --source')
    p.add_argument('--source', help='Reviewed source ID in sources.json')
    p.add_argument('--refresh', action='store_true', help='Recheck/update an existing URL')
    args = p.parse_args()
    if args.url and (not args.source or len(args.names) != 1):
        p.error('--url requires --source and exactly one name')
    return add(args.names, direct_url=args.url, source_id=args.source, refresh=args.refresh)


if __name__ == '__main__':
    raise SystemExit(main())
