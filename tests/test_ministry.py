from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMinistry(TransactionCase):

    def setUp(self):
        super(TestMinistry, self).setUp()
        self.Ministry = self.env['sn.ministry']
        self.Direction = self.env['sn.direction']
        self.Service = self.env['sn.service']
        self.Agent = self.env['sn.agent']

    def test_create_ministry(self):
        """Test creating a ministry with all required fields"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
            'state': 'active',
        })
        self.assertTrue(ministry)
        self.assertEqual(ministry.name, 'Ministère Test')
        self.assertEqual(ministry.code, 'TEST')
        self.assertEqual(ministry.type, 'ministry')

    def test_ministry_code_unique(self):
        """Test that ministry code must be unique"""
        self.Ministry.create({
            'name': 'Ministère Test 1',
            'code': 'TEST',
            'type': 'ministry',
        })
        with self.assertRaises(Exception):
            self.Ministry.create({
                'name': 'Ministère Test 2',
                'code': 'TEST',
                'type': 'ministry',
            })

    def test_ministry_name_unique(self):
        """Test that ministry name must be unique (case insensitive)"""
        self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST1',
            'type': 'ministry',
        })
        with self.assertRaises(Exception):
            self.Ministry.create({
                'name': 'ministère test',
                'code': 'TEST2',
                'type': 'ministry',
            })

    def test_compute_direction_count(self):
        """Test direction_count computed field"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        self.assertEqual(ministry.direction_count, 0)
        
        # Create 3 directions
        for i in range(3):
            self.Direction.create({
                'name': f'Direction {i}',
                'code': f'DIR{i}',
                'ministry_id': ministry.id,
            })
        
        ministry._compute_direction_count()
        self.assertEqual(ministry.direction_count, 3)

    def test_compute_service_count(self):
        """Test service_count computed field"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction1 = self.Direction.create({
            'name': 'Direction 1',
            'code': 'DIR1',
            'ministry_id': ministry.id,
        })
        
        direction2 = self.Direction.create({
            'name': 'Direction 2',
            'code': 'DIR2',
            'ministry_id': ministry.id,
        })
        
        # Create 3 services for direction1
        for i in range(3):
            self.Service.create({
                'name': f'Service 1-{i}',
                'code': f'SRV1{i}',
                'direction_id': direction1.id,
            })
        
        # Create 2 services for direction2
        for i in range(2):
            self.Service.create({
                'name': f'Service 2-{i}',
                'code': f'SRV2{i}',
                'direction_id': direction2.id,
            })
        
        ministry._compute_service_count()
        self.assertEqual(ministry.service_count, 5)

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
        
        service1 = self.Service.create({
            'name': 'Service 1',
            'code': 'SRV1',
            'direction_id': direction.id,
        })
        
        service2 = self.Service.create({
            'name': 'Service 2',
            'code': 'SRV2',
            'direction_id': direction.id,
        })
        
        # Create 3 agents for service1
        for i in range(3):
            self.Agent.create({
                'name': f'Agent 1-{i}',
                'function': 'Test',
                'service_id': service1.id,
            })
        
        # Create 2 agents for service2
        for i in range(2):
            self.Agent.create({
                'name': f'Agent 2-{i}',
                'function': 'Test',
                'service_id': service2.id,
            })
        
        ministry._compute_agent_count()
        self.assertEqual(ministry.agent_count, 5)

    def test_action_view_directions(self):
        """Test action_view_directions method"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        for i in range(2):
            self.Direction.create({
                'name': f'Direction {i}',
                'code': f'DIR{i}',
                'ministry_id': ministry.id,
            })
        
        action = ministry.action_view_directions()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'sn.direction')
        self.assertIn(('ministry_id', '=', ministry.id), action['domain'])

    def test_name_get(self):
        """Test name_get method"""
        ministry = self.Ministry.create({
            'name': 'Ministère de la Santé',
            'code': 'MSAS',
            'type': 'ministry',
        })
        
        name_get_result = ministry.name_get()
        self.assertEqual(len(name_get_result), 1)
        self.assertEqual(name_get_result[0][0], ministry.id)
        self.assertEqual(name_get_result[0][1], 'MSAS - Ministère de la Santé')
