import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import qrcode
import io
import base64


class Agent(models.Model):
    _name = 'sn.agent'
    _description = 'Agent de l\'Administration Publique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'service_id, name'

    # Champs identité
    name = fields.Char(
        string='Nom Complet',
        required=True,
        tracking=True,
        index=True,
    )
    first_name = fields.Char(string='Prénom')
    last_name = fields.Char(string='Nom de Famille')
    matricule = fields.Char(
        string='Matricule',
        index=True,
        help='Format: SN-YYYY-NNNNNN',
    )
    function = fields.Char(
        string='Fonction',
        required=True,
        tracking=True,
    )

    # Relations
    service_id = fields.Many2one(
        comodel_name='sn.service',
        string='Service',
        required=True,
        ondelete='cascade',
        index=True,
    )
    direction_id = fields.Many2one(
        comodel_name='sn.direction',
        string='Direction',
        related='service_id.direction_id',
        store=True,
        index=True,
    )
    ministry_id = fields.Many2one(
        comodel_name='sn.ministry',
        string='Ministère',
        related='service_id.ministry_id',
        store=True,
        index=True,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employé RH',
        ondelete='restrict',
        help='Lien vers le module RH',
    )
    job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Poste RH',
        help='Poste dans le module RH',
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        related='service_id.department_id',
        store=True,
        string='Département RH',
    )
    parent_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable hiérarchique',
    )
    coach_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Coach/Mentor',
    )
    work_location_id = fields.Many2one(
        comodel_name='hr.work.location',
        string='Lieu de travail',
    )

    # Champs de contact
    work_phone = fields.Char(string='Téléphone Bureau')
    mobile_phone = fields.Char(string='Téléphone Mobile')
    work_email = fields.Char(string='Email Professionnel')

    # Champs de nomination
    nomination_date = fields.Date(string='Date de nomination')
    nomination_decree = fields.Char(string='Numéro du décret')
    nomination_document = fields.Binary(string='Document de nomination')
    end_date = fields.Date(string='Date de fin de fonction')
    is_interim = fields.Boolean(string='Fonction intérimaire', default=False)
    
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
    public_show_photo = fields.Boolean(string='Afficher Photo', default=False)
    
    # Synchronisation RH
    auto_sync_hr = fields.Boolean(
        string='Synchronisation automatique RH',
        default=True,
        help='Synchroniser automatiquement avec hr.employee',
    )
    
    # Champs système
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

    # Contraintes SQL
    _sql_constraints = [
        ('matricule_unique', 'UNIQUE(matricule)', 'Le matricule doit être unique'),
    ]

    @api.depends('name')
    def _compute_qr_code_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id:
                record.qr_code_url = f"{base_url}/organigramme/agent/{record.id}"
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
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.name = self.employee_id.name
            self.first_name = self.employee_id.name.split()[-1] if self.employee_id.name else ''
            self.last_name = ' '.join(self.employee_id.name.split()[:-1]) if self.employee_id.name else ''
            self.work_phone = self.employee_id.work_phone
            self.mobile_phone = self.employee_id.mobile_phone
            self.work_email = self.employee_id.work_email
            self.job_id = self.employee_id.job_id
            self.parent_id = self.employee_id.parent_id
            self.coach_id = self.employee_id.coach_id
            self.work_location_id = self.employee_id.work_location_id

    @api.constrains('service_id')
    def _check_service_active(self):
        for record in self:
            if record.service_id and not record.service_id.active:
                raise ValidationError('Le service doit être actif.')

    @api.constrains('work_email')
    def _check_work_email(self):
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for record in self:
            if record.work_email and not email_pattern.match(record.work_email):
                raise ValidationError('Le format de l\'email est invalide.')

    @api.constrains('work_phone', 'mobile_phone')
    def _check_phone_format(self):
        phone_pattern = re.compile(r'^\+221[0-9]{9}$|^[0-9]{9}$')
        for record in self:
            if record.work_phone and not phone_pattern.match(record.work_phone.replace(' ', '')):
                raise ValidationError('Le format du téléphone bureau est invalide. Format attendu: +221XXXXXXXXX')
            if record.mobile_phone and not phone_pattern.match(record.mobile_phone.replace(' ', '')):
                raise ValidationError('Le format du téléphone mobile est invalide. Format attendu: +221XXXXXXXXX')

    def action_view_employee(self):
        self.ensure_one()
        if not self.employee_id:
            return {}
        return {
            'name': 'Employé',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'res_id': self.employee_id.id,
        }

    def action_create_hr_employee(self):
        self.ensure_one()
        if self.employee_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Un employé RH existe déjà pour cet agent',
                    'type': 'warning',
                }
            }
        
        employee = self.env['hr.employee'].create({
            'name': self.name,
            'work_phone': self.work_phone,
            'mobile_phone': self.mobile_phone,
            'work_email': self.work_email,
            'department_id': self.department_id.id if self.department_id else False,
            'job_id': self.job_id.id if self.job_id else False,
            'parent_id': self.parent_id.id if self.parent_id else False,
            'coach_id': self.coach_id.id if self.coach_id else False,
            'work_location_id': self.work_location_id.id if self.work_location_id else False,
            'sn_agent_id': self.id,
        })
        self.employee_id = employee.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Employé RH créé: {employee.name}',
                'type': 'success',
            }
        }
    
    def action_sync_from_hr_employee(self):
        self.ensure_one()
        if not self.employee_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Aucun employé RH lié',
                    'type': 'warning',
                }
            }
        
        self.write({
            'name': self.employee_id.name,
            'work_phone': self.employee_id.work_phone,
            'mobile_phone': self.employee_id.mobile_phone,
            'work_email': self.employee_id.work_email,
            'job_id': self.employee_id.job_id.id if self.employee_id.job_id else False,
            'parent_id': self.employee_id.parent_id.id if self.employee_id.parent_id else False,
            'coach_id': self.employee_id.coach_id.id if self.employee_id.coach_id else False,
            'work_location_id': self.employee_id.work_location_id.id if self.employee_id.work_location_id else False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Synchronisation réussie depuis l\'employé RH',
                'type': 'success',
            }
        }
    
    def action_sync_to_hr_employee(self):
        self.ensure_one()
        if not self.employee_id:
            return self.action_create_hr_employee()
        
        self.employee_id.write({
            'name': self.name,
            'work_phone': self.work_phone,
            'mobile_phone': self.mobile_phone,
            'work_email': self.work_email,
            'job_id': self.job_id.id if self.job_id else False,
            'parent_id': self.parent_id.id if self.parent_id else False,
            'coach_id': self.coach_id.id if self.coach_id else False,
            'work_location_id': self.work_location_id.id if self.work_location_id else False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Synchronisation réussie vers l\'employé RH',
                'type': 'success',
            }
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.auto_sync_hr and not record.employee_id and record.department_id:
                # Proposer de créer un employé RH automatiquement
                pass
        return records
    
    def write(self, vals):
        result = super().write(vals)
        for record in self:
            if record.auto_sync_hr and record.employee_id:
                # Synchroniser automatiquement vers hr.employee
                sync_vals = {}
                if 'name' in vals:
                    sync_vals['name'] = vals['name']
                if 'work_phone' in vals:
                    sync_vals['work_phone'] = vals['work_phone']
                if 'mobile_phone' in vals:
                    sync_vals['mobile_phone'] = vals['mobile_phone']
                if 'work_email' in vals:
                    sync_vals['work_email'] = vals['work_email']
                if sync_vals:
                    record.employee_id.write(sync_vals)
        return result
    
    def name_get(self):
        result = []
        for record in self:
            name = f'{record.name} - {record.function}'
            result.append((record.id, name))
        return result
