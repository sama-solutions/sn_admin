#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Optional

from docx import Document
from docx.oxml.ns import qn
from unidecode import unidecode
from slugify import slugify
import pandas as pd

# --- Normalizers (shared with xlsx extractor style) ---

def normalize_title(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = s.strip()
    s = s.replace('\n', ' ')
    # Title case but keep acronyms
    words = []
    for w in s.split():
        if w.isupper() and len(w) <= 6:
            words.append(w)
        else:
            words.append(w.capitalize())
    return ' '.join(words)


def normalize_code(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = unidecode(s)
    s = ''.join(ch for ch in s if ch.isalnum())
    return s.upper()


def build_external_id(prefix: str, code: str, name: str) -> str:
    code_part = normalize_code(str(code)) if code else ''
    if code_part:
        return f"{prefix}_{code_part.lower()}"
    if isinstance(name, str) and name:
        return f"{prefix}_{slugify(unidecode(name))[:30]}"
    return f"{prefix}_unknown"

# --- Heuristics ---
MINISTRY_KEYWORDS = [
    'ministère', 'ministere', 'présidence', 'presidence', 'primature', 'presidency'
]
DIRECTION_KEYWORDS = ['direction', 'inspection', 'secrétariat général', 'secretariat general', 'secrétariat du conseil', 'secretariat du conseil']
SERVICE_KEYWORDS = ['service', 'bureau', 'cellule', 'division']
SERVICE_EXTRA_KEYWORDS = [
    'secrétariat technique', 'secretariat technique',
    'secrétariat permanent', 'secretariat permanent',
    'unité', 'unite', 'antenne', 'observatoire', 'guichet', 'plateforme', 'plate-forme',
    'comité technique', 'comite technique', 'comité national', 'comite national',
]

# Special name -> code map
SPECIAL_MIN_CODES = {
    'présidence de la république': 'PR',
    'presidence de la republique': 'PR',
    'primature': 'PM',
}


def guess_ministry_code(name: str) -> str:
    key = unidecode(name).lower().strip()
    if key in SPECIAL_MIN_CODES:
        return SPECIAL_MIN_CODES[key]
    # Build acronym from capitalized words/first letters
    tokens = [t for t in re.split(r"[^A-Za-zÀ-ÿ']+", name) if t]
    letters = []
    for t in tokens:
        if t.isupper() and len(t) <= 5:
            letters.append(t[0])
        elif t[0].isupper():
            letters.append(t[0])
    code = ''.join(letters)[:10]
    return normalize_code(code) if code else ''

def is_bullet(text: str) -> bool:
    return bool(re.match(r"^\s*[-•–]\s*\d*\s*", text))

def clean_line(t: str) -> str:
    t = t.replace('\u00A0', ' ').replace('\u00AD', '')
    t = t.replace('\xa0', ' ').replace('\xad', '')
    t = t.replace('\n', ' ').replace('\r', ' ')
    # Fix words split by NBSP around capitals like "Répu blique"
    t = re.sub(r"([A-Za-zÀ-ÿ])\s+([A-Za-zÀ-ÿ])", r"\1 \2", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip(' -•–:\t\r\n ')

def split_items(text: str):
    """Split a long line into candidate items using semicolons and bullet-like separators.
    Returns cleaned non-empty parts.
    """
    # Replace long dashes with semicolons as separators
    s = re.sub(r"[•–]\s*", "; ", text)
    # Split on semicolons and numbered markers like '1°', '2°'
    parts = re.split(r";|\s\d+°\s", s)
    out = []
    for p in parts:
        c = clean_line(p)
        if c:
            out.append(c)
    return out

def get_num_level(paragraph) -> int:
    """Return numbering level for a paragraph if any, else -1."""
    p = paragraph._p
    pPr = p.pPr
    if pPr is None:
        return -1
    numPr = pPr.numPr
    if numPr is None:
        return -1
    ilvl = numPr.ilvl
    if ilvl is None:
        return 0
    try:
        return int(ilvl.val)
    except Exception:
        return 0


def main():
    base = Path(__file__).resolve().parents[1]
    docx_path = base / 'snadmin.docx'
    out_dir = base / 'data' / 'generated'
    out_dir.mkdir(parents=True, exist_ok=True)

    if not docx_path.exists():
        print('Fichier DOCX introuvable:', docx_path, file=sys.stderr)
        sys.exit(1)

    doc = Document(str(docx_path))

    ministries = []
    directions = []
    services = []

    current_min = None
    current_dir = None

    def push_min(name: str):
        nonlocal current_min
        name_n = normalize_title(name)
        code = guess_ministry_code(name_n)
        rec = {
            'external_id': build_external_id('ministry', code, name_n),
            'name': name_n,
            'code': code or '',
            'type': 'ministry' if 'minist' in unidecode(name).lower() else (
                'presidency' if 'presid' in unidecode(name).lower() else (
                    'primature' if 'primature' in unidecode(name).lower() else 'ministry'
                )
            ),
            'address': '', 'phone': '', 'email': '', 'website': '', 'description': ''
        }
        ministries.append(rec)
        current_min = rec

    def push_dir(name: str):
        nonlocal current_dir
        if not current_min:
            return
        name_n = normalize_title(name)
        # Try to derive short code from words containing uppercase/initial letter
        code_guess = ''.join([w[0] for w in name_n.split() if w and w[0].isalpha()])[:10]
        code = normalize_code(code_guess)
        rec = {
            'external_id': build_external_id('direction', code, name_n),
            'name': name_n,
            'code': code,
            'type': 'generale',
            'ministry_code': current_min['code'],
            'ministry_id/id': current_min['external_id'],
            'region': '', 'manager_name': '', 'phone': '', 'email': '', 'address': '', 'description': ''
        }
        directions.append(rec)
        current_dir = rec

    def push_service(name: str):
        if not current_dir:
            return
        name_n = normalize_title(name)
        code_guess = ''.join([w[0] for w in name_n.split() if w and w[0].isalpha()])[:10]
        code = normalize_code(code_guess)
        rec = {
            'external_id': build_external_id('service', code, name_n),
            'name': name_n,
            'code': code,
            'type': 'service',
            'direction_code': current_dir['code'],
            'direction_id/id': current_dir['external_id'],
            'manager_name': '', 'phone': '', 'email': '', 'address': '', 'description': ''
        }
        services.append(rec)

    # Pass 1: line-based parsing
    lines = []
    for p in doc.paragraphs:
        t = p.text
        if not t or not t.strip():
            continue
        level = get_num_level(p)
        cleaned = clean_line(t)
        if not cleaned:
            continue
        lines.append((cleaned, level))

    # Heuristic: when line contains a ministry keyword in Title/ALL CAPS, start a ministry
    for s, level in lines:
        s_l = unidecode(s).lower()
        if any(k in s_l for k in MINISTRY_KEYWORDS) and (s.isupper() or 'minist' in s_l or 'presid' in s_l or 'primature' in s_l):
            # Avoid obvious preamble like 'DECRETE' or 'VU la...'
            if 'vu ' in s_l or 'decrete' in s_l or 'article' in s_l:
                continue
            # Try to reduce extra clauses by splitting on ':'
            head = s.split(':', 1)[0]
            # Keep a reasonable length
            if len(head.split()) >= 1 and len(head) <= 200:
                push_min(head)
                continue
        # Direction: level 0 bullets/numbering or lines containing keywords right after a ministry
        if level == 0 and any(k in s_l for k in DIRECTION_KEYWORDS):
            push_dir(s)
            continue
        # Service: level 1+ bullets/numbering under a direction
        if level >= 1 and (any(k in s_l for k in SERVICE_KEYWORDS) or any(k in s_l for k in SERVICE_EXTRA_KEYWORDS)):
            push_service(s)
            continue
        # Fallback: textual bullets
        if is_bullet(s) and any(k in s_l for k in DIRECTION_KEYWORDS):
            name = clean_line(re.sub(r"^[-•–]\s+", "", s))
            push_dir(name)
            continue
        if is_bullet(s) and (any(k in s_l for k in SERVICE_KEYWORDS) or any(k in s_l for k in SERVICE_EXTRA_KEYWORDS)):
            name = clean_line(re.sub(r"^[-•–]\s+", "", s))
            push_service(name)
            continue

        # Extra: split long list lines into items under current ministry/direction
        # If we have a current ministry and the line contains semicolons, attempt to extract items
        if current_min and (';' in s or re.search(r"\d+°", s)):
            items = split_items(s)
            for it in items:
                it_l = unidecode(it).lower()
                if any(k in it_l for k in DIRECTION_KEYWORDS):
                    push_dir(it)
                elif any(k in it_l for k in SERVICE_KEYWORDS) or any(k in it_l for k in SERVICE_EXTRA_KEYWORDS):
                    push_service(it)
            continue

        # Fallback: under a current direction, classify sublevel text without direction keywords as service
        if current_dir and level >= 1 and not any(k in s_l for k in DIRECTION_KEYWORDS):
            # Avoid lines that look like pure articles or decree structure keywords
            if not any(x in s_l for x in ['article', 'vu ', 'decrete', 'considérant', 'considerant']):
                push_service(s)
                continue

    # Deduplicate by name per level
    def dedup(records, key='name'):
        seen = set()
        out = []
        for r in records:
            k = r[key].lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        return out

    ministries_df = pd.DataFrame(dedup(ministries))
    directions_df = pd.DataFrame(dedup(directions))
    services_df = pd.DataFrame(dedup(services))

    # Persist
    if not ministries_df.empty:
        ministries_df.to_csv(out_dir / 'ministry.csv', index=False)
        print(f"OK: ministry.csv ({len(ministries_df)} lignes)")
    if not directions_df.empty:
        directions_df.to_csv(out_dir / 'direction.csv', index=False)
        print(f"OK: direction.csv ({len(directions_df)} lignes)")
    if not services_df.empty:
        services_df.to_csv(out_dir / 'service.csv', index=False)
        print(f"OK: service.csv ({len(services_df)} lignes)")

    if ministries_df.empty and directions_df.empty and services_df.empty:
        print('Aucun élément détecté. Le document semble non structuré en listes. ' \
              'Veuillez fournir un XLSX structuré ou un DOCX avec listes à puces.', file=sys.stderr)
        sys.exit(2)

    print('Terminé. Fichiers générés dans:', out_dir)


if __name__ == '__main__':
    main()
