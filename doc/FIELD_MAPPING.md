# Mapping des champs : Excel → Odoo

Ce document détaille la correspondance entre les colonnes du fichier Excel `snadmin.xlsx` et les champs des modèles Odoo.

## Vue d'ensemble

Le mapping permet de transformer les données brutes Excel en enregistrements Odoo structurés. Chaque modèle Odoo correspond à un niveau hiérarchique de l'administration.

### Modèles Odoo

1. **sn.ministry** : Ministères et institutions (modèle autonome)
2. **sn.direction** : Directions générales, régionales et techniques
3. **sn.service** : Services, bureaux, cellules, divisions
4. **sn.agent** : Agents publics (peut hériter de `hr.employee`)

---

## Modèle : sn.ministry

**Description** : Ministères, Présidence, Primature

**Modèle autonome** : Tous les champs sont définis directement dans `sn.ministry`

### Champs du modèle sn.ministry

| Colonne Excel | Champ Odoo | Type Odoo | Obligatoire | Transformation | Exemple |
|---------------|------------|-----------|-------------|----------------|----------|
| nom_ministere | name | Char | ✓ | `.strip().title()` | "Ministère De La Santé Et De L'Action Sociale" |
| nom_du_ministere | name | Char | ✓ | `.strip().title()` | "Ministère De La Santé" |
| code_ministere | code | Char | ✓ | `.upper().strip()` | "MSAS" |
| code | code | Char | ✓ | `.upper().strip()` | "MEN" |
| type_ministere | type | Selection | | Mapping valeurs | "ministry" |
| type | type | Selection | | Mapping valeurs | "presidency" |
| adresse | address | Text | | `.strip()` | "Fann Résidence, Dakar" |
| telephone | phone | Char | | Format +221 | "+221 33 823 00 50" |
| email | email | Char | | `.lower().strip()` | "contact@sante.gouv.sn" |
| site_web | website | Char | | Ajouter http:// | "http://sante.gouv.sn" |
| description | description | Text | | `.strip()` | "Système de santé publique..." |

### Valeurs du champ type (Selection)

| Valeur Excel | Valeur Odoo | Description |
|--------------|-------------|-------------|
| Présidence | presidency | Présidence de la République |
| Primature | primature | Services du Premier Ministre |
| Ministère | ministry | Ministère |
| (vide) | ministry | Défaut : ministère |

### Champs calculés (non importés)

- `active` : Actif (défaut: True)
- `state` : État (défaut: "draft")

### Contraintes

- `UNIQUE(code)` : Code unique
- `UNIQUE(name)` : Nom unique (ignorer la casse)
- `CHECK(length(code) >= 2 AND length(code) <= 10)` : Longueur du code

### Exemple de mapping

**Excel** :
```csv
nom_ministere,code,type,adresse,telephone,email,site_web
"Ministère de la Santé et de l'Action Sociale",MSAS,Ministère,"Fann Résidence, Dakar",+221 33 823 00 50,contact@sante.gouv.sn,http://sante.gouv.sn
```

**Odoo (XML)** :
```xml
<record id="ministry_msas" model="sn.ministry">
  <field name="name">Ministère De La Santé Et De L'Action Sociale</field>
  <field name="code">MSAS</field>
  <field name="type">ministry</field>
  <field name="address">Fann Résidence, Dakar</field>
  <field name="phone">+221 33 823 00 50</field>
  <field name="email">contact@sante.gouv.sn</field>
  <field name="website">http://sante.gouv.sn</field>
</record>
```

---

## Modèle : sn.direction

**Description** : Directions générales, régionales, techniques, inspections, secrétariats

### Champs

| Colonne Excel | Champ Odoo | Type Odoo | Obligatoire | Relation | Exemple |
|---------------|------------|-----------|-------------|----------|----------|
| nom_direction | name | Char | ✓ | - | "Direction Générale De La Santé" |
| code_direction | code | Char | | - | "DGS" |
| code | code | Char | | - | "DRH" |
| ministere | ministry_id | Many2one | ✓ | → sn.ministry | Recherche par nom normalisé |
| code_ministere | ministry_id | Many2one | ✓ | → sn.ministry | Recherche par code |
| type_direction | type | Selection | | - | "generale" |
| type | type | Selection | | - | "regionale" |
| region | region_id | Many2one | | → res.country.state | ref('state_dakar') |
| responsable | manager_id | Many2one | | → hr.employee | Recherche par nom |
| nom_responsable | manager_id | Many2one | | → hr.employee | - |
| telephone | phone | Char | | - | "+221 33 XXX XX XX" |
| email | email | Char | | - | "dgs@sante.gouv.sn" |
| adresse | address | Text | | - | "Rue X, Dakar" |
| description | description | Text | | - | "Missions de la direction..." |

