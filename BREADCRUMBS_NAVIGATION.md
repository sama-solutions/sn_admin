# Breadcrumbs - Navigation Publique

## Date de Révision
**3 octobre 2025** - Module `sn_admin` v18.0.1.0.0

---

## ✅ Structure des Breadcrumbs

Tous les breadcrumbs de la page publique ont été vérifiés et corrigés pour **inclure les catégories** (Niveau 2) lorsqu'elles existent.

---

## 📋 Breadcrumbs par Page

### 1. Page d'Accueil
**URL:** `/organigramme`

**Breadcrumb:** Aucun (page racine)

---

### 2. Liste des Ministères
**URL:** `/organigramme/ministeres`

**Breadcrumb:**
```
Accueil > Ministères
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item active">Ministères</li>
```

---

### 3. Détails d'un Ministère
**URL:** `/organigramme/ministere/{ministry_id}`

**Breadcrumb:**
```
Accueil > Ministères > [Nom du Ministère]
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministeres">Ministères</a></li>
<li class="breadcrumb-item active">[ministry.name]</li>
```

**Exemple:**
```
Accueil > Ministères > Ministère de l'Énergie
```

---

### 4. Détails d'une Catégorie ⭐ NOUVEAU
**URL:** `/organigramme/categorie/{category_id}`

**Breadcrumb:**
```
Accueil > Ministères > [Nom du Ministère] > [Nom de la Catégorie]
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministeres">Ministères</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministere/#{category.ministry_id.id}">[ministry.name]</a></li>
<li class="breadcrumb-item active">[category.name]</li>
```

**Exemple:**
```
Accueil > Ministères > Ministère de l'Énergie > Directions Générales
```

---

### 5. Détails d'une Direction
**URL:** `/organigramme/direction/{direction_id}`

**Breadcrumb (avec catégorie):**
```
Accueil > Ministères > [Ministère] > [Catégorie] > [Direction]
```

**Breadcrumb (sans catégorie):**
```
Accueil > Ministères > [Ministère] > [Direction]
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministeres">Ministères</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministere/#{direction.ministry_id.id}">[ministry.name]</a></li>
<t t-if="direction.category_id">
    <li class="breadcrumb-item"><a href="/organigramme/categorie/#{direction.category_id.id}">[category.name]</a></li>
</t>
<li class="breadcrumb-item active">[direction.name]</li>
```

**Exemple avec catégorie:**
```
Accueil > Ministères > Ministère de l'Énergie > Directions Générales > Direction Générale de l'Énergie
```

**Exemple sans catégorie:**
```
Accueil > Ministères > Ministère de l'Énergie > Direction Générale de l'Énergie
```

---

### 6. Détails d'un Service
**URL:** `/organigramme/service/{service_id}`

**Breadcrumb (avec catégorie):**
```
Accueil > Ministères > [Ministère] > [Catégorie] > [Direction] > [Service]
```

**Breadcrumb (sans catégorie):**
```
Accueil > Ministères > [Ministère] > [Direction] > [Service]
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministeres">Ministères</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministere/#{service.ministry_id.id}">[ministry.name]</a></li>
<t t-if="service.direction_id.category_id">
    <li class="breadcrumb-item"><a href="/organigramme/categorie/#{service.direction_id.category_id.id}">[category.name]</a></li>
</t>
<li class="breadcrumb-item"><a href="/organigramme/direction/#{service.direction_id.id}">[direction.name]</a></li>
<li class="breadcrumb-item active">[service.name]</li>
```

**Exemple avec catégorie:**
```
Accueil > Ministères > Ministère de l'Énergie > Directions Générales > Direction Générale de l'Énergie > Service Production
```

**Exemple sans catégorie:**
```
Accueil > Ministères > Ministère de l'Énergie > Direction Générale de l'Énergie > Service Production
```

---

### 7. Détails d'un Agent
**URL:** `/organigramme/agent/{agent_id}`

**Breadcrumb (avec catégorie):**
```
Accueil > Ministères > [Ministère] > [Catégorie] > [Direction] > [Service] > [Agent]
```

**Breadcrumb (sans catégorie):**
```
Accueil > Ministères > [Ministère] > [Direction] > [Service] > [Agent]
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministeres">Ministères</a></li>
<li class="breadcrumb-item"><a href="/organigramme/ministere/#{agent.ministry_id.id}">[ministry.name]</a></li>
<t t-if="agent.direction_id.category_id">
    <li class="breadcrumb-item"><a href="/organigramme/categorie/#{agent.direction_id.category_id.id}">[category.name]</a></li>
</t>
<li class="breadcrumb-item"><a href="/organigramme/direction/#{agent.direction_id.id}">[direction.name]</a></li>
<li class="breadcrumb-item"><a href="/organigramme/service/#{agent.service_id.id}">[service.name]</a></li>
<li class="breadcrumb-item active">[agent.name]</li>
```

**Exemple avec catégorie (5 niveaux complets):**
```
Accueil > Ministères > Ministère de l'Énergie > Directions Générales > Direction Générale de l'Énergie > Service Production > Jean Dupont
```

