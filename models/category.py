from odoo import models, fields, api


class Category(models.Model):
    _name = 'sn.category'
    _description = 'Catégorie principale (Cabinet, Secrétariat général, Directions, Autres administrations)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ministry_id, name'

    name = fields.Char(string='Nom', required=True, tracking=True, index=True)
    code = fields.Char(string='Code', size=20, index=True)
    active = fields.Boolean(string='Actif', default=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'),
            ('active', 'Actif'),
            ('archived', 'Archivé'),
        ],
        string='État',
        default='draft',
    )

    ministry_id = fields.Many2one(
        comodel_name='sn.ministry',
        string='Autorité / Ministère',
        required=True,
        ondelete='cascade',
        index=True,
    )

    direction_ids = fields.One2many(
        comodel_name='sn.direction',
        inverse_name='category_id',
        string='Directions Générales',
    )
    
    direction_count = fields.Integer(
        string='Nombre de Directions',
        compute='_compute_direction_count',
        store=True,
    )
    
    service_count = fields.Integer(
        string='Nombre de Services',
        compute='_compute_service_count',
    )
    
    # Champs de visibilité publique
    public_visible = fields.Boolean(string='Visible Publiquement', default=True)
    
    @api.depends('direction_ids')
    def _compute_direction_count(self):
        for category in self:
            category.direction_count = len(category.direction_ids)
    
    def _compute_service_count(self):
        for category in self:
            category.service_count = sum(direction.service_count for direction in category.direction_ids)
    
    def action_view_directions(self):
        """Ouvrir la liste des directions de cette catégorie"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Directions - {self.name}',
            'res_model': 'sn.direction',
            'view_mode': 'list,form,kanban',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id, 'default_ministry_id': self.ministry_id.id},
        }
