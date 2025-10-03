#!/usr/bin/env python3
import re
import sys
from pathlib import Path
import pandas as pd
from unidecode import unidecode

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'data' / 'generated'

TRAILING_PUNCT = re.compile(r"[\s\u00A0]*(;|\.|:|,)+\s*$")


def clean_name(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = s.replace('\u00A0', ' ').replace('\xa0', ' ')
    s = s.replace('\u00AD', '').replace('\xad', '')
    s = s.replace('\n', ' ').replace('\r', ' ')
    s = re.sub(r"\s+", " ", s)
    s = TRAILING_PUNCT.sub("", s)
    return s.strip()


def clean_code(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = ''.join(ch for ch in s if ch.isalnum())
    return s.upper()[:10]


def process_csv(path: Path, kind: str):
    if not path.exists():
        return False
    df = pd.read_csv(path)
    # common fields
    if 'name' in df.columns:
        df['name'] = df['name'].map(clean_name)
    if 'code' in df.columns:
        df['code'] = df['code'].astype(str).map(clean_code)
    if kind == 'direction':
        if 'ministry_code' in df.columns:
            df['ministry_code'] = df['ministry_code'].astype(str).map(clean_code)
    if kind == 'service':
        if 'direction_code' in df.columns:
            df['direction_code'] = df['direction_code'].astype(str).map(clean_code)
    # ensure dedup by name within file to avoid duplicates introduced by punctuation fixes
    if 'external_id' in df.columns and 'name' in df.columns:
        df = df.drop_duplicates(subset=['name'])
    df.to_csv(path, index=False)
    print(f"Polished {path.name}: {len(df)} rows")
    return True


def main():
    changed = False
    changed |= process_csv(OUT / 'ministry.csv', 'ministry')
    changed |= process_csv(OUT / 'direction.csv', 'direction')
    changed |= process_csv(OUT / 'service.csv', 'service')
    if not changed:
        print('No generated CSVs found to polish in', OUT, file=sys.stderr)
        sys.exit(1)
    print('Polishing complete.')


if __name__ == '__main__':
    main()
