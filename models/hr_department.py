from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    # Liens vers la structure organique
    sn_ministry_id = fields.Many2one(
        comodel_name='sn.ministry',
        string='Ministère',
    )
    sn_direction_id = fields.Many2one(
        comodel_name='sn.direction',
        string='Direction',
    )
    sn_service_id = fields.Many2one(
        comodel_name='sn.service',
        string='Service',
    )
    sn_structure_type = fields.Selection(
        selection=[
            ('ministry', 'Ministère'),
            ('direction', 'Direction'),
            ('service', 'Service'),
        ],
        string='Type de structure',
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            # Vérifier s'il doit être lié à une structure sn_admin
            pass
        return records

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            # Synchroniser vers la structure organique si lié
            if record.sn_ministry_id:
                sync_vals = {}
                if 'name' in vals:
                    sync_vals['name'] = vals['name']
                if sync_vals:
                    record.sn_ministry_id.write(sync_vals)
            elif record.sn_direction_id:
                sync_vals = {}
                if 'name' in vals:
                    sync_vals['name'] = vals['name']
                if sync_vals:
                    record.sn_direction_id.write(sync_vals)
            elif record.sn_service_id:
                sync_vals = {}
                if 'name' in vals:
                    sync_vals['name'] = vals['name']
                if sync_vals:
                    record.sn_service_id.write(sync_vals)
        return result

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

    def action_sync_from_sn_structure(self):
        self.ensure_one()
        if self.sn_service_id:
            self.write({
                'name': self.sn_service_id.name,
            })
        elif self.sn_direction_id:
            self.write({
                'name': self.sn_direction_id.name,
            })
        elif self.sn_ministry_id:
            self.write({
                'name': self.sn_ministry_id.name,
            })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Synchronisation réussie depuis la structure organique',
                'type': 'success',
            }
        }

    def get_sn_structure(self):
        """Retourner l'objet sn.ministry/direction/service lié"""
        self.ensure_one()
        if self.sn_service_id:
            return self.sn_service_id
        elif self.sn_direction_id:
            return self.sn_direction_id
        elif self.sn_ministry_id:
            return self.sn_ministry_id
        return None

    def sync_to_sn_structure(self):
        """Synchroniser les données vers la structure organique"""
        self.ensure_one()
        structure = self.get_sn_structure()
        if structure:
            structure.write({
                'name': self.name,
            })
