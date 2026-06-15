"""一次性脚本：从 Sensitive-lexicon 下载词库到 lexicon/ 目录。"""
import json
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

BASE_DIR = Path(__file__).resolve().parent / 'lexicon'
API_URL = 'https://api.github.com/repos/konsheng/Sensitive-lexicon/contents/Vocabulary?ref=main'


def encode_url(url: str) -> str:
    parsed = urlparse(url)
    path = quote(parsed.path, safe='/:%')
    return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))


def main() -> int:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'jgzx-platform'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        items = json.load(resp)

    ok = 0
    for item in items:
        if item.get('type') != 'file':
            continue
        url = encode_url(item.get('download_url') or '')
        name = item.get('name', '')
        if not url or not name.endswith('.txt'):
            continue
        dest = BASE_DIR / name
        try:
            file_req = urllib.request.Request(url, headers={'User-Agent': 'jgzx-platform'})
            with urllib.request.urlopen(file_req, timeout=180) as r:
                dest.write_bytes(r.read())
            ok += 1
            sys.stdout.write(f'OK {ok}: {dest.name} ({dest.stat().st_size} bytes)\n')
        except Exception as exc:
            sys.stdout.write(f'FAIL {name}: {exc}\n')
    sys.stdout.write(f'Downloaded {ok} files into {BASE_DIR}\n')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