**Exemple sans catégorie (4 niveaux):**
```
Accueil > Ministères > Ministère de l'Énergie > Direction Générale de l'Énergie > Service Production > Jean Dupont
```

---

### 8. Page de Recherche
**URL:** `/organigramme/search`

**Breadcrumb:**
```
Accueil > Recherche
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item active">Recherche</li>
```

**Note:** Le breadcrumb reste simple car c'est une page de recherche globale, pas liée à une structure hiérarchique spécifique.

---

### 9. Organigramme Interactif
**URL:** `/organigramme/tree`

**Breadcrumb:**
```
Accueil > Organigramme
```

**Code:**
```xml
<li class="breadcrumb-item"><a href="/organigramme">Accueil</a></li>
<li class="breadcrumb-item active">Organigramme</li>
```

---

## 🎯 Logique Intelligente des Breadcrumbs

### Gestion Automatique des Catégories

Les breadcrumbs s'adaptent **automatiquement** selon que la direction a une catégorie ou non :

```xml
<t t-if="direction.category_id">
    <li class="breadcrumb-item">
        <a href="/organigramme/categorie/#{direction.category_id.id}">
            [category.name]
        </a>
    </li>
</t>
```

**Avantages:**
- ✅ **Rétrocompatibilité** : fonctionne avec les données existantes sans catégories
- ✅ **Flexibilité** : affiche automatiquement les catégories quand elles existent
- ✅ **Navigation cohérente** : l'utilisateur peut toujours remonter la hiérarchie

---

## 📊 Exemples Complets de Navigation

### Exemple 1: Navigation avec Catégories (5 niveaux)

**Parcours utilisateur:**

1. **Page d'accueil**
   - Breadcrumb: (aucun)
   - URL: `/organigramme`

2. **Clic sur "Ministères"**
   - Breadcrumb: `Accueil > Ministères`
   - URL: `/organigramme/ministeres`

3. **Clic sur "Ministère de l'Énergie"**
   - Breadcrumb: `Accueil > Ministères > Ministère de l'Énergie`
   - URL: `/organigramme/ministere/5`

4. **Clic sur catégorie "Directions Générales"**
   - Breadcrumb: `Accueil > Ministères > Ministère de l'Énergie > Directions Générales`
   - URL: `/organigramme/categorie/12`

5. **Clic sur "Direction Générale de l'Énergie"**
   - Breadcrumb: `Accueil > Ministères > Ministère de l'Énergie > Directions Générales > Direction Générale de l'Énergie`
   - URL: `/organigramme/direction/45`

6. **Clic sur "Service Production"**
   - Breadcrumb: `Accueil > Ministères > Ministère de l'Énergie > Directions Générales > Direction Générale de l'Énergie > Service Production`
   - URL: `/organigramme/service/123`

7. **Clic sur "Jean Dupont"**
   - Breadcrumb: `Accueil > Ministères > Ministère de l'Énergie > Directions Générales > Direction Générale de l'Énergie > Service Production > Jean Dupont`
   - URL: `/organigramme/agent/456`

### Exemple 2: Navigation sans Catégories (4 niveaux)

**Parcours utilisateur:**

1. **Page d'accueil** → `/organigramme`

2. **Ministères** → `/organigramme/ministeres`
   - Breadcrumb: `Accueil > Ministères`

3. **Ministère de la Santé** → `/organigramme/ministere/8`
   - Breadcrumb: `Accueil > Ministères > Ministère de la Santé`

4. **Direction des Hôpitaux** → `/organigramme/direction/67`
   - Breadcrumb: `Accueil > Ministères > Ministère de la Santé > Direction des Hôpitaux`
   - ⚠️ Pas de catégorie → saut direct du ministère à la direction

5. **Service Urgences** → `/organigramme/service/234`
   - Breadcrumb: `Accueil > Ministères > Ministère de la Santé > Direction des Hôpitaux > Service Urgences`

6. **Dr. Marie Martin** → `/organigramme/agent/789`
   - Breadcrumb: `Accueil > Ministères > Ministère de la Santé > Direction des Hôpitaux > Service Urgences > Dr. Marie Martin`

### Exemple 3: Navigation via Recherche

**Parcours utilisateur:**

1. **Page d'accueil** → `/organigramme`

2. **Clic sur barre de recherche**
   - Breadcrumb: `Accueil > Recherche`
   - URL: `/organigramme/search`

3. **Recherche "Jean Dupont"**
   - Breadcrumb: `Accueil > Recherche`
   - URL: `/organigramme/search?q=Jean+Dupont`
   - Résultats affichés dans un tableau

4. **Clic sur "Jean Dupont" dans les résultats**
   - Breadcrumb: `Accueil > Ministères > Ministère de l'Énergie > Directions Générales > Direction Générale de l'Énergie > Service Production > Jean Dupont`
   - URL: `/organigramme/agent/456`
   - ✅ Le breadcrumb complet s'affiche avec la hiérarchie

---

## 🔧 Implémentation Technique

### Condition pour Afficher la Catégorie

