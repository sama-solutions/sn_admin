# SN Admin - Registre Officiel de l'Administration Sénégalaise

**Auteurs :** Mamadou Mbagnick DOGUE & Rassol DOGUE  
**Version :** 18.0.1.2.0  
**Licence :** LGPL-3.0  
**Compatibilité :** Odoo 18 Community Edition  

---

## 🏛️ Fondement Institutionnel Officiel

**DÉCRET PRÉSIDENTIEL N° 2025-1431**

> **Décret n° 2025-1431 portant répartition des services de l'État et du contrôle des établissements publics, des sociétés nationales et des sociétés à participation publique entre la Présidence de la République, la Primature et les ministères**

Ce module **SN Admin** constitue l'**implémentation numérique officielle** du décret présidentiel n° 2025-1431, permettant :

✅ **Transparence constitutionnelle** : Application des principes de transparence administrative  
✅ **Conformité réglementaire** : Respect des textes d'organisation de l'État  
✅ **Modernisation digitale** : Digitalisation de l'organigramme gouvernemental  
✅ **Accessibilité citoyenne** : Facilitation de l'accès aux services publics  
✅ **Efficacité administrative** : Optimisation de la gestion des ressources humaines  

---

## 📋 Description

**RÉVOLUTION DANS LA TRANSPARENCE ADMINISTRATIVE DU SÉNÉGAL**

Module Odoo 18 CE pour le **Registre Officiel Complet** de l'administration publique sénégalaise. Ce n'est pas un simple module de démonstration, mais le registre national officiel avec TOUTES les données de l'État.

### ✨ Fonctionnalités principales

- ✓ **Données complètes** : TOUTE l'architecture organique de l'État (ministères, directions, services)
- ✓ **Intégration RH Odoo** : Synchronisation bidirectionnelle avec hr.employee et hr.department
- ✓ **Vues Organigramme** : Visualisation hiérarchique interactive (OrgChart.js)
- ✓ **QR Codes** : Chaque structure a un QR code partageable
- ✓ **Portail public enrichi** : Contacts détaillés, cartes GPS, partage sur réseaux sociaux
- ✓ **Gestion des nominations** : Dates, décrets, documents
- ✓ **Recherche avancée** : Par nom, fonction, ministère, région
- ✓ **Export** : PDF, Excel, PNG

### 🎯 Cas d'usage

- **Pour les citoyens** : Trouver facilement un interlocuteur dans l'administration
- **Pour le gouvernement** : Gérer les nominations et le personnel
- **Pour les ministères** : Maintenir à jour l'organigramme et les contacts
- **Pour les RH** : Utiliser l'interface RH standard d'Odoo pour gérer les agents

---

## 🚀 Installation rapide

### Prérequis

```bash
pip install -r requirements.txt
```

### Installation du module dans Odoo

```bash
# 1. Copier le module dans addons
cp -r sn_admin /path/to/odoo/addons/

# 2. Redémarrer Odoo
sudo systemctl restart odoo

# 3. Installer le module via l'interface Odoo
# Apps > Update Apps List > Search \"SN Admin\" > Install
```

---

## 🏗️ Architecture

**Module Standalone** : `sn_admin` est un module **autonome** qui ne dépend d'aucun module tiers. Il peut être installé sur n'importe quelle instance Odoo 18 CE avec uniquement les modules standards (`base`, `hr`, `website`).

### Structure du projet

```
sn_admin/
├── __init__.py
├── __manifest__.py
├── README.md
├── LICENSE
├── requirements.txt
├── controllers/                    # Contrôleurs web
├── data/                          # Données de démonstration
├── doc/                           # Documentation technique
├── models/                        # Modèles Odoo
├── reports/                       # Rapports PDF
├── security/                      # Règles de sécurité
├── static/                        # Assets CSS/JS
├── tests/                         # Tests unitaires
└── views/                         # Vues et templates
```

---

## ✅ Conformité Odoo 18 CE

**MODULE 100% CONFORME ODOO 18 COMMUNITY EDITION**

Ce module respecte strictement les directives Odoo 18 CE :

- ✅ **Vues modernes** : Utilisation systématique de `<list>` avec `multi_edit=\"1\"`
- ✅ **Dépendances sûres** : `base`, `hr`, `mail`, `website` uniquement
- ✅ **Pas de modules Enterprise** : Aucune dépendance à `account` ou modules EE
- ✅ **Python 3.11+** : Code compatible avec les dernières versions
- ✅ **PostgreSQL 13+** : Base de données moderne
- ✅ **Framework standard** : Utilisation des composants Odoo natifs

---

## 🔧 Configuration

### Groupes d'accès

- **SN Admin / User** : Consultation de l'organigramme
- **SN Admin / Manager** : Gestion de l'organigramme
- **SN Admin / Administrator** : Administration complète

### Données de démonstration

Le module inclut des données de démonstration basées sur l'organigramme réel :
- 23+ ministères
- 100+ directions
- 300+ services
- Agents (sera rempli progressivement)

---

## 📖 Documentation

- **[FONDEMENT_LEGAL.md](FONDEMENT_LEGAL.md)** : Base légale et institutionnelle
- **[ODOO18_CE_COMPLIANCE.md](ODOO18_CE_COMPLIANCE.md)** : Conformité Odoo 18 CE
- **[PHASES_ROADMAP.md](PHASES_ROADMAP.md)** : Planification des phases
- **[doc/ARCHITECTURE.md](doc/ARCHITECTURE.md)** : Architecture du module
- **[doc/IMPORT_GUIDE.md](doc/IMPORT_GUIDE.md)** : Guide d'import des données

---

## 🌐 Portail public

URL : `https://votre-domaine.sn/organigramme`

**Fonctionnalités** :
- Navigation hiérarchique interactive
- Recherche par nom, fonction, ministère
- Affichage des coordonnées (téléphone, email)
- Responsive (mobile, tablette, desktop)
- Accessible (WCAG 2.1 niveau AA)

---

## 🧪 Tests

### Tests unitaires

```bash
# Lancer les tests
python -m pytest tests/

# Avec couverture
python -m pytest --cov=sn_admin tests/
```

### Tests d'intégration

```bash
# Lancer Odoo en mode test
odoo-bin -d test_db -i sn_admin --test-enable --stop-after-init
```

---

## 🔒 Sécurité

### Données sensibles

- Les emails et téléphones sont publics (transparence administrative)
- Pas de données personnelles sensibles
- Conformité RGPD : données professionnelles uniquement

### Accès

- Consultation publique : organigramme et coordonnées
- Modification : réservée aux administrateurs
- Suppression : réservée aux super-administrateurs

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez consulter la documentation technique dans le dossier `doc/` avant de contribuer.

---

## 📞 Support

Pour toute question :
- Consulter la documentation dans `doc/`
- Ouvrir une issue sur GitHub
- Contacter les auteurs

---

## 📝 Changelog

### Version 18.0.1.2.0 - 2025-10-03
- ✓ Correction erreur 500 lors de l'installation
- ✓ Finalisation compatibilité Odoo 18
- ✓ Optimisation des règles de sécurité

### Version 18.0.1.1.0 - 2025-10-03
- ✓ Migration complète vers Odoo 18
- ✓ Correction des attributs attrs → options
- ✓ Optimisation des performances

### Version 18.0.1.0.0 - 2025-10-01
- ✓ Version initiale du module
- ✓ Modèles, vues et contrôleurs complets
- ✓ Documentation complète