### Valeurs du champ type (Selection)

| Valeur Excel | Valeur Odoo | Description |
|--------------|-------------|-------------|
| Générale | generale | Direction Générale |
| Régionale | regionale | Direction Régionale |
| Technique | technique | Direction Technique |
| Inspection | inspection | Inspection |
| Secrétariat | secretariat | Secrétariat Général |
| (vide) | generale | Défaut |

### Relations

- **ministry_id** (Many2one → sn.ministry) : Ministère parent
  - Recherche par `code` ou `name`
  - Obligatoire
  
- **manager_id** (Many2one → hr.employee) : Responsable
  - Recherche par `name`
  - Optionnel
  
- **region_id** (Many2one → res.country.state) : Région
  - Pour directions régionales uniquement
  - Recherche par `name` (ex: "Dakar", "Thiès")

### Contraintes

- `UNIQUE(code, ministry_id)` : Code unique par ministère
- `CHECK(type='regionale' IMPLIES region_id IS NOT NULL)` : Région obligatoire pour directions régionales

### Exemple de mapping

**Excel** :
```csv
nom_direction,code_direction,type_direction,ministere,responsable,telephone,email
"Direction Générale de la Santé",DGS,Générale,MSAS,"Dr. Amadou DIOP",+221 33 821 00 00,dgs@sante.gouv.sn
```

**Odoo (XML)** :
```xml
<record id="direction_dgs" model="sn.direction">
  <field name="name">Direction Générale De La Santé</field>
  <field name="code">DGS</field>
  <field name="type">generale</field>
  <field name="ministry_id" ref="ministry_msas"/>
  <field name="phone">+221 33 821 00 00</field>
  <field name="email">dgs@sante.gouv.sn</field>
</record>
```

---

## Modèle : sn.service

**Description** : Services, bureaux, cellules, divisions

### Champs

| Colonne Excel | Champ Odoo | Type Odoo | Obligatoire | Relation | Exemple |
|---------------|------------|-----------|-------------|----------|----------|
| nom_service | name | Char | ✓ | - | "Service Des Ressources Humaines" |
| code_service | code | Char | | - | "SRH" |
| code | code | Char | | - | "BAJ" |
| direction | direction_id | Many2one | ✓ | → sn.direction | Recherche par nom normalisé |
| code_direction | direction_id | Many2one | ✓ | → sn.direction | Recherche par code |
| type_service | type | Selection | | - | "service" |
| type | type | Selection | | - | "bureau" |
| responsable | manager_id | Many2one | | → hr.employee | Recherche par nom |
| chef_service | manager_id | Many2one | | → hr.employee | - |
| telephone | phone | Char | | - | "+221 33 XXX XX XX" |
| email | email | Char | | - | "srh@sante.gouv.sn" |
| adresse | address | Text | | - | "Bâtiment A, 2ème étage" |
| description | description | Text | | - | "Gestion des RH..." |

### Valeurs du champ type (Selection)

| Valeur Excel | Valeur Odoo | Description |
|--------------|-------------|-------------|
| Service | service | Service |
| Bureau | bureau | Bureau |
| Cellule | cellule | Cellule |
| Division | division | Division |
| (vide) | service | Défaut |

### Relations

- **direction_id** (Many2one → sn.direction) : Direction parente
  - Recherche par `code` ou `name`
  - Obligatoire
  
- **manager_id** (Many2one → hr.employee) : Chef de service
  - Recherche par `name`
  - Optionnel

### Contraintes

- `UNIQUE(code, direction_id)` : Code unique par direction

### Exemple de mapping

**Excel** :
```csv
nom_service,code_service,type_service,direction,responsable,telephone,email
"Service des Ressources Humaines",SRH,Service,DGS,"Mme Fatou SALL",+221 33 821 00 10,srh@sante.gouv.sn
```

**Odoo (XML)** :
```xml
<record id="service_srh" model="sn.service">
  <field name="name">Service Des Ressources Humaines</field>
  <field name="code">SRH</field>
  <field name="type">service</field>
  <field name="direction_id" ref="direction_dgs"/>
  <field name="phone">+221 33 821 00 10</field>
  <field name="email">srh@sante.gouv.sn</field>
</record>
```

---

