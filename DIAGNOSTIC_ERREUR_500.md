# Diagnostic Erreur HTTP 500 - Champ Inexistant

## Date
**3 octobre 2025**

## 🔍 Problème Signalé

**Erreur :** HTTP 500 "Service Unavailable"  
**Cause potentielle :** Référence à un champ `general_direction_id` inexistant

---

## ✅ Vérifications Effectuées

### 1. Recherche de `general_direction_id`

```bash
grep -r "general_direction_id" .
```

**Résultat :** ✅ **Aucune occurrence trouvée**

Le champ `general_direction_id` n'existe nulle part dans le module.

---

### 2. Vérification des Relations `direction_id`

Tous les modèles utilisent correctement `direction_id` :

#### Service (`models/service.py`)
```python
direction_id = fields.Many2one(
    comodel_name='sn.direction',
    string='Direction',
    required=True,
    ondelete='cascade',
    index=True,
)
```
✅ **Correct**

#### Agent (`models/agent.py`)
```python
direction_id = fields.Many2one(
    comodel_name='sn.direction',
    string='Direction',
    related='service_id.direction_id',
    store=True,
    index=True,
)
```
✅ **Correct**

---

### 3. Vérification des Champs `related`

Tous les champs `related` pointent vers des champs existants :

| Modèle | Champ | Related | Statut |
|--------|-------|---------|--------|
| `sn.service` | `ministry_id` | `direction_id.ministry_id` | ✅ OK |
| `sn.service` | `parent_department_id` | `direction_id.department_id` | ✅ OK |
| `sn.agent` | `direction_id` | `service_id.direction_id` | ✅ OK |
| `sn.agent` | `ministry_id` | `service_id.ministry_id` | ✅ OK |
| `sn.agent` | `department_id` | `service_id.department_id` | ✅ OK |
| `sn.direction` | `parent_department_id` | `ministry_id.department_id` | ✅ OK |

---

### 4. Vérification des Vues XML

Aucune vue ne référence `general_direction_id`.

---

## 🎯 Causes Potentielles de l'Erreur 500

Si l'erreur persiste, voici les causes possibles :

### 1. Données Corrompues en Base
```sql
-- Vérifier s'il y a des enregistrements avec des relations nulles
SELECT id, name, direction_id FROM sn_service WHERE direction_id IS NULL;
SELECT id, name, service_id FROM sn_agent WHERE service_id IS NULL;
```

### 2. Migration Incomplète
```bash
# Mettre à jour le module
odoo-bin -u sn_admin -d votre_base
```

### 3. Cache Odoo
```bash
# Redémarrer Odoo pour vider le cache
sudo systemctl restart odoo
```

### 4. Erreur dans un Champ Calculé
Vérifier les logs Odoo :
```bash
tail -f /var/log/odoo/odoo-server.log
```

---

## 🔧 Solutions Recommandées

### Solution 1 : Mise à Jour du Module
```bash
# En ligne de commande
odoo-bin -u sn_admin -d votre_base --stop-after-init

# Ou via l'interface
# Apps → SN Admin → Mettre à jour
```

### Solution 2 : Vérifier les Logs
```bash
# Logs en temps réel
tail -f /var/log/odoo/odoo-server.log | grep -i error

# Rechercher des erreurs spécifiques
grep "general_direction_id" /var/log/odoo/odoo-server.log
grep "KeyError" /var/log/odoo/odoo-server.log
grep "AttributeError" /var/log/odoo/odoo-server.log
```

### Solution 3 : Mode Debug
Activer le mode debug dans Odoo pour voir l'erreur complète :
```
URL: http://votre-serveur/web?debug=1
```

### Solution 4 : Vérifier la Base de Données
```sql
-- Vérifier la structure des tables
\d sn_service
\d sn_direction
\d sn_agent

-- Vérifier s'il y a des colonnes orphelines
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'sn_service' 
  AND column_name LIKE '%direction%';
```

---

## 📋 Checklist de Diagnostic

- [x] Recherche de `general_direction_id` → Aucune occurrence
- [x] Vérification des champs `direction_id` → Tous corrects
- [x] Vérification des champs `related` → Tous valides
- [x] Vérification des vues XML → Aucune référence problématique
- [ ] Vérifier les logs Odoo
- [ ] Mettre à jour le module
- [ ] Redémarrer Odoo
- [ ] Vérifier la base de données

---

## 🚨 Si l'Erreur Persiste

### Étape 1 : Capturer l'Erreur Exacte
```bash
# Activer le mode debug
# URL: http://votre-serveur/web?debug=1

# Reproduire l'erreur et copier le traceback complet
```

### Étape 2 : Analyser le Traceback
Rechercher dans le traceback :
- Le nom exact du champ problématique
- Le modèle concerné
- La ligne de code qui cause l'erreur

### Étape 3 : Corriger le Problème
Une fois le champ identifié :
1. Vérifier s'il existe dans le modèle Python
2. Vérifier s'il est utilisé dans une vue XML
3. Corriger ou supprimer la référence

---

## 📄 Informations Complémentaires

### Champs Disponibles dans `sn.direction`
```python
# Champs principaux
- id
- name
- code
- type
- ministry_id
- category_id
- manager_id
- service_ids
- department_id
- parent_department_id
- state
- active
```

### Champs Disponibles dans `sn.service`
```python
# Champs principaux
- id
- name
- code
- type
- direction_id  # ✅ Correct
- ministry_id   # Related
- manager_id
- agent_ids
- department_id
- parent_department_id
- state
- active
```

---

## ✅ Conclusion

**Aucun problème détecté dans le code du module.**

Le champ `general_direction_id` n'existe pas dans le module `sn_admin`.

Si l'erreur HTTP 500 persiste :
1. Vérifier les **logs Odoo** pour identifier l'erreur exacte
2. **Mettre à jour** le module
3. **Redémarrer** Odoo
4. Vérifier la **base de données** pour des données corrompues

---

**Pour obtenir de l'aide :**
Fournir le **traceback complet** de l'erreur depuis les logs Odoo.
