# Guide d'import - Organigramme Administration Sénégalaise

## 1. Prérequis

### Environnement Python
- **Python** : 3.10 ou supérieur
- **pip** : Gestionnaire de paquets Python

### Dépendances Python
Installer les dépendances requises :
```bash
cd /home/grand-as/psagsn/custom_addons/sn_admin
pip install -r requirements.txt
```

**Packages installés** :
- `pandas>=2.0.0` : Manipulation de données
- `openpyxl>=3.1.0` : Lecture de fichiers Excel
- `email-validator>=2.0.0` : Validation d'emails
- `phonenumbers>=8.13.0` : Validation de téléphones
- `python-slugify>=8.0.0` : Génération de slugs
- `unidecode>=1.3.0` : Suppression d'accents

### Environnement Odoo
- **Odoo** : Version 18 Community Edition
- **Modules requis** :
  - `base` : Modèles de base Odoo (pré-installé)
  - `hr` : Gestion des employés
  - `website` : Portail public (pour Phase 4)

### Vérification de l'installation
```bash
# Vérifier Python
python3 --version

# Vérifier les packages
pip list | grep -E "pandas|openpyxl|email-validator|phonenumbers"

# Vérifier Odoo
odoo --version
```

## 2. Extraction des données

### Étape 2.1 : Lister les feuilles disponibles

```bash
cd /home/grand-as/psagsn/custom_addons/sn_admin/scripts
python extract_xlsx.py --list-sheets
```

**Sortie attendue** :
```
Feuilles disponibles:
  1. Organigramme
  2. Ministères
  3. Directions
  ...
```

### Étape 2.2 : Extraire toutes les feuilles en CSV

```bash
python extract_xlsx.py --all --format csv --output-dir ../data/extracted/
```

**Options disponibles** :
- `--all` : Extraire toutes les feuilles
- `--sheet "Nom"` : Extraire une feuille spécifique
- `--format csv` : Format CSV (défaut)
- `--format json` : Format JSON
- `--output-dir PATH` : Répertoire de sortie

**Résultat** :
- Fichiers CSV dans `data/extracted/`
- Log détaillé dans `scripts/extraction.log`

### Étape 2.3 : Vérifier les fichiers extraits

```bash
ls -lh ../data/extracted/
head -n 5 ../data/extracted/*.csv
```

## 3. Normalisation des données

### Étape 3.1 : Normaliser avec rapport de qualité

```bash
python normalize_data.py \
  --input ../data/extracted/ \
  --output ../data/normalized/ \
  --report \
  --fix-errors
```

**Options disponibles** :
- `--input PATH` : Répertoire des fichiers bruts
- `--output PATH` : Répertoire de sortie
- `--report` : Générer un rapport de qualité
- `--fix-errors` : Corriger automatiquement les erreurs (recommandé)
- `--strict` : Mode strict (rejeter les enregistrements invalides)
- `--verbose` : Afficher plus de détails

**Transformations appliquées** :
1. **Noms de colonnes** : minuscules, underscores
2. **Noms propres** : Première lettre en majuscule
3. **Codes** : Majuscules, alphanumériques uniquement
4. **Emails** : Minuscules, validation RFC 5322
5. **Téléphones** : Format international +221
6. **URLs** : Ajout de http:// si absent
7. **Doublons** : Suppression automatique

**Résultat** :
- Fichiers normalisés dans `data/normalized/`
- Rapport de qualité dans `data/normalized/quality_report.txt`
- Log des erreurs dans `scripts/normalization_errors.log`

### Étape 3.2 : Consulter le rapport de qualité

```bash
cat ../data/normalized/quality_report.txt
```

**Exemple de rapport** :
```
=== RAPPORT DE VALIDATION ===

Lignes totales traitées: 1250
Lignes valides: 1198
Lignes rejetées: 52

⚠ 45 avertissements:
  - organigramme.csv ligne 23: Email invalide "contact@sante" (manque domaine)
  - organigramme.csv ligne 67: Téléphone invalide "33 823 00 50" (manque +221)
  ...

✗ 7 erreurs:
  - ministeres.csv ligne 12: Code "M" trop court (min 2 caractères)
  - directions.csv ligne 89: Direction orpheline (ministère "MINF" introuvable)
  ...
```

### Étape 3.3 : Corriger les erreurs manuellement (si nécessaire)

