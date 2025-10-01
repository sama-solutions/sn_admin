from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAgent(TransactionCase):

    def setUp(self):
        super(TestAgent, self).setUp()
        self.Ministry = self.env['sn.ministry']
        self.Direction = self.env['sn.direction']
        self.Service = self.env['sn.service']
        self.Agent = self.env['sn.agent']
        self.Employee = self.env['hr.employee']

    def test_create_agent(self):
        """Test creating an agent"""
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
        
        agent = self.Agent.create({
            'name': 'Amadou DIOP',
            'function': 'Chef de Service',
            'service_id': service.id,
        })
        
        self.assertTrue(agent)
        self.assertEqual(agent.name, 'Amadou DIOP')
        self.assertEqual(agent.service_id, service)

    def test_agent_matricule_unique(self):
        """Test that agent matricule must be unique"""
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
        
        self.Agent.create({
            'name': 'Agent 1',
            'function': 'Test',
            'matricule': 'SN-2024-001234',
            'service_id': service.id,
        })
        
        with self.assertRaises(Exception):
            self.Agent.create({
                'name': 'Agent 2',
                'function': 'Test',
                'matricule': 'SN-2024-001234',
                'service_id': service.id,
            })

    def test_agent_direction_ministry_related(self):
        """Test that direction_id and ministry_id are correctly related"""
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
        
        agent = self.Agent.create({
            'name': 'Agent Test',
            'function': 'Test',
            'service_id': service.id,
        })
        
        self.assertEqual(agent.direction_id, service.direction_id)
        self.assertEqual(agent.ministry_id, service.ministry_id)

    def test_onchange_employee_id(self):
        """Test onchange_employee_id synchronization"""
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
        
        employee = self.Employee.create({
            'name': 'Amadou DIOP',
            'work_phone': '+221338893400',
            'mobile_phone': '+221776543210',
            'work_email': 'amadou.diop@test.sn',
        })
        
        agent = self.Agent.create({
            'name': 'Agent Test',
            'function': 'Test',
            'service_id': service.id,
            'employee_id': employee.id,
        })
        
        agent._onchange_employee_id()
        self.assertEqual(agent.name, employee.name)
        self.assertEqual(agent.work_phone, employee.work_phone)
        self.assertEqual(agent.work_email, employee.work_email)

    def test_action_view_employee(self):
        """Test action_view_employee method"""
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
        
        employee = self.Employee.create({
            'name': 'Amadou DIOP',
        })
        
        agent = self.Agent.create({
            'name': 'Agent Test',
            'function': 'Test',
            'service_id': service.id,
            'employee_id': employee.id,
        })
        
        action = agent.action_view_employee()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'hr.employee')
        self.assertEqual(action['res_id'], employee.id)

    def test_name_get(self):
        """Test name_get method"""
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
        
        agent = self.Agent.create({
            'name': 'Amadou DIOP',
            'function': 'Directeur Général',
            'service_id': service.id,
        })
        
        name_get_result = agent.name_get()
        self.assertEqual(len(name_get_result), 1)
        self.assertEqual(name_get_result[0][0], agent.id)
        self.assertEqual(name_get_result[0][1], 'Amadou DIOP - Directeur Général')

    def test_constrains_work_email(self):
        """Test work_email validation"""
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
        
        with self.assertRaises(ValidationError):
            self.Agent.create({
                'name': 'Agent Test',
                'function': 'Test',
                'service_id': service.id,
                'work_email': 'invalid-email',
            })

    def test_constrains_work_phone(self):
        """Test work_phone validation"""
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
        
        with self.assertRaises(ValidationError):
            self.Agent.create({
                'name': 'Agent Test',
                'function': 'Test',
                'service_id': service.id,
                'work_phone': '123',
            })

    def test_constrains_service_active(self):
        """Test that service must be active"""
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
            'active': False,
        })
        
        with self.assertRaises(ValidationError):
            self.Agent.create({
                'name': 'Agent Test',
                'function': 'Test',
                'service_id': service.id,
            })
