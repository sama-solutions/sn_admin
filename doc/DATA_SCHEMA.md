# Schéma de données - Organigramme Administration Sénégalaise

## 1. Vue d'ensemble

Ce document décrit la structure des données extraites du fichier `snadmin.xlsx` contenant l'organigramme détaillé de l'administration publique sénégalaise.

**Source** : `snadmin.xlsx`
**Format** : Microsoft Excel (.xlsx)
**Encodage** : UTF-8

### Statistiques générales
- **Nombre de feuilles** : À déterminer après extraction
- **Nombre total d'enregistrements** : À déterminer après extraction
- **Niveaux hiérarchiques** : 4 niveaux principaux

## 2. Structure hiérarchique

```
Présidence / Primature / Ministère
  └─ Direction Générale / Direction Régionale / Direction Technique
      └─ Service / Bureau / Cellule / Division
          └─ Agent (nom, prénom, fonction, contacts)
```

### Description des niveaux

#### Niveau 1 : Institutions
- **Présidence de la République** : Institution suprême
- **Primature** : Services du Premier Ministre
- **Ministères** : Départements ministériels (environ 23-30)

#### Niveau 2 : Directions
- **Directions Générales** : Structures centrales des ministères
- **Directions Régionales** : Représentations territoriales
- **Directions Techniques** : Structures spécialisées
- **Inspections** : Organes de contrôle
- **Secrétariats Généraux** : Coordination administrative

#### Niveau 3 : Services
- **Services** : Unités opérationnelles
- **Bureaux** : Structures de support
- **Cellules** : Unités spécialisées
- **Divisions** : Sous-structures des services

#### Niveau 4 : Agents
- **Directeurs** : Responsables de directions
- **Chefs de service** : Responsables de services
- **Agents** : Personnel administratif et technique

## 3. Structure des feuilles

Les feuilles Excel peuvent contenir différents types de données :

### Type 1 : Organigramme complet
Contient tous les niveaux hiérarchiques avec relations parent-enfant.

**Colonnes attendues** :
- Ministère / Institution
- Direction
- Service
- Nom / Prénom
- Fonction / Poste
- Téléphone (bureau, mobile)
- Email (professionnel)
- Adresse

### Type 2 : Liste par ministère
Une feuille par ministère avec ses structures internes.

### Type 3 : Annuaire des agents
Liste des agents avec leurs coordonnées et affectations.

## 4. Champs identifiés

### Champs institutionnels

| Colonne source | Type | Obligatoire | Exemple | Notes |
|----------------|------|-------------|---------|-------|
| nom_ministere | Char(200) | Oui | "Ministère de la Santé et de l'Action Sociale" | Clé fonctionnelle |
| code_ministere | Char(10) | Oui | "MSAS" | Unique, majuscules |
| type_institution | Selection | Oui | "ministry" / "presidency" / "primature" | Type d'institution |
| adresse | Text | Non | "Fann Résidence, Dakar" | Adresse physique |
| telephone | Char(20) | Non | "+221 33 823 00 50" | Format international |
| email | Char(100) | Non | "contact@sante.gouv.sn" | Domaine .gouv.sn recommandé |
| site_web | Char(200) | Non | "http://sante.gouv.sn" | URL complète |
| description | Text | Non | "Système de santé publique..." | Description des missions |

### Champs des directions

| Colonne source | Type | Obligatoire | Exemple | Notes |
|----------------|------|-------------|---------|-------|
| nom_direction | Char(200) | Oui | "Direction Générale de la Santé" | Nom complet |
| code_direction | Char(10) | Non | "DGS" | Code court |
| type_direction | Selection | Non | "generale" / "regionale" / "technique" | Type de direction |
| ministere | Char(200) | Oui | "MSAS" | Référence au ministère parent |
| responsable | Char(100) | Non | "Dr. Amadou DIOP" | Nom du directeur |
| telephone | Char(20) | Non | "+221 33 XXX XX XX" | Ligne directe |
| email | Char(100) | Non | "dgs@sante.gouv.sn" | Email de la direction |
| region | Char(50) | Non | "Dakar" | Pour directions régionales |

### Champs des services

| Colonne source | Type | Obligatoire | Exemple | Notes |
|----------------|------|-------------|---------|-------|
| nom_service | Char(200) | Oui | "Service des Ressources Humaines" | Nom complet |
| code_service | Char(10) | Non | "SRH" | Code court |
| type_service | Selection | Non | "service" / "bureau" / "cellule" / "division" | Type de structure |
| direction | Char(200) | Oui | "DGS" | Référence à la direction parente |
| responsable | Char(100) | Non | "Mme Fatou SALL" | Nom du chef de service |
| telephone | Char(20) | Non | "+221 33 XXX XX XX" | Ligne directe |
| email | Char(100) | Non | "srh@sante.gouv.sn" | Email du service |

### Champs des agents

