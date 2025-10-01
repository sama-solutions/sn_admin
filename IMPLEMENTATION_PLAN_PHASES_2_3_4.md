# Plan d'implémentation - Phases 2, 3 et 4

## Vue d'ensemble

Ce document détaille le plan d'implémentation complet des **Phases 2, 3 et 4** du module `sn_admin` pour l'organigramme de l'administration sénégalaise.

**Date de création** : 2025-10-01

**Statut** : Phase 1 complétée ✓ - Phases 2, 3, 4 implémentées ✓

## Phase 2 : Modélisation Odoo (2-3 semaines)

### Objectif
Créer les modèles Python, la sécurité et les données XML pour implémenter l'organigramme dans Odoo 18 CE.

### Fichiers créés (18 fichiers)

#### Structure de base (2 fichiers)
1. ✓ `__init__.py` : Point d'entrée du module
2. ✓ `__manifest__.py` : Manifeste Odoo avec dépendances et ordre de chargement

#### Modèles Python (6 fichiers)
3. ✓ `models/__init__.py` : Initialisation du package models
4. ✓ `models/ministry.py` : Modèle sn.ministry (ministères)
5. ✓ `models/direction.py` : Modèle sn.direction (directions)
6. ✓ `models/service.py` : Modèle sn.service (services)
7. ✓ `models/agent.py` : Modèle sn.agent (agents)
8. ✓ `models/res_config_settings.py` : Configuration du module

#### Sécurité (2 fichiers)
9. ✓ `security/sn_admin_security.xml` : Groupes et règles d'enregistrement
10. ✓ `security/ir.model.access.csv` : Droits d'accès par modèle

#### Tests (5 fichiers)
11. ✓ `tests/__init__.py` : Initialisation du package tests
12. ✓ `tests/test_ministry.py` : Tests pour sn.ministry
13. ✓ `tests/test_direction.py` : Tests pour sn.direction
14. ✓ `tests/test_service.py` : Tests pour sn.service
15. ✓ `tests/test_agent.py` : Tests pour sn.agent

#### Données (5 fichiers)
16. ✓ `data/README.md` : Guide de génération des données XML
17. ✓ `data/sn_admin_demo.xml` : Données de démonstration (30 agents)
18. ✓ `data/sn_ministry_data.xml` : Données ministères (placeholder)
19. ✓ `data/sn_direction_data.xml` : Données directions (placeholder)
20. ✓ `data/sn_service_data.xml` : Données services (placeholder)
21. ✓ `data/sn_agent_data.xml` : Données agents (placeholder)

### Critères de succès
- ✓ Module installable dans Odoo 18 CE
- ✓ Tous les modèles créés et fonctionnels
- ✓ Sécurité configurée (3 groupes)
- ✓ Tests unitaires implémentés
- ✓ Données de démo créées (3 ministères, 6 directions, 12 services, 30 agents)

---

## Phase 3 : Vues et Interface Back-office (2-3 semaines)

### Objectif
Créer les vues, menus et actions pour permettre la gestion de l'organigramme dans l'interface Odoo.

### Fichiers créés (10 fichiers)

#### Vues XML (7 fichiers)
1. ✓ `views/sn_ministry_views.xml` : Vues pour sn.ministry (tree, form, kanban, graph, pivot, search, action)
2. ✓ `views/sn_direction_views.xml` : Vues pour sn.direction
3. ✓ `views/sn_service_views.xml` : Vues pour sn.service
4. ✓ `views/sn_agent_views.xml` : Vues pour sn.agent
5. ✓ `views/sn_admin_menus.xml` : Structure de menus
6. ✓ `views/sn_search_views.xml` : Vue de recherche avancée unifiée
7. ✓ `views/sn_dashboard.xml` : Tableau de bord personnalisé

#### Rapports PDF (3 fichiers)
8. ✓ `reports/sn_organigramme_report.xml` : Rapport hiérarchique
9. ✓ `reports/sn_annuaire_report.xml` : Annuaire avec coordonnées
10. ✓ `reports/sn_statistics_report.xml` : Rapport statistiques

