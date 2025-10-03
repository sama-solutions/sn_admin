from odoo import http
from odoo.http import request
from odoo.tools import str2bool
import qrcode
import io
import base64


class SNAdminController(http.Controller):

    @http.route('/organigramme', type='http', auth='public', website=True)
    def index(self, **kw):
        """Page d'accueil de l'organigramme"""
        Ministry = request.env['sn.ministry'].sudo()
        
        # Statistiques globales
        total_ministries = Ministry.search_count([('active', '=', True), ('state', '=', 'active')])
        total_directions = request.env['sn.direction'].sudo().search_count([('active', '=', True), ('state', '=', 'active')])
        total_services = request.env['sn.service'].sudo().search_count([('active', '=', True), ('state', '=', 'active')])
        total_agents = request.env['sn.agent'].sudo().search_count([('active', '=', True), ('state', '=', 'active')])
        
        # Récupérer les institutions par type
        presidency = Ministry.search([('type', '=', 'presidency'), ('active', '=', True), ('state', '=', 'active')])
        primature = Ministry.search([('type', '=', 'primature'), ('active', '=', True), ('state', '=', 'active')])
        ministries = Ministry.search([('type', '=', 'ministry'), ('active', '=', True), ('state', '=', 'active')], order='name')
        
        values = {
            'total_ministries': total_ministries,
            'total_directions': total_directions,
            'total_services': total_services,
            'total_agents': total_agents,
            'presidency': presidency,
            'primature': primature,
            'ministries': ministries,
        }
        
        return request.render('sn_admin.organigramme_index', values)

    @http.route('/organigramme/ministeres', type='http', auth='public', website=True)
    def ministries(self, **kw):
        """Liste des ministères"""
        Ministry = request.env['sn.ministry'].sudo()
        
        ministries = Ministry.search([('active', '=', True), ('state', '=', 'active')], order='type, name')
        
        values = {
            'ministries': ministries,
        }
        
        return request.render('sn_admin.organigramme_ministries', values)

    @http.route('/organigramme/ministere/<int:ministry_id>', type='http', auth='public', website=True)
    def ministry(self, ministry_id, **kw):
        """Détails d'un ministère"""
        Ministry = request.env['sn.ministry'].sudo()
        Category = request.env['sn.category'].sudo()
        
        ministry = Ministry.browse(ministry_id)
        
        if not ministry.exists() or not ministry.active or ministry.state != 'active':
            return request.render('website.404')
        
        # Récupérer les catégories du ministère
        categories = Category.search([
            ('ministry_id', '=', ministry_id),
            ('active', '=', True),
            ('state', '=', 'active')
        ], order='name')
        
        # Récupérer les directions (avec et sans catégorie)
        directions = ministry.direction_ids.filtered(lambda d: d.active and d.state == 'active')
        
        values = {
            'ministry': ministry,
            'categories': categories,
            'directions': directions,
        }
        
        return request.render('sn_admin.organigramme_ministry_detail', values)

    @http.route('/organigramme/categorie/<int:category_id>', type='http', auth='public', website=True)
    def category(self, category_id, **kw):
        """Détails d'une catégorie"""
        Category = request.env['sn.category'].sudo()
        
        category = Category.browse(category_id)
        
        if not category.exists() or not category.active or category.state != 'active':
            return request.render('website.404')
        
        directions = category.direction_ids.filtered(lambda d: d.active and d.state == 'active')
        
        values = {
            'category': category,
            'directions': directions,
        }
        
        return request.render('sn_admin.organigramme_category_detail', values)

    @http.route('/organigramme/direction/<int:direction_id>', type='http', auth='public', website=True)
    def direction(self, direction_id, **kw):
        """Détails d'une direction"""
        Direction = request.env['sn.direction'].sudo()
        
        direction = Direction.browse(direction_id)
        
        if not direction.exists() or not direction.active or direction.state != 'active':
            return request.render('website.404')
        
        services = direction.service_ids.filtered(lambda s: s.active and s.state == 'active')
        
        values = {
            'direction': direction,
            'services': services,
        }
        
        return request.render('sn_admin.organigramme_direction_detail', values)

    @http.route('/organigramme/service/<int:service_id>', type='http', auth='public', website=True)
    def service(self, service_id, **kw):
        """Détails d'un service"""
        Service = request.env['sn.service'].sudo()
        
        service = Service.browse(service_id)
        
        if not service.exists() or not service.active or service.state != 'active':
            return request.render('website.404')
        
        agents = service.agent_ids.filtered(lambda a: a.active and a.state == 'active')
        
        values = {
            'service': service,
            'agents': agents,
        }
        
        return request.render('sn_admin.organigramme_service_detail', values)

    @http.route('/organigramme/agent/<int:agent_id>', type='http', auth='public', website=True)
    def agent(self, agent_id, **kw):
        """Détails d'un agent"""
        Agent = request.env['sn.agent'].sudo()
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        
        agent = Agent.browse(agent_id)
        
        if not agent.exists() or not agent.active or agent.state != 'active':
            return request.render('website.404')
        
        # Récupérer les paramètres de configuration
        show_phone = str2bool(IrConfigParameter.get_param('sn_admin.show_phone_public', default='True'))
        show_email = str2bool(IrConfigParameter.get_param('sn_admin.show_email_public', default='True'))
        
        values = {
            'agent': agent,
            'show_phone': show_phone,
            'show_email': show_email,
        }
        
        return request.render('sn_admin.organigramme_agent_detail', values)

    @http.route('/organigramme/search', type='http', auth='public', website=True)
    def search(self, **kw):
        """Page de recherche"""
        Agent = request.env['sn.agent'].sudo()
        Ministry = request.env['sn.ministry'].sudo()
        Direction = request.env['sn.direction'].sudo()
        Service = request.env['sn.service'].sudo()
        
        # Paramètres de recherche
        query = kw.get('q', '')
        ministry_id = kw.get('ministry_id')
        direction_id = kw.get('direction_id')
        service_id = kw.get('service_id')
        page = int(kw.get('page', 1))
        per_page = 20
        
        # Construire le domaine de recherche
        domain = [('active', '=', True), ('state', '=', 'active')]
        
        if query:
            domain += ['|', '|', ('name', 'ilike', query), ('function', 'ilike', query), ('work_email', 'ilike', query)]
        
        if ministry_id:
            domain.append(('ministry_id', '=', int(ministry_id)))
        
        if direction_id:
            domain.append(('direction_id', '=', int(direction_id)))
        
        if service_id:
            domain.append(('service_id', '=', int(service_id)))
        
        # Recherche avec pagination
        total_count = Agent.search_count(domain)
        offset = (page - 1) * per_page
        agents = Agent.search(domain, limit=per_page, offset=offset, order='name')
        
        # Pagination
        total_pages = (total_count + per_page - 1) // per_page
        
        # Listes pour les filtres
        ministries = Ministry.search([('active', '=', True), ('state', '=', 'active')], order='name')
        directions = Direction.search([('active', '=', True), ('state', '=', 'active')], order='name')
        services = Service.search([('active', '=', True), ('state', '=', 'active')], order='name')
        
        values = {
            'agents': agents,
            'query': query,
            'ministry_id': ministry_id,
            'direction_id': direction_id,
            'service_id': service_id,
            'ministries': ministries,
            'directions': directions,
            'services': services,
            'page': page,
            'total_pages': total_pages,
            'total_count': total_count,
        }
        
        return request.render('sn_admin.organigramme_search', values)

    @http.route('/organigramme/api/search', type='json', auth='public', csrf=False)
    def api_search(self, **kw):
        """API AJAX pour recherche en temps réel"""
        Agent = request.env['sn.agent'].sudo()
        
        query = kw.get('q', '')
        
        if not query or len(query) < 3:
            return {'results': []}
        
        domain = [
            ('active', '=', True),
            ('state', '=', 'active'),
            '|', '|',
            ('name', 'ilike', query),
            ('function', 'ilike', query),
            ('work_email', 'ilike', query)
        ]
        
        agents = Agent.search(domain, limit=10, order='name')
        
        results = []
        for agent in agents:
            results.append({
                'type': 'agent',
                'id': agent.id,
                'name': agent.name,
                'function': agent.function,
                'service': agent.service_id.name,
                'direction': agent.direction_id.name,
                'ministry': agent.ministry_id.name,
                'phone': agent.work_phone or agent.mobile_phone or '',
                'email': agent.work_email or '',
            })
        
        return {'results': results}

    @http.route('/organigramme/qrcode/<string:model>/<int:record_id>', type='http', auth='public')
    def download_qrcode(self, model, record_id, **kw):
        """Télécharger le QR code d'une structure"""
        # Vérifier le modèle
        if model not in ['sn.ministry', 'sn.direction', 'sn.service', 'sn.agent']:
            return request.not_found()
        
        # Récupérer l'enregistrement
        record = request.env[model].sudo().browse(record_id)
        
        if not record.exists():
            return request.not_found()
        
        # Générer l'URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        model_name = model.split('.')[-1]
        url = f"{base_url}/organigramme/{model_name}/{record_id}"
        
        # Générer le QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_bytes = buffer.getvalue()
        
        # Retourner l'image
        return request.make_response(
            qr_bytes,
            headers=[
                ('Content-Type', 'image/png'),
                ('Content-Disposition', f'attachment; filename=qrcode_{model_name}_{record.code or record_id}.png')
            ]
        )

    @http.route('/organigramme/tree', type='http', auth='public', website=True)
    def organigramme_tree(self, **kw):
        """Organigramme interactif public"""
        ministry_id = kw.get('ministry_id')
        
        values = {
            'ministry_id': ministry_id,
        }
        
        return request.render('sn_admin.organigramme_tree', values)

    @http.route('/organigramme/api/tree', type='json', auth='public', csrf=False)
    def api_organigramme_tree(self, **kw):
        """API pour les données de l'organigramme interactif"""
        Ministry = request.env['sn.ministry'].sudo()
        
        ministry_id = kw.get('ministry_id')
        
        def build_node(record, model_type):
            """Construire un nœud de l'organigramme"""
            node = {
                'id': record.id,
                'name': record.name,
                'title': record.code if hasattr(record, 'code') else '',
                'type': model_type,
                'model': record._name,
                'children': []
            }
            
            # Ajouter les enfants selon le type
            if model_type == 'ministry':
                # Niveau 2: Catégories
                Category = request.env['sn.category'].sudo()
                categories = Category.search([
                    ('ministry_id', '=', record.id),
                    ('active', '=', True),
                    ('state', '=', 'active')
                ])
                
                if categories:
                    node['children_count'] = len(categories)
                    for category in categories:
                        node['children'].append(build_node(category, 'category'))
                else:
                    # Si pas de catégories, afficher directement les directions
                    node['children_count'] = len(record.direction_ids)
                    for direction in record.direction_ids.filtered(lambda d: d.active and d.state == 'active'):
                        node['children'].append(build_node(direction, 'direction'))
            elif model_type == 'category':
                # Niveau 3: Directions de la catégorie
                node['children_count'] = len(record.direction_ids)
                for direction in record.direction_ids.filtered(lambda d: d.active and d.state == 'active'):
                    node['children'].append(build_node(direction, 'direction'))
            elif model_type == 'direction':
                # Niveau 4: Services
                node['children_count'] = len(record.service_ids)
                for service in record.service_ids.filtered(lambda s: s.active and s.state == 'active'):
                    node['children'].append(build_node(service, 'service'))
            elif model_type == 'service':
                # Niveau 5: Agents
                node['children_count'] = len(record.agent_ids)
                # Limiter les agents affichés pour la performance
                for agent in record.agent_ids.filtered(lambda a: a.active and a.state == 'active')[:10]:
                    node['children'].append(build_node(agent, 'agent'))
            
            return node
        
        # Construire l'arbre
        if ministry_id:
            ministry = Ministry.browse(int(ministry_id))
            if ministry.exists():
                tree_data = build_node(ministry, 'ministry')
            else:
                tree_data = {}
        else:
            # Arbre complet (limité aux ministères)
            tree_data = {
                'id': 0,
                'name': 'Administration Sénégalaise',
                'title': 'SENEGAL',
                'type': 'root',
                'children': []
            }
            
            for ministry in Ministry.search([('active', '=', True), ('state', '=', 'active')], order='type, name'):
                tree_data['children'].append(build_node(ministry, 'ministry'))
        
        return tree_data
