# Roadmap des Phases - Module SN Admin

## Vue d'ensemble

Ce document détaille la planification des **Phases 2, 3 et 4** du module `sn_admin` pour l'organigramme de l'administration sénégalaise.

**Architecture** : Module **standalone** (autonome) - Aucune dépendance tierce.

**Inspiration UI** : Le module `sama_etat` peut servir de référence visuelle pour le design, mais **aucun code n'est copié ou hérité**.

---

## Phase 2 : Modélisation Odoo

### Objectif
Créer les modèles Python, la sécurité et les données XML pour implémenter l'organigramme dans Odoo 18 CE.

### Durée estimée
2-3 semaines

### Prérequis
- Phase 1 complétée ✓
- Données normalisées disponibles dans `data/normalized/`
- Mapping Odoo généré dans `data/odoo_mapping.json`

### Livrables

#### 1. Modèles Python (models/)

**models/__init__.py**
- Importer tous les modèles

**models/ministry.py** (sn.ministry)
- Modèle **autonome** héritant de `models.Model`
- Champs : `name`, `code`, `type`, `address`, `phone`, `email`, `website`, `description`, `active`, `state`
- Relations : `direction_ids` (One2many vers sn.direction)
- Champs calculés : `direction_count`, `service_count`, `agent_count`
- Contraintes SQL : `code_unique`, `name_unique`
- Méthodes : `name_get()`, `_compute_direction_count()`, recherche avancée
- Mixins : `mail.thread`, `mail.activity.mixin` (suivi et activités)

**models/direction.py** (sn.direction)
- Champs : `name`, `code`, `type`, `ministry_id`, `manager_id`, `phone`, `email`, `address`, `active`, `state`
- Relations : `ministry_id` (Many2one vers sn.ministry), `service_ids` (One2many vers sn.service)
- Champs calculés : `service_count`, `agent_count`
- Contraintes : `code_unique`, validation hiérarchique
- Types : `generale` (Direction Générale), `regionale` (Direction Régionale), `technique` (Direction Technique)

**models/service.py** (sn.service)
- Champs : `name`, `code`, `type`, `direction_id`, `manager_id`, `phone`, `email`, `active`, `state`
- Relations : `direction_id` (Many2one vers sn.direction), `agent_ids` (One2many vers sn.agent)
- Champs calculés : `agent_count`, `ministry_id` (related via direction_id)
- Types : `service` (Service), `bureau` (Bureau), `cellule` (Cellule), `division` (Division)

**models/agent.py** (sn.agent)
- Champs : `name`, `first_name`, `last_name`, `function`, `service_id`, `employee_id`, `work_phone`, `mobile_phone`, `work_email`, `matricule`, `active`, `state`
- Relations : `service_id` (Many2one vers sn.service), `employee_id` (Many2one optionnel vers hr.employee)
- Champs calculés : `direction_id`, `ministry_id` (related via service_id)
- Méthodes : `_onchange_employee_id()` (synchronisation avec hr.employee si lié)
- Contraintes : `matricule_unique` (si renseigné)

**models/res_config_settings.py** (extension)
- Ajouter paramètres de configuration du module
- Options : affichage public, champs visibles, format d'export

#### 2. Sécurité (security/)

**security/sn_admin_security.xml**
- Catégorie : `SN Admin`
- Groupes :
  - `group_sn_admin_user` : Utilisateur (consultation)
  - `group_sn_admin_manager` : Gestionnaire (modification)
  - `group_sn_admin_admin` : Administrateur (configuration)
- Règles d'enregistrement (record rules) :
  - Consultation publique des données actives
  - Modification réservée aux gestionnaires
  - Suppression réservée aux administrateurs

**security/ir.model.access.csv**
- Droits d'accès par modèle et par groupe
- Format : `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`
- Exemples :
  - `access_sn_ministry_user,sn.ministry.user,model_sn_ministry,group_sn_admin_user,1,0,0,0`
  - `access_sn_ministry_manager,sn.ministry.manager,model_sn_ministry,group_sn_admin_manager,1,1,1,0`
  - `access_sn_ministry_admin,sn.ministry.admin,model_sn_ministry,group_sn_admin_admin,1,1,1,1`

#### 3. Données XML (data/)

