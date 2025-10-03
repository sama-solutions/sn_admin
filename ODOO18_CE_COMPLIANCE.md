# Conformité Odoo 18 Community Edition

## Date de Révision
**3 octobre 2025** - Module `sn_admin` v18.0.1.0.0

---

## ✅ Certification de Conformité

Le module **SN Admin - Organigramme Administration Sénégalaise** est **100% compatible** avec **Odoo 18 Community Edition** selon les directives strictes de développement.

---

## 📋 Checklist de Conformité

### 1. Socle Technique Garanti

| Critère | Statut | Détails |
|---------|--------|---------|
| **Python 3.11+** | ✅ | Code compatible Python 3.11+ (pas de dépendances obsolètes) |
| **PostgreSQL 13+** | ✅ | Aucune requête SQL spécifique incompatible |
| **Framework Owl.js** | ✅ | Frontend utilise Owl.js (voir `static/src/js/sn_orgchart.js`) |
| **API REST** | ✅ | Contrôleurs REST dans `controllers/api.py` |

### 2. Vues et UI

| Critère | Statut | Détails |
|---------|--------|---------|
| **Tag `<list>`** | ✅ | Toutes les vues utilisent `<list>` au lieu de `<tree>` |
| **Sticky Headers** | ✅ | Fonctionnalité native d'Odoo 18 activée automatiquement |
| **`multi_edit="1"`** | ✅ | Activé sur toutes les vues list principales |
| **Attributs `attrs`** | ✅ | Utilisation correcte de `attrs` pour `invisible`, `readonly`, `required` |
| **Décorations** | ✅ | `decoration-muted`, `decoration-info` utilisés correctement |

### 3. Dépendances de Modules

| Module | Statut | Justification |
|--------|--------|---------------|
| **`base`** | ✅ | Module core Odoo CE |
| **`mail`** | ✅ | Module core Odoo CE (chatter, activités) |
| **`hr`** | ✅ | Module RH disponible en CE |
| **`website`** | ✅ | Module website disponible en CE |

**Aucune dépendance Enterprise ou obsolète détectée.**

### 4. Modules Exclus (Vérification)

| Module Interdit | Présent ? | Statut |
|-----------------|-----------|--------|
| **`account`** | ❌ | ✅ Aucune référence |
| **`social_media`** | ❌ | ✅ Aucune référence |
| **`website_mail`** | ❌ | ✅ Aucune référence |
| **`website_sms`** | ❌ | ✅ Aucune référence |
| **`website_payment`** | ❌ | ✅ Aucune référence |
| **`account_consolidation`** | ❌ | ✅ Aucune référence |

---

## 🔧 Corrections Appliquées

### 1. Migration `tree` → `list`

**Fichiers modifiés :**
- `views/sn_ministry_views.xml`
- `views/sn_direction_views.xml`
- `views/sn_service_views.xml`
- `views/sn_agent_views.xml`
- `views/sn_search_views.xml`
- `views/hr_department_views.xml`
- `views/hr_employee_views.xml`

**Changements :**
- IDs de vues : `*_view_tree` → `*_view_list`
- Noms de vues : `*.tree` → `*.list`
- Actions : `view_mode="tree,..."` → `view_mode="list,..."`

### 2. Correction du Code Frontend

**Fichier :** `static/src/js/sn_admin_public_owl.js`

**Problème :** Ligne corrompue avec texte parasite
**Solution :** Nettoyage de la première ligne et correction de la structure JSON-RPC

### 3. Framework Frontend

**Backend (`sn_orgchart.js`) :**
```javascript
import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
```
✅ Utilise Owl.js natif d'Odoo 18

**Frontend Public (`sn_admin_public_owl.js`) :**
✅ JavaScript vanilla moderne (ES6+), pas de dépendance externe

---

## 📦 Dépendances Python

**Fichier :** `requirements.txt`

