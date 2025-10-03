# Migration attrs → Syntaxe Odoo 18

## Date
**3 octobre 2025**

## ✅ Migration Complète

Tous les attributs `attrs` ont été remplacés par la nouvelle syntaxe Odoo 18.

### Anciennes Syntaxes (Odoo 17 et antérieurs)

```xml
<!-- ❌ OBSOLÈTE -->
<button attrs="{'invisible': [('field', '=', False)]}"/>
<button attrs="{'invisible': [('field', '!=', False)]}"/>
<button attrs="{'invisible': [('field', '=', 0)]}"/>
<button attrs="{'invisible': [('state', '!=', 'archived')]}"/>
```

### Nouvelles Syntaxes (Odoo 18)

```xml
<!-- ✅ ODOO 18 -->
<button invisible="not field"/>
<button invisible="field"/>
<button invisible="field == 0"/>
<button invisible="state != 'archived'"/>
```

## 📋 Conversions Appliquées

| Ancienne Syntaxe | Nouvelle Syntaxe |
|------------------|------------------|
| `attrs="{'invisible': [('department_id', '=', False)]}"` | `invisible="not department_id"` |
| `attrs="{'invisible': [('department_id', '!=', False)]}"` | `invisible="department_id"` |
| `attrs="{'invisible': [('employee_id', '=', False)]}"` | `invisible="not employee_id"` |
| `attrs="{'invisible': [('employee_id', '!=', False)]}"` | `invisible="employee_id"` |
| `attrs="{'invisible': [('employee_count', '=', 0)]}"` | `invisible="employee_count == 0"` |
| `attrs="{'invisible': [('state', '!=', 'archived')]}"` | `invisible="state != 'archived'"` |
| `attrs="{'invisible': [('is_interim', '=', False)]}"` | `invisible="not is_interim"` |
| `attrs="{'invisible': [('sn_structure_type', '=', False)]}"` | `invisible="not sn_structure_type"` |
| `attrs="{'invisible': [('sn_structure_type', '!=', 'ministry')]}"` | `invisible="sn_structure_type != 'ministry'"` |

## 📁 Fichiers Modifiés

### 1. `views/sn_ministry_views.xml`
- ✅ Boutons header (6 occurrences)
- ✅ Smart buttons (1 occurrence)
- ✅ Widget ribbon (1 occurrence)
- ✅ Boutons actions RH (2 occurrences)

### 2. `views/sn_direction_views.xml`
- ✅ Boutons header (2 occurrences)
- ✅ Smart buttons (1 occurrence)
- ✅ Widget ribbon (1 occurrence)
- ✅ Boutons actions RH (2 occurrences)

### 3. `views/sn_service_views.xml`
- ✅ Boutons header (2 occurrences)
- ✅ Smart buttons (1 occurrence)
- ✅ Widget ribbon (1 occurrence)
- ✅ Boutons actions RH (2 occurrences)

### 4. `views/sn_agent_views.xml`
- ✅ Boutons header (4 occurrences)
- ✅ Widget ribbon (2 occurrences)
- ✅ Boutons actions RH (3 occurrences)

### 5. `views/hr_department_views.xml`
- ✅ Champs conditionnels (3 occurrences)
- ✅ Boutons actions (2 occurrences)

## 🎯 Règles de Conversion

### Boolean Fields

```xml
<!-- Si le champ est False, masquer -->
attrs="{'invisible': [('field', '=', False)]}"
→ invisible="not field"

<!-- Si le champ est True, masquer -->
attrs="{'invisible': [('field', '!=', False)]}"
→ invisible="field"
```

### Numeric Comparisons

```xml
attrs="{'invisible': [('count', '=', 0)]}"
→ invisible="count == 0"

attrs="{'invisible': [('count', '>', 0)]}"
→ invisible="count > 0"
```

### String Comparisons

```xml
attrs="{'invisible': [('state', '!=', 'archived')]}"
→ invisible="state != 'archived'"

attrs="{'invisible': [('type', '=', 'ministry')]}"
→ invisible="type == 'ministry'"
```

### Selection Fields

```xml
attrs="{'invisible': [('sn_structure_type', '!=', 'ministry')]}"
→ invisible="sn_structure_type != 'ministry'"
```

## ✅ Avantages de la Nouvelle Syntaxe

1. **Plus lisible** : Syntaxe Python directe
2. **Plus concise** : Moins de caractères
3. **Plus maintenable** : Facile à comprendre
4. **Conforme Odoo 18** : Syntaxe officielle

## 🚀 Résultat

**Total de conversions :** ~40 occurrences  
**Fichiers modifiés :** 5 fichiers  
**Statut :** ✅ **100% Migré vers Odoo 18**

---

**Le module est maintenant entièrement compatible avec la syntaxe Odoo 18 !**
