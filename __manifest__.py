{
    'name': 'SN Admin - Organigramme Administration Sénégalaise',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': "Registre officiel complet de l'administration publique sénégalaise",
    'description': """
        Registre Officiel Complet de l'administration sénégalaise
        ============================================================
        - Données complètes: ministères, directions, services, agents
        - Intégration RH Odoo: synchronisation avec hr.employee et hr.department
        - Vues organigramme interactives et portail public
    """,
    'author': 'Équipe PSA-GSN',
    'website': 'https://www.gouv.sn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'mail',
        'website',
    ],
    'data': [
        'security/sn_admin_security.xml',
        'security/ir.model.access.csv',
        'views/sn_ministry_views.xml',
        'views/sn_category_views.xml',
        'views/sn_direction_views.xml',
        'views/sn_service_views.xml',
        'views/sn_agent_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/sn_admin_menus.xml',
        'views/sn_search_views.xml',
        'views/sn_dashboard.xml',
        'views/website_templates.xml',
        'reports/sn_organigramme_report.xml',
        'reports/sn_annuaire_report.xml',
        'reports/sn_statistics_report.xml',
        'data/sn_ministry_data.xml',
        'data/sn_category_data.xml',
        'data/sn_direction_data.xml',
        'data/sn_service_data.xml',
        'data/sn_agent_data.xml',
    ],
    'demo': [
        'data/sn_admin_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sn_admin/static/src/css/sn_orgchart.css',
            'sn_admin/static/src/js/sn_orgchart.js',
        ],
        'web.assets_frontend': [
            'sn_admin/static/src/css/sn_admin_public.css',
            'sn_admin/static/src/js/sn_admin_public_owl.js',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'Pillow'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
