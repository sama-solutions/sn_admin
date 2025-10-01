# Guide d'implémentation complet - Registre Officiel de l'Administration Sénégalaise

## Vue d'ensemble

Ce guide détaille les étapes pour transformer le module `sn_admin` en **registre officiel complet** de l'administration sénégalaise avec :
- Données complètes (ministères, directions, services)
- Intégration RH Odoo
- Vues organigramme interactives
- QR codes partageables
- Portail public enrichi

## Conformité Odoo 18 CE

✅ **Ce module est 100% conforme aux directives strictes Odoo 18 Community Edition**

**Points de conformité** :
- Vues modernes : `<list>` avec `multi_edit="1"` sur toutes les vues principales
- Dépendances sûres : `base`, `hr`, `mail`, `website` uniquement (tous en CE)
- Pas de dépendances à `account` ou modules Enterprise
- Python 3.11+ et PostgreSQL 13+ compatibles
- Framework standard Odoo avec exception justifiée (OrgChart.js)

**Validation** : Consulter `ODOO18_COMPLIANCE.md` pour les détails techniques complets.

---

## Phase 1 : Extraction des données complètes

### Étape 1.1 : Exécuter les scripts d'extraction

```bash
cd /home/grand-as/psagsn/custom_addons/sn_admin

# Installer les dépendances Python
pip install -r requirements.txt

# Extraire toutes les feuilles du fichier Excel
python scripts/extract_xlsx.py --all --format csv --output-dir data/extracted/

# Vérifier les fichiers extraits
ls -lh data/extracted/
```

**Résultat attendu** : Fichiers CSV dans `data/extracted/` avec toutes les données du fichier Excel.

### Étape 1.2 : Normaliser les données

```bash
# Normaliser et valider les données
python scripts/normalize_data.py --input data/extracted/ --output data/normalized/ --report --fix-errors

# Consulter le rapport de qualité
cat data/normalized/quality_report.txt
```

**Résultat attendu** : Fichiers CSV normalisés dans `data/normalized/` avec rapport de qualité.

### Étape 1.3 : Générer les fichiers XML Odoo

```bash
# Générer les fichiers XML depuis les CSV normalisés
python scripts/generate_xml_from_csv.py --input data/normalized/ --output data/ --all --validate

# Vérifier les fichiers XML générés
ls -lh data/*.xml
```

**Résultat attendu** : Fichiers XML Odoo dans `data/` :
- `sn_ministry_data.xml` (23+ ministères)
- `sn_direction_data.xml` (100+ directions)
- `sn_service_data.xml` (300+ services)
- `sn_agent_data.xml` (vide initialement)

## Phase 2 : Installation et configuration du module

### Étape 2.1 : Installer le module dans Odoo

```bash
# Redémarrer Odoo
sudo systemctl restart odoo

# Installer le module
odoo-bin -c /etc/odoo/odoo.conf -d <database> -i sn_admin

# Vérifier l'installation
odoo-bin -c /etc/odoo/odoo.conf -d <database> --test-enable --test-tags sn_admin
```

**Résultat attendu** : Module installé avec toutes les données importées.

### Étape 2.2 : Vérifier les données importées

1. Se connecter à Odoo
2. Aller dans **SN Admin > Organigramme > Ministères**
3. Vérifier que tous les ministères sont présents (23+)
4. Ouvrir un ministère et vérifier les directions
5. Ouvrir une direction et vérifier les services

**Résultat attendu** : Toute la structure organique est visible et navigable.

### Étape 2.3 : Configurer les paramètres de visibilité publique

1. Aller dans **SN Admin > Configuration > Paramètres**
2. Activer :
   - ✓ Portail public activé
   - ✓ Afficher téléphones publiquement
   - ✓ Afficher emails publiquement
   - ✓ Afficher adresses publiquement
3. Enregistrer

## Phase 3 : Intégration RH

### Étape 3.1 : Créer les départements RH depuis les services

1. Aller dans **SN Admin > Organigramme > Services**
2. Pour chaque service (ou en masse) :
   - Ouvrir la fiche service
   - Onglet "Intégration RH"
   - Cliquer sur "Créer Département RH"
3. Vérifier dans **Employés > Configuration > Départements** que les départements sont créés

**Résultat attendu** : Chaque service a un département RH correspondant avec la hiérarchie correcte.

### Étape 3.2 : Former les utilisateurs à la saisie des agents

**Option A : Saisie via SN Admin**
1. Aller dans **SN Admin > Organigramme > Agents**
2. Cliquer sur "Créer"
3. Remplir les champs : Nom, Prénom, Fonction, Service
4. Cliquer sur "Créer Employé RH" pour créer automatiquement un hr.employee

**Option B : Saisie via module RH**
1. Aller dans **Employés > Employés**
2. Cliquer sur "Créer"
3. Remplir les champs standards RH
4. Sélectionner le département (lié à un service)
5. Un sn.agent sera créé automatiquement

**Recommandation** : Utiliser l'Option B (module RH) car elle offre plus de fonctionnalités (congés, évaluations, recrutement, etc.).

## Phase 4 : Vues Organigramme

### Étape 4.1 : Télécharger la bibliothèque OrgChart.js

```bash
cd /home/grand-as/psagsn/custom_addons/sn_admin/static/src/js/

# Télécharger OrgChart.js
wget https://cdn.jsdelivr.net/npm/orgchart@3.8.0/dist/js/jquery.orgchart.min.js

# Télécharger le CSS
cd ../css/
wget https://cdn.jsdelivr.net/npm/orgchart@3.8.0/dist/css/jquery.orgchart.min.css
```

### Étape 4.2 : Tester les vues organigramme

