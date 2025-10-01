# Règles de validation des données

Ce document décrit toutes les règles de validation appliquées aux données de l'organigramme sénégalais avant import dans Odoo.

## 1. Validation des champs texte

### 1.1 Noms (ministère, direction, service, agent)

#### Règles de format
- **Longueur minimale** : 3 caractères
- **Longueur maximale** : 200 caractères
- **Caractères autorisés** : Lettres (avec accents), chiffres, espaces, apostrophes, tirets
- **Caractères interdits** : `< > & " ' ; | \ / * ? : [ ] { } ( ) @ # $ % ^ ~ ` =`

#### Normalisation
```python
# Première lettre en majuscule pour chaque mot
text = text.strip().title()
```

#### Exemples valides
- "Ministère de la Santé et de l'Action Sociale"
- "Direction Générale de la Santé"
- "Service des Ressources Humaines"
- "Amadou DIOP"
- "Fatou N'DIAYE"

#### Exemples invalides
- "MS" (trop court)
- "Ministère <Santé>" (caractères interdits)
- "Direction@Santé" (caractère interdit)

### 1.2 Codes

#### Règles de format
- **Longueur minimale** : 2 caractères
- **Longueur maximale** : 10 caractères
- **Caractères autorisés** : Lettres majuscules (A-Z) et chiffres (0-9) uniquement
- **Pas d'espaces** ni caractères spéciaux

#### Normalisation
```python
# Majuscules, supprimer espaces et caractères spéciaux
code = code.strip().upper()
code = re.sub(r'[^A-Z0-9]', '', code)
```

#### Exemples valides
- "MSAS"
- "DGS"
- "SRH01"
- "PR"
- "PM"

#### Exemples invalides
- "M" (trop court)
- "ms-as" (minuscules et tiret)
- "DGS 01" (espace)
- "MINISTÈRESANTÉ" (trop long, accents)

### 1.3 Descriptions

#### Règles de format
- **Longueur maximale** : 5000 caractères
- **Caractères autorisés** : Tous caractères Unicode
- **Format** : Texte libre, peut contenir des retours à la ligne

#### Normalisation
```python
# Supprimer espaces superflus
description = description.strip()
```

---

## 2. Validation des contacts

### 2.1 Emails

#### Règles de format
- **Format** : RFC 5322 (standard international)
- **Regex** : `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$`
- **Domaines recommandés** : `.gouv.sn`, `.sn`
- **Longueur maximale** : 100 caractères

#### Normalisation
```python
# Minuscules uniquement
email = email.strip().lower()
```

#### Validation avec email-validator
```python
from email_validator import validate_email, EmailNotValidError

try:
    valid = validate_email(email, check_deliverability=False)
    email = valid.email
except EmailNotValidError as e:
    # Email invalide
    pass
```

#### Exemples valides
- "contact@sante.gouv.sn"
- "info@presidence.sn"
- "dgs@sante.gouv.sn"
- "amadou.diop@education.gouv.sn"

#### Exemples invalides
- "contact@sante" (pas de domaine complet)
- "@gouv.sn" (pas de partie locale)
- "contact sante@gouv.sn" (espace)
- "contact@sante@gouv.sn" (double @)
- "contact.@sante.gouv.sn" (point avant @)

#### Warnings (non bloquants)
- Email sans domaine `.gouv.sn` ou `.sn` : "Email non gouvernemental"
- Email avec domaine public (gmail.com, yahoo.fr) : "Email personnel détecté"

### 2.2 Téléphones

#### Règles de format
- **Format international** : `+221 XX XXX XX XX` (Sénégal)
- **Regex** : `^\+221\s?[0-9]{2}\s?[0-9]{3}\s?[0-9]{2}\s?[0-9]{2}$`
- **Préfixes valides** :
  - `33` : Téléphones fixes
  - `77`, `78`, `76`, `70` : Téléphones mobiles

#### Normalisation
```python
import phonenumbers

# Parser et formater
phone = phonenumbers.parse(phone, 'SN')
phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
# Résultat : "+221 33 823 00 50"
```

#### Correction automatique
Si le numéro commence par 33, 77, 78, 76, 70 sans +221 :
```python
# Ajouter +221
if phone.startswith(('33', '77', '78', '76', '70')):
    phone = f"+221 {phone}"
