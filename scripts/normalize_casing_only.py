#!/usr/bin/env python3
import re
from pathlib import Path
import pandas as pd
from unidecode import unidecode

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'data' / 'generated'

LOWER_EXCEPT = {
    'de','du','des','d’','d\'','la','le','les','l’','l\'','et','en','au','aux','à','a','pour','avec','sur','dans','par'
}
ACRONYM_MAX = 6

def smart_title(name: str) -> str:
    if not isinstance(name, str) or not name:
        return name
    s = name.strip().replace('\n', ' ').replace('\r', ' ')
    s = s.replace('\u00A0', ' ').replace('\xa0', ' ').replace('\u00AD','').replace('\xad','')
    s = re.sub(r"\s+", " ", s)
    parts = s.split(' ')
    out = []
    for i, w in enumerate(parts):
        if not w:
            continue
        wl = unidecode(w).lower()
        # lowercase french articles/prepositions (even if uppercase), except first word
        if i != 0 and wl in LOWER_EXCEPT:
            out.append(w.lower())
        else:
            # keep acronyms (but not if they are french articles handled above)
            if w.isupper() and len(w) <= ACRONYM_MAX:
                out.append(w)
            else:
                out.append(w[0].upper() + w[1:].lower())
    return ' '.join(out)


def normalize_file(path: Path, columns):
    if not path.exists():
        return False
    df = pd.read_csv(path)
    for col in columns:
        if col in df.columns:
            df[col] = df[col].map(smart_title)
    df.to_csv(path, index=False)
    print(f"Casing normalized: {path.name}")
    return True


def main():
    changed = False
    changed |= normalize_file(OUT / 'ministry.csv', ['name'])
    changed |= normalize_file(OUT / 'direction.csv', ['name'])
    changed |= normalize_file(OUT / 'service.csv', ['name'])
    if not changed:
        print('No CSVs found to normalize in', OUT)

if __name__ == '__main__':
    main()