Si des erreurs bloquantes sont détectées :
1. Ouvrir les fichiers CSV dans `data/normalized/`
2. Corriger les valeurs invalides
3. Relancer la normalisation

## 4. Génération du mapping Odoo

### Étape 4.1 : Générer le mapping avec analyse

```bash
python generate_odoo_mapping.py \
  --input ../data/normalized/ \
  --output ../data/odoo_mapping.json \
  --analyze
```

**Options disponibles** :
- `--input PATH` : Répertoire des fichiers normalisés
- `--output PATH` : Fichier JSON de sortie
- `--analyze` : Générer un rapport d'analyse détaillé
- `--verbose` : Mode verbeux

**Résultat** :
- Fichier de mapping dans `data/odoo_mapping.json`
- Rapport d'analyse dans `data/mapping_analysis.txt`
- Log dans `scripts/mapping.log`

### Étape 4.2 : Consulter le mapping généré

```bash
cat ../data/odoo_mapping.json | python -m json.tool
```

**Structure du mapping** :
```json
{
  "metadata": {
    "version": "1.0",
    "odoo_version": "18.0",
    "generated_from": "../data/normalized/",
    "files_analyzed": 3
  },
  "models": {
    "sn.ministry": {
      "description": "Ministères et institutions",
      "source_files": ["ministeres_normalized.csv"],
      "fields": {
        "name": {
          "type": "char",
          "source_columns": ["nom_ministere"],
          "required": true
        },
        "code": {
          "type": "char",
          "source_columns": ["code_ministere", "code"],
          "required": true
        },
        ...
      },
      "required_fields": ["name", "code"],
      "relations": {}
    },
    "sn.direction": {...},
    "sn.service": {...},
    "sn.agent": {...}
  }
}
```

### Étape 4.3 : Consulter le rapport d'analyse

```bash
cat ../data/mapping_analysis.txt
```

## 5. Validation manuelle

### Étape 5.1 : Vérifier les fichiers normalisés

```bash
# Compter les enregistrements par fichier
wc -l ../data/normalized/*.csv

# Vérifier les colonnes
head -n 1 ../data/normalized/*.csv

# Rechercher des valeurs suspectes
grep -i "null\|n/a\|--" ../data/normalized/*.csv
```

### Étape 5.2 : Vérifier la cohérence hiérarchique

```bash
# Lister les ministères uniques
cut -d',' -f1 ../data/normalized/ministeres_normalized.csv | sort -u

# Vérifier les références parent-enfant
# (À adapter selon la structure réelle des fichiers)
```

### Étape 5.3 : Corriger les anomalies

Si des incohérences sont détectées :
1. Éditer les fichiers CSV dans `data/normalized/`
2. Respecter le format : colonnes en minuscules, valeurs normalisées
3. Sauvegarder en UTF-8

## 6. Import dans Odoo (Phase 2)

**Note** : Cette étape sera détaillée dans la Phase 2 (Modélisation Odoo).

### Option 1 : Import via fichiers XML de données

Les données normalisées seront converties en fichiers XML Odoo :
```xml
<odoo>
  <data noupdate="1">
    <record id="ministry_health" model="sn.ministry">
      <field name="name">Ministère de la Santé et de l'Action Sociale</field>
      <field name="code">MSAS</field>
      <field name="type">ministry</field>
      <field name="phone">+221 33 823 00 50</field>
      <field name="email">contact@sante.gouv.sn</field>
      <field name="website">http://sante.gouv.sn</field>
    </record>
    ...
  </data>
</odoo>
```

### Option 2 : Import via interface Odoo

1. Aller dans **Settings > Technical > Import**
2. Sélectionner le modèle (ex: `sn.ministry`)
3. Charger le fichier CSV normalisé
4. Mapper les colonnes aux champs Odoo
5. Valider et importer

### Option 3 : Import via script Python/ORM

```python
import csv
from odoo import api, SUPERUSER_ID

with api.Environment.manage():
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    with open('data/normalized/ministeres_normalized.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            env['sn.ministry'].create({
                'name': row['nom_ministere'],
                'code': row['code'],
                'phone': row['telephone'],
                'email': row['email'],
                ...
            })
```

## 7. Champs obligatoires par modèle

### sn.ministry (modèle autonome)

