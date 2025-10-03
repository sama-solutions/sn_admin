# Intégration des 5 Niveaux Hiérarchiques

## Date d'Implémentation
**3 octobre 2025** - Module `sn_admin` v18.0.1.0.0

---

## ✅ Hiérarchie Complète Intégrée

Le module **SN Admin** intègre maintenant **les 5 niveaux hiérarchiques complets** de l'administration sénégalaise dans la page publique et l'API.

### Structure Hiérarchique

```
┌─────────────────────────────────────────────────────────────┐
│ Niveau 1: MINISTÈRE / AUTORITÉ                              │
│ (Présidence, Primature, Ministère)                          │
│ Modèle: sn.ministry                                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Niveau 2: CATÉGORIE PRINCIPALE                              │
│ (Cabinet, Secrétariat général, Directions Générales,        │
│  Autres administrations)                                     │
│ Modèle: sn.category                                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Niveau 3: DIRECTION / PÔLE                                  │
│ (Pôle Juridique, Direction de l'Électricité,                │
│  Direction générale de la Planification)                     │
│ Modèle: sn.direction                                        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Niveau 4: SERVICE / ORGANISME / CELLULE                     │
│ (Service, Bureau, Cellule, Division, Inspection)            │
│ Modèle: sn.service                                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Niveau 5: AGENT                                             │
│ (Responsable, Directeur, Chef de service, Agent)            │
│ Modèle: sn.agent                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Composants Implémentés

### 1. Modèle de Données (`sn.category`)

**Fichier:** `models/category.py`

```python
class Category(models.Model):
    _name = 'sn.category'
    _description = 'Catégorie principale (Cabinet, Secrétariat général, Directions, Autres administrations)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Champs principaux
    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code', size=20)
    active = fields.Boolean(string='Actif', default=True)
    state = fields.Selection([...])
    
    # Relations
    ministry_id = fields.Many2one('sn.ministry', required=True)
    direction_ids = fields.One2many('sn.direction', 'category_id')
    
    # Compteurs
    direction_count = fields.Integer(compute='_compute_direction_count')
    service_count = fields.Integer(compute='_compute_service_count')
    
    # Visibilité publique
    public_visible = fields.Boolean(default=True)
```

**Caractéristiques:**
- ✅ Héritage `mail.thread` et `mail.activity.mixin` (chatter)
- ✅ Champ `state` pour workflow (draft, active, archived)
- ✅ Compteurs automatiques (directions, services)
- ✅ Visibilité publique configurable
- ✅ Action `action_view_directions()`

### 2. Vues Backend

**Fichier:** `views/sn_category_views.xml`

**Vues créées:**
- ✅ **Vue List** avec `multi_edit="1"` (conforme Odoo 18)
- ✅ **Vue Form** avec chatter et boutons d'action
- ✅ **Vue Kanban** groupée par ministère
- ✅ **Vue Search** avec filtres et groupements
- ✅ **Action** `sn_category_action`

**Menu:**
- ✅ Ajouté dans `views/sn_admin_menus.xml` (séquence 15)
- ✅ Accessible via: **SN Admin → Organigramme → Catégories**

### 3. Contrôleurs Web

**Fichier:** `controllers/main.py`

**Routes ajoutées:**

#### Route de détail catégorie
```python
@http.route('/organigramme/categorie/<int:category_id>', 
            type='http', auth='public', website=True)
def category(self, category_id, **kw):
    """Détails d'une catégorie"""
    # Affiche les directions de la catégorie
```

#### Route ministère (modifiée)
```python
@http.route('/organigramme/ministere/<int:ministry_id>', ...)
def ministry(self, ministry_id, **kw):
    """Détails d'un ministère"""
    # Récupère les catégories du ministère
    categories = Category.search([
        ('ministry_id', '=', ministry_id),
        ('active', '=', True),
        ('state', '=', 'active')
    ])
```

### 4. API Organigramme (modifiée)

**Fichier:** `controllers/main.py`

**Fonction `build_node()` enrichie:**

```python
def build_node(record, model_type):
    if model_type == 'ministry':
        # Niveau 2: Catégories
        categories = Category.search([...])
        if categories:
            for category in categories:
                node['children'].append(build_node(category, 'category'))
        else:
            # Fallback: directions directes
            for direction in record.direction_ids:
                node['children'].append(build_node(direction, 'direction'))
    
    elif model_type == 'category':
        # Niveau 3: Directions de la catégorie
        for direction in record.direction_ids:
            node['children'].append(build_node(direction, 'direction'))
    
    elif model_type == 'direction':
        # Niveau 4: Services
        ...
    
    elif model_type == 'service':
        # Niveau 5: Agents
        ...