**data/sn_ministry_data.xml**
- Import des ministères depuis `data/normalized/ministeres_normalized.csv`
- Format : `<record id="ministry_xxx" model="sn.ministry">`
- Utiliser `external_id` pour faciliter les mises à jour
- Environ 23+ ministères

**data/sn_direction_data.xml**
- Import des directions depuis `data/normalized/directions_normalized.csv`
- Lien vers ministères via `ref()`
- Environ 100+ directions

**data/sn_service_data.xml**
- Import des services depuis `data/normalized/services_normalized.csv`
- Lien vers directions via `ref()`
- Environ 300+ services

**data/sn_agent_data.xml**
- Import des agents depuis `data/normalized/agents_normalized.csv`
- Lien vers services via `ref()`
- Environ 1000+ agents

**data/sn_admin_demo.xml** (optionnel)
- Données de démonstration pour tests
- Sous-ensemble représentatif de l'organigramme

#### 4. Manifeste (__manifest__.py)

```python
{
    'name': 'SN Admin - Organigramme Administration Sénégalaise',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Gestion de l\'organigramme de l\'administration publique sénégalaise',
    'description': '''
        Module autonome pour gérer l'organigramme complet de l'administration sénégalaise.
        - Ministères, Directions, Services, Agents
        - Intégration avec module RH
        - Portail public de transparence
    ''',
    'author': 'Équipe PSA-GSN',
    'website': 'https://www.gouv.sn',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'mail'],  # Pas de sama_etat
    'data': [
        'security/sn_admin_security.xml',
        'security/ir.model.access.csv',
        'data/sn_ministry_data.xml',
        'data/sn_direction_data.xml',
        'data/sn_service_data.xml',
        'data/sn_agent_data.xml',
    ],
    'demo': [
        'data/sn_admin_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

#### 5. Tests (tests/)

**tests/__init__.py**
- Importer tous les tests

**tests/test_ministry.py**
- Test création ministère
- Test contraintes (code unique, nom unique)
- Test champs calculés (direction_count)
- Test recherche

**tests/test_direction.py**
- Test création direction
- Test relation avec ministère
- Test validation hiérarchique

**tests/test_service.py**
- Test création service
- Test relation avec direction
- Test champs calculés

**tests/test_agent.py**
- Test création agent
- Test lien avec hr.employee
- Test synchronisation des champs

### Critères de succès Phase 2
- ✓ Module installable dans Odoo 18 CE
- ✓ Tous les modèles créés et fonctionnels
- ✓ Sécurité configurée (3 groupes)
- ✓ Données importées (ministères, directions, services, agents)
- ✓ Tests unitaires passent (>80% couverture)
- ✓ Aucune dépendance à `sama_etat`

---

## Phase 3 : Vues et Interface Back-office

### Objectif
Créer les vues, menus et actions pour permettre la gestion de l'organigramme dans l'interface Odoo.

### Durée estimée
2-3 semaines

### Prérequis
- Phase 2 complétée
- Module installé et fonctionnel

### Livrables

#### 1. Vues Ministères (views/sn_ministry_views.xml)

**Vue Tree (liste)**
- Colonnes : `name`, `code`, `type`, `phone`, `email`, `direction_count`, `state`
- Filtres : par type (présidence, primature, ministère), par état
- Groupement : par type
- Recherche : par nom, code, email

**Vue Form (formulaire)**
- Onglets :
  - **Informations générales** : name, code, type, description
  - **Coordonnées** : address, phone, email, website
  - **Directions** : One2many tree (direction_ids)
  - **Statistiques** : direction_count, service_count, agent_count
- Boutons d'action : Voir directions, Voir services, Voir agents
- Chatter : suivi des modifications (mail.thread)

**Vue Kanban**
- Cartes avec : nom, code, type, nombre de directions
- Couleurs par type (présidence: rouge, primature: bleu, ministère: vert)
- Actions rapides : Voir détails, Voir directions

**Vue Graph (graphique)**
- Graphique en barres : nombre de directions par ministère
- Graphique en camembert : répartition par type

**Vue Pivot (tableau croisé)**
- Lignes : ministères
- Colonnes : types de directions
- Mesures : nombre de directions, nombre de services, nombre d'agents

**Inspiration UI** : S'inspirer du design de `sama_etat/views/government_ministry_views.xml` pour la mise en page et les couleurs, mais **créer du code 100% autonome**.

#### 2. Vues Directions (views/sn_direction_views.xml)

**Vue Tree**
- Colonnes : `name`, `code`, `type`, `ministry_id`, `manager_id`, `service_count`, `state`
- Filtres : par type, par ministère
- Groupement : par ministère, par type

**Vue Form**
- Onglets :
  - **Informations** : name, code, type, ministry_id, manager_id
  - **Coordonnées** : phone, email, address
  - **Services** : One2many tree (service_ids)
  - **Statistiques** : service_count, agent_count

**Vue Kanban**
- Cartes groupées par ministère
- Couleurs par type de direction

#### 3. Vues Services (views/sn_service_views.xml)

**Vue Tree**
- Colonnes : `name`, `code`, `type`, `direction_id`, `ministry_id`, `manager_id`, `agent_count`
- Filtres : par type, par direction, par ministère
- Groupement : par direction

**Vue Form**
- Onglets :
  - **Informations** : name, code, type, direction_id, manager_id
  - **Coordonnées** : phone, email
  - **Agents** : One2many tree (agent_ids)

**Vue Kanban**
- Cartes groupées par direction

#### 4. Vues Agents (views/sn_agent_views.xml)

**Vue Tree**
- Colonnes : `name`, `function`, `service_id`, `direction_id`, `ministry_id`, `work_phone`, `work_email`
- Filtres : par service, par direction, par ministère, par fonction
- Groupement : par service, par fonction

**Vue Form**
- Sections :
  - **Identité** : name, first_name, last_name, matricule
  - **Fonction** : function, service_id
  - **Coordonnées** : work_phone, mobile_phone, work_email
  - **Lien RH** : employee_id (optionnel)

**Vue Kanban**
- Cartes avec photo (si lié à hr.employee)
- Groupées par service

#### 5. Menus et Actions (views/sn_admin_menus.xml)

**Menu principal** : `SN Admin`
- Icône : `fa-sitemap`

**Sous-menus** :
- **Organigramme**
  - Ministères (action vers vue kanban)
  - Directions (action vers vue tree)
  - Services (action vers vue tree)
  - Agents (action vers vue tree)
- **Recherche**
  - Recherche d'interlocuteur (vue search avancée)
  - Annuaire (vue liste complète)
- **Rapports**
  - Organigramme hiérarchique (rapport PDF)
  - Annuaire par ministère (rapport PDF)
  - Statistiques (tableau de bord)
- **Configuration**
  - Paramètres (res.config.settings)
  - Groupes d'accès (security groups)

#### 6. Recherche Avancée (views/sn_search_views.xml)

**Vue de recherche unifiée**
- Recherche globale dans tous les modèles (ministères, directions, services, agents)
- Filtres combinés : nom, fonction, ministère, région, téléphone, email
- Résultats groupés par type (ministère, direction, service, agent)
- Actions : Voir détails, Contacter, Exporter

#### 7. Rapports (reports/)

**reports/sn_organigramme_report.xml**
- Rapport PDF de l'organigramme hiérarchique
- Format : arbre avec indentation
- Filtrable par ministère

**reports/sn_annuaire_report.xml**
- Rapport PDF de l'annuaire
- Format : liste avec coordonnées
- Groupé par ministère/direction/service

**reports/sn_statistics_report.xml**
- Tableau de bord avec statistiques
- Graphiques : répartition par type, par région, par fonction

#### 8. Tableau de Bord (views/sn_dashboard.xml)

**Dashboard personnalisé**
- Widgets :
  - Nombre total de ministères, directions, services, agents
  - Graphique : répartition par type de ministère
  - Graphique : top 10 ministères par nombre d'agents
  - Liste : dernières modifications
  - Recherche rapide

**Inspiration UI** : S'inspirer du tableau de bord de `sama_etat` pour le design et la disposition des widgets, mais **créer du code autonome**.

### Critères de succès Phase 3
- ✓ Toutes les vues créées et fonctionnelles
- ✓ Menus et actions configurés
- ✓ Recherche avancée opérationnelle
- ✓ Rapports PDF générés correctement
- ✓ Tableau de bord affiché
- ✓ Interface ergonomique et responsive
- ✓ Aucun code copié de `sama_etat`

---

## Phase 4 : Portail Public de Transparence

### Objectif
Créer une page publique navigable permettant aux citoyens de consulter l'organigramme et de trouver leurs interlocuteurs.

### Durée estimée
2-3 semaines

### Prérequis
- Phase 3 complétée
- Module `website` installé

### Livrables

#### 1. Contrôleurs Web (controllers/)

**controllers/__init__.py**
- Importer tous les contrôleurs

**controllers/main.py**
- Route `/organigramme` : Page d'accueil de l'organigramme
- Route `/organigramme/ministeres` : Liste des ministères
- Route `/organigramme/ministere/<int:id>` : Détails d'un ministère
- Route `/organigramme/direction/<int:id>` : Détails d'une direction
- Route `/organigramme/service/<int:id>` : Détails d'un service
- Route `/organigramme/agent/<int:id>` : Détails d'un agent
- Route `/organigramme/search` : Recherche d'interlocuteur
- Route `/organigramme/api/search` : API JSON pour recherche AJAX

**Sécurité** :
- Toutes les routes sont publiques (`auth='public'`)
- Filtrer uniquement les enregistrements actifs (`active=True`, `state='active'`)
- Masquer les données sensibles (si configuré)

#### 2. Templates QWeb (views/website_templates.xml)

**Template : Page d'accueil (/organigramme)**
- Hero section : Titre "Organigramme de l'Administration Sénégalaise"
- Barre de recherche globale (AJAX)
- Cartes cliquables : Présidence, Primature, Ministères
- Statistiques : nombre de ministères, directions, services, agents
- Footer : liens utiles, contact

**Template : Liste des ministères**
- Grille de cartes (3 colonnes responsive)
- Chaque carte : nom, code, téléphone, email, nombre de directions
- Filtres : par type (présidence, primature, ministère)
- Tri : alphabétique, par nombre de directions

**Template : Détails d'un ministère**
- Breadcrumb : Accueil > Ministères > [Nom]
- Section informations : nom, code, adresse, téléphone, email, site web, description
- Section directions : liste des directions (accordéon ou cartes)
- Bouton : Voir l'organigramme complet (arbre hiérarchique)

**Template : Détails d'une direction**
- Breadcrumb : Accueil > Ministères > [Ministère] > [Direction]
- Informations : nom, code, type, responsable, coordonnées
- Liste des services (accordéon)

**Template : Détails d'un service**
- Breadcrumb : Accueil > ... > [Service]
- Informations : nom, code, type, responsable, coordonnées
- Liste des agents (tableau)

**Template : Détails d'un agent**
- Breadcrumb : Accueil > ... > [Agent]
- Informations : nom, fonction, service, direction, ministère
- Coordonnées : téléphone bureau, mobile, email
- Photo (si lié à hr.employee et photo disponible)

**Template : Recherche**
- Formulaire de recherche avancée :
  - Champ texte : nom, fonction
  - Select : ministère, direction, service
  - Bouton : Rechercher
- Résultats en temps réel (AJAX)
- Affichage : cartes avec nom, fonction, service, coordonnées
- Pagination : 20 résultats par page

**Template : Organigramme hiérarchique**
- Arbre interactif (JavaScript) :
  - Nœuds cliquables (expand/collapse)
  - Zoom et pan
  - Export en PNG/PDF
- Bibliothèque : D3.js ou OrgChart.js (open source)

#### 3. Assets (static/)

**static/src/css/sn_admin_public.css**
- Styles personnalisés pour le portail public
- Couleurs : drapeau sénégalais (vert, jaune, rouge)
- Responsive : mobile-first
- Accessibilité : contraste WCAG 2.1 AA

**static/src/js/sn_admin_public.js**
- Recherche AJAX en temps réel
- Filtres dynamiques
- Organigramme interactif (D3.js)
- Lazy loading des images

**static/src/img/**
- Logo République du Sénégal
- Icônes (ministères, directions, services, agents)
- Placeholder pour photos

#### 4. SEO et Accessibilité

**Métadonnées**
- Titre : "Organigramme de l'Administration Sénégalaise"
- Description : "Trouvez vos interlocuteurs dans l'administration publique sénégalaise"
- Mots-clés : organigramme, administration, Sénégal, ministères, transparence
- Open Graph : image, titre, description (partage réseaux sociaux)

**Accessibilité (WCAG 2.1 niveau AA)**
- Attributs `alt` sur toutes les images
- Navigation au clavier (tabindex)
- Contraste des couleurs (ratio 4.5:1)
- Formulaires avec labels explicites
- ARIA labels pour éléments interactifs

**Performance**
- Lazy loading des images
- Minification CSS/JS
- Cache HTTP (1 heure)
- CDN pour bibliothèques externes

#### 5. API Publique (optionnel)

**controllers/api.py**
- Route `/api/v1/ministries` : Liste des ministères (JSON)
- Route `/api/v1/ministry/<int:id>` : Détails d'un ministère (JSON)
- Route `/api/v1/search?q=<query>` : Recherche (JSON)
- Format : JSON API standard
- Documentation : Swagger/OpenAPI
- Rate limiting : 100 requêtes/minute

### Critères de succès Phase 4
- ✓ Page publique accessible à `/organigramme`
- ✓ Navigation hiérarchique fonctionnelle
- ✓ Recherche d'interlocuteur opérationnelle
- ✓ Affichage des coordonnées correct
- ✓ Responsive (mobile, tablette, desktop)
- ✓ Accessible (WCAG 2.1 AA)
- ✓ Performance optimale (< 2s chargement)
- ✓ SEO optimisé
- ✓ Aucune dépendance à `sama_etat`

---

## Planning global

### Timeline
- **Phase 1** : ✓ Complétée (1 semaine)
- **Phase 2** : Semaines 2-4 (2-3 semaines)
- **Phase 3** : Semaines 5-7 (2-3 semaines)
- **Phase 4** : Semaines 8-10 (2-3 semaines)
- **Total** : 8-10 semaines

### Jalons (Milestones)
1. **M1** : Phase 1 complétée ✓
2. **M2** : Module installable (fin Phase 2)
3. **M3** : Interface back-office fonctionnelle (fin Phase 3)
4. **M4** : Portail public en ligne (fin Phase 4)
5. **M5** : Mise en production

### Ressources
- **Développeur backend** : Phases 2-3 (modèles, vues)
- **Développeur frontend** : Phase 4 (portail public)
- **Designer UI/UX** : Phases 3-4 (design, ergonomie)
- **Testeur QA** : Toutes phases (tests, validation)

---

## Risques et mitigation

### Risques identifiés

**R1 : Données incomplètes ou incorrectes**
- Impact : Moyen
- Probabilité : Moyenne
- Mitigation : Validation stricte en Phase 1, rapport de qualité

**R2 : Performance (1000+ agents)**
- Impact : Élevé
- Probabilité : Faible
- Mitigation : Index SQL, pagination, cache, lazy loading

**R3 : Sécurité (données publiques)**
- Impact : Moyen
- Probabilité : Faible
- Mitigation : Filtrage des données sensibles, rate limiting API

**R4 : Compatibilité Odoo (versions futures)**
- Impact : Moyen
- Probabilité : Moyenne
- Mitigation : Code standard Odoo, tests automatisés

**R5 : Accessibilité (WCAG)**
- Impact : Moyen
- Probabilité : Moyenne
- Mitigation : Audit accessibilité, tests avec lecteurs d'écran

---

## Maintenance et évolution

### Maintenance corrective
- Correction de bugs
- Mises à jour de sécurité
- Compatibilité avec nouvelles versions Odoo

### Maintenance évolutive
- Ajout de nouveaux ministères/directions/services
- Mise à jour des coordonnées
- Ajout de nouvelles fonctionnalités

### Évolutions futures
- **V2** : Intégration avec système RH existant
- **V3** : Application mobile (Android/iOS)
- **V4** : Chatbot pour recherche d'interlocuteur
- **V5** : Carte interactive (géolocalisation des services)

---

## Conclusion

Ce roadmap détaille les **Phases 2, 3 et 4** du module `sn_admin` avec une architecture **100% autonome**.

**Points clés** :
- ✓ Aucune dépendance à `sama_etat` (uniquement inspiration UI)
- ✓ Tous les modèles définis localement
- ✓ Code réutilisable et maintenable
- ✓ Portail public accessible et performant
- ✓ Conformité aux standards (WCAG, SEO, performance)

Le module sera prêt pour la mise en production à la fin de la Phase 4.
