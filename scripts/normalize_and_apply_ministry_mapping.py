#!/usr/bin/env python3
import re
from pathlib import Path
import pandas as pd
from unidecode import unidecode

BASE = Path(__file__).resolve().parents[1]
GEN = BASE / 'data' / 'generated'
REF = BASE / 'data' / 'reference'

LOWER_EXCEPT = {
    'de','du','des','d’','d\'','la','le','les','l’','l\'','et','en','au','aux','à','a','pour','avec','sur','dans','par','du','de','des','du','d’','d\''
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
        # keep acronyms
        if w.isupper() and len(w) <= ACRONYM_MAX:
            out.append(w)
            continue
        wl = unidecode(w).lower()
        if i != 0 and wl in LOWER_EXCEPT:
            out.append(w.lower())
        else:
            # title-case first char only
            out.append(w[0].upper() + w[1:].lower())
    return ' '.join(out)


def rebuild_external_id(prefix: str, code: str, fallback_name: str) -> str:
    code = re.sub(r"[^A-Za-z0-9]", "", str(code or ''))
    if code:
        return f"{prefix}_{code.lower()}"
    # fallback
    slug = re.sub(r"[^a-z0-9]+","-", unidecode((fallback_name or '').lower())).strip('-')
    return f"{prefix}_{slug[:30]}" if slug else f"{prefix}_unknown"


def load_mapping() -> dict:
    path = REF / 'ministry_codes.csv'
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    mp = {}
    for _, r in df.iterrows():
        desired = str(r.get('desired_code') or '').strip()
        if desired:
            key = unidecode(str(r.get('key') or r.get('name'))).lower().strip()
            mp[key] = desired.upper()
    return mp


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    REF.mkdir(parents=True, exist_ok=True)

    map_code = load_mapping()

    # Process ministry.csv
    mpath = GEN / 'ministry.csv'
    if mpath.exists():
        mdf = pd.read_csv(mpath)
        # Normalize names
        if 'name' in mdf.columns:
            mdf['name'] = mdf['name'].map(smart_title)
        # Apply mapping for codes
        if map_code:
            new_external_ids = []
            new_codes = []
            for _, row in mdf.iterrows():
                key = unidecode(str(row['name'])).lower().strip()
                desired = map_code.get(key)
                if desired:
                    new_codes.append(desired[:10])
                    new_external_ids.append(rebuild_external_id('ministry', desired, row['name']))
                else:
                    new_codes.append(row['code'])
                    new_external_ids.append(row['external_id'])
            mdf['code'] = new_codes
            # rebuild external_id to match code for stability
            mdf['external_id'] = new_external_ids
        mdf.to_csv(mpath, index=False)
        print(f"Updated ministry.csv ({len(mdf)} rows)")
    else:
        print('ministry.csv not found, skip ministry updates')
        return

    # Reload for propagation
    mdf = pd.read_csv(mpath)
    # Build ref map name->external_id and code->external_id
    min_by_name = {unidecode(n).lower().strip(): eid for n, eid in zip(mdf['name'], mdf['external_id'])}
    min_by_code = {c: eid for c, eid in zip(mdf['code'], mdf['external_id'])}

    # Process direction.csv
    dpath = GEN / 'direction.csv'
    if dpath.exists():
        ddf = pd.read_csv(dpath)
        if 'name' in ddf.columns:
            ddf['name'] = ddf['name'].map(smart_title)
        # propagate new ministry_code/id
        if 'ministry_code' in ddf.columns:
            ddf['ministry_code'] = ddf['ministry_code'].astype(str).str.upper().str.replace(r"[^A-Z0-9]","", regex=True)
            ddf['ministry_id/id'] = ddf['ministry_code'].map(lambda c: min_by_code.get(c, ''))
        ddf.to_csv(dpath, index=False)
        print(f"Updated direction.csv ({len(ddf)} rows)")

    # Process service.csv
    spath = GEN / 'service.csv'
    if spath.exists():
        sdf = pd.read_csv(spath)
        if 'name' in sdf.columns:
            sdf['name'] = sdf['name'].map(smart_title)
        sdf.to_csv(spath, index=False)
        print(f"Updated service.csv ({len(sdf)} rows)")

if __name__ == '__main__':
    main()
