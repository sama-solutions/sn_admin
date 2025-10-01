from odoo import http
from odoo.http import request
from odoo.tools import str2bool


class SNAdminAPIController(http.Controller):

    @http.route('/api/v1/ministries', type='json', auth='public', csrf=False)
    def api_ministries(self, **kw):
        """Liste des ministères (JSON)"""
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        
        # Vérifier si l'API est activée
        api_enabled = str2bool(IrConfigParameter.get_param('sn_admin.enable_api', default='False'))
        if not api_enabled:
            return {'error': 'API not enabled', 'code': 403}
        
        Ministry = request.env['sn.ministry'].sudo()
        
        ministries = Ministry.search([('active', '=', True), ('state', '=', 'active')], order='name')
        
        data = []
        for ministry in ministries:
            data.append({
                'id': ministry.id,
                'name': ministry.name,
                'code': ministry.code,
                'type': ministry.type,
                'phone': ministry.phone,
                'email': ministry.email,
                'website': ministry.website,
                'direction_count': ministry.direction_count,
            })
        
        return {
            'data': data,
            'meta': {
                'count': len(data),
            }
        }

    @http.route('/api/v1/ministry/<int:ministry_id>', type='json', auth='public', csrf=False)
    def api_ministry(self, ministry_id, **kw):
        """Détails d'un ministère (JSON)"""
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        
        # Vérifier si l'API est activée
        api_enabled = str2bool(IrConfigParameter.get_param('sn_admin.enable_api', default='False'))
        if not api_enabled:
            return {'error': 'API not enabled', 'code': 403}
        
        Ministry = request.env['sn.ministry'].sudo()
        
        ministry = Ministry.browse(ministry_id)
        
        if not ministry.exists() or not ministry.active or ministry.state != 'active':
            return {'error': 'Ministry not found', 'code': 404}
        
        return {
            'data': {
                'id': ministry.id,
                'name': ministry.name,
                'code': ministry.code,
                'type': ministry.type,
                'address': ministry.address,
                'phone': ministry.phone,
                'email': ministry.email,
                'website': ministry.website,
                'description': ministry.description,
                'direction_count': ministry.direction_count,
                'service_count': ministry.service_count,
                'agent_count': ministry.agent_count,
            }
        }

    @http.route('/api/v1/directions', type='json', auth='public', csrf=False)
    def api_directions(self, **kw):
        """Liste des directions (JSON)"""
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        
        # Vérifier si l'API est activée
        api_enabled = str2bool(IrConfigParameter.get_param('sn_admin.enable_api', default='False'))
        if not api_enabled:
            return {'error': 'API not enabled', 'code': 403}
        
        Direction = request.env['sn.direction'].sudo()
        
        domain = [('active', '=', True), ('state', '=', 'active')]
        
        ministry_id = kw.get('ministry_id')
        if ministry_id:
            domain.append(('ministry_id', '=', int(ministry_id)))
        
        directions = Direction.search(domain, order='name')
        
        data = []
        for direction in directions:
            data.append({
                'id': direction.id,
                'name': direction.name,
                'code': direction.code,
                'type': direction.type,
                'ministry_id': direction.ministry_id.id,
                'ministry_name': direction.ministry_id.name,
                'service_count': direction.service_count,
            })
        
        return {
            'data': data,
            'meta': {
                'count': len(data),
            }
        }

    @http.route('/api/v1/services', type='json', auth='public', csrf=False)
    def api_services(self, **kw):
        """Liste des services (JSON)"""
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        
        # Vérifier si l'API est activée
        api_enabled = str2bool(IrConfigParameter.get_param('sn_admin.enable_api', default='False'))
        if not api_enabled:
            return {'error': 'API not enabled', 'code': 403}
        
        Service = request.env['sn.service'].sudo()
        
        domain = [('active', '=', True), ('state', '=', 'active')]
        
        direction_id = kw.get('direction_id')
        ministry_id = kw.get('ministry_id')
        
        if direction_id:
            domain.append(('direction_id', '=', int(direction_id)))
        
        if ministry_id:
            domain.append(('ministry_id', '=', int(ministry_id)))
        
        services = Service.search(domain, order='name')
        
        data = []
        for service in services:
            data.append({
                'id': service.id,
                'name': service.name,
                'code': service.code,
                'type': service.type,
                'direction_id': service.direction_id.id,
                'direction_name': service.direction_id.name,
                'ministry_id': service.ministry_id.id,
                'ministry_name': service.ministry_id.name,
                'agent_count': service.agent_count,
            })
        
        return {
            'data': data,
            'meta': {
                'count': len(data),
            }
        }

    @http.route('/api/v1/agents', type='json', auth='public', csrf=False)
    def api_agents(self, **kw):
        """Liste des agents (JSON)"""
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        
        # Vérifier si l'API est activée
        api_enabled = str2bool(IrConfigParameter.get_param('sn_admin.enable_api', default='False'))
        if not api_enabled:
            return {'error': 'API not enabled', 'code': 403}
        
        Agent = request.env['sn.agent'].sudo()
        
        domain = [('active', '=', True), ('state', '=', 'active')]
        
        service_id = kw.get('service_id')
        direction_id = kw.get('direction_id')
        ministry_id = kw.get('ministry_id')
        
        if service_id:
            domain.append(('service_id', '=', int(service_id)))
        
        if direction_id:
            domain.append(('direction_id', '=', int(direction_id)))
        
        if ministry_id:
            domain.append(('ministry_id', '=', int(ministry_id)))
        
        agents = Agent.search(domain, order='name')
        
        # Vérifier les paramètres de visibilité
        show_phone = str2bool(IrConfigParameter.get_param('sn_admin.show_phone_public', default='True'))
        show_email = str2bool(IrConfigParameter.get_param('sn_admin.show_email_public', default='True'))
        
        data = []
        for agent in agents:
            agent_data = {
                'id': agent.id,
                'name': agent.name,
                'function': agent.function,
                'service_id': agent.service_id.id,
                'service_name': agent.service_id.name,
                'direction_id': agent.direction_id.id,
                'direction_name': agent.direction_id.name,
                'ministry_id': agent.ministry_id.id,
                'ministry_name': agent.ministry_id.name,
            }
            
            if show_phone:
                agent_data['work_phone'] = agent.work_phone or ''
                agent_data['mobile_phone'] = agent.mobile_phone or ''
            
            if show_email:
                agent_data['work_email'] = agent.work_email or ''
            
            data.append(agent_data)
        
        return {
            'data': data,
            'meta': {
                'count': len(data),
            }
        }

    @http.route('/api/v1/search', type='json', auth='public', csrf=False)
    def api_search(self, **kw):
        """Recherche globale (JSON)"""
        IrConfigParameter = request.env['ir.config_parameter'].sudo()
        
        # Vérifier si l'API est activée
        api_enabled = str2bool(IrConfigParameter.get_param('sn_admin.enable_api', default='False'))
        if not api_enabled:
            return {'error': 'API not enabled', 'code': 403}
        
        query = kw.get('q', '')
        
        if not query or len(query) < 3:
            return {'error': 'Query too short (minimum 3 characters)', 'code': 400}
        
        Agent = request.env['sn.agent'].sudo()
        
        domain = [
            ('active', '=', True),
            ('state', '=', 'active'),
            '|', '|',
            ('name', 'ilike', query),
            ('function', 'ilike', query),
            ('work_email', 'ilike', query)
        ]
        
        agents = Agent.search(domain, limit=50, order='name')
        
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
            })
        
        return {
            'data': results,
            'meta': {
                'count': len(results),
                'query': query,
            }
        }
