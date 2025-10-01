{
    'name': 'SN Admin - Organigramme Administration Sénégalaise',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Registre Officiel Complet de l\'administration publique sénégalaise',
    'description': """
        Registre Officiel Complet de l'administration sénégalaise
        ============================================================
        
        **RÉVOLUTION DANS LA TRANSPARENCE ADMINISTRATIVE DU SÉNÉGAL**
        
        Ce module est le registre officiel national complet de l'administration publique sénégalaise :
        
        * **Données complètes** : TOUTE l'architecture organique de l'État (ministères, directions, services)
        * **Intégration RH Odoo** : Synchronisation bidirectionnelle avec hr.employee et hr.department
        * **Vues Organigramme** : Visualisation hiérarchique interactive (OrgChart.js)
        * **QR Codes** : Chaque structure a un QR code partageable
        * **Portail public enrichi** : Contacts détaillés, cartes GPS, partage sur réseaux sociaux
        * **Gestion des nominations** : Dates, décrets, documents
        * **Recherche avancée** : Par nom, fonction, ministère, région
        * **Export** : PDF, Excel, PNG
        
        **Cas d'usage** :
        - Pour les citoyens : Trouver facilement un interlocuteur dans l'administration
        - Pour le gouvernement : Gérer les nominations et le personnel
        - Pour les ministères : Maintenir à jour l'organigramme et les contacts
        - Pour les RH : Utiliser l'interface RH standard d'Odoo pour gérer les agents
    """,
    'author': 'Équipe PSA-GSN',
    'website': 'https://www.gouv.sn',
    'license': 'LGPL-3',
    # Conformité Odoo 18 CE : Ce module respecte strictement les directives Odoo 18 Community Edition
    # - Dépendances minimalistes : base, hr, mail, website (tous disponibles en CE)
    # - Vues modernes : <list> avec multi_edit="1"
    # - Pas de dépendances à account ou modules Enterprise
    # - Framework standard avec exception justifiée (OrgChart.js pour organigramme interactif)
    # Voir ODOO18_COMPLIANCE.md pour les détails complets
    'depends': [
        'base',
        'hr',
        'mail',
        'website',
    ],
    'data': [
        # Security
        'security/sn_admin_security.xml',
        'security/ir.model.access.csv',
        
        # Views
        'views/sn_ministry_views.xml',
        'views/sn_direction_views.xml',
        'views/sn_service_views.xml',
        'views/sn_agent_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/sn_admin_menus.xml',
        'views/sn_search_views.xml',
        'views/sn_dashboard.xml',
        'views/website_templates.xml',
        
        # Reports
        'reports/sn_organigramme_report.xml',
        'reports/sn_annuaire_report.xml',
        'reports/sn_statistics_report.xml',
        
        # Data (données complètes, pas démo)
        'data/sn_ministry_data.xml',
        'data/sn_direction_data.xml',
        'data/sn_service_data.xml',
        'data/sn_agent_data.xml',
    ],
    'demo': [
        'data/sn_admin_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # OrgChart.js library (jQuery plugin)
            'sn_admin/static/src/css/lib/jquery.orgchart.css',
            'sn_admin/static/src/js/lib/jquery.orgchart.js',
            # Custom OrgChart widget
            'sn_admin/static/src/css/sn_orgchart.css',
            'sn_admin/static/src/js/sn_orgchart.js',
        ],
        'web.assets_frontend': [
            # OrgChart.js library for public pages
            'sn_admin/static/src/css/lib/jquery.orgchart.css',
            'sn_admin/static/src/js/lib/jquery.orgchart.js',
            # Public styles and scripts
            'sn_admin/static/src/css/sn_admin_public.css',
            'sn_admin/static/src/js/sn_admin_public.js',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'PIL'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