**Note** : `sn.ministry` est un modèle autonome qui définit tous ses champs directement, sans héritage externe.
- ✓ `name` : Nom du ministère (unique)
- ✓ `code` : Code court (unique, 2-10 caractères)
- `type` : Type d'institution (ministry/presidency/primature)
- `address` : Adresse physique
- `phone` : Téléphone
- `email` : Email
- `website` : Site web
- `description` : Description des missions

### sn.direction
- ✓ `name` : Nom de la direction
- ✓ `ministry_id` : Référence au ministère parent (Many2one)
- `code` : Code court
- `type` : Type de direction (generale/regionale/technique)
- `manager_id` : Responsable (Many2one → hr.employee)
- `phone` : Téléphone
- `email` : Email

### sn.service
- ✓ `name` : Nom du service
- ✓ `direction_id` : Référence à la direction parente (Many2one)
- `code` : Code court
- `type` : Type de service (service/bureau/cellule/division)
- `manager_id` : Responsable (Many2one → hr.employee)
- `phone` : Téléphone
- `email` : Email

### sn.agent
- ✓ `name` : Nom complet ou référence à hr.employee
- ✓ `function` : Fonction/poste
- ✓ `service_id` : Référence au service (Many2one)
- `employee_id` : Lien vers hr.employee (Many2one, optionnel)
- `work_phone` : Téléphone bureau
- `mobile_phone` : Téléphone mobile
- `work_email` : Email professionnel
- `matricule` : Matricule (unique)

## 8. Contraintes de validation

### Contraintes de format

#### Emails
- **Regex** : `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$`
- **Exemple valide** : contact@sante.gouv.sn
- **Exemple invalide** : contact@sante, @gouv.sn

#### Téléphones
- **Format** : `+221 XX XXX XX XX` (Sénégal)
- **Regex** : `^\+221\s?[0-9]{2}\s?[0-9]{3}\s?[0-9]{2}\s?[0-9]{2}$`
- **Exemple valide** : +221 33 823 00 50
- **Exemple invalide** : 33 823 00 50, +221 123

#### Codes
- **Longueur** : 2-10 caractères
- **Format** : Lettres majuscules et chiffres uniquement
- **Exemple valide** : MSAS, DGS, SRH01
- **Exemple invalide** : M, ms-as, DGS 01

### Contraintes hiérarchiques

1. **Pas de cycles** : Un service ne peut pas être son propre parent
2. **Profondeur max** : 4 niveaux (Ministère → Direction → Service → Sous-service)
3. **Cohérence géographique** : Directions régionales doivent avoir une région
4. **Unicité** : Codes ministères et directions doivent être uniques

### Contraintes métier

1. **Présidence unique** : Un seul enregistrement avec `type="presidency"`
2. **Codes réservés** : "PR" (Présidence), "PM" (Primature)
3. **Responsable actif** : Si renseigné, doit être un employé actif
4. **Taille service** : Max 50 agents par service (warning)

## 9. Exemples de données complètes

### Exemple 1 : Ministère de la Santé

**Ministère** :
```csv
nom_ministere,code,type,adresse,telephone,email,site_web,description
"Ministère de la Santé et de l'Action Sociale",MSAS,ministry,"Fann Résidence, Dakar",+221 33 823 00 50,contact@sante.gouv.sn,http://sante.gouv.sn,"Système de santé publique et action sociale"
```

**Direction** :
```csv
nom_direction,code_direction,type_direction,ministere,responsable,telephone,email
"Direction Générale de la Santé",DGS,generale,MSAS,"Dr. Amadou DIOP",+221 33 821 00 00,dgs@sante.gouv.sn
```

**Service** :
```csv
nom_service,code_service,type_service,direction,responsable,telephone,email
"Service des Ressources Humaines",SRH,service,DGS,"Mme Fatou SALL",+221 33 821 00 10,srh@sante.gouv.sn
```

**Agent** :
```csv
nom,prenom,fonction,service,matricule,telephone_bureau,telephone_mobile,email
DIOP,Amadou,"Directeur Général",DGS,SN-2024-001234,+221 33 821 00 00,+221 77 123 45 67,adiop@sante.gouv.sn
```

### Exemple 2 : Présidence de la République

**Institution** :
```csv
nom_ministere,code,type,adresse,telephone,email,site_web
"Présidence de la République",PR,presidency,"Avenue Léopold Sédar Senghor, Dakar",+221 33 889 20 00,contact@presidence.sn,http://presidence.sn
```

