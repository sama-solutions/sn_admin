from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Paramètres du module SN Admin
    sn_admin_auto_sync = fields.Boolean(
        string='Synchronisation automatique RH',
        config_parameter='sn_admin.auto_sync',
        default=True,
        help='Synchroniser automatiquement les agents avec hr.employee',
    )
    sn_admin_public_access = fields.Boolean(
        string='Accès public à l\'organigramme',
        config_parameter='sn_admin.public_access',
        default=True,
        help='Permettre l\'accès public à l\'organigramme sur le site web',
    )
    sn_admin_qr_code_size = fields.Integer(
        string='Taille des QR codes',
        config_parameter='sn_admin.qr_code_size',
        default=150,
        help='Taille des QR codes en pixels',
    )
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
