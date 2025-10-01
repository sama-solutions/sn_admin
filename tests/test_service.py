from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestService(TransactionCase):

    def setUp(self):
        super(TestService, self).setUp()
        self.Ministry = self.env['sn.ministry']
        self.Direction = self.env['sn.direction']
        self.Service = self.env['sn.service']
        self.Agent = self.env['sn.agent']

    def test_create_service(self):
        """Test creating a service"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DIR',
            'ministry_id': ministry.id,
        })
        
        service = self.Service.create({
            'name': 'Service Test',
            'code': 'SRV',
            'type': 'service',
            'direction_id': direction.id,
        })
        
        self.assertTrue(service)
        self.assertEqual(service.name, 'Service Test')
        self.assertEqual(service.direction_id, direction)

    def test_service_code_direction_unique(self):
        """Test that service code must be unique per direction"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DIR',
            'ministry_id': ministry.id,
        })
        
        self.Service.create({
            'name': 'Service 1',
            'code': 'SRH',
            'direction_id': direction.id,
        })
        
        with self.assertRaises(Exception):
            self.Service.create({
                'name': 'Service 2',
                'code': 'SRH',
                'direction_id': direction.id,
            })

    def test_service_ministry_id_related(self):
        """Test that ministry_id is correctly related"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DIR',
            'ministry_id': ministry.id,
        })
        
        service = self.Service.create({
            'name': 'Service Test',
            'code': 'SRV',
            'direction_id': direction.id,
        })
        
        self.assertEqual(service.ministry_id, direction.ministry_id)

    def test_compute_agent_count(self):
        """Test agent_count computed field"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DIR',
            'ministry_id': ministry.id,
        })
        
        service = self.Service.create({
            'name': 'Service Test',
            'code': 'SRV',
            'direction_id': direction.id,
        })
        
        self.assertEqual(service.agent_count, 0)
        
        # Create 5 agents
        for i in range(5):
            self.Agent.create({
                'name': f'Agent {i}',
                'function': 'Test',
                'service_id': service.id,
            })
        
        service._compute_agent_count()
        self.assertEqual(service.agent_count, 5)

    def test_action_view_agents(self):
        """Test action_view_agents method"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DIR',
            'ministry_id': ministry.id,
        })
        
        service = self.Service.create({
            'name': 'Service Test',
            'code': 'SRV',
            'direction_id': direction.id,
        })
        
        for i in range(4):
            self.Agent.create({
                'name': f'Agent {i}',
                'function': 'Test',
                'service_id': service.id,
            })
        
        action = service.action_view_agents()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'sn.agent')
        self.assertIn(('service_id', '=', service.id), action['domain'])

    def test_name_get(self):
        """Test name_get method"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'MSAS',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DGS',
            'ministry_id': ministry.id,
        })
        
        service = self.Service.create({
            'name': 'Service des Ressources Humaines',
            'code': 'SRH',
            'direction_id': direction.id,
        })
        
        name_get_result = service.name_get()
        self.assertEqual(len(name_get_result), 1)
        self.assertEqual(name_get_result[0][0], service.id)
        self.assertIn('DGS/SRH', name_get_result[0][1])

    def test_constrains_direction_active(self):
        """Test that direction must be active"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DIR',
            'ministry_id': ministry.id,
            'active': False,
        })
        
        with self.assertRaises(ValidationError):
            self.Service.create({
                'name': 'Service Test',
                'code': 'SRV',
                'direction_id': direction.id,
            })
