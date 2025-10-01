from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Liens vers la structure organique
    sn_agent_id = fields.Many2one(
        comodel_name='sn.agent',
        string='Agent SN Admin',
        help='Lien vers le registre officiel',
    )
    sn_ministry_id = fields.Many2one(
        comodel_name='sn.ministry',
        string='Ministère',
        compute='_compute_sn_structure',
        store=True,
    )
    sn_direction_id = fields.Many2one(
        comodel_name='sn.direction',
        string='Direction',
        compute='_compute_sn_structure',
        store=True,
    )
    sn_service_id = fields.Many2one(
        comodel_name='sn.service',
        string='Service',
        compute='_compute_sn_structure',
        store=True,
    )

    # Champs de nomination
    nomination_date = fields.Date(string='Date de nomination')
    nomination_decree = fields.Char(string='Numéro du décret')
    nomination_document = fields.Binary(string='Document de nomination')

    @api.depends('sn_agent_id', 'sn_agent_id.service_id', 'sn_agent_id.direction_id', 'sn_agent_id.ministry_id', 'department_id')
    def _compute_sn_structure(self):
        for record in self:
            if record.sn_agent_id:
                record.sn_ministry_id = record.sn_agent_id.ministry_id
                record.sn_direction_id = record.sn_agent_id.direction_id
                record.sn_service_id = record.sn_agent_id.service_id
            elif record.department_id:
                # Chercher depuis le département
                if record.department_id.sn_service_id:
                    record.sn_service_id = record.department_id.sn_service_id
                    record.sn_direction_id = record.department_id.sn_service_id.direction_id
                    record.sn_ministry_id = record.department_id.sn_service_id.ministry_id
                elif record.department_id.sn_direction_id:
                    record.sn_service_id = False
                    record.sn_direction_id = record.department_id.sn_direction_id
                    record.sn_ministry_id = record.department_id.sn_direction_id.ministry_id
                elif record.department_id.sn_ministry_id:
                    record.sn_service_id = False
                    record.sn_direction_id = False
                    record.sn_ministry_id = record.department_id.sn_ministry_id
                else:
                    record.sn_service_id = False
                    record.sn_direction_id = False
                    record.sn_ministry_id = False
            else:
                record.sn_service_id = False
                record.sn_direction_id = False
                record.sn_ministry_id = False

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
            # Synchroniser vers sn.agent si lié
            if record.sn_agent_id:
                sync_vals = {}
                if 'name' in vals:
                    sync_vals['name'] = vals['name']
                if 'work_phone' in vals:
                    sync_vals['work_phone'] = vals['work_phone']
                if 'mobile_phone' in vals:
                    sync_vals['mobile_phone'] = vals['mobile_phone']
                if 'work_email' in vals:
                    sync_vals['work_email'] = vals['work_email']
                if 'job_id' in vals:
                    sync_vals['job_id'] = vals['job_id']
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
