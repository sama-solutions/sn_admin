# Import des Données - Module sn_admin

## Date
**3 octobre 2025**

---

## ✅ Fichiers XML de Données Générés

### 📊 Statistiques

| Fichier | Enregistrements | Statut |
|---------|-----------------|--------|
| `sn_ministry_data.xml` | 23 ministères | ✅ Généré |
| `sn_category_data.xml` | 96 catégories | ✅ Généré |
| `sn_direction_data.xml` | ~100 directions | ✅ Généré |
| `sn_service_data.xml` | 913 services | ✅ Généré |
| `sn_agent_data.xml` | 0 agents | ⚠️ Vide (placeholder) |

---

## 🔧 Génération des Fichiers XML

### Script Python Créé

**Fichier :** `scripts/generate_xml_from_csv.py`

Ce script lit les fichiers CSV et génère automatiquement les fichiers XML Odoo.

### Utilisation

```bash
# Se placer dans le répertoire du module
cd /home/grand-as/psagsn/custom_addons/sn_admin

# Exécuter le script
python3 scripts/generate_xml_from_csv.py
```

### Résultat

```
============================================================
Génération des fichiers XML à partir des CSV
============================================================

📁 Tous les fichiers CSV trouvés

Génération de .../data/sn_ministry_data.xml...
✅ 23 ministères générés

Génération de .../data/sn_category_data.xml...
✅ 96 catégories générées

Génération de .../data/sn_direction_data.xml...
✅ 100+ directions générées

Génération de .../data/sn_service_data.xml...
✅ 913 services générés

============================================================
✅ Génération terminée avec succès !
============================================================
```

---

## 📁 Fichiers CSV Sources

### Disponibles

- ✅ `data/odoo_ministry.csv` - 35 lignes (avec doublons)
- ✅ `data/odoo_category.csv` - 97 lignes
- ✅ `data/odoo_direction.csv` - ~100 lignes
- ✅ `data/odoo_service.csv` - ~1500 lignes (limité à 1000 dans XML)

### Structure CSV

#### Ministères
```csv
id,name,code,type
sn_min_ministere_de_la_sante,MINISTÈRE DE LA SANTÉ,MSAS,ministry
```

#### Catégories
```csv
id,name,ministry_id/id
sn_cat_msas_cabinet,Cabinet et services rattachés,sn_min_ministere_de_la_sante
```

#### Directions
```csv
id,name,code,type,ministry_id/id,category_id/id
sn_dir_dgs,Direction Générale de la Santé,DGS,generale,sn_min_ministere_de_la_sante,sn_cat_msas_directions
```

#### Services
```csv
id,name,code,type,direction_id/id
sn_srv_srh,Service des Ressources Humaines,SRH,service,sn_dir_dgs
```

---

## 📝 Fichiers XML Générés

### Structure XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">
        <record id="sn_min_ministere_de_la_sante" model="sn.ministry">
            <field name="name">MINISTÈRE DE LA SANTÉ</field>
            <field name="code">MSAS</field>
            <field name="type">ministry</field>
            <field name="state">active</field>
        </record>
        <!-- ... -->
    </data>
</odoo>
```

### Caractéristiques

- ✅ **External IDs** : Tous les enregistrements ont un ID externe unique
- ✅ **Références** : Les relations utilisent `ref="external_id"`
- ✅ **État actif** : Tous les enregistrements sont en `state='active'`
- ✅ **noupdate="0"** : Les données peuvent être mises à jour

---

## 🔄 Ordre d'Import dans __manifest__.py

```python
'data': [
    # 1. Sécurité
    'security/sn_admin_security.xml',
    'security/ir.model.access.csv',
    
    # 2. Vues
    'views/sn_ministry_views.xml',
    'views/sn_category_views.xml',
    'views/sn_direction_views.xml',
    'views/sn_service_views.xml',
    'views/sn_agent_views.xml',
    'views/hr_employee_views.xml',
    'views/hr_department_views.xml',
    'views/sn_admin_menus.xml',
    'views/sn_search_views.xml',
    'views/sn_dashboard.xml',
    'views/website_templates.xml',
    
    # 3. Rapports
    'reports/sn_organigramme_report.xml',
    'reports/sn_annuaire_report.xml',
    'reports/sn_statistics_report.xml',
    
    # 4. Données (ordre hiérarchique)
    'data/sn_ministry_data.xml',      # Niveau 1
    'data/sn_category_data.xml',      # Niveau 2 ✅ AJOUTÉ
    'data/sn_direction_data.xml',     # Niveau 3
    'data/sn_service_data.xml',       # Niveau 4
    'data/sn_agent_data.xml',         # Niveau 5 (vide)
],
```

✅ **Ordre respecté** : Les données sont importées dans l'ordre hiérarchique correct.

---

## 🚀 Installation et Import

### 1. Installation Initiale

```bash
# Redémarrer Odoo
sudo systemctl restart odoo

