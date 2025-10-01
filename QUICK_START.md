# Guide de démarrage rapide - Phase 1

## Installation (1 minute)

```bash
cd /home/grand-as/psagsn/custom_addons/sn_admin
pip install -r requirements.txt
```

## Workflow complet (5 minutes)

```bash
cd scripts

# 1. Extraction (30 secondes)
python extract_xlsx.py --all --format csv --output-dir ../data/extracted/

# 2. Normalisation (1 minute)
python normalize_data.py --input ../data/extracted/ --output ../data/normalized/ --report --fix-errors

# 3. Mapping (10 secondes)
python generate_odoo_mapping.py --input ../data/normalized/ --output ../data/odoo_mapping.json --analyze

# 4. Résultats
echo "=== RAPPORT DE QUALITÉ ==="
cat ../data/normalized/quality_report.txt
echo ""
echo "=== MAPPING ODOO ==="
cat ../data/mapping_analysis.txt
```

## Vérification rapide

```bash
# Compter les enregistrements
wc -l ../data/normalized/*.csv

# Lister les ministères
cut -d',' -f1 ../data/normalized/*ministere*.csv 2>/dev/null | tail -n +2 | sort -u

# Vérifier les erreurs
grep -i "erreur\|error" ../data/normalized/quality_report.txt
```

## Documentation

- **README.md** : Vue d'ensemble complète
- **doc/IMPORT_GUIDE.md** : Guide détaillé étape par étape
- **doc/DATA_SCHEMA.md** : Structure des données
- **doc/FIELD_MAPPING.md** : Mapping Excel → Odoo
- **doc/VALIDATION_RULES.md** : Règles de validation
- **PHASE1_SUMMARY.md** : Résumé de l'implémentation

## Commandes utiles

### Lister les feuilles Excel
```bash
cd scripts
python extract_xlsx.py --list-sheets
```

### Extraire une seule feuille
```bash
python extract_xlsx.py --sheet "Organigramme" --format csv --output-dir ../data/extracted/
```

### Normalisation en mode strict
```bash
python normalize_data.py --input ../data/extracted/ --output ../data/normalized/ --strict --verbose
```

### Rechercher dans les données
```bash
# Rechercher un ministère
grep -i "santé" ../data/normalized/*.csv

# Rechercher un email
grep -E "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}" ../data/normalized/*.csv

# Compter les directions par ministère
cut -d',' -f4 ../data/normalized/*direction*.csv 2>/dev/null | tail -n +2 | sort | uniq -c
```

## Dépannage rapide

### Erreur : Module pandas non trouvé
```bash
pip install pandas openpyxl
```

### Erreur : Fichier Excel introuvable
Vérifier que `snadmin.xlsx` existe dans le répertoire racine du module.

### Erreur : Permission denied
```bash
chmod +x scripts/*.py
```

### Erreur : Encodage
```bash
# Vérifier l'encodage
file -i ../data/extracted/*.csv

# Convertir si nécessaire
iconv -f ISO-8859-1 -t UTF-8 fichier.csv > fichier_utf8.csv
```

## Prochaines étapes

Une fois les données extraites et validées :

1. **Phase 2** : Créer les modèles Odoo (sn.ministry, sn.direction, sn.service, sn.agent)
2. **Phase 3** : Créer les vues et menus
3. **Phase 4** : Créer le portail public

Consulter `README.md` pour plus de détails.

## Support

- Logs : `scripts/*.log`
- Rapport de qualité : `data/normalized/quality_report.txt`
- Documentation complète : `doc/`