```

#### Exemples valides
- "+221 33 823 00 50" (fixe)
- "+221 77 123 45 67" (mobile)
- "+221 78 999 88 77" (mobile)
- "33 823 00 50" (sera corrigé en "+221 33 823 00 50")

#### Exemples invalides
- "33 823 00 50 00" (trop long)
- "+221 123" (trop court)
- "00 33 823 00 50" (format international incorrect)
- "+33 1 23 45 67 89" (France, pas Sénégal)

### 2.3 Sites web

#### Règles de format
- **Format** : URL complète avec protocole
- **Protocoles acceptés** : `http://`, `https://`
- **Longueur maximale** : 200 caractères

#### Normalisation
```python
# Ajouter http:// si absent
if not url.startswith(('http://', 'https://')):
    url = f"http://{url}"

# Minuscules
url = url.lower()
```

#### Validation basique
```python
import re

# Vérifier format URL
if not re.match(r'^https?://[a-z0-9.-]+\.[a-z]{2,}', url):
    # URL invalide
    pass
```

#### Exemples valides
- "http://sante.gouv.sn"
- "https://presidence.sn"
- "http://www.education.gouv.sn"
- "sante.gouv.sn" (sera corrigé en "http://sante.gouv.sn")

#### Exemples invalides
- "www.sante" (pas de domaine complet)
- "http://" (pas de domaine)
- "ftp://sante.gouv.sn" (protocole non supporté)

---

## 3. Validation hiérarchique

### 3.1 Relations parent-enfant

#### Règle : Direction → Ministère
- **Contrainte** : Chaque direction doit référencer un ministère existant
- **Validation** : Vérifier que `ministry_id` existe dans `sn.ministry`
- **Recherche** : Par `code` ou `name` (insensible à la casse)

```python
# Recherche du ministère parent
ministry = env['sn.ministry'].search([
    '|',
    ('code', '=', ministere_code),
    ('name', 'ilike', ministere_name)
], limit=1)

if not ministry:
    raise ValidationError(f"Ministère '{ministere_code}' introuvable")
```

#### Règle : Service → Direction
- **Contrainte** : Chaque service doit référencer une direction existante
- **Validation** : Vérifier que `direction_id` existe dans `sn.direction`
- **Recherche** : Par `code` ou `name`

#### Règle : Agent → Service
- **Contrainte** : Chaque agent doit référencer un service existant
- **Validation** : Vérifier que `service_id` existe dans `sn.service`
- **Recherche** : Par `code` ou `name`

### 3.2 Pas de cycles

#### Règle
Un service ne peut pas être son propre parent (directement ou indirectement).

#### Validation
```python
def _check_no_cycle(self):
    """Vérifier qu'il n'y a pas de cycle dans la hiérarchie"""
    if not self._check_recursion():
        raise ValidationError("Erreur : cycle détecté dans la hiérarchie")
```

### 3.3 Profondeur maximale

#### Règle
La hiérarchie ne peut pas dépasser 4 niveaux :
1. Ministère
2. Direction
3. Service
4. Sous-service (optionnel)

#### Validation
```python
def _check_depth(self):
    """Vérifier la profondeur maximale"""
    depth = 0
    current = self
    while current.parent_id and depth < 5:
        current = current.parent_id
        depth += 1
    
    if depth >= 4:
        raise ValidationError("Profondeur maximale dépassée (4 niveaux)")
```

### 3.4 Cohérence géographique

#### Règle : Directions régionales
Si `type_direction = "regionale"`, alors `region_id` doit être renseigné.

```python
@api.constrains('type', 'region_id')
def _check_regional_consistency(self):
    for record in self:
        if record.type == 'regionale' and not record.region_id:
            raise ValidationError(
                "Une direction régionale doit avoir une région définie"
            )
```

#### Règle : Services régionaux
Les services régionaux doivent appartenir à des directions régionales.

```python
@api.constrains('type', 'direction_id')
def _check_service_regional(self):
    for record in self:
        if record.type == 'regionale' and record.direction_id.type != 'regionale':
            raise ValidationError(
                "Un service régional doit appartenir à une direction régionale"
            )
```

---

## 4. Validation métier

### 4.1 Ministères

#### Codes réservés
- **"PR"** : Présidence de la République (unique)
- **"PM"** : Primature (unique)