| Colonne source | Type | Obligatoire | Exemple | Notes |
|----------------|------|-------------|---------|-------|
| nom | Char(100) | Oui | "DIOP" | Nom de famille |
| prenom | Char(100) | Non | "Amadou" | Prénom(s) |
| nom_complet | Char(200) | Non | "Amadou DIOP" | Nom complet formaté |
| fonction | Char(100) | Oui | "Directeur Général" | Poste occupé |
| service | Char(200) | Oui | "SRH" | Référence au service |
| matricule | Char(20) | Non | "SN-2024-001234" | Identifiant unique |
| telephone_bureau | Char(20) | Non | "+221 33 XXX XX XX" | Téléphone fixe |
| telephone_mobile | Char(20) | Non | "+221 77 XXX XX XX" | Téléphone mobile |
| email | Char(100) | Non | "adiop@sante.gouv.sn" | Email professionnel |
| date_prise_service | Date | Non | "2020-01-15" | Date d'entrée en fonction |

## 5. Statistiques de qualité

Les statistiques suivantes seront générées après extraction :

### Taux de complétude
- **Ministères** : % avec email, téléphone, site web
- **Directions** : % avec responsable, contacts
- **Services** : % avec responsable, contacts
- **Agents** : % avec email, téléphone

### Doublons potentiels
- Codes ministères/directions dupliqués
- Noms d'agents similaires (même nom + prénom)
- Emails/téléphones partagés

### Valeurs aberrantes
- Emails sans domaine .sn
- Téléphones non sénégalais
- Codes trop courts/longs
- Noms avec caractères spéciaux

## 6. Relations hiérarchiques

### Relations Many2one

```
sn.direction.ministry_id → sn.ministry
sn.service.direction_id → sn.direction
sn.agent.service_id → sn.service
sn.agent.employee_id → hr.employee (optionnel)
```

### Relations One2many (inverses)

```
sn.ministry.direction_ids → sn.direction
sn.direction.service_ids → sn.service
sn.service.agent_ids → sn.agent
```

### Contraintes d'intégrité

- **Pas de cycles** : Un service ne peut pas être son propre parent
- **Profondeur maximale** : 4 niveaux (Ministère → Direction → Service → Sous-service)
- **Cohérence géographique** : Les directions régionales doivent avoir une région définie
- **Unicité des codes** : Les codes ministères et directions doivent être uniques

## 7. Règles de validation

### Validation des noms
- Longueur : 3-200 caractères
- Caractères autorisés : lettres, chiffres, espaces, apostrophes, tirets
- Première lettre en majuscule

### Validation des codes
- Longueur : 2-10 caractères
- Caractères autorisés : lettres majuscules et chiffres
- Pas d'espaces ni caractères spéciaux

### Validation des emails
- Format RFC 5322
- Domaine recommandé : .gouv.sn ou .sn
- Minuscules uniquement

### Validation des téléphones
- Format international : +221 XX XXX XX XX
- Préfixes valides : 33 (fixe), 77/78/76/70 (mobile)

### Validation hiérarchique
- Chaque direction doit référencer un ministère existant
- Chaque service doit référencer une direction existante
- Chaque agent doit référencer un service existant

## 8. Exemples de données

### Exemple : Ministère de la Santé

```csv
nom_ministere,code,type,adresse,telephone,email,site_web
"Ministère de la Santé et de l'Action Sociale",MSAS,ministry,"Fann Résidence, Dakar",+221 33 823 00 50,contact@sante.gouv.sn,http://sante.gouv.sn
```

### Exemple : Direction Générale

```csv
nom_direction,code_direction,type_direction,ministere,responsable,telephone,email
"Direction Générale de la Santé",DGS,generale,MSAS,"Dr. Amadou DIOP",+221 33 XXX XX XX,dgs@sante.gouv.sn
```

### Exemple : Service

```csv
nom_service,code_service,type_service,direction,responsable,telephone,email
"Service des Ressources Humaines",SRH,service,DGS,"Mme Fatou SALL",+221 33 XXX XX XX,srh@sante.gouv.sn
```

### Exemple : Agent

```csv
nom,prenom,fonction,service,matricule,telephone_bureau,telephone_mobile,email
DIOP,Amadou,"Directeur Général",DGS,SN-2024-001234,+221 33 XXX XX XX,+221 77 XXX XX XX,adiop@sante.gouv.sn
```

## 9. Notes techniques

### Encodage
- Tous les fichiers doivent être en UTF-8
- Les caractères spéciaux (accents, cédilles) doivent être préservés

### Format des dates
- Format ISO 8601 : YYYY-MM-DD
- Exemple : 2024-01-15

### Valeurs nulles
- Représentées par des chaînes vides dans les CSV
- Pas de valeurs "NULL", "N/A", "-"

### Séparateurs CSV
- Séparateur de champs : virgule (,)
- Délimiteur de texte : guillemets doubles (")
- Encodage : UTF-8 sans BOM

## 10. Prochaines étapes

Après extraction et normalisation :

1. **Validation** : Vérifier la conformité avec ce schéma
2. **Enrichissement** : Ajouter les champs manquants (codes, emails)
3. **Dédoublonnage** : Fusionner les enregistrements dupliqués
4. **Mapping Odoo** : Créer la correspondance avec les modèles Odoo
5. **Import** : Charger les données dans Odoo 18 CE

Consulter `IMPORT_GUIDE.md` pour les instructions détaillées.