## Modèle : sn.agent

**Description** : Agents publics (employés)

**Options d'implémentation** :
1. Modèle indépendant avec lien vers `hr.employee`
2. Extension de `hr.employee` avec champs supplémentaires

### Champs (Option 1 : Modèle indépendant)

| Colonne Excel | Champ Odoo | Type Odoo | Obligatoire | Relation | Exemple |
|---------------|------------|-----------|-------------|----------|----------|
| nom | name | Char | ✓ | - | "DIOP" |
| prenom | first_name | Char | | - | "Amadou" |
| nom_complet | name | Char | ✓ | - | "Amadou DIOP" |
| fonction | function | Char | ✓ | - | "Directeur Général" |
| poste | function | Char | ✓ | - | "Chef de Service" |
| service | service_id | Many2one | ✓ | → sn.service | Recherche par nom normalisé |
| code_service | service_id | Many2one | ✓ | → sn.service | Recherche par code |
| interlocuteur | manager_id | Many2one | | → hr.employee | Recherche par nom normalisé |
| matricule | employee_id | Char | | - | "SN-2024-001234" |
| telephone_bureau | work_phone | Char | | - | "+221 33 XXX XX XX" |
| telephone_mobile | mobile_phone | Char | | - | "+221 77 XXX XX XX" |
| email | work_email | Char | | - | "adiop@sante.gouv.sn" |
| email_professionnel | work_email | Char | | - | "contact@example.sn" |
| date_prise_service | hire_date | Date | | - | "2020-01-15" |
| employee_id | employee_id | Many2one | | → hr.employee | Lien optionnel |

### Champs (Option 2 : Extension de hr.employee)

Ajouter les champs suivants à `hr.employee` :

| Champ ajouté | Type Odoo | Description |
|--------------|-----------|-------------|
| service_id | Many2one → sn.service | Service d'affectation |
| direction_id | Many2one → sn.direction | Direction (calculé via service) |
| ministry_id | Many2one → sn.ministry | Ministère (calculé via direction) |
| function_public | Char | Fonction dans l'administration |
| matricule_public | Char | Matricule administratif |

### Relations

- **service_id** (Many2one → sn.service) : Service d'affectation
  - Recherche par `code` ou `name`
  - Obligatoire
  
- **employee_id** (Many2one → hr.employee) : Lien vers fiche employé
  - Optionnel
  - Permet de synchroniser avec le module RH

### Contraintes

- `UNIQUE(matricule)` : Matricule unique (si renseigné)
- `UNIQUE(work_email)` : Email unique (si renseigné)

### Exemple de mapping

**Excel** :
```csv
nom,prenom,fonction,service,matricule,telephone_bureau,telephone_mobile,email
DIOP,Amadou,"Directeur Général",DGS,SN-2024-001234,+221 33 821 00 00,+221 77 123 45 67,adiop@sante.gouv.sn
```

**Odoo (XML)** :
```xml
<record id="agent_adiop" model="sn.agent">
  <field name="name">Amadou Diop</field>
  <field name="first_name">Amadou</field>
  <field name="function">Directeur Général</field>
  <field name="service_id" ref="direction_dgs"/>
  <field name="employee_id">SN-2024-001234</field>
  <field name="work_phone">+221 33 821 00 00</field>
  <field name="mobile_phone">+221 77 123 45 67</field>
  <field name="work_email">adiop@sante.gouv.sn</field>
</record>
```

---

## Champs communs à tous les modèles

Ces champs sont disponibles sur tous les modèles Odoo (hérités de `models.Model`) :

| Champ Odoo | Type | Description |
|------------|------|-------------|
| id | Integer | Identifiant unique (auto-incrémenté) |
| create_date | Datetime | Date de création |
| create_uid | Many2one → res.users | Utilisateur créateur |
| write_date | Datetime | Date de dernière modification |
| write_uid | Many2one → res.users | Dernier utilisateur modificateur |
| active | Boolean | Actif (défaut: True) |

---

## Valeurs par défaut

### sn.ministry
- `type` : "ministry" (sauf Présidence → "presidency", Primature → "primature")
- `active` : True
- `state` : "draft"

### sn.direction
- `type` : "generale"
- `active` : True

### sn.service
- `type` : "service"
- `active` : True

### sn.agent
- `active` : True

---

## Transformations de données

### Normalisation des noms
```python
# Première lettre en majuscule pour chaque mot
# S'applique aux colonnes: nom, prenom, fonction, adresse, description,
# ministere, direction, service, interlocuteur
"ministère de la santé" → "Ministère De La Santé"
"direction générale" → "Direction Générale"
"service des ressources humaines" → "Service Des Ressources Humaines"
```

