#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
from unidecode import unidecode

BASE = Path(__file__).resolve().parents[1]
GEN = BASE / 'data' / 'generated'
REF = BASE / 'data' / 'reference'
REF.mkdir(parents=True, exist_ok=True)

min_df = pd.read_csv(GEN / 'ministry.csv') if (GEN / 'ministry.csv').exists() else None
if min_df is None or min_df.empty:
    raise SystemExit('No ministry.csv found in generated/')

# Prepare mapping template: normalized key, original name, current code, desired_code (to fill), notes
out = pd.DataFrame({
    'key': min_df['name'].map(lambda s: unidecode(str(s)).lower().strip()),
    'name': min_df['name'],
    'current_code': min_df['code'],
    'desired_code': [''] * len(min_df),
    'notes': [''] * len(min_df),
})
# Drop duplicates by key to keep one row per ministry name
out = out.drop_duplicates(subset=['key']).sort_values('name')

path = REF / 'ministry_codes.csv'
out.to_csv(path, index=False)
print('Wrote mapping template:', path)
