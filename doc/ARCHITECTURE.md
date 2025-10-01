# Architecture du module SN Admin

## Philosophie : Module Standalone

Le module `sn_admin` est conçu comme un **module autonome** (standalone) pour l'administration sénégalaise. Il ne dépend d'aucun module tiers et peut être installé indépendamment.

## Dépendances Odoo

### Dépendances obligatoires
- `base` : Framework de base Odoo (pré-installé)
- `hr` : Gestion des employés (pour lier les agents aux employés RH)
- `website` : Framework web (pour le portail public - Phase 4)

### Aucune dépendance tierce
Le module ne dépend d'aucun module externe ou communautaire.

## Relation avec sama_etat

### sama_etat comme inspiration UI
Le module `sama_etat` (s'il est installé) peut servir de **référence d'inspiration** pour :
- Design du tableau de bord
- Mise en page des vues
- Ergonomie de l'interface
- Patterns d'interaction

### Pas de dépendance technique
`sn_admin` **ne dépend PAS** de `sama_etat` :
- ✗ Pas d'héritage de modèles
- ✗ Pas d'import de vues
- ✗ Pas de référence dans `__manifest__.py`
- ✓ Peut être installé sans `sama_etat`
- ✓ Fonctionne de manière totalement indépendante

## Architecture des modèles

### Hiérarchie autonome

```
models.Model (Odoo base class)
  |
  ├─ sn.ministry (Ministères)
  │   └─ Champs : name, code, type, address, phone, email, website, description
  │
  ├─ sn.direction (Directions)
  │   └─ Relation : ministry_id → sn.ministry
  │
  ├─ sn.service (Services)
  │   └─ Relation : direction_id → sn.direction
  │
  └─ sn.agent (Agents)
      └─ Relations : service_id → sn.service
                     employee_id → hr.employee (optionnel)
```

### Tous les champs définis localement

Chaque modèle définit **tous ses champs** directement :
- Pas d'héritage de modèles externes
- Pas de délégation (`_inherits`)
- Contrôle total sur la structure de données

## Modèle sn.ministry

### Définition complète

```python
class Ministry(models.Model):
    _name = 'sn.ministry'
    _description = 'Ministère ou Institution'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Odoo mixins standards
    
    # Champs de base
    name = fields.Char('Nom', required=True, index=True)
    code = fields.Char('Code', required=True, size=10, index=True)
    type = fields.Selection([
        ('presidency', 'Présidence'),
        ('primature', 'Primature'),
        ('ministry', 'Ministère')
    ], default='ministry', required=True)
    
    # Coordonnées
    address = fields.Text('Adresse')
    phone = fields.Char('Téléphone')
    email = fields.Char('Email')
    website = fields.Char('Site Web')
    
    # Informations
    description = fields.Text('Description')
    active = fields.Boolean('Actif', default=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('archived', 'Archivé')
    ], default='draft')
    
    # Relations
    direction_ids = fields.One2many('sn.direction', 'ministry_id', 'Directions')
    direction_count = fields.Integer('Nombre de directions', compute='_compute_direction_count')
    
    # Contraintes
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code doit être unique'),
        ('name_unique', 'UNIQUE(LOWER(name))', 'Le nom doit être unique')
    ]
```

### Pas d'héritage externe
- Hérite uniquement de `models.Model` (classe de base Odoo)
- Utilise des mixins Odoo standards (`mail.thread`, `mail.activity.mixin`)
- Tous les champs métier sont définis dans le modèle

## Avantages de l'architecture standalone

### Indépendance
- ✓ Installation simple (pas de dépendances complexes)
- ✓ Maintenance facilitée (pas de couplage externe)
- ✓ Évolution autonome (pas de contraintes d'API externe)

### Flexibilité
- ✓ Personnalisation complète des champs
- ✓ Adaptation aux besoins spécifiques sénégalais
- ✓ Pas de contraintes héritées d'autres modules

### Performance
- ✓ Pas de surcharge d'héritage
- ✓ Requêtes SQL optimisées
- ✓ Contrôle total sur les index

### Portabilité
- ✓ Déploiement sur n'importe quelle instance Odoo 18 CE
- ✓ Export/import facilité
- ✓ Pas de dépendances à gérer

## Intégration avec le module HR

### Lien optionnel avec hr.employee

Le modèle `sn.agent` peut être lié à `hr.employee` :

```python
class Agent(models.Model):
    _name = 'sn.agent'
    
    # Champs propres
    name = fields.Char('Nom complet', required=True)
    function = fields.Char('Fonction', required=True)
    service_id = fields.Many2one('sn.service', 'Service', required=True)
    
    # Lien optionnel vers HR
    employee_id = fields.Many2one('hr.employee', 'Employé RH')
    
    # Si lié à HR, synchroniser certains champs
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.name = self.employee_id.name
            self.work_phone = self.employee_id.work_phone
            self.work_email = self.employee_id.work_email
```

### Pas d'héritage de hr.employee
- `sn.agent` est un modèle indépendant
- Le lien vers `hr.employee` est optionnel
- Permet de gérer des agents non présents dans le module RH

## Phases de développement

**Planification détaillée** : Consulter le document **[PHASES_ROADMAP.md](../PHASES_ROADMAP.md)** pour la planification complète des phases 2, 3 et 4 avec tous les livrables, critères de succès et timeline.

### Phase 1 : Extraction et normalisation ✓
- Scripts Python autonomes
- Pas de dépendance Odoo
- Données normalisées prêtes pour import

### Phase 2 : Modélisation Odoo (à venir)
- Modèles autonomes (`sn.ministry`, `sn.direction`, `sn.service`, `sn.agent`)
- Dépendances : `base`, `hr` uniquement
- Pas de référence à `sama_etat` dans le code

### Phase 3 : Vues et interface (à venir)
- Vues personnalisées
- Inspiration UI de `sama_etat` (si disponible)
- Mais code totalement indépendant

### Phase 4 : Portail public (à venir)
- Contrôleurs web autonomes
- Templates QWeb personnalisés
- Dépendance : `website` uniquement

## Conclusion

Le module `sn_admin` est conçu pour être **totalement autonome** :
- ✓ Aucune dépendance tierce
- ✓ Tous les modèles définis localement
- ✓ Installation simple
- ✓ Maintenance facilitée
- ✓ Évolution indépendante

Le module `sama_etat` peut servir d'**inspiration visuelle** pour l'UI (Phase 3), mais n'est **jamais une dépendance technique**. Aucun code n'est copié ou hérité de `sama_etat`.

**Prochaines étapes** : Consulter `PHASES_ROADMAP.md` pour la planification détaillée des phases 2, 3 et 4.
