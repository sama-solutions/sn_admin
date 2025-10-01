# Scripts d'extraction et normalisation

## Vue d'ensemble

Ce répertoire contient les utilitaires Python pour extraire, nettoyer et préparer les données de l'organigramme sénégalais depuis le fichier Excel `snadmin.xlsx`.

## Scripts disponibles

### 1. `extract_xlsx.py`

**Objectif** : Extraire les feuilles Excel en fichiers CSV/JSON.

**Usage** :
```bash
# Extraire toutes les feuilles en CSV
python extract_xlsx.py --all --format csv --output-dir ../data/extracted/

# Extraire une feuille spécifique en JSON
python extract_xlsx.py --sheet "Organigramme" --format json --output-dir ../data/extracted/

# Aide
python extract_xlsx.py --help
```

**Options** :
- `--sheet NAME` : Nom de la feuille à extraire (défaut: toutes)
- `--all` : Extraire toutes les feuilles
- `--format {csv,json}` : Format de sortie (défaut: csv)
- `--output-dir PATH` : Répertoire de sortie (défaut: ../data/extracted/)
- `--encoding ENCODING` : Encodage (défaut: utf-8)
- `--verbose` : Mode verbeux

**Sortie** :
- Fichiers CSV : `{sheet_name}.csv`
- Fichiers JSON : `{sheet_name}.json`
- Log : `extraction.log`

### 2. `normalize_data.py`

**Objectif** : Nettoyer, valider et normaliser les données extraites.

**Usage** :
```bash
# Normaliser avec rapport de qualité
python normalize_data.py --input ../data/extracted/ --output ../data/normalized/ --report

# Normaliser sans rapport
python normalize_data.py --input ../data/extracted/ --output ../data/normalized/

# Aide
python normalize_data.py --help
```

**Options** :
- `--input PATH` : Répertoire des fichiers CSV bruts
- `--output PATH` : Répertoire de sortie
- `--report` : Générer un rapport de qualité
- `--fix-errors` : Corriger automatiquement les erreurs mineures
- `--strict` : Mode strict (rejeter les enregistrements invalides)
- `--verbose` : Mode verbeux

**Sortie** :
- Fichiers CSV normalisés : `{sheet_name}_normalized.csv`
- Rapport de qualité : `quality_report.txt`
- Log des erreurs : `normalization_errors.log`

**Transformations appliquées** :
- Noms de colonnes : minuscules, underscores
- Noms propres : première lettre en majuscule
- Codes : majuscules
- Emails : minuscules, validation RFC 5322
- Téléphones : format international +221
- Suppression des doublons
- Validation hiérarchique

### 3. `generate_odoo_mapping.py`

**Objectif** : Générer le fichier de mapping entre données normalisées et modèles Odoo.

**Usage** :
```bash
# Générer le mapping
python generate_odoo_mapping.py --input ../data/normalized/ --output ../data/odoo_mapping.json

# Avec analyse détaillée
python generate_odoo_mapping.py --input ../data/normalized/ --output ../data/odoo_mapping.json --analyze

# Aide
python generate_odoo_mapping.py --help
```

**Options** :
- `--input PATH` : Répertoire des fichiers normalisés
- `--output PATH` : Fichier JSON de sortie
- `--analyze` : Analyser la structure et proposer des modèles
- `--verbose` : Mode verbeux

**Sortie** :
- Fichier JSON : `odoo_mapping.json`
- Rapport d'analyse : `mapping_analysis.txt` (si --analyze)

## Workflow complet

```bash
# 1. Installer les dépendances
pip install -r ../requirements.txt

# 2. Extraire les données
python extract_xlsx.py --all --format csv --output-dir ../data/extracted/

# 3. Normaliser et valider
python normalize_data.py --input ../data/extracted/ --output ../data/normalized/ --report --fix-errors

# 4. Générer le mapping Odoo
python generate_odoo_mapping.py --input ../data/normalized/ --output ../data/odoo_mapping.json --analyze

# 5. Vérifier les résultats
cat ../data/normalized/quality_report.txt
cat ../data/odoo_mapping.json
```

## Gestion des erreurs

### Erreurs courantes

**Fichier Excel introuvable** :
```
FileNotFoundError: [Errno 2] No such file or directory: '../snadmin.xlsx'
```
→ Vérifier le chemin du fichier Excel

**Feuille inexistante** :
```
ValueError: Worksheet 'Organigramme' not found
```
→ Lister les feuilles disponibles : `python extract_xlsx.py --list-sheets`

**Erreur d'encodage** :
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```
→ Spécifier l'encodage : `--encoding latin-1`

**Dépendances manquantes** :
```
ModuleNotFoundError: No module named 'pandas'
```
→ Installer : `pip install -r ../requirements.txt`

## Logs

Tous les scripts génèrent des logs dans le répertoire courant :
- `extraction.log` : Détails de l'extraction
- `normalization_errors.log` : Erreurs de normalisation
- `mapping.log` : Génération du mapping

## Tests

Pour tester les scripts sur un échantillon :
```bash
# Extraire seulement la première feuille
python extract_xlsx.py --sheet 0 --output-dir ../data/test/

# Normaliser en mode strict
python normalize_data.py --input ../data/test/ --output ../data/test_normalized/ --strict --verbose
```

## Contribution

Pour ajouter de nouvelles règles de validation :
1. Éditer `normalize_data.py`
2. Ajouter la règle dans la section "Validation rules"
3. Mettre à jour `../doc/VALIDATION_RULES.md`
4. Tester sur un échantillon

## Support

Consulter la documentation complète dans `../doc/IMPORT_GUIDE.md`.
