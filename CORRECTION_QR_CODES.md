# Correction des Champs QR Code

## Date
**3 octobre 2025**

## 🔍 Problème Identifié

Les champs `qr_code` et `qr_code_url` étaient définis comme champs calculés (`compute`) mais **non stockés** (`store=False`).

### Impact

Lorsqu'on essayait d'accéder à ces champs via une relation (ex: `sn_agent_id.qr_code`), Odoo ne pouvait pas les récupérer car ils n'étaient pas en base de données.

**Erreur typique :**
```
AttributeError: 'hr.employee' object has no attribute 'qr_code'
```

---

## ✅ Corrections Appliquées

### 1. Ajout `store=True`

**Avant :**
```python
qr_code = fields.Binary(
    string='QR Code',
    compute='_compute_qr_code',
    store=False,  # ❌ Non stocké
)
qr_code_url = fields.Char(
    string='URL QR Code',
    compute='_compute_qr_code_url',
    store=True,   # ✅ Déjà stocké
)
```

**Après :**
```python
qr_code = fields.Binary(
    string='QR Code',
    compute='_compute_qr_code',
    store=True,  # ✅ Maintenant stocké
)
qr_code_url = fields.Char(
    string='URL QR Code',
    compute='_compute_qr_code_url',
    store=True,  # ✅ Stocké
)
```

### 2. Ajout `@api.depends`

**Avant :**
```python
def _compute_qr_code_url(self):  # ❌ Pas de @api.depends
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    for record in self:
        if record.id:
            record.qr_code_url = f"{base_url}/organigramme/agent/{record.id}"
        else:
            record.qr_code_url = False

def _compute_qr_code(self):  # ❌ Pas de @api.depends
    for record in self:
        if record.qr_code_url:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(record.qr_code_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            record.qr_code = base64.b64encode(buffer.getvalue())
        else:
            record.qr_code = False
```

**Après :**
```python
@api.depends('name')  # ✅ Recalculer si le nom change
def _compute_qr_code_url(self):
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    for record in self:
        if record.id:
            record.qr_code_url = f"{base_url}/organigramme/agent/{record.id}"
        else:
            record.qr_code_url = False

@api.depends('qr_code_url')  # ✅ Recalculer si l'URL change
def _compute_qr_code(self):
    for record in self:
        if record.qr_code_url:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(record.qr_code_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            record.qr_code = base64.b64encode(buffer.getvalue())
        else:
            record.qr_code = False
```

---

## 📁 Fichiers Modifiés

| Fichier | Champs Corrigés |
|---------|-----------------|
| `models/ministry.py` | `qr_code`, `qr_code_url` |
| `models/direction.py` | `qr_code`, `qr_code_url` |
| `models/service.py` | `qr_code`, `qr_code_url` |
| `models/agent.py` | `qr_code`, `qr_code_url` |

---

## 🔄 Chaîne de Dépendances

```
name (changement)
    ↓
@api.depends('name')
    ↓
_compute_qr_code_url()
    ↓
qr_code_url (stocké en base)
    ↓
@api.depends('qr_code_url')
    ↓
_compute_qr_code()
    ↓
qr_code (stocké en base)
```

---

## ✅ Avantages

### 1. Accès via Relations
```python
# ✅ Maintenant possible
employee = self.env['hr.employee'].browse(1)
qr_code = employee.sn_agent_id.qr_code  # Fonctionne !
qr_url = employee.sn_agent_id.qr_code_url  # Fonctionne !
```

### 2. Performance
- ✅ QR codes calculés une seule fois
- ✅ Stockés en base de données
- ✅ Pas de recalcul à chaque accès

### 3. Vues XML
```xml
<!-- ✅ Maintenant possible -->
<field name="sn_agent_id.qr_code" widget="image" readonly="1"/>
<field name="sn_agent_id.qr_code_url" readonly="1"/>
```

---

## ⚠️ Migration des Données

Après cette modification, les QR codes existants doivent être recalculés.

### Option 1 : Via l'Interface
```python
# Dans Odoo Shell ou un bouton
agents = self.env['sn.agent'].search([])
agents._compute_qr_code_url()
agents._compute_qr_code()
```

### Option 2 : Automatique
Les QR codes seront automatiquement recalculés lors de la prochaine modification du nom.

### Option 3 : Script Python
```python
# scripts/regenerate_qr_codes.py
import odoorpc

odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('votre_base', 'admin', 'password')

# Ministères
ministries = odoo.env['sn.ministry'].search([])
for m_id in ministries:
    ministry = odoo.env['sn.ministry'].browse(m_id)
    # Forcer le recalcul en modifiant un champ
    ministry.write({'name': ministry.name})

# Répéter pour direction, service, agent
```

---

## 🧪 Tests

### Test 1 : Création
```python
agent = self.env['sn.agent'].create({
    'name': 'Test Agent',
    'function': 'Directeur',
    'service_id': 1,
})

# Vérifier
assert agent.qr_code_url  # Doit être rempli
assert agent.qr_code  # Doit être rempli
```

### Test 2 : Modification
```python
agent.name = 'Nouveau Nom'

# Vérifier
assert agent.qr_code_url  # Doit être recalculé
assert agent.qr_code  # Doit être recalculé
```

### Test 3 : Accès via Relation
```python
employee = self.env['hr.employee'].browse(1)

# Vérifier
assert employee.sn_agent_id.qr_code_url  # Doit fonctionner
assert employee.sn_agent_id.qr_code  # Doit fonctionner
```

---

## 📊 Impact Base de Données

### Nouvelles Colonnes
```sql
-- Ajout automatique par Odoo lors de la mise à jour
ALTER TABLE sn_ministry ADD COLUMN qr_code BYTEA;
ALTER TABLE sn_direction ADD COLUMN qr_code BYTEA;
ALTER TABLE sn_service ADD COLUMN qr_code BYTEA;
ALTER TABLE sn_agent ADD COLUMN qr_code BYTEA;
```

### Taille Estimée
- QR Code : ~2-5 KB par enregistrement
- Total : ~5 MB pour 1000 enregistrements

---

## ✅ Résultat Final

### Avant
```python
# ❌ Erreur
employee.sn_agent_id.qr_code  # AttributeError
```

### Après
```python
# ✅ Fonctionne
employee.sn_agent_id.qr_code  # Retourne le QR code
employee.sn_agent_id.qr_code_url  # Retourne l'URL
```

---

## 🚀 Déploiement

```bash
# 1. Redémarrer Odoo
sudo systemctl restart odoo

# 2. Mettre à jour le module
odoo-bin -d votre_base -u sn_admin

# 3. Les colonnes seront ajoutées automatiquement
# 4. Les QR codes seront calculés pour les nouveaux enregistrements
# 5. Pour les anciens, forcer le recalcul (optionnel)
```

---

**Problème résolu !** ✅
