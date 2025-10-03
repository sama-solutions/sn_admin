#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import csv
from pathlib import Path

"""
Parse orgadmin.txt into a 4-level CSV with columns:
Level1, Level2, Level3, Level4

Heuristics:
- Level 1: Top authority (PRÉSIDENCE, PRIMATURE, MINISTÈRE ...). Detected by:
  * Keyword startswith in {PRÉSIDENCE, PRIMATURE, MINISTÈRE}
  * Or all-uppercase line (letters + spaces + accents + apostrophes) with length > 3
- Level 2: Category under the authority (Cabinet, Secrétariat général, Directions, Autres administrations, Services du Palais ...)
  * Lines like "1° Cabinet ..." or lines ending with ':' and containing category keywords
  * Also tolerate without colon if matches known category tokens
- Level 3: Direction générale / Pôle / Etat-major / Heading ending with ':' that groups granular entities
  * Lines with 'Pôle', 'Direction générale', 'Etat-Major', 'Cabinet militaire', etc. Often ends with ':' but not always
  * When a 'Direction générale ...' appears, it becomes a Level 3 heading until next heading of same or higher level
- Level 4: Granular entities under Level 3 or directly under Level 2 when no Level 3 exists
  * Bullet lines starting with '-', '•', '➢' or plain lines that look like items (end with ';' or '.'),
    or start with common nouns: Service, Bureau, Cellule, Commission, Agence, Autorité, Conseil, Direction (when under a Direction générale), etc.

We try to be conservative: only emit a CSV row when we are reasonably sure it's a Level 4 item.
"""

CATEGORY_KEYWORDS = [
    'cabinet',
    'secrétariat général',
    'secrétariat général du gouvernement',
    'services du palais',
    'autres administrations',
    'directions',
    'services propres',
    'secrétariat général et services rattachés',
    'cabinet civil',
    'cabinet militaire',
]

UPPER_RE = re.compile(r"^[A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ'\-\s]+$")

LEVEL3_HINTS = [
    'pôle',
    'direction générale',
    'direction generale',
    'etat-major',
    'état-major',
    'haute autorité',
    'secrétariat',  # sometimes Level3 headings like "Secrétariat ... :"
]

LEVEL4_START_TOKENS = [
    '-', '•', '➢', '>', '–', '—'
]

LEVEL4_NOUNS = [
    'service', 'bureau', 'cellule', 'commission', 'comité', 'conseil', 'agence', 'autorité', 'fonds', 'centre', 'observatoire', 'office', 'inspection', 'délégation', 'secrétariat', 'grande chancellerie', 'direction', 'unité', 'paierie', 'recette', 'trésorerie', 'école', 'institut', 'fondation'
]

# Numeric prefix pattern (e.g., "1° ", "2)", "3.")
NUM_PREFIX_RE = re.compile(r"^\s*(\d+\s*°?\s*|\d+\)|\d+\.)")

COLON_END_RE = re.compile(r":\s*$")


def normalize(text: str) -> str:
    t = text.strip()
    # remove trailing list punctuation
    t = t.rstrip(' ;·•—–-')
    # collapse internal whitespace
    t = re.sub(r"\s+", " ", t)
    return t

def is_upper_heading(line: str) -> bool:
    t = normalize(line)
    if not t:
        return False
    # Quick keyword checks first
    if t.startswith(('PRÉSIDENCE', 'PRIMATURE', 'MINISTÈRE', 'MINISTERE')):
        return True
    # All uppercase? allow spaces and accents and hyphens/apostrophes
    return bool(UPPER_RE.match(t)) and len(t) >= 4


def extract_level2(line: str) -> str | None:
    t = normalize(line)
    if not t:
        return None
    # e.g., "1° Cabinet ... :" or "2° Secrétariat général ... :"
    m = re.match(r"^(\d+)\s*°\s*(.+)$", t, re.IGNORECASE)
    if m:
        cat = m.group(2)
        cat = normalize(cat)
        cat = cat.rstrip(':')
        return cat
    # lines ending with ':' and containing a category keyword
    if COLON_END_RE.search(t):
        t_no_colon = t[:-1]
        low = t_no_colon.lower()
        for kw in CATEGORY_KEYWORDS:
            if kw in low:
                return normalize(t_no_colon)
    # if contains a category keyword even without colon and short-ish
    low = t.lower()
    for kw in CATEGORY_KEYWORDS:
        if kw in low and len(t) <= 120:
            return t
    return None