1. Aller dans **SN Admin > Organigramme > Organigramme Complet**
2. Vérifier que l'organigramme interactif s'affiche
3. Tester les fonctionnalités :
   - Expand/collapse des nœuds
   - Zoom et pan
   - Clic sur un nœud → ouvrir la fiche
   - Export PNG/PDF

**Résultat attendu** : Organigramme interactif fonctionnel avec toute la hiérarchie.

## Phase 5 : QR Codes

### Étape 5.1 : Générer les QR codes

Les QR codes sont générés automatiquement lors de l'accès à une fiche (ministère, direction, service, agent).

1. Ouvrir une fiche ministère
2. Aller dans l'onglet "QR Code"
3. Vérifier que le QR code est affiché
4. Tester le bouton "Télécharger QR Code"
5. Scanner le QR code avec un smartphone → doit ouvrir la page publique

**Résultat attendu** : QR codes fonctionnels pour toutes les structures.

## Phase 6 : Portail Public

### Étape 6.1 : Activer le portail public

1. Aller dans **Paramètres > Site Web > Configuration**
2. Vérifier que le site web est activé
3. Accéder à l'URL : `http://<votre-domaine>/organigramme`

**Résultat attendu** : Page d'accueil du portail public affichée.

### Étape 6.2 : Tester le portail public

1. **Page d'accueil** :
   - Vérifier les statistiques (nombre de ministères, directions, services)
   - Tester la barre de recherche
   - Cliquer sur "Voir l'organigramme complet"

2. **Liste des ministères** :
   - Vérifier que tous les ministères sont affichés
   - Tester les filtres par type
   - Cliquer sur un ministère

3. **Détails d'un ministère** :
   - Vérifier les informations complètes (nom, code, adresse, téléphone, email, site web)
   - Vérifier le QR code
   - Tester le bouton "Télécharger QR Code"
   - Tester les boutons de partage (Facebook, Twitter, WhatsApp)
   - Vérifier la liste des directions
   - Tester la carte GPS (si coordonnées disponibles)

4. **Organigramme interactif public** :
   - Accéder à `/organigramme/tree`
   - Vérifier que l'organigramme complet s'affiche
   - Tester les fonctionnalités (expand/collapse, zoom, clic)

**Résultat attendu** : Portail public complet, professionnel et fonctionnel.

## Phase 7 : Formation et déploiement

### Étape 7.1 : Former les administrateurs

**Formation 1 : Gestion de la structure organique**
- Créer/modifier des ministères, directions, services
- Gérer la visibilité publique
- Générer et télécharger les QR codes
- Exporter l'organigramme en PDF

**Formation 2 : Saisie des agents**
- Créer des agents via SN Admin ou module RH
- Lier les agents aux employés RH
- Gérer les nominations (date, décret)
- Gérer la visibilité publique des agents

**Formation 3 : Utilisation du portail public**
- Naviguer dans l'organigramme public
- Rechercher un interlocuteur
- Partager des QR codes
- Consulter les contacts

### Étape 7.2 : Déployer en production

1. **Backup de la base de données** :
   ```bash
   pg_dump -U odoo -d <database> > backup_before_sn_admin.sql
   ```

2. **Déployer le module** :
   ```bash
   # Copier le module sur le serveur de production
   scp -r sn_admin/ user@production:/opt/odoo/custom_addons/
   
   # Redémarrer Odoo
   ssh user@production "sudo systemctl restart odoo"
   
   # Installer le module
   ssh user@production "odoo-bin -c /etc/odoo/odoo.conf -d production_db -i sn_admin"
   ```

3. **Vérifier le déploiement** :
   - Accéder à l'URL de production
   - Vérifier que toutes les données sont présentes
   - Tester le portail public
   - Vérifier les performances

4. **Configurer le domaine** :
   - Configurer le DNS pour pointer vers le serveur Odoo
   - Configurer le SSL (Let's Encrypt)
   - Exemple : `https://organigramme.gouv.sn`

### Étape 7.3 : Communication et lancement

1. **Communiqué de presse** :
   - Annoncer le lancement du registre officiel
   - Expliquer les bénéfices pour les citoyens
   - Donner l'URL du portail public

2. **Formation des ministères** :
   - Organiser des sessions de formation pour chaque ministère
   - Distribuer des guides d'utilisation
   - Créer des comptes utilisateurs pour les gestionnaires RH

3. **Suivi et support** :
   - Mettre en place un support technique
   - Suivre les statistiques d'utilisation
   - Collecter les retours des utilisateurs

## Maintenance et évolution

### Maintenance corrective
- Corriger les bugs signalés
- Mettre à jour les données (nouveaux ministères, changements de structure)
- Mettre à jour les coordonnées

### Maintenance évolutive
- Ajouter de nouvelles fonctionnalités (ex: notifications de nomination)
- Améliorer les performances
- Ajouter des statistiques avancées
- Intégrer avec d'autres systèmes gouvernementaux

## Conclusion

Ce guide permet de transformer le module `sn_admin` en un **registre officiel complet** de l'administration sénégalaise. C'est une **révolution** dans la transparence administrative qui permettra aux citoyens de trouver facilement leurs interlocuteurs et au gouvernement de gérer efficacement son personnel.

**Prochaines étapes** :
1. Exécuter les scripts d'extraction (Phase 1)
2. Installer le module (Phase 2)
3. Configurer l'intégration RH (Phase 3)
4. Tester les vues organigramme (Phase 4)
5. Vérifier les QR codes (Phase 5)
6. Tester le portail public (Phase 6)
7. Former et déployer (Phase 7)

**Contact** : Pour toute question, contacter l'équipe de développement PSA-GSN.
