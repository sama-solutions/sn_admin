# 🏛️ SN Admin - Registre Officiel de l'Administration Sénégalaise

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0%20CE-blue.svg)](https://github.com/odoo/odoo)
[![License](https://img.shields.io/badge/License-LGPL--3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

## 📋 Description

**SN Admin** est un module Odoo 18 Community Edition qui fournit un **registre officiel complet** de l'administration sénégalaise. Il permet la gestion transparente et accessible de l'organigramme gouvernemental du Sénégal.

## ✨ Fonctionnalités Principales

### 🏢 Gestion Administrative
- **Ministères** : Gestion complète des ministères et institutions
- **Directions** : Organisation des directions par ministère
- **Services** : Structure détaillée des services administratifs
- **Agents** : Registre des fonctionnaires avec informations de contact

### 🌐 Interface Publique
- **Organigramme interactif** : Visualisation hiérarchique navigable
- **Recherche avancée** : Moteur de recherche multi-critères
- **Annuaire public** : Répertoire accessible aux citoyens
- **Interface responsive** : Compatible mobile et desktop

### 📊 Rapports et Analytics
- **Statistiques administratives** : Tableaux de bord détaillés
- **Rapports PDF** : Génération d'organigrammes et annuaires
- **Exports** : Données exportables en différents formats

### 🔌 API et Intégrations
- **API REST** : Endpoints pour intégrations externes
- **Webhooks** : Notifications en temps réel
- **Synchronisation** : Compatible avec systèmes tiers

## 🚀 Installation Rapide

### Prérequis
- Odoo 18.0 Community Edition
- Python 3.8+
- PostgreSQL 12+

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/sama-solutions/sama_administration.git
   cd sama_administration
   ```

2. **Copier dans Odoo**
   ```bash
   cp -r . /path/to/odoo/addons/sn_admin/
   ```

3. **Installer le module**
   - Aller dans Apps > Update Apps List
   - Rechercher "SN Admin"
   - Cliquer sur "Install"

4. **Importer les données de démonstration**
   ```bash
   # Optionnel : données de test avec 30+ ministères
   odoo-bin -d your_database -i sn_admin --load-language=fr_FR
   ```

## 📁 Structure du Projet

```
sn_admin/
├── 📄 __manifest__.py          # Configuration du module
├── 📁 controllers/             # Contrôleurs web et API
│   ├── main.py                # Interface publique
│   └── api.py                 # API REST
├── 📁 models/                  # Modèles de données
│   ├── ministry.py            # Ministères
│   ├── direction.py           # Directions
│   ├── service.py             # Services
│   └── agent.py               # Agents/Fonctionnaires
├── 📁 views/                   # Interfaces utilisateur
│   ├── sn_ministry_views.xml  # Vues ministères
│   ├── sn_admin_menus.xml     # Structure des menus
│   └── website_templates.xml  # Templates web publics
├── 📁 static/                  # Ressources statiques
│   ├── src/css/               # Styles CSS
│   └── src/js/                # JavaScript
├── 📁 data/                    # Données de démonstration
├── 📁 security/                # Règles de sécurité
├── 📁 reports/                 # Rapports PDF
└── 📁 tests/                   # Tests unitaires
```

## 🎯 Utilisation

### Interface Administrative (Backend)
1. **Accès** : Menu "SN Admin" dans Odoo
2. **Gestion** : CRUD complet sur toutes les entités
3. **Rapports** : Génération de documents officiels
4. **Configuration** : Paramètres de visibilité publique

### Interface Publique (Frontend)
1. **URL** : `http://your-domain/organigramme`
2. **Navigation** : Exploration hiérarchique intuitive
3. **Recherche** : `http://your-domain/organigramme/search`
4. **API** : `http://your-domain/api/sn_admin/`

## 🔧 Configuration

### Paramètres Système
```python
# Activer l'interface publique
sn_admin.public_portal_enabled = True

# Affichage des informations de contact
sn_admin.show_phone_public = True
sn_admin.show_email_public = True

# Activer l'API REST
sn_admin.enable_api = True
```

### Groupes de Sécurité
- **SN Admin User** : Consultation uniquement
- **SN Admin Manager** : Modification des données
- **SN Admin Admin** : Configuration complète

## 📊 Données Incluses

Le module inclut des données de démonstration représentatives :
- **30+ Ministères** et institutions gouvernementales
- **100+ Directions** administratives
- **200+ Services** spécialisés
- **500+ Agents** avec informations de contact

## 🔗 API Documentation

### Endpoints Principaux
```bash
# Liste des ministères
GET /api/sn_admin/ministries

# Détail d'un ministère
GET /api/sn_admin/ministry/{id}

# Recherche d'agents
GET /api/sn_admin/search?q=terme&type=agent

# Organigramme complet
GET /api/sn_admin/organigramme
```

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/

# Tests d'intégration Odoo
odoo-bin --test-enable --test-tags sn_admin --stop-after-init
```

## 🤝 Contribution

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** les changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

## 📝 Licence

Ce projet est sous licence **LGPL-3.0**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🏢 À Propos

**Développé par** : [Sama Solutions](https://github.com/sama-solutions)  
**Pour** : République du Sénégal  
**Objectif** : Transparence et modernisation de l'administration publique

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/sama-solutions/sama_administration/issues)
- **Documentation** : Voir le dossier `/doc`
- **Email** : support@sama-solutions.com

---

⭐ **Si ce projet vous aide, n'hésitez pas à lui donner une étoile !**