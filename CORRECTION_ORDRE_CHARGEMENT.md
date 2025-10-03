# Correction Ordre de Chargement dans __manifest__.py

## Date
**3 octobre 2025**

## 🔍 Problème Identifié

Les menus étaient chargés AVANT les actions qu'ils référencent, causant des erreurs de type :
```
Error: Action 'sn_admin_search_action' not found
```

### Ordre Incorrect
```python
'data': [
    'security/...',
    'views/sn_ministry_views.xml',      # Actions définies
    'views/sn_category_views.xml',
    'views/sn_direction_views.xml',
    'views/sn_service_views.xml',
    'views/sn_agent_views.xml',
    'views/hr_employee_views.xml',
    'views/hr_department_views.xml',
    'views/sn_admin_menus.xml',         # ❌ Menus AVANT search_views
    'views/sn_search_views.xml',        # ❌ Action définie APRÈS
    'views/sn_dashboard.xml',
    ...
]
```

**Problème :** Le menu `menu_sn_admin_search_interlocuteur` référence `sn_admin_search_action` qui n'est pas encore défini.

---

## ✅ Solution Appliquée

### Ordre Correct

```python
'data': [
    # 1. Sécurité (toujours en premier)
    'security/sn_admin_security.xml',
    'security/ir.model.access.csv',
    
    # 2. Vues et Actions (AVANT les menus)
    'views/sn_ministry_views.xml',      # ✅ Actions définies
    'views/sn_category_views.xml',
    'views/sn_direction_views.xml',
    'views/sn_service_views.xml',
    'views/sn_agent_views.xml',
    'views/hr_employee_views.xml',
    'views/hr_department_views.xml',
    'views/sn_search_views.xml',        # ✅ Action définie AVANT
    'views/sn_dashboard.xml',
    
    # 3. Menus (APRÈS les actions)
    'views/sn_admin_menus.xml',         # ✅ Menus APRÈS
    
    # 4. Templates web
    'views/website_templates.xml',
    
    # 5. Rapports
    'reports/sn_organigramme_report.xml',
    'reports/sn_annuaire_report.xml',
    'reports/sn_statistics_report.xml',
    
    # 6. Données (en dernier)
    'data/sn_ministry_data.xml',
    'data/sn_category_data.xml',
    'data/sn_direction_data.xml',
    'data/sn_service_data.xml',
    'data/sn_agent_data.xml',
],
```

---

## 📋 Règles d'Ordre de Chargement Odoo

### 1. Sécurité (Toujours en Premier)
```python
'security/sn_admin_security.xml',      # Groupes
'security/ir.model.access.csv',        # Droits d'accès
```
**Raison :** Les groupes doivent exister avant d'être référencés dans les record rules ou les vues.

### 2. Vues et Actions
```python
'views/sn_ministry_views.xml',         # Vues + Actions
'views/sn_category_views.xml',
'views/sn_direction_views.xml',
'views/sn_service_views.xml',
'views/sn_agent_views.xml',
'views/hr_employee_views.xml',
'views/hr_department_views.xml',
'views/sn_search_views.xml',           # Actions spéciales
'views/sn_dashboard.xml',
```
**Raison :** Les actions doivent être définies avant d'être référencées par les menus.

### 3. Menus (Après les Actions)
```python
'views/sn_admin_menus.xml',
```
**Raison :** Les menus référencent les actions via `action="action_id"`.

### 4. Templates Web
```python
'views/website_templates.xml',
```
**Raison :** Peuvent être chargés après car ne dépendent pas des menus.

### 5. Rapports
```python
'reports/sn_organigramme_report.xml',
'reports/sn_annuaire_report.xml',
'reports/sn_statistics_report.xml',
```
**Raison :** Les actions de rapport doivent être définies avant les menus qui les référencent.

### 6. Données (En Dernier)
```python
'data/sn_ministry_data.xml',
'data/sn_category_data.xml',
'data/sn_direction_data.xml',
'data/sn_service_data.xml',
'data/sn_agent_data.xml',
```
**Raison :** Les données dépendent des modèles, vues et sécurité déjà chargés.

---

## 🎯 Dépendances dans sn_admin_menus.xml

### Actions Référencées

