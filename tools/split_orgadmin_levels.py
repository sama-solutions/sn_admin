#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import re
from pathlib import Path
from typing import Dict, Tuple

# Input: orgadmin.csv with columns: Niveau 1, Niveau 2, Niveau 3, Niveau 4
# Output:
# - orgadmin_level1.csv: id,name
# - orgadmin_level2.csv: id,name,parent_level1
# - orgadmin_level3.csv: id,name,parent_level1,parent_level2
# - orgadmin_level4.csv: id,name,parent_level1,parent_level2,parent_level3


def slugify(s: str) -> str:
    t = s.strip().lower()
    # remove accents basic
    accents = str.maketrans({
        'à':'a','â':'a','ä':'a','ç':'c','é':'e','è':'e','ê':'e','ë':'e',
        'î':'i','ï':'i','ô':'o','ö':'o','ù':'u','û':'u','ü':'u','ÿ':'y',
        'À':'a','Â':'a','Ä':'a','Ç':'c','É':'e','È':'e','Ê':'e','Ë':'e',
        'Î':'i','Ï':'i','Ô':'o','Ö':'o','Ù':'u','Û':'u','Ü':'u','Ÿ':'y',
        'œ':'oe','Œ':'oe'
    })
    t = t.translate(accents)
    t = re.sub(r"[^a-z0-9]+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    if not t:
        t = "item"
    return t


def main():
    if len(sys.argv) < 2:
        print("Usage: split_orgadmin_levels.py <input_orgadmin_csv>")
        sys.exit(1)

    input_csv = Path(sys.argv[1])
    if not input_csv.exists():
        print(f"Input file not found: {input_csv}")
        sys.exit(2)

    with input_csv.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Maps for unique nodes per level
    l1_map: Dict[str, str] = {}  # name -> id
    l2_map: Dict[Tuple[str, str], str] = {}  # (l1, name) -> id
    l3_map: Dict[Tuple[str, str, str], str] = {}  # (l1, l2, name) -> id
    l4_map: Dict[Tuple[str, str, str, str], str] = {}  # (l1, l2, l3, name) -> id

    def get_l1_id(name: str) -> str:
        name = name.strip()
        if not name:
            return ''
        if name not in l1_map:
            l1_map[name] = f"L1_{slugify(name)}"
        return l1_map[name]

    def get_l2_id(l1: str, name: str) -> str:
        name = name.strip()
        if not name:
            return ''
        key = (l1, name)
        if key not in l2_map:
            l2_map[key] = f"L2_{slugify(l1)}__{slugify(name)}"
        return l2_map[key]

    def get_l3_id(l1: str, l2: str, name: str) -> str:
        name = name.strip()
        if not name:
            return ''
        key = (l1, l2, name)
        if key not in l3_map:
            l3_map[key] = f"L3_{slugify(l1)}__{slugify(l2)}__{slugify(name)}"
        return l3_map[key]

    def get_l4_id(l1: str, l2: str, l3: str, name: str) -> str:
        name = name.strip()
        if not name:
            return ''
        key = (l1, l2, l3, name)
        if key not in l4_map:
            l4_map[key] = f"L4_{slugify(l1)}__{slugify(l2)}__{slugify(l3)}__{slugify(name)}"
        return l4_map[key]

    # Build maps from rows
    for r in rows:
        l1 = (r.get('Niveau 1') or '').strip()
        l2 = (r.get('Niveau 2') or '').strip()
        l3 = (r.get('Niveau 3') or '').strip()
        l4 = (r.get('Niveau 4') or '').strip()

        if l1:
            get_l1_id(l1)
        if l2:
            get_l2_id(l1, l2)
        if l3:
            get_l3_id(l1, l2, l3)
        if l4:
            get_l4_id(l1, l2, l3, l4)

    base = input_csv.parent

    # Write L1
    with (base / 'orgadmin_level1.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name'])
        for name, _id in sorted(l1_map.items(), key=lambda x: x[0].lower()):
            w.writerow([_id, name])

    # Write L2
    with (base / 'orgadmin_level2.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'parent_level1'])
        for (l1, name), _id in sorted(l2_map.items(), key=lambda x: (x[0][0].lower(), x[0][1].lower())):
            w.writerow([_id, name, l1_map.get(l1, '')])

    # Write L3
    with (base / 'orgadmin_level3.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'parent_level1', 'parent_level2'])
        for (l1, l2, name), _id in sorted(l3_map.items(), key=lambda x: (x[0][0].lower(), x[0][1].lower(), x[0][2].lower())):
            w.writerow([_id, name, l1_map.get(l1, ''), l2_map.get((l1, l2), '')])

    # Write L4
    with (base / 'orgadmin_level4.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'parent_level1', 'parent_level2', 'parent_level3'])
        for (l1, l2, l3, name), _id in sorted(l4_map.items(), key=lambda x: (x[0][0].lower(), x[0][1].lower(), x[0][2].lower(), x[0][3].lower())):
            w.writerow([_id, name, l1_map.get(l1, ''), l2_map.get((l1, l2), ''), l3_map.get((l1, l2, l3), '')])

    print("Wrote:")
    print(f" - {base / 'orgadmin_level1.csv'} ({len(l1_map)} rows)")
    print(f" - {base / 'orgadmin_level2.csv'} ({len(l2_map)} rows)")
    print(f" - {base / 'orgadmin_level3.csv'} ({len(l3_map)} rows)")
    print(f" - {base / 'orgadmin_level4.csv'} ({len(l4_map)} rows)")


if __name__ == '__main__':
    main()