```python
@api.constrains('code', 'type')
def _check_reserved_codes(self):
    if self.code == 'PR' and self.type != 'presidency':
        raise ValidationError("Le code 'PR' est réservé à la Présidence")
    if self.code == 'PM' and self.type != 'primature':
        raise ValidationError("Le code 'PM' est réservé à la Primature")
```

#### Type présidence unique
Il ne peut y avoir qu'un seul enregistrement avec `type="presidency"`.

```python
@api.constrains('type')
def _check_unique_presidency(self):
    if self.type == 'presidency':
        count = self.search_count([('type', '=', 'presidency'), ('id', '!=', self.id)])
        if count > 0:
            raise ValidationError("Il ne peut y avoir qu'une seule Présidence")
```

#### Unicité des noms
Pas de doublons de noms (ignorer la casse).

```python
@api.constrains('name')
def _check_unique_name(self):
    count = self.search_count([
        ('name', 'ilike', self.name),
        ('id', '!=', self.id)
    ])
    if count > 0:
        raise ValidationError(f"Un ministère avec le nom '{self.name}' existe déjà")
```

### 4.2 Directions

#### Nommage
Le nom doit contenir l'un des mots-clés : "Direction", "Inspection", "Secrétariat".

```python
@api.constrains('name')
def _check_direction_naming(self):
    keywords = ['direction', 'inspection', 'secrétariat', 'secretariat']
    if not any(kw in self.name.lower() for kw in keywords):
        # Warning seulement, pas d'erreur bloquante
        _logger.warning(f"Le nom '{self.name}' ne contient pas de mot-clé standard")
```

#### Responsable actif
Si un responsable est renseigné, il doit être un employé actif.

```python
@api.constrains('manager_id')
def _check_manager_active(self):
    if self.manager_id and not self.manager_id.active:
        raise ValidationError(
            f"Le responsable '{self.manager_id.name}' n'est pas actif"
        )
```

### 4.3 Services

#### Nommage
Le nom doit contenir l'un des mots-clés : "Service", "Bureau", "Cellule", "Division".

```python
@api.constrains('name')
def _check_service_naming(self):
    keywords = ['service', 'bureau', 'cellule', 'division']
    if not any(kw in self.name.lower() for kw in keywords):
        _logger.warning(f"Le nom '{self.name}' ne contient pas de mot-clé standard")
```

#### Taille maximale
Maximum 50 agents par service (warning si dépassé).

```python
def _check_service_size(self):
    agent_count = self.env['sn.agent'].search_count([('service_id', '=', self.id)])
    if agent_count > 50:
        _logger.warning(
            f"Le service '{self.name}' a {agent_count} agents (max recommandé: 50)"
        )
```

### 4.4 Agents

#### Format matricule
Format : "SN-YYYY-NNNNNN" (année + numéro séquentiel).

```python
@api.constrains('matricule')
def _check_matricule_format(self):
    if self.matricule:
        if not re.match(r'^SN-\d{4}-\d{6}$', self.matricule):
            raise ValidationError(
                f"Format matricule invalide: '{self.matricule}' "
                "(attendu: SN-YYYY-NNNNNN)"
            )
```

#### Fonction (liste contrôlée)
Liste recommandée de fonctions :
- Directeur Général
- Directeur
- Chef de Service
- Chef de Bureau
- Chef de Cellule
- Agent
- Secrétaire
- Technicien
- Conseiller

```python
FUNCTION_LIST = [
    'directeur_general', 'directeur', 'chef_service', 'chef_bureau',
    'chef_cellule', 'agent', 'secretaire', 'technicien', 'conseiller'
]

# Warning si fonction non standard
if self.function and self.function.lower() not in FUNCTION_LIST:
    _logger.warning(f"Fonction non standard: '{self.function}'")
```

#### Doublons
Vérifier nom + prénom + date de naissance (si disponible).

```python
@api.constrains('name', 'first_name', 'birth_date')
def _check_duplicate_agent(self):
    domain = [
        ('name', '=', self.name),
        ('first_name', '=', self.first_name),
        ('id', '!=', self.id)
    ]
    if self.birth_date:
        domain.append(('birth_date', '=', self.birth_date))
    
    count = self.search_count(domain)
    if count > 0:
        _logger.warning(
            f"Agent potentiellement en doublon: {self.first_name} {self.name}"
        )
```