def is_level3_heading(line: str) -> bool:
    t = normalize(line)
    if not t:
        return False
    low = t.lower()
    if COLON_END_RE.search(t):
        return True
    for kw in LEVEL3_HINTS:
        if kw in low:
            return True
    # many Level3 are like "Direction générale de ..." without colon
    if low.startswith('direction générale') or low.startswith('direction generale'):
        return True
    if low.startswith('etat-major') or low.startswith('état-major'):
        return True
    return False


def looks_like_level4(line: str, under_dir_generale: bool) -> bool:
    t = normalize(line)
    if not t:
        return False
    # bullets
    if any(t.startswith(tok) for tok in LEVEL4_START_TOKENS):
        return True
    # punctuation style
    if t.endswith(';') or t.endswith('.'):
        return True
    low = t.lower()
    # typical nouns that indicate entities
    if any(low.startswith(noun + ' ') for noun in LEVEL4_NOUNS):
        return True
    # when we are under a 'Direction générale ...', accept child lines starting with 'Direction '
    if under_dir_generale and low.startswith('direction '):
        return True
    # short entries separated by ' ; '
    if ' ; ' in t:
        return True
    return False


def clean_item_text(line: str) -> str:
    t = normalize(line)
    # remove leading bullets or numbers
    t = re.sub(r"^(?:[-•➢>–—]+\s*)", "", t)
    # remove heading-number like '1-' '1.' at start
    t = re.sub(r"^\d+\s*[-.)]\s*", "", t)
    # strip trailing '.' or ';'
    t = t.rstrip(';.')
    return t.strip()


def parse(lines: list[str]):
    rows = []
    L1 = L2 = L3 = ''
    under_dir_generale = False

    def flush_row(level4_text: str):
        rows.append([L1, L2, L3, clean_item_text(level4_text)])

    for raw in lines:
        line = raw.rstrip('\n')
        # skip empty/noise lines
        if not normalize(line):
            continue
        t = normalize(line)

        # Detect Level1
        if is_upper_heading(t):
            L1 = t.rstrip(':')
            L2 = ''
            L3 = ''
            under_dir_generale = False
            continue

        # Detect Level2
        l2 = extract_level2(t)
        if l2:
            L2 = l2
            L3 = ''
            under_dir_generale = False
            continue

        # Detect Level3
        if is_level3_heading(t):
            # treat colon-terminated lines as pure headings
            L3 = t.rstrip(':')
            under_dir_generale = L3.lower().startswith('direction générale') or L3.lower().startswith('direction generale')
            continue

        # Level4 under current context
        if looks_like_level4(t, under_dir_generale):
            flush_row(t)
            continue

        # Fallback: if under a category with no Level3 and line looks like an entity noun, record it
        low = t.lower()
        if L1 and L2 and not L3 and any(low.startswith(noun + ' ') for noun in LEVEL4_NOUNS):
            flush_row(t)
            continue

        # If line contains multiple entries separated by ';', split and add
        if ';' in t and (L1 and (L2 or L3)):
            parts = [p.strip() for p in t.split(';') if p.strip()]
            if len(parts) > 1:
                for p in parts:
                    flush_row(p)
                continue
        # Otherwise, ignore unclassified lines
        # print(f"IGNORED: {t}")

    return rows


def main():
    if len(sys.argv) < 3:
        print("Usage: parse_orgadmin.py <input_txt> <output_csv>")
        sys.exit(1)
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(2)

    # Read as UTF-8 with BOM tolerance
    content = input_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.splitlines()

    rows = parse(lines)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Niveau 1', 'Niveau 2', 'Niveau 3', 'Niveau 4'])
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == '__main__':
    main()
