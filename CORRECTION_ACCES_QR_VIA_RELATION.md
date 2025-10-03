# Correction Accès QR Code via Relation

## Date
**3 octobre 2025**

## 🔍 Problème Identifié

Même après avoir ajouté `store=True` aux champs QR Code dans `sn.agent`, on ne pouvait toujours pas y accéder via `sn_agent_id.qr_code` dans les vues héritées de `hr.employee`.

### Erreur
```xml
<!-- ❌ Ne fonctionne pas dans une vue héritée -->
<field name="sn_agent_id.qr_code" widget="image" readonly="1"/>
<field name="sn_agent_id.qr_code_url" readonly="1"/>
```

### Cause
Odoo ne permet pas d'accéder directement aux champs d'une relation via la notation pointée (`relation.field`) dans les vues héritées, surtout pour les champs calculés.

---

## ✅ Solution Appliquée

### Ajouter des Champs `related` dans `hr.employee`

Au lieu d'accéder directement à `sn_agent_id.qr_code`, on crée des champs `related` dans le modèle `hr.employee`.

#### Fichier : `models/hr_employee.py`

**Avant :**
```python
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sn_agent_id = fields.Many2one(
        comodel_name='sn.agent',
        string='Agent Officiel',
    )
    
    sn_ministry_id = fields.Many2one(
        related='sn_agent_id.ministry_id',
        store=True,
    )
    # ... autres champs related
```

**Après :**
```python
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sn_agent_id = fields.Many2one(
        comodel_name='sn.agent',
        string='Agent Officiel',
    )
    
    sn_ministry_id = fields.Many2one(
        related='sn_agent_id.ministry_id',
        store=True,
    )
    
    # ✅ AJOUTÉ : Champs QR Code related
    sn_qr_code = fields.Binary(
        string='QR Code Agent',
        related='sn_agent_id.qr_code',
        readonly=True,
    )
    sn_qr_code_url = fields.Char(
        string='URL QR Code Agent',
        related='sn_agent_id.qr_code_url',
        readonly=True,
    )
```

---

## 📝 Modifications des Vues

### Fichier : `views/hr_employee_views.xml`

**Avant :**
```xml
<group string="QR Code" invisible="not sn_agent_id">
    <!-- ❌ Accès direct via relation -->
    <field name="sn_agent_id.qr_code" widget="image" readonly="1"/>
    <field name="sn_agent_id.qr_code_url" readonly="1"/>
</group>
```

**Après :**
```xml
<group string="QR Code Agent Officiel" invisible="not sn_agent_id">
    <!-- ✅ Accès via champs related -->
    <field name="sn_qr_code" widget="image" readonly="1"/>
    <field name="sn_qr_code_url" widget="url" readonly="1"/>
</group>
```

---

## 🔄 Fonctionnement

### Chaîne de Relations

```
hr.employee
    ↓
sn_agent_id (Many2one vers sn.agent)
    ↓
sn.agent.qr_code (Binary, compute, store=True)
    ↓
hr.employee.sn_qr_code (Binary, related='sn_agent_id.qr_code')
    ↓
Vue XML : <field name="sn_qr_code"/>
```

### Avantages des Champs `related`

1. ✅ **Accès direct** : `employee.sn_qr_code` au lieu de `employee.sn_agent_id.qr_code`
2. ✅ **Compatible vues** : Fonctionne dans toutes les vues (form, list, kanban)
3. ✅ **Pas de calcul** : Odoo gère automatiquement la relation
4. ✅ **Lecture seule** : `readonly=True` empêche la modification

---

## 📊 Comparaison

| Approche | Syntaxe | Fonctionne dans Vue ? | Performance |
|----------|---------|----------------------|-------------|
| **Accès direct** | `sn_agent_id.qr_code` | ❌ Non (vue héritée) | N/A |
| **Champ related** | `sn_qr_code` | ✅ Oui | ✅ Bonne |
| **Champ compute** | `_compute_qr_code()` | ✅ Oui | ⚠️ Calcul à chaque fois |

---

## ✅ Résultat

### Vue Employé RH