---

## 5. Règles de qualité (warnings)

### 5.1 Complétude

#### Email manquant
- **Ministère/Direction sans email** : Warning
- **Service sans email** : Info (non bloquant)

```python
if not self.email:
    if self._name == 'sn.ministry':
        _logger.warning(f"Ministère '{self.name}' sans email")
    elif self._name == 'sn.direction':
        _logger.warning(f"Direction '{self.name}' sans email")
```

#### Téléphone manquant
- **Ministère sans téléphone** : Warning
- **Direction sans téléphone** : Warning
- **Service sans téléphone** : Info

#### Responsable manquant
- **Direction sans responsable** : Warning
- **Service sans responsable** : Info

### 5.2 Cohérence

#### Email/téléphone incohérents
Email d'un ministère A dans une direction du ministère B.

```python
if self.email and self.ministry_id.email:
    # Extraire le domaine
    domain_direction = self.email.split('@')[1]
    domain_ministry = self.ministry_id.email.split('@')[1]
    
    if domain_direction != domain_ministry:
        _logger.warning(
            f"Domaine email incohérent: {domain_direction} != {domain_ministry}"
        )
```

#### Codes similaires
Warning si codes trop proches (distance de Levenshtein < 2).

```python
from difflib import SequenceMatcher

def _check_similar_codes(self):
    similar = self.search([
        ('code', '!=', self.code),
        ('ministry_id', '=', self.ministry_id.id)
    ])
    
    for record in similar:
        ratio = SequenceMatcher(None, self.code, record.code).ratio()
        if ratio > 0.8:
            _logger.warning(
                f"Codes similaires: '{self.code}' et '{record.code}'"
            )
```

---

## 6. Gestion des erreurs

### 6.1 Erreurs bloquantes (import refusé)

Ces erreurs empêchent l'import de l'enregistrement :

1. **Champs obligatoires manquants**
   - `name` manquant
   - `code` manquant (pour ministères/directions)
   - `ministry_id` manquant (pour directions)
   - `direction_id` manquant (pour services)
   - `service_id` manquant (pour agents)

2. **Format invalide**
   - Email invalide (ne respecte pas RFC 5322)
   - Téléphone invalide (ne respecte pas format +221)
   - Code trop court (< 2 caractères)
   - Nom trop court (< 3 caractères)

3. **Contraintes d'unicité**
   - Code ministère dupliqué
   - Code direction dupliqué (même ministère)
   - Matricule agent dupliqué
   - Email dupliqué

4. **Références manquantes**
   - Ministère parent introuvable
   - Direction parente introuvable
   - Service parent introuvable

5. **Contraintes hiérarchiques**
   - Cycle détecté
   - Profondeur maximale dépassée

### 6.2 Erreurs non-bloquantes (import avec warning)

Ces erreurs génèrent un warning mais n'empêchent pas l'import :

1. **Champs optionnels manquants**
   - Email manquant
   - Téléphone manquant
   - Responsable manquant

2. **Valeurs hors liste recommandée**
   - Fonction non standard
   - Type non reconnu

3. **Incohérences mineures**
   - Domaine email non gouvernemental
   - Codes similaires
   - Nommage non standard

---

## 7. Script de validation

Le script `normalize_data.py` implémente toutes ces règles et génère un rapport détaillé.

### Exemple de rapport

```
=== RAPPORT DE VALIDATION ===

Lignes totales traitées: 1250
Lignes valides: 1198
Lignes rejetées: 52

✓ 245 ministères/directions/services validés

⚠ 45 avertissements:
  - Ligne 23: Email manquant (Direction Générale de la Santé)
  - Ligne 67: Téléphone invalide "+221 123" (trop court)
  - Ligne 89: Fonction non standard "Super Directeur"
  - Ligne 102: Domaine email non gouvernemental "contact@gmail.com"
  - Ligne 156: Codes similaires "DGS" et "DGS1"
  ...

✗ 7 erreurs bloquantes:
  - Ligne 12: Code "M" trop court (min 2 caractères)
  - Ligne 45: Champ obligatoire 'name' manquant
  - Ligne 78: Email invalide "contact@sante" (manque domaine)
  - Ligne 102: Direction orpheline (ministère "MINF" introuvable)
  - Ligne 134: Code "MSAS" dupliqué
  - Ligne 189: Cycle détecté dans la hiérarchie
  - Ligne 234: Profondeur maximale dépassée (5 niveaux)

=== RECOMMANDATIONS ===

1. Corriger les 7 erreurs bloquantes avant import
2. Vérifier les 45 avertissements (non bloquants)
3. Compléter les emails manquants (23 enregistrements)
4. Standardiser les fonctions (12 valeurs non standard)
```