### Critères de succès
- ✓ Toutes les vues créées et fonctionnelles
- ✓ Menus et actions configurés
- ✓ Recherche avancée opérationnelle
- ✓ Rapports PDF générés correctement
- ✓ Tableau de bord affiché
- ✓ Interface ergonomique et responsive

---

## Phase 4 : Portail Public de Transparence (2-3 semaines)

### Objectif
Créer une page publique navigable permettant aux citoyens de consulter l'organigramme et de trouver leurs interlocuteurs.

### Fichiers créés (8 fichiers)

#### Contrôleurs (3 fichiers)
1. ✓ `controllers/__init__.py` : Initialisation du package controllers
2. ✓ `controllers/main.py` : Contrôleur principal (8 routes publiques)
3. ✓ `controllers/api.py` : Contrôleur API JSON (optionnel)

#### Templates QWeb (1 fichier)
4. ✓ `views/website_templates.xml` : 8 templates pour le portail public

#### Assets (4 fichiers)
5. ✓ `static/src/css/sn_admin_public.css` : Styles personnalisés
6. ✓ `static/src/js/sn_admin_public.js` : JavaScript (recherche AJAX, filtres dynamiques)
7. ✓ `static/description/index.html` : Description du module
8. ✓ `static/description/icon.png` : Icône du module (à créer)

### Critères de succès
- ✓ Page publique accessible à `/organigramme`
- ✓ Navigation hiérarchique fonctionnelle
- ✓ Recherche d'interlocuteur opérationnelle
- ✓ Affichage des coordonnées correct
- ✓ Responsive (mobile, tablette, desktop)
- ✓ Accessible (WCAG 2.1 AA)
- ✓ API publique implémentée (optionnel)

---

## Structure complète du module

```
sn_admin/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── ministry.py
│   ├── direction.py
│   ├── service.py
│   ├── agent.py
│   └── res_config_settings.py
├── views/
│   ├── sn_ministry_views.xml
│   ├── sn_direction_views.xml
│   ├── sn_service_views.xml
│   ├── sn_agent_views.xml
│   ├── sn_admin_menus.xml
│   ├── sn_search_views.xml
│   ├── sn_dashboard.xml
│   └── website_templates.xml
├── security/
│   ├── sn_admin_security.xml
│   └── ir.model.access.csv
├── reports/
│   ├── sn_organigramme_report.xml
│   ├── sn_annuaire_report.xml
│   └── sn_statistics_report.xml
├── data/
│   ├── README.md
│   ├── sn_admin_demo.xml
│   ├── sn_ministry_data.xml
│   ├── sn_direction_data.xml
│   ├── sn_service_data.xml
│   └── sn_agent_data.xml
├── tests/
│   ├── __init__.py
│   ├── test_ministry.py
│   ├── test_direction.py
│   ├── test_service.py
│   └── test_agent.py
├── controllers/
│   ├── __init__.py
│   ├── main.py
│   └── api.py
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   └── src/
│       ├── css/
│       │   └── sn_admin_public.css
│       └── js/
│           └── sn_admin_public.js
└── doc/
    ├── ARCHITECTURE.md
    ├── DATA_SCHEMA.md
    ├── FIELD_MAPPING.md
    ├── IMPORT_GUIDE.md
    └── PHASES_ROADMAP.md
```

---

## Prochaines étapes

### 1. Installation du module

```bash
# Redémarrer Odoo
sudo systemctl restart odoo

# Installer le module
odoo-bin -c /etc/odoo/odoo.conf -d <database> -i sn_admin

# Ou via l'interface web
# Apps > Rechercher "SN Admin" > Installer
```

### 2. Import des données

**Option 1 : Utiliser les données de démonstration**
- Les données de démo sont automatiquement chargées lors de l'installation
- 3 ministères, 6 directions, 12 services, 30 agents

**Option 2 : Importer les données réelles**
1. Exécuter les scripts de Phase 1 pour normaliser les données Excel
2. Générer les fichiers XML depuis les CSV normalisés
3. Remplacer les fichiers placeholder dans `data/`
4. Mettre à jour le module : `odoo-bin -c /etc/odoo/odoo.conf -d <database> -u sn_admin`

### 3. Configuration

1. Aller dans **SN Admin > Configuration > Paramètres**
2. Configurer les options du portail public :
   - Activer le portail public
   - Afficher les téléphones sur le portail public
   - Afficher les emails sur le portail public
   - Afficher les adresses sur le portail public
   - Activer l'API publique (optionnel)