```

**Logique intelligente:**
- ✅ Si catégories existent → affiche Ministère → Catégorie → Direction
- ✅ Si pas de catégories → affiche Ministère → Direction (rétrocompatibilité)

### 5. Templates Website

**Fichier:** `views/website_templates.xml`

#### Template détail ministère (modifié)
```xml
<template id="organigramme_ministry_detail">
    <!-- Affichage par catégories si elles existent -->
    <t t-if="categories">
        <h3>Structure Organisationnelle</h3>
        <t t-foreach="categories" t-as="category">
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h4><i class="fa fa-folder-open"/> 
                        <t t-esc="category.name"/>
                    </h4>
                </div>
                <div class="card-body">
                    <!-- Liste des directions de la catégorie -->
                </div>
            </div>
        </t>
    </t>
    
    <!-- Directions sans catégorie (fallback) -->
    <t t-if="directions_without_category">
        ...
    </t>
</template>
```

#### Template détail catégorie (nouveau)
```xml
<template id="organigramme_category_detail">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li>Accueil</li>
            <li>Ministères</li>
            <li>Ministère X</li>
            <li class="active">Catégorie Y</li>
        </ol>
    </nav>
    
    <h1><i class="fa fa-folder-open"/> Catégorie</h1>
    
    <!-- Statistiques -->
    <p>Nombre de directions: X</p>
    <p>Nombre de services: Y</p>
    
    <!-- Liste des directions -->
    <div class="list-group">
        <t t-foreach="directions" t-as="direction">
            <a href="/organigramme/direction/...">...</a>
        </t>
    </div>
</template>
```

### 6. JavaScript Frontend

**Fichier:** `static/src/js/sn_admin_public_owl.js`

**Fonction `nodeUrlForModel()` enrichie:**
```javascript
function nodeUrlForModel(model, id) {
    switch (model) {
        case 'sn.ministry':
            return `/organigramme/ministere/${id}`;
        case 'sn.category':  // ← NOUVEAU
            return `/organigramme/categorie/${id}`;
        case 'sn.direction':
            return `/organigramme/direction/${id}`;
        case 'sn.service':
            return `/organigramme/service/${id}`;
        case 'sn.agent':
            return `/organigramme/agent/${id}`;
    }
}
```

### 7. Sécurité

**Fichier:** `security/ir.model.access.csv`

**Droits d'accès déjà présents:**
```csv
access_sn_category_user,sn.category.user,model_sn_category,group_sn_admin_user,1,0,0,0
access_sn_category_manager,sn.category.manager,model_sn_category,group_sn_admin_manager,1,1,1,0
access_sn_category_admin,sn.category.admin,model_sn_category,group_sn_admin_admin,1,1,1,1
```

---

## 🎯 Exemples d'Utilisation

### Exemple 1: Ministère avec Catégories

**Ministère de l'Énergie**
```
Ministère de l'Énergie, du Pétrole et des Mines
│
├── Cabinet (Catégorie)
│   ├── Cabinet du Ministre
│   └── Secrétariat Particulier
│
├── Secrétariat Général (Catégorie)
│   ├── Direction des Ressources Humaines
│   └── Direction des Affaires Financières
│
├── Directions Générales (Catégorie)
│   ├── Direction Générale de l'Énergie
│   │   ├── Direction de l'Électricité (Niveau 3)
│   │   │   ├── Service Production (Niveau 4)
│   │   │   │   └── Chef de Service (Niveau 5)
│   │   │   └── Service Distribution (Niveau 4)
│   │   └── Direction des Énergies Renouvelables
│   └── Direction Générale des Mines
│
└── Autres Administrations (Catégorie)
    ├── Inspection Interne
    └── Cellule de Communication
```

### Exemple 2: Navigation Publique

**Parcours utilisateur:**
1. `/organigramme` → Page d'accueil
2. Clic sur "Ministère de l'Énergie"
3. `/organigramme/ministere/5` → Affiche les catégories:
   - Cabinet
   - Secrétariat Général
   - Directions Générales
   - Autres Administrations
4. Clic sur "Directions Générales"
5. `/organigramme/categorie/12` → Affiche les directions:
   - Direction Générale de l'Énergie
   - Direction Générale des Mines
6. Clic sur "Direction Générale de l'Énergie"
7. `/organigramme/direction/45` → Affiche les services
8. etc.

### Exemple 3: API JSON

**Requête:**
```javascript
fetch('/organigramme/api/tree', {
    method: 'POST',
    body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: { ministry_id: 5 }
    })
})
```

**Réponse:**
```json
{
    "id": 5,
    "name": "Ministère de l'Énergie",
    "type": "ministry",
    "children": [
        {
            "id": 12,
            "name": "Directions Générales",
            "type": "category",
            "children": [
                {
                    "id": 45,
                    "name": "Direction Générale de l'Énergie",
                    "type": "direction",
                    "children": [...]
                }
            ]
        }
    ]
}
```

---

## 🔄 Rétrocompatibilité

### Gestion des Données Existantes

Le module gère **automatiquement** les deux scénarios:

#### Scénario A: Avec Catégories
```
Ministère → Catégorie → Direction → Service → Agent
```

#### Scénario B: Sans Catégories (ancien système)
```
Ministère → Direction → Service → Agent
```

**Logique de fallback:**
```python
if categories:
    # Afficher la hiérarchie avec catégories
    for category in categories:
        display_category_with_directions(category)
