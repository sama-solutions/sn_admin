from odoo import models, fields, api
import qrcode
import io
import base64


class Ministry(models.Model):
    _name = 'sn.ministry'
    _description = 'Ministère ou Institution Sénégalaise'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Champs de base
    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True,
        index=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
        size=10,
        tracking=True,
        index=True,
    )
    type = fields.Selection(
        selection=[
            ('presidency', 'Présidence'),
            ('primature', 'Primature'),
            ('ministry', 'Ministère'),
        ],
        string='Type',
        default='ministry',
        required=True,
    )
    description = fields.Text(string='Description')
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

    # Champs de contact
    address = fields.Text(string='Adresse')
    phone = fields.Char(string='Téléphone')
    phone_2 = fields.Char(string='Téléphone Secondaire')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Email')
    website = fields.Char(string='Site Web')
    
    # Adresse détaillée
    address_street = fields.Char(string='Rue')
    address_city = fields.Char(string='Ville')
    address_zip = fields.Char(string='Code Postal')
    address_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Pays',
        default=lambda self: self.env.ref('base.sn', raise_if_not_found=False),
    )
    gps_latitude = fields.Float(string='Latitude GPS', digits=(10, 7))
    gps_longitude = fields.Float(string='Longitude GPS', digits=(10, 7))

    # Relations
    direction_ids = fields.One2many(
        comodel_name='sn.direction',
        inverse_name='ministry_id',
        string='Directions',
    )
    category_ids = fields.One2many(
        comodel_name='sn.category',
        inverse_name='ministry_id',
        string='Catégories',
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Département RH',
        help='Département RH correspondant pour faciliter la gestion du personnel',
    )

    # Champs QR Code
    qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code',
        store=True,
    )
    qr_code_url = fields.Char(
        string='URL QR Code',
        compute='_compute_qr_code_url',
        store=True,
    )
    
    # Champs de visibilité publique
    public_visible = fields.Boolean(string='Visible Publiquement', default=True)
    public_show_phone = fields.Boolean(string='Afficher Téléphone', default=True)
    public_show_email = fields.Boolean(string='Afficher Email', default=True)
    public_show_address = fields.Boolean(string='Afficher Adresse', default=True)
    
    # Champs calculés
    category_count = fields.Integer(
        string='Nombre de Catégories',
        compute='_compute_category_count',
        store=True,
    )
    direction_count = fields.Integer(
        string='Nombre de Directions',
        compute='_compute_direction_count',
        store=True,
    )
    service_count = fields.Integer(
        string='Nombre de Services',
        compute='_compute_service_count',
        store=True,
    )
    agent_count = fields.Integer(
        string='Nombre d\'Agents',
        compute='_compute_agent_count',
        store=True,
    )
    employee_count = fields.Integer(
        string='Nombre d\'Employés RH',
        compute='_compute_employee_count',
        store=True,
    )

    # Contraintes SQL
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code doit être unique'),
        ('name_unique', 'UNIQUE(LOWER(name))', 'Le nom doit être unique'),
    ]

    @api.depends('category_ids')
    def _compute_category_count(self):
        for record in self:
            record.category_count = len(record.category_ids)
    
    @api.depends('direction_ids')
    def _compute_direction_count(self):
        for record in self:
            record.direction_count = len(record.direction_ids)

    @api.depends('direction_ids.service_ids')
    def _compute_service_count(self):
        for record in self:
            record.service_count = sum(record.direction_ids.mapped('service_count'))

    @api.depends('direction_ids.service_ids.agent_ids')
    def _compute_agent_count(self):
        for record in self:
            record.agent_count = sum(record.direction_ids.mapped('agent_count'))
    
    @api.depends('department_id.total_employee')
    def _compute_employee_count(self):
        for record in self:
            if record.department_id:
                record.employee_count = record.department_id.total_employee
            else:
                record.employee_count = 0
    
    @api.depends('name')
    def _compute_qr_code_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id:
                record.qr_code_url = f"{base_url}/organigramme/ministere/{record.id}"
            else:
                record.qr_code_url = False
    
    @api.depends('qr_code_url')
    def _compute_qr_code(self):
        for record in self:
            if record.qr_code_url:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(record.qr_code_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                record.qr_code = base64.b64encode(buffer.getvalue())
            else:
                record.qr_code = False

    def action_view_directions(self):
        self.ensure_one()
        return {
            'name': f'Directions - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.direction',
            'view_mode': 'list,form,kanban',
            'domain': [('ministry_id', '=', self.id)],
            'context': {'default_ministry_id': self.id},
        }

    def action_view_services(self):
        self.ensure_one()
        return {
            'name': f'Services - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.service',
            'view_mode': 'list,form,kanban',
            'domain': [('ministry_id', '=', self.id)],
            'context': {'default_ministry_id': self.id},
        }

    def action_view_agents(self):
        self.ensure_one()
        return {
            'name': f'Agents - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.agent',
            'view_mode': 'list,form,kanban',
            'domain': [('ministry_id', '=', self.id)],
            'context': {'default_ministry_id': self.id},
        }
    
    def action_view_categories(self):
        """Voir les catégories du ministère"""
        self.ensure_one()
        return {
            'name': f'Catégories - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.category',
            'view_mode': 'list,form,kanban',
            'domain': [('ministry_id', '=', self.id)],
            'context': {'default_ministry_id': self.id},
        }

    def action_create_hr_department(self):
        self.ensure_one()
        if self.department_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Un département RH existe déjà pour ce ministère',
                    'type': 'warning',
                }
            }
        
        department = self.env['hr.department'].create({
            'name': self.name,
            'sn_ministry_id': self.id,
            'sn_structure_type': 'ministry',
        })
        self.department_id = department.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Département RH créé: {department.name}',
                'type': 'success',
            }
        }
    
    def action_sync_to_hr_department(self):
        self.ensure_one()
        if not self.department_id:
            return self.action_create_hr_department()
        
        self.department_id.write({
            'name': self.name,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Synchronisation réussie vers le département RH',
                'type': 'success',
            }
        }
    
    def action_export_organigramme(self):
        self.ensure_one()
        return self.env.ref('sn_admin.action_report_organigramme').report_action(self)
    
    def get_orgchart_data(self, ministry_id=None):
        """
        Retourne les données hiérarchiques pour l'organigramme interactif
        Compatible avec OrgChart.js
        """
        def build_node(record, model_type):
            """Construire un nœud de l'organigramme"""
            node = {
                'id': record.id,
                'name': record.name,
                'code': record.code if hasattr(record, 'code') else '',
                'title': record.code if hasattr(record, 'code') else '',
                'type': model_type,
                'model': record._name,
                'children': []
            }
            
            # Ajouter les enfants selon le type
            if model_type == 'ministry':
                node['children_count'] = len(record.direction_ids)
                for direction in record.direction_ids.filtered(lambda d: d.active and d.state == 'active'):
                    node['children'].append(build_node(direction, 'direction'))
            elif model_type == 'direction':
                node['children_count'] = len(record.service_ids)
                for service in record.service_ids.filtered(lambda s: s.active and s.state == 'active'):
                    node['children'].append(build_node(service, 'service'))
            elif model_type == 'service':
                node['children_count'] = len(record.agent_ids)
                # Limiter les agents affichés pour la performance
                for agent in record.agent_ids.filtered(lambda a: a.active and a.state == 'active')[:10]:
                    node['children'].append(build_node(agent, 'agent'))
            
            return node
        
        # Construire l'arbre
        if ministry_id:
            ministry = self.browse(ministry_id)
            if ministry.exists():
                return build_node(ministry, 'ministry')
            else:
                return {}
        else:
            # Arbre complet (limité aux ministères)
            tree_data = {
                'id': 0,
                'name': 'Administration Sénégalaise',
                'title': 'SENEGAL',
                'type': 'root',
                'children': []
            }
            
            for ministry in self.search([('active', '=', True), ('state', '=', 'active')], order='type, name'):
                tree_data['children'].append(build_node(ministry, 'ministry'))
            
            return tree_data
    
    def name_get(self):
        result = []
        for record in self:
            name = f'{record.code} - {record.name}'
            result.append((record.id, name))
        return result
