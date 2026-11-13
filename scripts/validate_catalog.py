"""Validate without modifying catalog data; online failures preserve existing items."""
import argparse
from pathlib import Path
from catalog import ROOT, validate, write_json, now


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--online', action='store_true')
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    try:
        results = validate(online=args.online)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            write_json(args.report, {'checked_at': now(), 'packages': results})
        for result in results:
            print(result['status'], result['name'], result.get('error', ''))
        if any(r['status'] != 'verified' for r in results):
            return 1
        print('Catalog valid' + ('; remote packages verified' if args.online else ' (offline)'))
        return 0
    except Exception as exc:
        print('Validation failed:', exc)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