---

## 8. Exemples de validation

### Exemple 1 : Enregistrement valide

**Entrée** :
```csv
nom_ministere,code,type,email,telephone
"Ministère de la Santé et de l'Action Sociale",MSAS,ministry,contact@sante.gouv.sn,+221 33 823 00 50
```

**Validation** : ✓ Tous les champs sont valides

### Exemple 2 : Enregistrement avec corrections automatiques

**Entrée** :
```csv
nom_ministere,code,type,email,telephone
"ministère de la santé",msas,ministry,CONTACT@SANTE.GOUV.SN,33 823 00 50
```

**Corrections appliquées** :
- Nom : "Ministère De La Santé" (`.title()`)
- Code : "MSAS" (`.upper()`)
- Email : "contact@sante.gouv.sn" (`.lower()`)
- Téléphone : "+221 33 823 00 50" (ajout +221)

**Résultat** : ✓ Enregistrement corrigé et validé

### Exemple 3 : Enregistrement avec erreurs bloquantes

**Entrée** :
```csv
nom_ministere,code,type,email,telephone
"MS",M,ministry,contact@sante,123
```

**Erreurs détectées** :
1. Nom trop court : "MS" (< 3 caractères)
2. Code trop court : "M" (< 2 caractères)
3. Email invalide : "contact@sante" (pas de domaine complet)
4. Téléphone invalide : "123" (format incorrect)

**Résultat** : ✗ Import refusé

### Exemple 4 : Enregistrement avec warnings

**Entrée** :
```csv
nom_direction,code_direction,ministere,email
"Direction Générale de la Santé",DGS,MSAS,
```

**Warnings générés** :
- Email manquant (recommandé pour directions)
- Téléphone manquant (recommandé pour directions)
- Responsable manquant (optionnel)

**Résultat** : ✓ Import autorisé avec warnings

---

## 9. Tests de validation

### Test 1 : Validation des emails

```python
def test_email_validation():
    # Valides
    assert validate_email("contact@sante.gouv.sn") == "contact@sante.gouv.sn"
    assert validate_email("CONTACT@SANTE.GOUV.SN") == "contact@sante.gouv.sn"
    
    # Invalides
    with pytest.raises(ValidationError):
        validate_email("contact@sante")
    with pytest.raises(ValidationError):
        validate_email("@gouv.sn")
    with pytest.raises(ValidationError):
        validate_email("contact sante@gouv.sn")
```

### Test 2 : Validation des téléphones

```python
def test_phone_validation():
    # Valides
    assert validate_phone("+221 33 823 00 50") == "+221 33 823 00 50"
    assert validate_phone("33 823 00 50") == "+221 33 823 00 50"  # Correction auto
    
    # Invalides
    with pytest.raises(ValidationError):
        validate_phone("123")
    with pytest.raises(ValidationError):
        validate_phone("+33 1 23 45 67 89")  # France
```

### Test 3 : Validation hiérarchique

```python
def test_hierarchy_validation():
    # Créer un ministère
    ministry = env['sn.ministry'].create({'name': 'Test', 'code': 'TEST'})
    
    # Créer une direction (valide)
    direction = env['sn.direction'].create({
        'name': 'Direction Test',
        'code': 'DT',
        'ministry_id': ministry.id
    })
    
    # Créer une direction orpheline (invalide)
    with pytest.raises(ValidationError):
        env['sn.direction'].create({
            'name': 'Direction Orpheline',
            'code': 'DO',
            'ministry_id': 99999  # N'existe pas
        })
```

---

## 10. Voir aussi

- **DATA_SCHEMA.md** : Structure des données
- **FIELD_MAPPING.md** : Mapping des champs
- **IMPORT_GUIDE.md** : Guide d'import complet
