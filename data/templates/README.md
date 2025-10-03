# Modèles CSV d'import SN Admin

Chemin: `sn_admin/data/templates/`

## Fichiers fournis
- `ministry_template.csv`
- `direction_template.csv`
- `service_template.csv`
- `agent_template.csv`

## Ordre d'import recommandé (Odoo)
1. `sn.ministry` → `ministry_template.csv`
2. `sn.direction` → `direction_template.csv`
3. `sn.service` → `service_template.csv`
4. `sn.agent` → `agent_template.csv`

Importer dans cet ordre garantit que les relations Many2one existent déjà.

## Colonnes clés et références
- `external_id`: ID externe stable pour faciliter les mises à jour (ex: `ministry_msas`).
- Références Many2one (Odoo Import UI accepte deux approches):
  - Par code/nom (ex: `ministry_code`, `direction_code`, `service_code`) que vous mappez vers un champ de recherche lors de l'import.
  - Par External ID: utilisez la colonne `ministry_id/id`, `direction_id/id`, `service_id/id` avec la valeur `external_id` de la ligne parente (ex: `ministry_msas`).

Astuce: conserver les deux colonnes (code ET `..._id/id`) facilite le mapping selon le besoin.

## Mapping modèle ↔ fichier
- `ministry_template.csv` → modèle `sn.ministry` (champs: `name`, `code`, `type`, `address`, `phone`, `email`, `website`, `description`).
- `direction_template.csv` → modèle `sn.direction` (champs: `name`, `code`, `type`, `ministry_id`, `region_id`, `manager_id`, `phone`, `email`, `address`, `description`).
- `service_template.csv` → modèle `sn.service` (champs: `name`, `code`, `type`, `direction_id`, `manager_id`, `phone`, `email`, `address`, `description`).
- `agent_template.csv` → modèle `sn.agent` (champs: `name`, `first_name`, `last_name`, `function`, `service_id`, `matricule`, `work_phone`, `mobile_phone`, `work_email`, `nomination_date`, `nomination_decree`, `is_interim`).

Pour les détails de transformation/validation, voir `sn_admin/doc/FIELD_MAPPING.md` et `sn_admin/doc/IMPORT_GUIDE.md`.

## Conseils Import UI (Odoo)
- Encodage CSV: UTF-8. Séparateur: virgule. Guillemet: `"`.
- Démo: importer d'abord 5 lignes pour valider le mapping.
- Cocher « Montrer les champs avancés » pour exposer `xxx_id/id`.
- Pour `type` (sélections), utiliser les valeurs techniques: `ministry`, `presidency`, `primature`, `generale`, `regionale`, `technique`, `service`, `bureau`, `cellule`, `division`.
- Dates: format `YYYY-MM-DD`.

## À propos des sources PDF/DOCX/XLSX
- Préférer l'XLSX (`snadmin.xlsx`) pour générer ces CSV.
- Si besoin d'extraire depuis PDF/DOCX, utiliser un outil externe (ex: tabula-py pour PDF tabulaires, python-docx/textract pour DOCX), puis normaliser selon `FIELD_MAPPING.md`.

## Prochaines étapes
- Remplir les templates à partir de `snadmin.xlsx`.
- Importer dans Odoo selon l'ordre ci-dessus.
- Optionnel: ajouter un script d'extraction/normalisation si récurrent.
