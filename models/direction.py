from odoo import models, fields, api
from odoo.exceptions import ValidationError
import qrcode
import io
import base64


class Direction(models.Model):
    _name = 'sn.direction'
    _description = 'Direction Générale ou Régionale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ministry_id, name'

    # Champs de base
    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True,
        index=True,
    )
    code = fields.Char(
        string='Code',
        size=10,
        tracking=True,
        index=True,
    )
    type = fields.Selection(
        selection=[
            ('generale', 'Direction Générale'),
            ('regionale', 'Direction Régionale'),
            ('technique', 'Direction Technique'),
        ],
        string='Type',
        default='generale',
    )
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

    # Relations
    ministry_id = fields.Many2one(
        comodel_name='sn.ministry',
        string='Ministère',
        required=True,
        ondelete='cascade',
        index=True,
    )
    manager_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable',
        ondelete='restrict',
    )
    service_ids = fields.One2many(
        comodel_name='sn.service',
        inverse_name='direction_id',
        string='Services',
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Département RH',
    )
    parent_department_id = fields.Many2one(
        comodel_name='hr.department',
        related='ministry_id.department_id',
        store=True,
        string='Département RH Parent',
    )

    # Champs de contact
    phone = fields.Char(string='Téléphone')
    phone_2 = fields.Char(string='Téléphone Secondaire')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Email')
    address = fields.Text(string='Adresse')
    
    # Adresse détaillée
    address_street = fields.Char(string='Rue')
    address_city = fields.Char(string='Ville')
    address_zip = fields.Char(string='Code Postal')
    gps_latitude = fields.Float(string='Latitude GPS', digits=(10, 7))
    gps_longitude = fields.Float(string='Longitude GPS', digits=(10, 7))
    
    # Région (pour directions régionales)
    region_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Région',
        domain="[('country_id.code', '=', 'SN')]",
    )

    # Champs QR Code
    qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code',
        store=False,
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
        ('code_ministry_unique', 'UNIQUE(code, ministry_id)', 'Le code doit être unique par ministère'),
    ]

    @api.depends('service_ids')
    def _compute_service_count(self):
        for record in self:
            record.service_count = len(record.service_ids)

    @api.depends('service_ids.agent_ids')
    def _compute_agent_count(self):
        for record in self:
            record.agent_count = sum(record.service_ids.mapped('agent_count'))
    
    @api.depends('department_id.total_employee')
    def _compute_employee_count(self):
        for record in self:
            if record.department_id:
                record.employee_count = record.department_id.total_employee
            else:
                record.employee_count = 0
    
    @api.depends('id')
    def _compute_qr_code_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id:
                record.qr_code_url = f"{base_url}/organigramme/direction/{record.id}"
            else:
                record.qr_code_url = False
    
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

    @api.constrains('ministry_id')
    def _check_ministry_active(self):
        for record in self:
            if record.ministry_id and not record.ministry_id.active:
                raise ValidationError('Le ministère doit être actif.')

    def action_view_services(self):
        self.ensure_one()
        return {
            'name': 'Services',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.service',
            'view_mode': 'tree,form',
            'domain': [('direction_id', '=', self.id)],
            'context': {'default_direction_id': self.id},
        }

    def action_view_agents(self):
        self.ensure_one()
        return {
            'name': 'Agents',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.agent',
            'view_mode': 'tree,form',
            'domain': [('direction_id', '=', self.id)],
            'context': {'default_direction_id': self.id},
        }

    def action_create_hr_department(self):
        self.ensure_one()
        if self.department_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Un département RH existe déjà pour cette direction',
                    'type': 'warning',
                }
            }
        
        department = self.env['hr.department'].create({
            'name': self.name,
            'parent_id': self.parent_department_id.id if self.parent_department_id else False,
            'sn_direction_id': self.id,
            'sn_structure_type': 'direction',
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
            'parent_id': self.parent_department_id.id if self.parent_department_id else False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Synchronisation réussie vers le département RH',
                'type': 'success',
            }
        }
    
    def name_get(self):
        result = []
        for record in self:
            ministry_code = record.ministry_id.code if record.ministry_id else ''
            code = record.code if record.code else ''
            name = f'{ministry_code}/{code} - {record.name}' if code else f'{ministry_code} - {record.name}'
            result.append((record.id, name))
        return result
