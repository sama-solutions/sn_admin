from odoo import models, fields, api
from odoo.exceptions import ValidationError
import qrcode
import io
import base64


class Service(models.Model):
    _name = 'sn.service'
    _description = 'Service, Bureau ou Cellule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'direction_id, name'

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
            ('service', 'Service'),
            ('bureau', 'Bureau'),
            ('cellule', 'Cellule'),
            ('division', 'Division'),
        ],
        string='Type',
        default='service',
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
    direction_id = fields.Many2one(
        comodel_name='sn.direction',
        string='Direction',
        required=True,
        ondelete='cascade',
        index=True,
    )
    ministry_id = fields.Many2one(
        comodel_name='sn.ministry',
        string='Ministère',
        related='direction_id.ministry_id',
        store=True,
        index=True,
    )
    manager_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable',
        ondelete='restrict',
    )
    agent_ids = fields.One2many(
        comodel_name='sn.agent',
        inverse_name='service_id',
        string='Agents',
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Département RH',
    )
    parent_department_id = fields.Many2one(
        comodel_name='hr.department',
        related='direction_id.department_id',
        store=True,
        string='Département RH Parent',
    )

    # Champs de contact
    phone = fields.Char(string='Téléphone')
    phone_2 = fields.Char(string='Téléphone Secondaire')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Email')
    
    # Adresse détaillée
    address_street = fields.Char(string='Rue')
    address_city = fields.Char(string='Ville')
    address_zip = fields.Char(string='Code Postal')
    gps_latitude = fields.Float(string='Latitude GPS', digits=(10, 7))
    gps_longitude = fields.Float(string='Longitude GPS', digits=(10, 7))

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
        ('code_direction_unique', 'UNIQUE(code, direction_id)', 'Le code doit être unique par direction'),
    ]

    @api.depends('agent_ids')
    def _compute_agent_count(self):
        for record in self:
            record.agent_count = len(record.agent_ids)
    
    @api.depends('department_id.total_employee')
    def _compute_employee_count(self):
        for record in self:
            if record.department_id:
                record.employee_count = record.department_id.total_employee
            else:
                record.employee_count = 0
    
    def _compute_qr_code_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id:
                record.qr_code_url = f"{base_url}/organigramme/service/{record.id}"
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

    @api.constrains('direction_id')
    def _check_direction_active(self):
        for record in self:
            if record.direction_id and not record.direction_id.active:
                raise ValidationError('La direction doit être active.')

    def action_view_agents(self):
        self.ensure_one()
        return {
            'name': f'Agents - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.agent',
            'view_mode': 'list,form,kanban',
            'domain': [('service_id', '=', self.id)],
            'context': {
                'default_service_id': self.id,
                'default_direction_id': self.direction_id.id,
                'default_ministry_id': self.ministry_id.id,
            },
        }

    def action_create_hr_department(self):
        self.ensure_one()
        if self.department_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Un département RH existe déjà pour ce service',
                    'type': 'warning',
                }
            }
        
        department = self.env['hr.department'].create({
            'name': self.name,
            'parent_id': self.parent_department_id.id if self.parent_department_id else False,
            'sn_service_id': self.id,
            'sn_structure_type': 'service',
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
    
    def action_create_agents(self):
        self.ensure_one()
        return {
            'name': 'Créer des agents',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.agent',
            'view_mode': 'form',
            'context': {'default_service_id': self.id},
            'target': 'new',
        }
    
    def name_get(self):
        result = []
        for record in self:
            direction_code = record.direction_id.code if record.direction_id and record.direction_id.code else ''
            code = record.code if record.code else ''
            name = f'{direction_code}/{code} - {record.name}' if code else f'{direction_code} - {record.name}'
            result.append((record.id, name))
        return result