### Normalisation des codes
```python
# Majuscules, alphanumériques uniquement
"ms-as" → "MSAS"
"dgs 01" → "DGS01"
```

### Normalisation des emails
```python
# Minuscules
"Contact@Sante.Gouv.SN" → "contact@sante.gouv.sn"
```

### Normalisation des téléphones
```python
# Format international +221
"33 823 00 50" → "+221 33 823 00 50"
"77 123 45 67" → "+221 77 123 45 67"
```

### Normalisation des URLs
```python
# Ajouter http:// si absent
"sante.gouv.sn" → "http://sante.gouv.sn"
"www.presidence.sn" → "http://www.presidence.sn"
```

---

## Références externes (external_id)

Pour faciliter l'import et les mises à jour, utiliser des `external_id` cohérents :

### Convention de nommage

```
{model_prefix}_{code_lower}
```

**Exemples** :
- `ministry_msas` : Ministère de la Santé (code MSAS)
- `ministry_pr` : Présidence de la République (code PR)
- `direction_dgs` : Direction Générale de la Santé (code DGS)
- `service_srh` : Service des Ressources Humaines (code SRH)
- `agent_sn2024001234` : Agent avec matricule SN-2024-001234

### Utilisation dans XML

```xml
<record id="ministry_msas" model="sn.ministry">
  <field name="name">Ministère de la Santé</field>
  <field name="code">MSAS</field>
</record>

<record id="direction_dgs" model="sn.direction">
  <field name="name">Direction Générale de la Santé</field>
  <field name="code">DGS</field>
  <field name="ministry_id" ref="ministry_msas"/>
</record>
```

---

## Contraintes SQL

### sn.ministry
```sql
ALTER TABLE sn_ministry
  ADD CONSTRAINT sn_ministry_code_unique UNIQUE(code),
  ADD CONSTRAINT sn_ministry_name_unique UNIQUE(LOWER(name)),
  ADD CONSTRAINT sn_ministry_code_length CHECK(LENGTH(code) >= 2 AND LENGTH(code) <= 10),
  ADD CONSTRAINT sn_ministry_email_format CHECK(email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
  ADD CONSTRAINT sn_ministry_phone_format CHECK(phone ~* '^\+221');
```

### sn.direction
```sql
ALTER TABLE sn_direction
  ADD CONSTRAINT sn_direction_code_ministry_unique UNIQUE(code, ministry_id),
  ADD CONSTRAINT sn_direction_email_format CHECK(email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
  ADD CONSTRAINT sn_direction_phone_format CHECK(phone ~* '^\+221');
```

### sn.service
```sql
ALTER TABLE sn_service
  ADD CONSTRAINT sn_service_code_direction_unique UNIQUE(code, direction_id),
  ADD CONSTRAINT sn_service_email_format CHECK(email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
  ADD CONSTRAINT sn_service_phone_format CHECK(phone ~* '^\+221');
```

### sn.agent
```sql
ALTER TABLE sn_agent
  ADD CONSTRAINT sn_agent_matricule_unique UNIQUE(employee_id),
  ADD CONSTRAINT sn_agent_email_unique UNIQUE(work_email),
  ADD CONSTRAINT sn_agent_email_format CHECK(work_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
  ADD CONSTRAINT sn_agent_phone_format CHECK(work_phone ~* '^\+221' OR mobile_phone ~* '^\+221');
```

---

## Mapping inversé : Odoo → Excel

Pour exporter les données Odoo vers Excel :

| Modèle | Champ Odoo | Colonne Excel |
|--------|------------|---------------|
| sn.ministry | name | Nom du Ministère |
| sn.ministry | code | Code |
| sn.ministry | type | Type |
| sn.ministry | phone | Téléphone |
| sn.ministry | email | Email |
| sn.direction | name | Nom de la Direction |
| sn.direction | code | Code Direction |
| sn.direction | ministry_id.name | Ministère |
| sn.service | name | Nom du Service |
| sn.service | direction_id.name | Direction |
| sn.agent | name | Nom Complet |
| sn.agent | function | Fonction |
| sn.agent | service_id.name | Service |

---

## Voir aussi

- **DATA_SCHEMA.md** : Structure complète des données
- **VALIDATION_RULES.md** : Règles de validation détaillées
- **IMPORT_GUIDE.md** : Guide d'import pas à pas
