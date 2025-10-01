# Génération des fichiers de données XML

## Prérequis
- Les scripts de Phase 1 doivent avoir été exécutés
- Les fichiers CSV normalisés doivent être disponibles dans `data/normalized/`

## Processus de génération

### Option 1 : Script Python (recommandé)
Créer un script `scripts/generate_xml_data.py` qui :
1. Lit les fichiers CSV normalisés
2. Génère les fichiers XML Odoo avec external_id
3. Respecte l'ordre hiérarchique (ministères → directions → services → agents)

### Option 2 : Import CSV via Odoo
1. Installer le module `sn_admin` (sans données)
2. Aller dans Settings > Technical > Import
3. Importer les CSV dans l'ordre : ministères, directions, services, agents
4. Exporter les données en XML via Settings > Technical > Export

### Option 3 : Création manuelle
Pour un petit jeu de données de démonstration, créer manuellement les fichiers XML.

## Fichiers à générer

1. **sn_ministry_data.xml** : ~23 ministères
   - Format : `<record id="ministry_xxx" model="sn.ministry">`
   - Champs : name, code, type, address, phone, email, website, description, state='active'

2. **sn_direction_data.xml** : ~100 directions
   - Format : `<record id="direction_xxx" model="sn.direction">`
   - Champs : name, code, type, ministry_id (ref), phone, email, address, state='active'

3. **sn_service_data.xml** : ~300 services
   - Format : `<record id="service_xxx" model="sn.service">`
   - Champs : name, code, type, direction_id (ref), phone, email, state='active'

4. **sn_agent_data.xml** : ~1000 agents
   - Format : `<record id="agent_xxx" model="sn.agent">`
   - Champs : name, first_name, last_name, function, service_id (ref), work_phone, mobile_phone, work_email, matricule, state='active'

## Convention de nommage des external_id
- Ministères : `ministry_<code_lower>` (ex: ministry_msas)
- Directions : `direction_<code_lower>` (ex: direction_dgs)
- Services : `service_<code_lower>` (ex: service_srh)
- Agents : `agent_<matricule>` (ex: agent_sn_2024_001234)

## Validation
Après génération, valider les fichiers XML :
```bash
xmllint --noout data/sn_ministry_data.xml
xmllint --noout data/sn_direction_data.xml
xmllint --noout data/sn_service_data.xml
xmllint --noout data/sn_agent_data.xml
```

## Import dans Odoo
Les fichiers seront automatiquement importés lors de l'installation du module (déclarés dans `__manifest__.py`).