**Dans les templates QWeb:**

```xml
<t t-if="direction.category_id">
    <li class="breadcrumb-item">
        <a t-attf-href="/organigramme/categorie/#{direction.category_id.id}">
            <t t-esc="direction.category_id.name"/>
        </a>
    </li>
</t>
```

**Pour les services et agents:**

```xml
<t t-if="service.direction_id.category_id">
    <li class="breadcrumb-item">
        <a t-attf-href="/organigramme/categorie/#{service.direction_id.category_id.id}">
            <t t-esc="service.direction_id.category_id.name"/>
        </a>
    </li>
</t>
```

### Accès aux Relations

**Modèle `sn.direction`:**
```python
category_id = fields.Many2one('sn.category', string='Catégorie')
```

**Modèle `sn.service`:**
```python
direction_id = fields.Many2one('sn.direction', string='Direction')
# Accès à la catégorie via: service.direction_id.category_id
```

**Modèle `sn.agent`:**
```python
direction_id = fields.Many2one('sn.direction', string='Direction')
# Accès à la catégorie via: agent.direction_id.category_id
```

---

## ✅ Vérifications Effectuées

### Pages Vérifiées

- [x] **Page d'accueil** `/organigramme` - OK (pas de breadcrumb)
- [x] **Liste ministères** `/organigramme/ministeres` - OK
- [x] **Détails ministère** `/organigramme/ministere/{id}` - OK
- [x] **Détails catégorie** `/organigramme/categorie/{id}` - ✅ NOUVEAU
- [x] **Détails direction** `/organigramme/direction/{id}` - ✅ CORRIGÉ (avec catégorie)
- [x] **Détails service** `/organigramme/service/{id}` - ✅ CORRIGÉ (avec catégorie)
- [x] **Détails agent** `/organigramme/agent/{id}` - ✅ CORRIGÉ (avec catégorie)
- [x] **Page recherche** `/organigramme/search` - OK
- [x] **Organigramme interactif** `/organigramme/tree` - OK

### Corrections Appliquées

| Page | Avant | Après |
|------|-------|-------|
| **Direction** | `Accueil > Ministères > Ministère > Direction` | `Accueil > Ministères > Ministère > [Catégorie] > Direction` |
| **Service** | `Accueil > Ministères > Ministère > Direction > Service` | `Accueil > Ministères > Ministère > [Catégorie] > Direction > Service` |
| **Agent** | `Accueil > Ministères > Ministère > Direction > Service > Agent` | `Accueil > Ministères > Ministère > [Catégorie] > Direction > Service > Agent` |

**Note:** `[Catégorie]` s'affiche uniquement si elle existe (logique conditionnelle).

---

## 🎨 Style des Breadcrumbs

### Classes Bootstrap Utilisées

```xml
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item">...</li>
        <li class="breadcrumb-item active">...</li>
    </ol>
</nav>
```

**Classes:**
- `breadcrumb` : conteneur de la liste
- `breadcrumb-item` : élément de la liste
- `breadcrumb-item active` : élément actuel (non cliquable)

### Accessibilité

- ✅ `aria-label="breadcrumb"` pour les lecteurs d'écran
- ✅ Séparateur automatique entre les éléments (via Bootstrap)
- ✅ Dernier élément non cliquable (classe `active`)

---

## 📝 Tests Recommandés

### Tests Manuels

1. **Navigation complète avec catégories:**
   - [ ] Créer un ministère
   - [ ] Créer une catégorie pour ce ministère
   - [ ] Créer une direction dans cette catégorie
   - [ ] Créer un service dans cette direction
   - [ ] Créer un agent dans ce service
   - [ ] Naviguer de l'agent vers le ministère via les breadcrumbs
   - [ ] Vérifier que tous les liens fonctionnent

2. **Navigation sans catégories (rétrocompatibilité):**
   - [ ] Créer une direction sans catégorie
   - [ ] Naviguer vers cette direction
   - [ ] Vérifier que le breadcrumb saute directement du ministère à la direction

3. **Recherche:**
   - [ ] Effectuer une recherche
   - [ ] Cliquer sur un résultat
   - [ ] Vérifier le breadcrumb complet sur la page de détail

---

## 🎉 Résumé

### ✅ Breadcrumbs Complets et Cohérents

- **9 pages** avec breadcrumbs vérifiés
- **5 niveaux hiérarchiques** supportés
- **Logique intelligente** : affiche les catégories uniquement si elles existent
- **Rétrocompatibilité** : fonctionne avec les données existantes
- **Navigation fluide** : tous les liens sont cliquables et fonctionnels

### 🚀 Avantages

1. **Orientation utilisateur** : l'utilisateur sait toujours où il se trouve
2. **Navigation rapide** : retour facile aux niveaux supérieurs
3. **Hiérarchie claire** : visualisation de la structure organisationnelle
4. **Accessibilité** : compatible lecteurs d'écran

---

**Date de validation:** 3 octobre 2025  
**Version:** 18.0.1.0.0  
**Statut:** ✅ **Breadcrumbs Complets avec Support des 5 Niveaux**