else:
    # Afficher directement les directions (ancien système)
    for direction in directions:
        display_direction(direction)
```

---

## 📊 Impact sur les Performances

### Optimisations Implémentées

1. **Champs calculés avec `store=True`:**
   ```python
   direction_count = fields.Integer(compute='...', store=True)
   ```

2. **Filtrage au niveau SQL:**
   ```python
   categories = Category.search([
       ('ministry_id', '=', ministry_id),
       ('active', '=', True),
       ('state', '=', 'active')
   ])
   ```

3. **Limitation des agents affichés:**
   ```python
   # Limiter à 10 agents par service dans l'organigramme
   for agent in record.agent_ids[: 10]:
       ...
   ```

---

## ✅ Tests de Validation

### Tests Manuels à Effectuer

- [ ] **Backend:**
  - [ ] Créer une catégorie depuis le menu
  - [ ] Associer des directions à une catégorie
  - [ ] Vérifier les compteurs (direction_count, service_count)
  - [ ] Tester l'action "Voir Directions"

- [ ] **Frontend Public:**
  - [ ] Accéder à `/organigramme/ministere/X` avec catégories
  - [ ] Vérifier l'affichage des cartes de catégories
  - [ ] Cliquer sur une catégorie → `/organigramme/categorie/Y`
  - [ ] Vérifier le breadcrumb complet
  - [ ] Tester l'organigramme interactif `/organigramme/tree`

- [ ] **API:**
  - [ ] Appeler `/organigramme/api/tree` avec `ministry_id`
  - [ ] Vérifier la structure JSON avec 5 niveaux
  - [ ] Tester avec un ministère sans catégories (fallback)

---

## 📝 Migration des Données

### Script de Migration (si nécessaire)

Si vous avez des données existantes et souhaitez créer des catégories:

```python
# Script à exécuter dans Odoo shell
from odoo import api, SUPERUSER_ID

with api.Environment.manage():
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Exemple: Créer des catégories standard pour tous les ministères
    ministries = env['sn.ministry'].search([])
    
    for ministry in ministries:
        # Cabinet
        cabinet = env['sn.category'].create({
            'name': 'Cabinet',
            'code': 'CAB',
            'ministry_id': ministry.id,
            'state': 'active',
        })
        
        # Secrétariat Général
        sg = env['sn.category'].create({
            'name': 'Secrétariat Général',
            'code': 'SG',
            'ministry_id': ministry.id,
            'state': 'active',
        })
        
        # Directions Générales
        dg = env['sn.category'].create({
            'name': 'Directions Générales',
            'code': 'DG',
            'ministry_id': ministry.id,
            'state': 'active',
        })
        
        # Associer les directions existantes à la catégorie "Directions Générales"
        ministry.direction_ids.write({'category_id': dg.id})
```

---

## 🎉 Résumé

### ✅ Fonctionnalités Implémentées

| Niveau | Modèle | Backend | Frontend | API | Templates |
|--------|--------|---------|----------|-----|-----------|
| **1. Ministère** | `sn.ministry` | ✅ | ✅ | ✅ | ✅ |
| **2. Catégorie** | `sn.category` | ✅ | ✅ | ✅ | ✅ |
| **3. Direction** | `sn.direction` | ✅ | ✅ | ✅ | ✅ |
| **4. Service** | `sn.service` | ✅ | ✅ | ✅ | ✅ |
| **5. Agent** | `sn.agent` | ✅ | ✅ | ✅ | ✅ |

### 🚀 Prochaines Étapes

1. **Tester le module** après redémarrage Odoo
2. **Créer des catégories** pour vos ministères
3. **Associer les directions** aux catégories appropriées
4. **Vérifier la page publique** `/organigramme`
5. **Tester l'organigramme interactif** `/organigramme/tree`

---

**Date de validation:** 3 octobre 2025  
**Version:** 18.0.1.0.0  
**Statut:** ✅ **5 Niveaux Hiérarchiques Complets Intégrés**
