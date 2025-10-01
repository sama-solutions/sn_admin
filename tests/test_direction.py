from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestDirection(TransactionCase):

    def setUp(self):
        super(TestDirection, self).setUp()
        self.Ministry = self.env['sn.ministry']
        self.Direction = self.env['sn.direction']
        self.Service = self.env['sn.service']
        self.Agent = self.env['sn.agent']

    def test_create_direction(self):
        """Test creating a direction"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Test',
            'code': 'DIR',
            'type': 'generale',
            'ministry_id': ministry.id,
        })
        
        self.assertTrue(direction)
        self.assertEqual(direction.name, 'Direction Test')
        self.assertEqual(direction.ministry_id, ministry)

    def test_direction_code_ministry_unique(self):
        """Test that direction code must be unique per ministry"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
        })
        
        self.Direction.create({
            'name': 'Direction 1',
            'code': 'DGS',
            'ministry_id': ministry.id,
        })
        
        with self.assertRaises(Exception):
            self.Direction.create({
                'name': 'Direction 2',
                'code': 'DGS',
                'ministry_id': ministry.id,
            })

    def test_direction_code_different_ministry(self):
        """Test that same code can exist in different ministries"""
        ministry1 = self.Ministry.create({
            'name': 'Ministère 1',
            'code': 'TEST1',
            'type': 'ministry',
        })
        
        ministry2 = self.Ministry.create({
            'name': 'Ministère 2',
            'code': 'TEST2',
            'type': 'ministry',
        })
        
        direction1 = self.Direction.create({
            'name': 'Direction 1',
            'code': 'DGS',
            'ministry_id': ministry1.id,
        })
        
        direction2 = self.Direction.create({
            'name': 'Direction 2',
            'code': 'DGS',
            'ministry_id': ministry2.id,
        })
        
        self.assertTrue(direction1)
        self.assertTrue(direction2)

    def test_compute_service_count(self):
        """Test service_count computed field"""
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
        
        self.assertEqual(direction.service_count, 0)
        
        # Create 4 services
        for i in range(4):
            self.Service.create({
                'name': f'Service {i}',
                'code': f'SRV{i}',
                'direction_id': direction.id,
            })
        
        direction._compute_service_count()
        self.assertEqual(direction.service_count, 4)

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
        
        direction._compute_agent_count()
        self.assertEqual(direction.agent_count, 5)

    def test_action_view_services(self):
        """Test action_view_services method"""
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
        
        for i in range(3):
            self.Service.create({
                'name': f'Service {i}',
                'code': f'SRV{i}',
                'direction_id': direction.id,
            })
        
        action = direction.action_view_services()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'sn.service')
        self.assertIn(('direction_id', '=', direction.id), action['domain'])

    def test_name_get(self):
        """Test name_get method"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'MSAS',
            'type': 'ministry',
        })
        
        direction = self.Direction.create({
            'name': 'Direction Générale de la Santé',
            'code': 'DGS',
            'ministry_id': ministry.id,
        })
        
        name_get_result = direction.name_get()
        self.assertEqual(len(name_get_result), 1)
        self.assertEqual(name_get_result[0][0], direction.id)
        self.assertIn('MSAS/DGS', name_get_result[0][1])

    def test_constrains_ministry_active(self):
        """Test that ministry must be active"""
        ministry = self.Ministry.create({
            'name': 'Ministère Test',
            'code': 'TEST',
            'type': 'ministry',
            'active': False,
        })
        
        with self.assertRaises(ValidationError):
            self.Direction.create({
                'name': 'Direction Test',
                'code': 'DIR',
                'ministry_id': ministry.id,
            })
