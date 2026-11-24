#!/usr/bin/env python3
"""Generate WCD normalization and delimiter test cases without network requests."""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


DEFAULT_DELIMITERS = Path(__file__).resolve().with_name('delimiters.txt')
CONTROL_DELIMITERS = ["%00", "%0A", "%09"]


def load_delimiters(filename):
    # Whitespace-separated tokens; #, quotes and backslashes are literal data.
    tokens = filename.read_text(encoding='utf-8-sig').split()
    if not tokens:
        raise ValueError('Delimiter file is empty.')
    if any(any(ord(c) < 33 or ord(c) == 127 for c in token) for token in tokens):
        raise ValueError('Use percent-encoded control characters in the delimiter file.')
    return list(dict.fromkeys(tokens))


def generate_normalization(path, directory):
    target = path.lstrip('/')
    prefix = '/' + directory
    cases = [
        ('baseline', path),
        ('dot-segment', f'{prefix}/../{target}'),
        ('encoded slash lower', f'{prefix}/..%2f{target}'),
        ('encoded slash upper', f'{prefix}/..%2F{target}'),
        ('encoded first dot', f'{prefix}/%2e./{target}'),
        ('encoded second dot', f'{prefix}/.%2e/{target}'),
        ('encoded both dots', f'{prefix}/%2e%2e/{target}'),
        ('encoded dots and slash', f'{prefix}/%2e%2e%2f{target}'),
        ('encoded directory separator', f'{prefix}%2f../{target}'),
        ('double-encoded slash', f'{prefix}/..%252f{target}'),
        ('double-encoded dots', f'{prefix}/%252e%252e/{target}'),
        ('double-encoded dots and slash', f'{prefix}/%252e%252e%252f{target}'),
        ('two dot-segments', f'{prefix}/bbb/../../{target}'),
        ('two encoded slashes', f'{prefix}/bbb/..%2f..%2f{target}'),
        ('current directory', f'/./{target}'),
        ('encoded current directory', f'/%2e/{target}'),
        ('repeated internal slash', f'{prefix}//../{target}'),
        ('trailing slash (separate behavior)', path[:-1] if path.endswith('/') and path != '/' else path + '/' if path != '/' else '/'),
    ]
    # Deduplicate without changing test order.
    seen = set()
    for label, value in cases:
        if value not in seen:
            seen.add(value)
            yield label, value


def generate_delimiters(path, suffix, chars):
    yield 'baseline', path
    yield 'negative control (no delimiter)', path + suffix
    for char in chars:
        yield f'delimiter {char!r}', path + char + suffix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', help='Absolute HTTP(S) URL, e.g. https://example.test/profile')
    parser.add_argument('--dir', default='aaa', help='Arbitrary path segment (default: aaa)')
    parser.add_argument('--mode', choices=['all', 'normalization', 'delimiter'], default='all', help='Test family (default: all)')
    parser.add_argument('--suffix', default='xyz', help='Arbitrary marker after each delimiter (default: xyz)')
    parser.add_argument('-d', '--delimiters', type=Path, default=DEFAULT_DELIMITERS, help='Delimiter file; default: delimiters.txt beside this script')
    parser.add_argument('--controls', action='store_true', help='Also test encoded controls: %%00, %%0A, %%09')
    parser.add_argument('--paths', action='store_true', help='Output request targets instead of full URLs')
    parser.add_argument('--details', action='store_true', help='Write test labels to stderr')
    parser.add_argument('-o', '--output', type=Path, help='Write one URL or request target per line')
    args = parser.parse_args()
    try:
        parsed = urlsplit(args.url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Use an absolute HTTP(S) URL without credentials.')
        if parsed.fragment or '#' in args.url:
            raise ValueError('Remove the URL fragment; it is not sent in HTTP requests.')
        if any(ord(c) <= 32 or ord(c) == 127 for c in args.url):
            raise ValueError('Use a URL without raw spaces or control characters.')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', args.dir):
            raise ValueError('--dir must be a single alphanumeric segment (hyphen/underscore allowed).')
        if not re.fullmatch(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*', args.suffix):
            raise ValueError('--suffix must be a simple marker, optionally with an extension.')
        chars = load_delimiters(args.delimiters) if args.mode in ('all', 'delimiter') else []
        if args.controls:
            chars = list(dict.fromkeys(chars + CONTROL_DELIMITERS))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))

    lines = []
    base_path = parsed.path or '/'
    cases = []
    if args.mode in ('all', 'normalization'):
        cases.extend(generate_normalization(base_path, args.dir))
    if args.mode in ('all', 'delimiter'):
        cases.extend(generate_delimiters(base_path, args.suffix, chars))
        if not args.paths:
            print('Warning: raw #, ? and invalid URI characters may be interpreted or rejected by URL clients; use --paths for raw request-target testing.', file=sys.stderr)
    seen = set()
    for label, path in cases:
        # Preserve the exact test path. Do not quote, unquote, or normalize it.
        # If a raw ? was inserted, the existing query becomes part of the new query.
        target = path + (('&' if '?' in path else '?') + parsed.query if parsed.query else '')
        value = target if args.paths else f'{parsed.scheme}://{parsed.netloc}{target}'
        if value in seen:
            continue
        seen.add(value)
        lines.append(value)
        if args.details:
            print(f'{label:34} {value}', file=sys.stderr)
    result = '\n'.join(lines) + '\n'
    if args.output:
        args.output.write_text(result, encoding='utf-8')
    else:
        sys.stdout.write(result)


if __name__ == '__main__':
    main()