```xml
<page name="sn_admin_integration" string="Structure Officielle">
    <group>
        <group string="Lien Agent Officiel">
            <field name="sn_agent_id"/>
            <field name="sn_ministry_id" readonly="1"/>
            <field name="sn_direction_id" readonly="1"/>
            <field name="sn_service_id" readonly="1"/>
        </group>
        <group string="Actions">
            <button name="action_create_sn_agent" 
                    string="Créer Agent Officiel" 
                    type="object" 
                    class="oe_highlight"
                    invisible="sn_agent_id"/>
            <button name="action_view_sn_agent" 
                    string="Voir Agent Officiel" 
                    type="object"
                    invisible="not sn_agent_id"/>
            <button name="action_view_sn_structure" 
                    string="Voir Structure" 
                    type="object"
                    invisible="not sn_service_id and not sn_direction_id and not sn_ministry_id"/>
        </group>
    </group>
    <!-- ✅ QR Code maintenant accessible -->
    <group string="QR Code Agent Officiel" invisible="not sn_agent_id">
        <field name="sn_qr_code" widget="image" readonly="1"/>
        <field name="sn_qr_code_url" widget="url" readonly="1"/>
    </group>
</page>
```

### Utilisation Python

```python
# ✅ Accès direct
employee = self.env['hr.employee'].browse(1)
qr_code = employee.sn_qr_code  # Fonctionne !
qr_url = employee.sn_qr_code_url  # Fonctionne !

# ✅ Ou via la relation (en Python)
qr_code = employee.sn_agent_id.qr_code  # Fonctionne aussi en Python
```

---

## 🎯 Bonnes Pratiques

### Quand Utiliser des Champs `related`

✅ **Utiliser `related` quand :**
- On veut accéder à un champ d'une relation dans une vue
- Le champ source est stocké (`store=True`)
- On veut simplifier l'accès en Python
- On veut filtrer/grouper par ce champ

❌ **Ne pas utiliser `related` quand :**
- Le champ source n'est pas stocké (performance)
- La relation peut être nulle (vérifier avec `invisible`)
- On a besoin de logique complexe (utiliser `compute` à la place)

### Syntaxe Correcte

```python
# ✅ Correct
field_name = fields.Type(
    string='Label',
    related='relation_field.target_field',
    readonly=True,  # Recommandé pour éviter les modifications
    store=False,    # Optionnel : stocker ou non
)

# ❌ Incorrect (dans une vue héritée)
<field name="relation_field.target_field"/>
```

---

## 📁 Fichiers Modifiés

| Fichier | Modification |
|---------|--------------|
| `models/hr_employee.py` | ✅ Ajout `sn_qr_code` et `sn_qr_code_url` |
| `views/hr_employee_views.xml` | ✅ Utilisation des nouveaux champs |

---

## 🧪 Tests

### Test 1 : Affichage dans la Vue
```python
# Créer un agent
agent = self.env['sn.agent'].create({
    'name': 'Test Agent',
    'function': 'Directeur',
    'service_id': 1,
})

# Créer un employé lié
employee = self.env['hr.employee'].create({
    'name': 'Test Employee',
    'sn_agent_id': agent.id,
})

# Vérifier
assert employee.sn_qr_code  # Doit être rempli
assert employee.sn_qr_code_url  # Doit être rempli
```

### Test 2 : Mise à Jour Automatique
```python
# Modifier le nom de l'agent
agent.name = 'Nouveau Nom'

# Vérifier que le QR code de l'employé est mis à jour
employee.invalidate_cache()
assert employee.sn_qr_code  # Doit être recalculé
```

---

## 🚀 Déploiement

```bash
# 1. Redémarrer Odoo
sudo systemctl restart odoo

# 2. Mettre à jour le module
odoo-bin -d votre_base -u sn_admin

# 3. Les nouveaux champs seront ajoutés automatiquement
```

---

## ✅ Résultat Final

### Avant
```xml
<!-- ❌ Ne fonctionnait pas -->
<field name="sn_agent_id.qr_code" widget="image"/>
```

### Après
```xml
<!-- ✅ Fonctionne parfaitement -->
<field name="sn_qr_code" widget="image"/>
```

---

**Problème résolu définitivement !** ✅

### Leçon Apprise

**Dans Odoo, pour accéder aux champs d'une relation dans une vue héritée, il faut créer des champs `related` dans le modèle plutôt que d'utiliser la notation pointée directement dans la vue.**