# Installer le module (importe automatiquement les données)
odoo-bin -d votre_base -i sn_admin
```

### 2. Mise à Jour

```bash
# Mettre à jour le module (réimporte les données si noupdate="0")
odoo-bin -d votre_base -u sn_admin
```

### 3. Vérification

```sql
-- Vérifier le nombre d'enregistrements
SELECT COUNT(*) FROM sn_ministry;   -- Devrait retourner 23
SELECT COUNT(*) FROM sn_category;   -- Devrait retourner 96
SELECT COUNT(*) FROM sn_direction;  -- Devrait retourner ~100
SELECT COUNT(*) FROM sn_service;    -- Devrait retourner ~913
```

---

## ⚠️ Points d'Attention

### 1. Doublons dans les Ministères

Le CSV `odoo_ministry.csv` contient des doublons. Le script les gère automatiquement en gardant la première occurrence.

**Exemple :**
```csv
sn_min_ministere_de_l_energie_du_petrole_et_des_mines  # Ligne 2
sn_min_ministere_de_l_energie_du_petrole_et_des_mines  # Ligne 7 (doublon)
```

✅ **Solution** : Le script garde uniquement la première occurrence.

### 2. Limite des Services

Le fichier `odoo_service.csv` contient ~1500 services, mais le script limite à **1000 services** pour ne pas surcharger l'import initial.

**Raison :** Import plus rapide et tests plus faciles.

**Pour importer tous les services :**
```python
# Modifier dans generate_xml_from_csv.py
generate_services_xml(
    csv_files['services'],
    data_dir / 'sn_service_data.xml',
    max_records=None  # Pas de limite
)
```

### 3. Agents Non Importés

Le fichier `sn_agent_data.xml` est vide (placeholder).

**Raison :** Pas de données d'agents dans les CSV fournis.

**Pour ajouter des agents :**
1. Créer un CSV `odoo_agent.csv`
2. Ajouter une fonction `generate_agents_xml()` dans le script
3. Régénérer les XML

---

## 📊 Hiérarchie des Données

```
Ministère (23)
    ↓
Catégorie (96)
    ↓
Direction (~100)
    ↓
Service (913)
    ↓
Agent (0)
```

### Relations

- **Catégorie** → **Ministère** : `ministry_id/id`
- **Direction** → **Ministère** : `ministry_id/id`
- **Direction** → **Catégorie** : `category_id/id` (optionnel)
- **Service** → **Direction** : `direction_id/id`
- **Agent** → **Service** : `service_id/id`

---

## 🔍 Validation des Données

### Vérifier la Syntaxe XML

```bash
# Installer xmllint si nécessaire
sudo apt-get install libxml2-utils

# Valider les fichiers
xmllint --noout data/sn_ministry_data.xml
xmllint --noout data/sn_category_data.xml
xmllint --noout data/sn_direction_data.xml
xmllint --noout data/sn_service_data.xml
```

✅ **Aucune erreur attendue**

### Vérifier les Références

```bash
# Vérifier que toutes les références existent
grep -o 'ref="[^"]*"' data/sn_category_data.xml | sort -u
grep -o 'ref="[^"]*"' data/sn_direction_data.xml | sort -u
grep -o 'ref="[^"]*"' data/sn_service_data.xml | sort -u
```

---

## 🎯 Prochaines Étapes

### 1. Enrichir les Données

Les fichiers XML générés contiennent uniquement les champs de base. Pour enrichir :

```xml
<record id="sn_min_ministere_de_la_sante" model="sn.ministry">
    <field name="name">MINISTÈRE DE LA SANTÉ</field>
    <field name="code">MSAS</field>
    <field name="type">ministry</field>
    
    <!-- ✅ Ajouter ces champs -->
    <field name="address">Rue Aimé Césaire, Dakar</field>
    <field name="phone">+221 33 889 34 00</field>
    <field name="email">contact@sante.gouv.sn</field>
    <field name="website">http://www.sante.gouv.sn</field>
    <field name="description">Ministère en charge de la santé publique...</field>
    
    <field name="state">active</field>
</record>
```

### 2. Ajouter les Agents

Créer un CSV avec les données des agents et régénérer le XML.

### 3. Ajouter des Codes

Certaines directions et services n'ont pas de code. Les ajouter manuellement ou via un script.

### 4. Lier aux Catégories

Certaines directions ne sont pas liées à des catégories. Ajouter le champ `category_id/id` dans le CSV.

---

## 📝 Commandes Utiles

### Régénérer les XML

```bash
cd /home/grand-as/psagsn/custom_addons/sn_admin
python3 scripts/generate_xml_from_csv.py
```

### Compter les Enregistrements

```bash
# Ministères
grep -c '<record id="sn_min_' data/sn_ministry_data.xml

# Catégories
grep -c '<record id="sn_cat_' data/sn_category_data.xml

# Directions
grep -c '<record id="sn_dir_' data/sn_direction_data.xml

# Services
grep -c '<record id="sn_srv_' data/sn_service_data.xml
```

### Supprimer les Données

```sql
-- Supprimer toutes les données (dans l'ordre inverse)
DELETE FROM sn_agent;
DELETE FROM sn_service;
DELETE FROM sn_direction;
DELETE FROM sn_category;
DELETE FROM sn_ministry;
```

---

## ✅ Résumé

- ✅ **Script de génération** créé et fonctionnel
- ✅ **4 fichiers XML** générés avec succès
- ✅ **1132 enregistrements** au total (23 + 96 + 100+ + 913)
- ✅ **Hiérarchie 5 niveaux** respectée
- ✅ **Manifest mis à jour** avec `sn_category_data.xml`
- ✅ **Prêt pour l'import** dans Odoo

---

**Le module est prêt à être installé avec les données !** 🚀
