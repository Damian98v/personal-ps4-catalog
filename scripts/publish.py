"""Test, validate, commit project changes, push, and verify exact public JSON."""
import argparse
import json
import subprocess
import sys
import time
from catalog import ROOT, read_json, request, validate

PUBLIC_URL = 'https://damian98v.github.io/personal-ps4-catalog/games.json'


def run(*args, capture=False):
    r = subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=capture, encoding='utf-8')
    return r.stdout.strip() if capture else None


def verify_public(timeout=240):
    expected = read_json(ROOT / 'games.json')
    deadline = time.monotonic() + timeout
    while True:
        try:
            with request(PUBLIC_URL + '?v=' + run('git', 'rev-parse', 'HEAD', capture=True)) as response:
                if response.status != 200:
                    raise ValueError('Publication did not return HTTP 200')
                actual = json.loads(response.read(8 * 1024 * 1024 + 1))
            if actual != expected:
                raise ValueError('Public catalog is not the current local catalog yet')
            print('Published JSON matches local catalog:', PUBLIC_URL, flush=True)
            return
        except Exception as exc:
            if time.monotonic() >= deadline:
                raise RuntimeError('Push may have succeeded, but publication is unconfirmed; inspect GitHub Actions') from exc
            print('Waiting for GitHub Pages:', str(exc), flush=True)
            time.sleep(10)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--message', default='Update verified PS4 catalog')
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    if args.verify_only:
        verify_public()
        return
    run(sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v')
    results = validate(online=True)
    if any(r['status'] != 'verified' for r in results):
        raise ValueError('Remote validation failed; catalog retained, nothing committed')
    # Only this project's known files; never sweep personal/unrelated files into a public commit.
    allowed = {'games.json', 'sources.json', 'research.json', 'missing.json', 'README.md',
               'AGENTS.md', '.gitignore', 'docs/compatibility.md'}
    allowed.update(str(x.relative_to(ROOT)).replace('\\', '/') for folder in ['scripts', 'tests', '.github/workflows']
                   for x in (ROOT / folder).glob('*') if x.is_file() and x.suffix in ('.py', '.yml'))
    changed = run('git', 'diff', '--name-only', 'HEAD', capture=True).splitlines()
    untracked = run('git', 'ls-files', '--others', '--exclude-standard', capture=True).splitlines()
    if set(changed + untracked) - allowed:
        raise ValueError('Unrelated changes present; review them before publishing')
    if run('git', 'branch', '--show-current', capture=True) != 'main':
        raise ValueError('Publish from main after reviewing/merging your branch')
    run('git', 'add', '--', *sorted(allowed))
    if run('git', 'diff', '--cached', '--name-only', capture=True):
        run('git', 'commit', '-m', args.message)
    run('git', 'push', 'origin', 'main')
    verify_public()


if __name__ == '__main__':
    main()