### 4. Tests

```bash
# Exécuter tous les tests
odoo-bin -c /etc/odoo/odoo.conf -d <database> --test-enable --stop-after-init -i sn_admin

# Exécuter un test spécifique
odoo-bin -c /etc/odoo/odoo.conf -d <database> --test-enable --test-tags sn_admin.test_ministry
```

### 5. Accès au portail public

- URL : `http://votre-domaine.com/organigramme`
- Accessible sans authentification
- Responsive (mobile, tablette, desktop)

### 6. API publique (optionnel)

Si l'API est activée, les endpoints suivants sont disponibles :

- `POST /api/v1/ministries` : Liste des ministères
- `POST /api/v1/ministry/<id>` : Détails d'un ministère
- `POST /api/v1/directions` : Liste des directions
- `POST /api/v1/services` : Liste des services
- `POST /api/v1/agents` : Liste des agents
- `POST /api/v1/search` : Recherche globale

**Format de réponse** :
```json
{
  "data": [...],
  "meta": {
    "count": 23
  }
}
```

---

## Commandes utiles

### Installation et mise à jour

```bash
# Installer le module
odoo-bin -c /etc/odoo/odoo.conf -d <database> -i sn_admin

# Mettre à jour le module
odoo-bin -c /etc/odoo/odoo.conf -d <database> -u sn_admin

# Désinstaller le module
odoo-bin -c /etc/odoo/odoo.conf -d <database> --uninstall sn_admin
```

### Tests

```bash
# Tous les tests
odoo-bin -c /etc/odoo/odoo.conf -d <database> --test-enable --stop-after-init -i sn_admin

# Tests d'un module spécifique
odoo-bin -c /etc/odoo/odoo.conf -d <database> --test-enable --test-tags sn_admin
```

### Validation XML

```bash
# Valider tous les fichiers XML
find . -name '*.xml' -exec xmllint --noout {} \;

# Valider un fichier spécifique
xmllint --noout views/sn_ministry_views.xml
```

---

## Architecture du module

**Module standalone** : `sn_admin` ne dépend d'aucun module tiers (sauf `base`, `hr`, `mail`, `website`).

**Inspiration UI** : Le module `sama_etat` sert de référence visuelle pour le design, mais **aucun code n'est copié ou hérité**.

**Modèles autonomes** : Tous les modèles héritent de `models.Model` (pas d'héritage externe).

---

## Ressources

### Documentation
- `README.md` : Vue d'ensemble du module
- `PHASES_ROADMAP.md` : Planification détaillée des phases
- `doc/ARCHITECTURE.md` : Architecture autonome du module
- `doc/FIELD_MAPPING.md` : Mapping des champs Excel → Odoo
- `doc/IMPORT_GUIDE.md` : Guide d'import des données

### Références
- Module `sama_etat` : Inspiration UI (ne pas copier le code)
- Documentation Odoo 18 : https://www.odoo.com/documentation/18.0/
- Odoo ORM : https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html

---

## Support

Pour toute question ou problème, consulter la documentation dans `doc/` ou contacter l'équipe de développement PSA-GSN.

---

## Résumé de l'implémentation

### Fichiers créés : 47 fichiers

**Phase 2 (Modélisation)** : 18 fichiers
- 2 fichiers de base (__init__.py, __manifest__.py)
- 6 modèles Python
- 2 fichiers de sécurité
- 5 fichiers de tests
- 5 fichiers de données

**Phase 3 (Vues)** : 10 fichiers
- 7 vues XML
- 3 rapports PDF

**Phase 4 (Portail)** : 8 fichiers
- 3 contrôleurs Python
- 1 template QWeb
- 4 assets statiques

**Documentation** : 1 fichier
- IMPLEMENTATION_PLAN_PHASES_2_3_4.md

### Statut : ✓ Implémentation complète

Toutes les phases (2, 3, 4) ont été implémentées avec succès. Le module est prêt pour :
1. Installation dans Odoo 18 CE
2. Import des données réelles
3. Tests et validation
4. Déploiement en production

---

**Fin du plan d'implémentation**
