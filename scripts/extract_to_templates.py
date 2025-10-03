#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
import pandas as pd
from unidecode import unidecode
from slugify import slugify

# Simple normalizers based on doc/FIELD_MAPPING.md

def normalize_title(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = s.strip()
    # Title case with basic French stop handling
    return ' '.join([w.capitalize() if not w.isupper() else w for w in s.split()])

def normalize_code(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = unidecode(s)
    s = ''.join(ch for ch in s if ch.isalnum())
    return s.upper()

def normalize_email(s: str) -> str:
    if not isinstance(s, str):
        return s
    return s.strip().lower()

def normalize_phone(sn: str) -> str:
    if not isinstance(sn, str):
        return sn
    digits = ''.join(ch for ch in sn if ch.isdigit())
    if digits.startswith('221'):
        digits = digits
    elif digits.startswith('0') and len(digits) == 10:
        digits = '221' + digits[1:]
    elif len(digits) == 9:
        digits = '221' + digits
    # format +221 XX XXX XX XX
    if len(digits) == 12 and digits.startswith('221'):
        return f"+221 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"
    return f"+{digits}" if not sn.startswith('+') else sn

def first_nonnull(row, cols):
    for c in cols:
        if c in row and pd.notna(row[c]) and str(row[c]).strip() != '':
            return row[c]
    return None

# Column maps: destination -> list of candidate source names (lowercased)
MINISTRY_MAP = {
    'name': ['nom_ministere', 'nom_du_ministere', 'ministere', 'name'],
    'code': ['code_ministere', 'code'],
    'type': ['type_ministere', 'type'],
    'address': ['adresse', 'address'],
    'phone': ['telephone', 'phone'],
    'email': ['email'],
    'website': ['site_web', 'website'],
    'description': ['description'],
}

DIRECTION_MAP = {
    'name': ['nom_direction', 'direction', 'name'],
    'code': ['code_direction', 'code'],
    'type': ['type_direction', 'type'],
    'ministry_code': ['code_ministere', 'ministere_code', 'ministry_code'],
    'ministry_name': ['ministere', 'ministry', 'ministry_name'],
    'region': ['region'],
    'manager_name': ['responsable', 'nom_responsable', 'manager_name'],
    'phone': ['telephone', 'phone'],
    'email': ['email'],
    'address': ['adresse', 'address'],
    'description': ['description'],
}

SERVICE_MAP = {
    'name': ['nom_service', 'service', 'name'],
    'code': ['code_service', 'code'],
    'type': ['type_service', 'type'],
    'direction_code': ['code_direction', 'direction_code'],
    'direction_name': ['direction', 'direction_name'],
    'manager_name': ['responsable', 'chef_service', 'manager_name'],
    'phone': ['telephone', 'phone'],
    'email': ['email'],
    'address': ['adresse', 'address'],
    'description': ['description'],
}

AGENT_MAP = {
    'name': ['nom_complet', 'nom complet', 'name', 'nom'],
    'first_name': ['prenom', 'first_name'],
    'last_name': ['nom', 'last_name'],
    'function': ['fonction', 'poste', 'function'],
    'service_code': ['code_service', 'service_code'],
    'service_name': ['service', 'service_name'],
    'matricule': ['matricule'],
    'work_phone': ['telephone_bureau', 'work_phone'],
    'mobile_phone': ['telephone_mobile', 'mobile_phone'],
    'work_email': ['email', 'email_professionnel', 'work_email'],
    'nomination_date': ['date_prise_service', 'nomination_date'],
    'nomination_decree': ['nomination_decree', 'numero_decret'],
    'is_interim': ['interim', 'is_interim'],
}

SHEET_CANDIDATES = {
    'ministries': ['Ministères', 'Ministries', 'ministeres', 'Ministry', 'sn.ministry'],
    'directions': ['Directions', 'sn.direction'],
    'services': ['Services', 'sn.service'],
    'agents': ['Agents', 'sn.agent', 'Employés', 'Employees'],
    # Fallback sheet that can contain all
    'organigram': ['Organigramme', 'Orgchart']
}

TYPE_MAP_MINISTRY = {
    'presidence': 'presidency',
    'présidence': 'presidency',
    'primature': 'primature',
    'ministere': 'ministry',
    'ministère': 'ministry',
}

TYPE_MAP_DIRECTION = {
    'generale': 'generale',
    'générale': 'generale',
    'regionale': 'regionale',
    'régionale': 'regionale',
    'technique': 'technique',
    'inspection': 'technique',
    'secretariat': 'technique',
    'secrétariat': 'technique',
}

TYPE_MAP_SERVICE = {
    'service': 'service',
    'bureau': 'bureau',
    'cellule': 'cellule',
    'division': 'division',
}

def pick(df: pd.DataFrame, keys):
    cols = [c for c in keys if c in df.columns]
    return df[cols] if cols else pd.DataFrame(columns=[])


def build_external_id(prefix: str, code: str, name: str) -> str:
    code_part = normalize_code(str(code)) if pd.notna(code) and str(code).strip() else ''
    if code_part:
        return f"{prefix}_{code_part.lower()}"
    # fallback from name
    if isinstance(name, str) and name:
        return f"{prefix}_{slugify(unidecode(name))[:30]}"
    return f"{prefix}_unknown"


def extract_ministries(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        name = first_nonnull(row, MINISTRY_MAP['name'])
        code = first_nonnull(row, MINISTRY_MAP['code'])
        if not name or not code:
            continue
        mtype = first_nonnull(row, MINISTRY_MAP['type']) or 'ministry'
        mtype_norm = TYPE_MAP_MINISTRY.get(str(mtype).strip().lower(), 'ministry')
        address = first_nonnull(row, MINISTRY_MAP['address'])
        phone = normalize_phone(str(first_nonnull(row, MINISTRY_MAP['phone']))) if first_nonnull(row, MINISTRY_MAP['phone']) else ''
        email = normalize_email(str(first_nonnull(row, MINISTRY_MAP['email']))) if first_nonnull(row, MINISTRY_MAP['email']) else ''
        website = first_nonnull(row, MINISTRY_MAP['website'])
        desc = first_nonnull(row, MINISTRY_MAP['description'])
        out.append({
            'external_id': build_external_id('ministry', code, name),
            'name': normalize_title(str(name)),
            'code': normalize_code(str(code)),
            'type': mtype_norm,
            'address': address or '',
            'phone': phone,
            'email': email,
            'website': website or '',
            'description': desc or '',
        })
    return pd.DataFrame(out)


def extract_directions(df: pd.DataFrame, ministries_df: pd.DataFrame) -> pd.DataFrame:
    # Build ministry lookups by code and name
    min_by_code = {row['code']: row['external_id'] for _, row in ministries_df.iterrows()}
    min_by_name = {row['name'].lower(): row['external_id'] for _, row in ministries_df.iterrows()}

    out = []
    for _, row in df.iterrows():
        name = first_nonnull(row, DIRECTION_MAP['name'])
        min_code = first_nonnull(row, DIRECTION_MAP['ministry_code'])
        min_name = first_nonnull(row, DIRECTION_MAP['ministry_name'])
        if not name or (not min_code and not min_name):
            continue
        code = first_nonnull(row, DIRECTION_MAP['code']) or ''
        dtype = first_nonnull(row, DIRECTION_MAP['type']) or 'generale'
        dtype_norm = TYPE_MAP_DIRECTION.get(str(dtype).strip().lower(), 'generale')
        ministry_ext = None
        if min_code:
            ministry_ext = min_by_code.get(normalize_code(str(min_code)))
        if not ministry_ext and isinstance(min_name, str):
            ministry_ext = min_by_name.get(normalize_title(min_name).lower())
        phone = normalize_phone(str(first_nonnull(row, DIRECTION_MAP['phone']))) if first_nonnull(row, DIRECTION_MAP['phone']) else ''
        email = normalize_email(str(first_nonnull(row, DIRECTION_MAP['email']))) if first_nonnull(row, DIRECTION_MAP['email']) else ''
        out.append({
            'external_id': build_external_id('direction', code, name),
            'name': normalize_title(str(name)),
            'code': normalize_code(str(code)) if code else '',
            'type': dtype_norm,
            'ministry_code': normalize_code(str(min_code)) if min_code else '',
            'ministry_id/id': ministry_ext or '',
            'region': first_nonnull(row, DIRECTION_MAP['region']) or '',
            'manager_name': first_nonnull(row, DIRECTION_MAP['manager_name']) or '',
            'phone': phone,
            'email': email,
            'address': first_nonnull(row, DIRECTION_MAP['address']) or '',
            'description': first_nonnull(row, DIRECTION_MAP['description']) or '',
        })
    return pd.DataFrame(out)


def extract_services(df: pd.DataFrame, directions_df: pd.DataFrame) -> pd.DataFrame:
    dir_by_code = {}
    for _, row in directions_df.iterrows():
        code = str(row.get('code') or '').strip()
        if code:
            dir_by_code[normalize_code(code)] = row['external_id']
        # also index by name
        dir_by_code[slugify(row['name']).upper()] = row['external_id']

    out = []
    for _, row in df.iterrows():
        name = first_nonnull(row, SERVICE_MAP['name'])
        dcode = first_nonnull(row, SERVICE_MAP['direction_code'])
        dname = first_nonnull(row, SERVICE_MAP['direction_name'])
        if not name or (not dcode and not dname):
            continue
        code = first_nonnull(row, SERVICE_MAP['code']) or ''
        stype = first_nonnull(row, SERVICE_MAP['type']) or 'service'
        stype_norm = TYPE_MAP_SERVICE.get(str(stype).strip().lower(), 'service')
        dir_ext = None
        if dcode:
            dir_ext = dir_by_code.get(normalize_code(str(dcode)))
        if not dir_ext and isinstance(dname, str):
            dir_ext = dir_by_code.get(slugify(normalize_title(dname)).upper())
        phone = normalize_phone(str(first_nonnull(row, SERVICE_MAP['phone']))) if first_nonnull(row, SERVICE_MAP['phone']) else ''
        email = normalize_email(str(first_nonnull(row, SERVICE_MAP['email']))) if first_nonnull(row, SERVICE_MAP['email']) else ''
        out.append({
            'external_id': build_external_id('service', code, name),
            'name': normalize_title(str(name)),
            'code': normalize_code(str(code)) if code else '',
            'type': stype_norm,
            'direction_code': normalize_code(str(dcode)) if dcode else '',
            'direction_id/id': dir_ext or '',
            'manager_name': first_nonnull(row, SERVICE_MAP['manager_name']) or '',
            'phone': phone,
            'email': email,
            'address': first_nonnull(row, SERVICE_MAP['address']) or '',
            'description': first_nonnull(row, SERVICE_MAP['description']) or '',
        })
    return pd.DataFrame(out)


def extract_agents(df: pd.DataFrame, services_df: pd.DataFrame) -> pd.DataFrame:
    svc_by_code = {}
    for _, row in services_df.iterrows():
        code = str(row.get('code') or '').strip()
        if code:
            svc_by_code[normalize_code(code)] = row['external_id']
        svc_by_code[slugify(row['name']).upper()] = row['external_id']

    out = []
    for _, row in df.iterrows():
        name = first_nonnull(row, AGENT_MAP['name'])
        if not name:
            # try build from first/last name
            fn = first_nonnull(row, AGENT_MAP['first_name']) or ''
            ln = first_nonnull(row, AGENT_MAP['last_name']) or ''
            name = f"{fn} {ln}".strip()
        svc_code = first_nonnull(row, AGENT_MAP['service_code'])
        svc_name = first_nonnull(row, AGENT_MAP['service_name'])
        if not name or (not svc_code and not svc_name):
            continue
        function = first_nonnull(row, AGENT_MAP['function']) or 'Agent'
        svc_ext = None
        if svc_code:
            svc_ext = svc_by_code.get(normalize_code(str(svc_code)))
        if not svc_ext and isinstance(svc_name, str):
            svc_ext = svc_by_code.get(slugify(normalize_title(svc_name)).upper())
        out.append({
            'external_id': build_external_id('agent', first_nonnull(row, AGENT_MAP['matricule']) or '', name),
            'name': normalize_title(str(name)),
            'first_name': normalize_title(str(first_nonnull(row, AGENT_MAP['first_name']) or '')),
            'last_name': normalize_title(str(first_nonnull(row, AGENT_MAP['last_name']) or '')),
            'function': normalize_title(str(function)),
            'service_code': normalize_code(str(svc_code)) if svc_code else '',
            'service_id/id': svc_ext or '',
            'matricule': first_nonnull(row, AGENT_MAP['matricule']) or '',
            'work_phone': normalize_phone(str(first_nonnull(row, AGENT_MAP['work_phone']))) if first_nonnull(row, AGENT_MAP['work_phone']) else '',
            'mobile_phone': normalize_phone(str(first_nonnull(row, AGENT_MAP['mobile_phone']))) if first_nonnull(row, AGENT_MAP['mobile_phone']) else '',
            'work_email': normalize_email(str(first_nonnull(row, AGENT_MAP['work_email']))) if first_nonnull(row, AGENT_MAP['work_email']) else '',
            'nomination_date': first_nonnull(row, AGENT_MAP['nomination_date']) or '',
            'nomination_decree': first_nonnull(row, AGENT_MAP['nomination_decree']) or '',
            'is_interim': first_nonnull(row, AGENT_MAP['is_interim']) or '',
        })
    return pd.DataFrame(out)


def load_xlsx(path: Path) -> dict:
    try:
        xls = pd.ExcelFile(path)
    except Exception as e:
        print(f"Erreur d'ouverture du fichier Excel: {e}", file=sys.stderr)
        sys.exit(1)
    sheets = {}
    for key, names in SHEET_CANDIDATES.items():
        for n in names:
            if n in xls.sheet_names:
                sheets[key] = xls.parse(n)
                break
    # Fallback: map any remaining from first sheet
    if 'ministries' not in sheets:
        sheets['ministries'] = xls.parse(xls.sheet_names[0])
    return sheets


def main():
    parser = argparse.ArgumentParser(description='Extraire snadmin.xlsx vers CSV templates Odoo')
    parser.add_argument('--xlsx', default=str(Path(__file__).resolve().parents[1] / 'snadmin.xlsx'), help='Chemin du fichier Excel source')
    parser.add_argument('--out', default=str(Path(__file__).resolve().parents[1] / 'data' / 'generated'), help='Répertoire de sortie')
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    sheets = load_xlsx(xlsx_path)

    # Normalize columns to lowercase without accents/extra spaces
    for k, df in sheets.items():
        df.columns = [unidecode(str(c)).strip().lower() for c in df.columns]
        sheets[k] = df

    # Extract per model
    ministries_df = extract_ministries(sheets.get('ministries', pd.DataFrame()))
    if not ministries_df.empty:
        ministries_df.to_csv(out_dir / 'ministry.csv', index=False)
        print(f"OK: ministry.csv ({len(ministries_df)} lignes)")

    directions_df = pd.DataFrame()
    if 'directions' in sheets:
        directions_df = extract_directions(sheets['directions'], ministries_df)
        if not directions_df.empty:
            directions_df.to_csv(out_dir / 'direction.csv', index=False)
            print(f"OK: direction.csv ({len(directions_df)} lignes)")

    services_df = pd.DataFrame()
    if 'services' in sheets:
        services_df = extract_services(sheets['services'], directions_df)
        if not services_df.empty:
            services_df.to_csv(out_dir / 'service.csv', index=False)
            print(f"OK: service.csv ({len(services_df)} lignes)")

    if 'agents' in sheets:
        agents_df = extract_agents(sheets['agents'], services_df)
        if not agents_df.empty:
            agents_df.to_csv(out_dir / 'agent.csv', index=False)
            print(f"OK: agent.csv ({len(agents_df)} lignes)")

    # If a monolithic organigram sheet exists, try best-effort split
    if 'organigram' in sheets and (ministries_df.empty or directions_df.empty or services_df.empty):
        org = sheets['organigram']
        # Heuristics: try to separate by presence of columns
        if ministries_df.empty:
            ministries_df = extract_ministries(org)
            if not ministries_df.empty:
                ministries_df.to_csv(out_dir / 'ministry.csv', index=False)
                print(f"OK: ministry.csv depuis Organigramme ({len(ministries_df)} lignes)")
        if directions_df.empty:
            directions_df = extract_directions(org, ministries_df)
            if not directions_df.empty:
                directions_df.to_csv(out_dir / 'direction.csv', index=False)
                print(f"OK: direction.csv depuis Organigramme ({len(directions_df)} lignes)")
        if services_df.empty:
            services_df = extract_services(org, directions_df)
            if not services_df.empty:
                services_df.to_csv(out_dir / 'service.csv', index=False)
                print(f"OK: service.csv depuis Organigramme ({len(services_df)} lignes)")

    print("Terminé. Fichiers générés dans:", out_dir)


if __name__ == '__main__':
    main()
