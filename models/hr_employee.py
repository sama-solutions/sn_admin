from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Lien vers l'agent officiel
    sn_agent_id = fields.Many2one(
        comodel_name='sn.agent',
        string='Agent Officiel',
        ondelete='restrict',
        help='Lien vers le registre officiel de l\'administration',
    )
    
    # Champs relationnels (related depuis l'agent)
    sn_ministry_id = fields.Many2one(
        comodel_name='sn.ministry',
        related='sn_agent_id.ministry_id',
        string='Ministère',
        store=True,
        readonly=True,
    )
    sn_direction_id = fields.Many2one(
        comodel_name='sn.direction',
        related='sn_agent_id.direction_id',
        string='Direction',
        store=True,
        readonly=True,
    )
    sn_service_id = fields.Many2one(
        comodel_name='sn.service',
        related='sn_agent_id.service_id',
        string='Service',
        store=True,
        readonly=True,
    )
    
    # Champs QR Code (related depuis l'agent)
    sn_qr_code = fields.Binary(
        string='QR Code Agent',
        related='sn_agent_id.qr_code',
        readonly=True,
    )
    sn_qr_code_url = fields.Char(
        string='URL QR Code Agent',
        related='sn_agent_id.qr_code_url',
        readonly=True,
    )

    # Champs de nomination
    nomination_date = fields.Date(string='Date de nomination')
    nomination_decree = fields.Char(string='Numéro du décret')
    nomination_document = fields.Binary(string='Document de nomination')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            # Créer automatiquement un sn.agent si le département est lié à un service
            if record.department_id and record.department_id.sn_service_id and not record.sn_agent_id:
                agent = self.env['sn.agent'].create({
                    'name': record.name,
                    'function': record.job_id.name if record.job_id else 'Agent',
                    'service_id': record.department_id.sn_service_id.id,
                    'work_phone': record.work_phone,
                    'mobile_phone': record.mobile_phone,
                    'work_email': record.work_email,
                    'employee_id': record.id,
                    'auto_sync_hr': True,
                })
                record.sn_agent_id = agent.id
        return records

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            # Synchroniser vers sn.agent si lié et auto_sync activé
            if record.sn_agent_id and record.sn_agent_id.auto_sync_hr:
                sync_vals = {}
                if 'name' in vals:
                    sync_vals['name'] = vals['name']
                if 'work_phone' in vals:
                    sync_vals['work_phone'] = vals['work_phone']
                if 'mobile_phone' in vals:
                    sync_vals['mobile_phone'] = vals['mobile_phone']
                if 'work_email' in vals:
                    sync_vals['work_email'] = vals['work_email']
                if 'job_id' in vals and vals['job_id']:
                    job = self.env['hr.job'].browse(vals['job_id'])
                    sync_vals['function'] = job.name
                if sync_vals:
                    record.sn_agent_id.write(sync_vals)
        return result

    def action_create_sn_agent(self):
        self.ensure_one()
        if self.sn_agent_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Un agent officiel existe déjà pour cet employé',
                    'type': 'warning',
                }
            }
        
        if not self.department_id or not self.department_id.sn_service_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Le département doit être lié à un service pour créer un agent officiel',
                    'type': 'warning',
                }
            }
        
        agent = self.env['sn.agent'].create({
            'name': self.name,
            'function': self.job_id.name if self.job_id else 'Agent',
            'service_id': self.department_id.sn_service_id.id,
            'work_phone': self.work_phone,
            'mobile_phone': self.mobile_phone,
            'work_email': self.work_email,
            'employee_id': self.id,
            'auto_sync_hr': True,
        })
        self.sn_agent_id = agent.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Agent officiel créé: {agent.name}',
                'type': 'success',
            }
        }

    def action_view_sn_agent(self):
        self.ensure_one()
        if not self.sn_agent_id:
            return {}
        return {
            'name': 'Agent Officiel',
            'type': 'ir.actions.act_window',
            'res_model': 'sn.agent',
            'view_mode': 'form',
            'res_id': self.sn_agent_id.id,
        }

    def action_view_sn_structure(self):
        self.ensure_one()
        if self.sn_service_id:
            return {
                'name': 'Service',
                'type': 'ir.actions.act_window',
                'res_model': 'sn.service',
                'view_mode': 'form',
                'res_id': self.sn_service_id.id,
            }
        elif self.sn_direction_id:
            return {
                'name': 'Direction',
                'type': 'ir.actions.act_window',
                'res_model': 'sn.direction',
                'view_mode': 'form',
                'res_id': self.sn_direction_id.id,
            }
        elif self.sn_ministry_id:
            return {
                'name': 'Ministère',
                'type': 'ir.actions.act_window',
                'res_model': 'sn.ministry',
                'view_mode': 'form',
                'res_id': self.sn_ministry_id.id,
            }
        return {}