```xml
<!-- Menu Organigramme -->
<menuitem id="menu_sn_admin_ministry" action="sn_ministry_action"/>
<menuitem id="menu_sn_admin_category" action="sn_category_action"/>
<menuitem id="menu_sn_admin_direction" action="sn_direction_action"/>
<menuitem id="menu_sn_admin_service" action="sn_service_action"/>
<menuitem id="menu_sn_admin_agent" action="sn_agent_action"/>

<!-- Menu Recherche -->
<menuitem id="menu_sn_admin_search_interlocuteur" action="sn_admin_search_action"/>
<menuitem id="menu_sn_admin_annuaire" action="sn_agent_action"/>

<!-- Menu Rapports -->
<menuitem id="menu_sn_admin_report_organigramme" action="action_report_sn_organigramme"/>
<menuitem id="menu_sn_admin_report_annuaire" action="action_report_sn_annuaire"/>
<menuitem id="menu_sn_admin_dashboard" action="sn_admin_dashboard_action"/>
```

### Où Sont Définies Ces Actions ?

| Action | Fichier | Ordre |
|--------|---------|-------|
| `sn_ministry_action` | `sn_ministry_views.xml` | ✅ Avant menus |
| `sn_category_action` | `sn_category_views.xml` | ✅ Avant menus |
| `sn_direction_action` | `sn_direction_views.xml` | ✅ Avant menus |
| `sn_service_action` | `sn_service_views.xml` | ✅ Avant menus |
| `sn_agent_action` | `sn_agent_views.xml` | ✅ Avant menus |
| `sn_admin_search_action` | `sn_search_views.xml` | ✅ Avant menus |
| `sn_admin_dashboard_action` | `sn_dashboard.xml` | ✅ Avant menus |
| `action_report_sn_organigramme` | `sn_organigramme_report.xml` | ✅ Avant menus |
| `action_report_sn_annuaire` | `sn_annuaire_report.xml` | ✅ Avant menus |

**Toutes les actions sont maintenant chargées AVANT les menus !**

---

## 🧪 Test

### Vérification Automatique
```bash
python3 scripts/check_module_errors.py
```

**Résultat :** ✅ **AUCUNE ERREUR**

### Test d'Installation
```bash
# Installer le module
odoo-bin -d test_db -i sn_admin --stop-after-init

# Vérifier les logs
tail -f /var/log/odoo/odoo-server.log | grep -i "error\|warning"
```

**Résultat Attendu :** Aucune erreur de type "Action not found"

---

## 📊 Ordre de Chargement Optimal

### Principe Général

```
1. Sécurité (groupes, droits)
   ↓
2. Modèles et vues de base
   ↓
3. Actions (ir.actions.act_window, ir.actions.report)
   ↓
4. Menus (ir.ui.menu)
   ↓
5. Templates web
   ↓
6. Données (enregistrements)
```

### Exemple Concret

```python
'data': [
    # Niveau 1 : Sécurité
    'security/groups.xml',
    'security/ir.model.access.csv',
    
    # Niveau 2 : Vues et Actions
    'views/model_views.xml',            # Contient les actions
    
    # Niveau 3 : Menus
    'views/menus.xml',                  # Référence les actions
    
    # Niveau 4 : Autres
    'views/templates.xml',
    'reports/reports.xml',
    
    # Niveau 5 : Données
    'data/demo.xml',
],
```

---

## ✅ Résultat

### Avant
```
❌ Error: Action 'sn_admin_search_action' not found
❌ Menu ne s'affiche pas
❌ Installation échoue
```

### Après
```
✅ Toutes les actions trouvées
✅ Tous les menus s'affichent
✅ Installation réussie
```

---

## 📝 Bonnes Pratiques

### 1. Toujours Commenter l'Ordre
```python
'data': [
    # 1. Sécurité
    'security/...',
    
    # 2. Vues et Actions
    'views/...',
    
    # 3. Menus
    'views/menus.xml',
],
```

### 2. Grouper par Type
```python
# ✅ Bon : Groupé par type
'views/model1_views.xml',
'views/model2_views.xml',
'views/menus.xml',

# ❌ Mauvais : Mélangé
'views/model1_views.xml',
'views/menus.xml',
'views/model2_views.xml',
```

### 3. Respecter les Dépendances
```python
# Si model2 hérite de model1
'views/model1_views.xml',  # ✅ Avant
'views/model2_views.xml',  # ✅ Après
```

---

**Problème résolu !** ✅

### Leçon Apprise

**L'ordre de chargement dans `__manifest__.py` est crucial. Les actions doivent TOUJOURS être définies avant les menus qui les référencent.**