### Exemple 3 : Direction Régionale

**Direction** :
```csv
nom_direction,code_direction,type_direction,ministere,region,responsable,telephone,email
"Direction Régionale de la Santé de Dakar",DRSD,regionale,MSAS,Dakar,"Dr. Ousmane NDIAYE",+221 33 XXX XX XX,drsd@sante.gouv.sn
```

## 10. Dépannage

### Problème : Erreur d'encodage

**Symptôme** :
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Solution** :
```bash
# Vérifier l'encodage du fichier
file -i ../data/extracted/fichier.csv

# Convertir en UTF-8 si nécessaire
iconv -f ISO-8859-1 -t UTF-8 fichier.csv > fichier_utf8.csv

# Ou spécifier l'encodage dans le script
python extract_xlsx.py --encoding latin-1
```

### Problème : Doublons détectés

**Symptôme** :
```
⚠ 12 doublons détectés et supprimés
```

**Solution** :
1. Consulter le rapport de qualité
2. Identifier les doublons (même nom + code)
3. Fusionner manuellement les enregistrements
4. Relancer la normalisation

### Problème : Relations manquantes

**Symptôme** :
```
✗ Direction orpheline (ministère "MINF" introuvable)
```

**Solution** :
1. Vérifier que le ministère parent existe
2. Corriger le code du ministère dans le fichier directions
3. Ou créer le ministère manquant
4. Importer dans l'ordre hiérarchique : Ministères → Directions → Services → Agents

### Problème : Champs obligatoires manquants

**Symptôme** :
```
✗ Champ obligatoire 'name' manquant ligne 45
```

**Solution** :
1. Ouvrir le fichier CSV
2. Remplir le champ manquant
3. Sauvegarder et relancer la normalisation

### Problème : Format de téléphone invalide

**Symptôme** :
```
⚠ Téléphone invalide: "33 823 00 50"
```

**Solution** :
Le script corrige automatiquement avec `--fix-errors` :
- Ajoute +221 si absent
- Formate avec espaces : +221 33 823 00 50

Si la correction échoue, vérifier manuellement le numéro.

## 11. Commandes utiles

### Workflow complet en une seule commande

```bash
#!/bin/bash
cd /home/grand-as/psagsn/custom_addons/sn_admin/scripts

# 1. Extraction
python extract_xlsx.py --all --format csv --output-dir ../data/extracted/

# 2. Normalisation
python normalize_data.py \
  --input ../data/extracted/ \
  --output ../data/normalized/ \
  --report \
  --fix-errors

# 3. Mapping
python generate_odoo_mapping.py \
  --input ../data/normalized/ \
  --output ../data/odoo_mapping.json \
  --analyze

# 4. Afficher le résumé
echo "=== RÉSUMÉ ==="
cat ../data/normalized/quality_report.txt
echo ""
echo "=== MAPPING ==="
cat ../data/mapping_analysis.txt
```

### Vérification rapide

```bash
# Compter les enregistrements
wc -l ../data/normalized/*.csv

# Lister les ministères
cut -d',' -f1 ../data/normalized/ministeres_normalized.csv | tail -n +2 | sort

# Rechercher un ministère spécifique
grep -i "santé" ../data/normalized/*.csv
```

## 12. Prochaines étapes

Une fois les données extraites, normalisées et validées :

1. **Phase 2 : Modélisation Odoo**
   - Créer les modèles Python (`sn.ministry`, `sn.direction`, `sn.service`, `sn.agent`)
   - Définir les champs, relations et contraintes
   - Créer les règles de sécurité et groupes d'accès

2. **Phase 3 : Intégration RH**
   - Créer les vues (tree, form, kanban)
   - Implémenter la recherche et les filtres
   - Créer les menus et actions

3. **Phase 4 : Portail citoyen**
   - Créer la page publique de l'organigramme
   - Implémenter la navigation hiérarchique
   - Ajouter la recherche d'interlocuteurs

## Support

Pour toute question ou problème :
- Consulter `DATA_SCHEMA.md` pour la structure des données
- Consulter `FIELD_MAPPING.md` pour le mapping des champs
- Consulter `VALIDATION_RULES.md` pour les règles de validation
- Consulter les logs dans `scripts/*.log`