Toutes les dépendances sont compatibles Python 3.11+ :
- `qrcode>=7.4.2` - Génération QR codes
- `Pillow>=10.0.0` - Manipulation images
- `pandas>=2.0.0` - Traitement données
- `openpyxl>=3.1.0` - Excel
- `email-validator>=2.0.0` - Validation emails
- `phonenumbers>=8.13.0` - Validation téléphones
- `python-slugify>=8.0.0` - Slugification
- `unidecode>=1.3.0` - Normalisation texte
- `folium>=0.14.0` - Cartes (optionnel)

---

## 🎯 Fonctionnalités Conformes

### Modèles de Données
- ✅ `sn.ministry` - Ministères
- ✅ `sn.direction` - Directions
- ✅ `sn.service` - Services
- ✅ `sn.agent` - Agents
- ✅ Extensions `hr.employee` et `hr.department`

### Vues
- ✅ Vues List avec `multi_edit`
- ✅ Vues Form avec chatter (`mail.thread`, `mail.activity.mixin`)
- ✅ Vues Kanban
- ✅ Vues Graph et Pivot (statistiques)
- ✅ Vues Search avec filtres et groupements

### Intégrations
- ✅ Synchronisation bidirectionnelle avec module RH
- ✅ Génération automatique de QR codes
- ✅ Portail public avec organigramme interactif
- ✅ API REST pour intégrations externes
- ✅ Rapports PDF (organigramme, annuaire, statistiques)

### Sécurité
- ✅ Groupes de sécurité (`sn_admin_user`, `sn_admin_manager`)
- ✅ Règles d'accès (ir.model.access)
- ✅ Visibilité publique configurable par entité

---

## 🚀 Installation et Déploiement

### Prérequis
```bash
# Python 3.11+
python3 --version

# PostgreSQL 13+
psql --version

# Odoo 18 CE
odoo --version
```

### Installation
```bash
# 1. Copier le module
cp -r sn_admin /path/to/odoo/addons/

# 2. Installer les dépendances Python
pip install -r sn_admin/requirements.txt

# 3. Redémarrer Odoo
sudo systemctl restart odoo

# 4. Activer le mode développeur et installer le module
```

### Vérification
```bash
# Vérifier les logs Odoo
tail -f /var/log/odoo/odoo-server.log

# Aucune erreur de dépendance ne doit apparaître
```

---

## 📝 Notes Importantes

### Conventions Odoo 18
1. **Vues List** : Toujours utiliser `<list>` (jamais `<tree>`)
2. **Multi-édition** : Activer `multi_edit="1"` sur les vues list
3. **Owl.js** : Framework JavaScript standard (pas de jQuery, Vue.js sauf besoin spécifique)
4. **Attributs dynamiques** : Utiliser `attrs` pour les conditions d'affichage
5. **Décorations** : Utiliser `decoration-*` pour le style conditionnel

### Modules CE vs EE
- ✅ **CE** : `base`, `mail`, `hr`, `website`, `contacts`, `portal`
- ❌ **EE uniquement** : `account_*`, `social_*`, modules de comptabilité avancée

### Maintenance
- Le module suit les conventions Odoo 18 CE
- Aucune dépendance à des modules Enterprise
- Code maintenable et évolutif
- Documentation complète dans `/doc`

---

## 🔍 Tests de Conformité

### Tests Manuels Effectués
- [x] Installation du module sans erreur
- [x] Création de ministères, directions, services, agents
- [x] Synchronisation avec module RH
- [x] Génération de QR codes
- [x] Affichage portail public
- [x] Édition en masse (multi_edit)
- [x] Filtres et groupements
- [x] Génération de rapports PDF

### Tests Automatisés
Voir `/tests` pour les tests unitaires Python.

---

## 📞 Support

Pour toute question sur la conformité Odoo 18 CE :
- **Documentation** : `/doc`
- **Issues** : GitHub repository
- **Équipe** : PSA-GSN

---

## 📄 Licence

**LGPL-3** - Compatible avec Odoo Community Edition

---

**Certification :** Ce module est conforme aux directives strictes de développement Odoo 18 Community Edition et ne contient aucune dépendance à des modules Enterprise ou obsolètes.

**Validé le :** 3 octobre 2025  
**Version :** 18.0.1.0.0  
**Statut :** ✅ Production Ready
