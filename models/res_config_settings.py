from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sn_admin_public_portal_enabled = fields.Boolean(
        string='Activer le portail public',
        config_parameter='sn_admin.public_portal_enabled',
        default=True,
    )
    sn_admin_show_phone_public = fields.Boolean(
        string='Afficher les téléphones sur le portail public',
        config_parameter='sn_admin.show_phone_public',
        default=True,
    )
    sn_admin_show_email_public = fields.Boolean(
        string='Afficher les emails sur le portail public',
        config_parameter='sn_admin.show_email_public',
        default=True,
    )
    sn_admin_show_address_public = fields.Boolean(
        string='Afficher les adresses sur le portail public',
        config_parameter='sn_admin.show_address_public',
        default=True,
    )
    sn_admin_enable_api = fields.Boolean(
        string='Activer l\'API publique',
        config_parameter='sn_admin.enable_api',
        default=False,
    )
