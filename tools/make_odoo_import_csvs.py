#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import re
from pathlib import Path
from typing import Dict, Tuple

# Generate Odoo-import-ready CSVs from orgadmin.csv (4-level file)
# Output files in data/ (created if missing):
# - odoo_ministry.csv: id,name,code,type
# - odoo_category.csv: id,name,authority_id/id
# - odoo_direction.csv: id,name,ministry_id/id,category_id/id
# - odoo_service.csv: id,name,direction_id/id


def slugify(s: str) -> str:
    t = s.strip().lower()
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
    return t or 'item'


def make_ministry_code(name: str) -> str:
    base = slugify(name)
    # take initials of words to build a compact code up to 8 chars
    words = [w for w in re.split(r"[_\s]+", base) if w]
    initials = ''.join(w[0] for w in words)[:8].upper()
    if len(initials) < 3:
        initials = (base[:8]).upper()
    return initials


def ministry_type_from_name(name: str) -> str:
    n = name.strip().upper()
    if n.startswith('PRÉSIDENCE') or n.startswith('PRESIDENCE'):
        return 'presidency'
    if n.startswith('PRIMATURE'):
        return 'primature'
    return 'ministry'


def main():
    if len(sys.argv) < 2:
        print("Usage: make_odoo_import_csvs.py <input_orgadmin_csv>")
        sys.exit(1)

    input_csv = Path(sys.argv[1])
    if not input_csv.exists():
        print(f"Input file not found: {input_csv}")
        sys.exit(2)

    with input_csv.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Maps for unique nodes per level
    l1_map: Dict[str, str] = {}  # name -> external id
    l2_map: Dict[Tuple[str, str], str] = {}  # (l1, name) -> external id
    l3_map: Dict[Tuple[str, str, str], str] = {}  # (l1, l2, name) -> external id
    l4_map: Dict[Tuple[str, str, str, str], str] = {}  # (l1, l2, l3, name) -> external id

    # Prepare unique sets
    for r in rows:
        l1 = (r.get('Niveau 1') or '').strip()
        l2 = (r.get('Niveau 2') or '').strip()
        l3 = (r.get('Niveau 3') or '').strip()
        l4 = (r.get('Niveau 4') or '').strip()

        if l1:
            l1_map.setdefault(l1, f"sn_min_{slugify(l1)}")
        if l2:
            l2_map.setdefault((l1, l2), f"sn_cat_{slugify(l1)}__{slugify(l2)}")
        if l3:
            l3_map.setdefault((l1, l2, l3), f"sn_dir_{slugify(l1)}__{slugify(l2)}__{slugify(l3)}")
        if l4:
            l4_map.setdefault((l1, l2, l3, l4), f"sn_srv_{slugify(l1)}__{slugify(l2)}__{slugify(l3)}__{slugify(l4)}")

    out_dir = input_csv.parent / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Ministries
    with (out_dir / 'odoo_ministry.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'code', 'type'])
        for name, ext_id in sorted(l1_map.items(), key=lambda x: x[0].lower()):
            w.writerow([ext_id, name, make_ministry_code(name), ministry_type_from_name(name)])

    # Categories
    with (out_dir / 'odoo_category.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'ministry_id/id'])
        for (l1, name), ext_id in sorted(l2_map.items(), key=lambda x: (x[0][0].lower(), x[0][1].lower())):
            w.writerow([ext_id, name, l1_map.get(l1, '')])

    # Directions (N3)
    with (out_dir / 'odoo_direction.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'ministry_id/id', 'category_id/id'])
        for (l1, l2, name), ext_id in sorted(l3_map.items(), key=lambda x: (x[0][0].lower(), x[0][1].lower(), x[0][2].lower())):
            w.writerow([ext_id, name, l1_map.get(l1, ''), l2_map.get((l1, l2), '')])

    # Services (N4)
    with (out_dir / 'odoo_service.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'direction_id/id'])
        for (l1, l2, l3, name), ext_id in sorted(l4_map.items(), key=lambda x: (x[0][0].lower(), x[0][1].lower(), x[0][2].lower(), x[0][3].lower())):
            w.writerow([ext_id, name, l3_map.get((l1, l2, l3), '')])

    print('Wrote Odoo import CSVs in', out_dir)


if __name__ == '__main__':
    main()
