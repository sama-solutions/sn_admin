# Correction Menu Configuration

## Date
**3 octobre 2025**

## 🔍 Problème Identifié

L'action `base.action_res_config` n'existe plus dans Odoo 18 CE.

### Erreur
```xml
<menuitem id="menu_sn_admin_settings"
          name="Paramètres"
          parent="menu_sn_admin_config"
          action="base.action_res_config"  <!-- ❌ N'existe plus -->
          sequence="10"/>
```

**Message d'erreur :**
```
Error: Action 'base.action_res_config' not found
```

---

## ✅ Solution Appliquée

### Option 1 : Supprimer le Menu (Solution Actuelle)

```xml
<!-- Sous-menu Configuration -->
<menuitem id="menu_sn_admin_config"
          name="Configuration"
          parent="menu_sn_admin_root"
          groups="group_sn_admin_admin"
          sequence="100"/>

<!-- Note: Pas de menu Paramètres car base.action_res_config n'existe plus dans Odoo 18 -->
<!-- Les paramètres peuvent être ajoutés via res.config.settings si nécessaire -->
```

**Avantage :** Simple, pas d'erreur.  
**Inconvénient :** Pas de menu de paramètres pour l'instant.

---

## 🔧 Option 2 : Créer une Action de Configuration (Future)

Si vous voulez ajouter des paramètres de configuration pour le module, voici comment faire :

### 1. Créer un Modèle de Configuration

```python
# models/res_config_settings.py (déjà existant)
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Paramètres du module
    sn_admin_auto_sync = fields.Boolean(
        string='Synchronisation automatique RH',
        config_parameter='sn_admin.auto_sync',
        default=True,
    )
    sn_admin_public_access = fields.Boolean(
        string='Accès public à l\'organigramme',
        config_parameter='sn_admin.public_access',
        default=True,
    )
    sn_admin_qr_code_size = fields.Integer(
        string='Taille des QR codes',
        config_parameter='sn_admin.qr_code_size',
        default=150,
    )
```

### 2. Créer une Vue de Configuration

```xml
<!-- views/res_config_settings_views.xml -->
<record id="res_config_settings_view_form" model="ir.ui.view">
    <field name="name">res.config.settings.view.form.inherit.sn.admin</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="base.res_config_settings_view_form"/>
    <field name="arch" type="xml">
        <xpath expr="//div[hasclass('settings')]" position="inside">
            <div class="app_settings_block" data_string="SN Admin" string="SN Admin" data_key="sn_admin">
                <h2>Organigramme Administration</h2>
                <div class="row mt16 o_settings_container">
                    <div class="col-12 col-lg-6 o_setting_box">
                        <div class="o_setting_left_pane">
                            <field name="sn_admin_auto_sync"/>
                        </div>
                        <div class="o_setting_right_pane">
                            <label for="sn_admin_auto_sync"/>
                            <div class="text-muted">
                                Synchroniser automatiquement avec le module RH
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-lg-6 o_setting_box">
                        <div class="o_setting_left_pane">
                            <field name="sn_admin_public_access"/>
                        </div>
                        <div class="o_setting_right_pane">
                            <label for="sn_admin_public_access"/>
                            <div class="text-muted">
                                Permettre l'accès public à l'organigramme
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-lg-6 o_setting_box">
                        <div class="o_setting_left_pane">
                            <field name="sn_admin_qr_code_size"/>
                        </div>
                        <div class="o_setting_right_pane">
                            <label for="sn_admin_qr_code_size"/>
                            <div class="text-muted">
                                Taille des QR codes en pixels
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </xpath>
    </field>
</record>
```

### 3. Créer une Action et un Menu

```xml
<!-- views/sn_admin_menus.xml -->
<record id="action_sn_admin_config" model="ir.actions.act_window">
    <field name="name">Paramètres SN Admin</field>
    <field name="res_model">res.config.settings</field>
    <field name="view_mode">form</field>
    <field name="target">inline</field>
    <field name="context">{'module': 'sn_admin'}</field>
</record>

<menuitem id="menu_sn_admin_settings"
          name="Paramètres"
          parent="menu_sn_admin_config"
          action="action_sn_admin_config"
          sequence="10"/>
```

---

## 📋 Actions de Configuration dans Odoo 18

### Actions Obsolètes (Odoo 17 et antérieurs)
```xml
<!-- ❌ N'existe plus -->
<menuitem action="base.action_res_config"/>
```

### Actions Modernes (Odoo 18)
```xml
<!-- ✅ Utiliser res.config.settings -->
<record id="action_config" model="ir.actions.act_window">
    <field name="name">Paramètres</field>
    <field name="res_model">res.config.settings</field>
    <field name="view_mode">form</field>
    <field name="target">inline</field>
</record>
```

---

## 🎯 Structure des Menus Actuelle

```
SN Admin
├── Organigramme
│   ├── Ministères
│   ├── Catégories
│   ├── Directions
│   ├── Services
│   └── Agents
├── Recherche
│   ├── Recherche d'interlocuteur
│   └── Annuaire complet
├── Rapports
│   ├── Organigramme hiérarchique
│   ├── Annuaire par ministère
│   └── Statistiques
└── Configuration
    └── (vide pour l'instant)
```

---

## ✅ Résultat

### Avant
```
❌ Error: Action 'base.action_res_config' not found
❌ Menu ne se charge pas
```

### Après
```
✅ Aucune erreur
✅ Menu Configuration existe (vide)
✅ Peut être enrichi plus tard si nécessaire
```

---

## 📝 Recommandations

### Pour l'Instant
Le menu Configuration existe mais est vide. C'est suffisant pour l'installation.

### Pour le Futur
Si vous voulez ajouter des paramètres :
1. Enrichir `models/res_config_settings.py`
2. Créer `views/res_config_settings_views.xml`
3. Créer une action `action_sn_admin_config`
4. Ajouter le menu avec cette action

---

**Problème résolu !** ✅

### Leçon Apprise

**Dans Odoo 18, `base.action_res_config` n'existe plus. Utiliser `res.config.settings` avec une action personnalisée pour les paramètres de module.**
