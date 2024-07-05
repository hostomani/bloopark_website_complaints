# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


@tagged('-at_install', 'post_install')
class TestWebsiteComplaint(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.complaint_stage_model = cls.env['website.complaint.stage']
        cls.complaint_type_model = cls.env['website.complaint.type']
        cls.partner_model = cls.env['res.partner']
        cls.complaint_model = cls.env['website.complaint']
        cls.drop_reason_model = cls.env['website.complaint.drop.reason']
        cls.drop_wizard_model = cls.env['website.complaint.drop.wizard']

        cls.default_stage_id = cls.complaint_stage_model.search([
            ('default', '=', True)
        ], limit=1)

        cls.default_type_id = cls.complaint_type_model.search([
            ('default', '=', True)
        ], limit=1)

        cls.drop_reason = cls.drop_reason_model.search([], limit=1)
        # Create a partner
        cls.partner = cls.partner_model.create({
            'name': 'Test Partner',
            'email': 'test@domain.com',
            'phone': '+9718000092'
        })
        cls.complaint_description = '''
        Test Description
        '''

    def test_default_stage_type(self):
        complaint = self.complaint_model.create({
            'partner_id': self.partner.id,
            'type': self.default_type_id.id,
            'description': self.complaint_description
        })

        self.assertEqual(complaint.stage_id, self.default_stage_id, "Default stage is not set correctly")
        self.assertEqual(complaint.type, self.default_type_id, "Default stage is not set correctly")

    def test_contact_name_computation(self):
        complaint = self.complaint_model.create({
            'partner_id': self.partner.id,
            'type': self.default_type_id.id,
            'description': self.complaint_description
        })

        self.assertEqual(complaint.contact_name, self.partner.name, "Contact name is not computed correctly")

        complaint.partner_id = False
        complaint._compute_contact_name()
        self.assertEqual(complaint.contact_name, '', "Contact name is not empty when partner is not set")

    def test_action_drop_wizard(self):
        complaint = self.complaint_model.create({
            'partner_id': self.partner.id,
            'type': self.default_type_id.id,
            'description': self.complaint_description
        })

        action = complaint.action_drop_wizard()
        self.assertEqual(action['res_model'], 'website.complaint.drop.wizard',
                         "Action drop wizard res_model is incorrect")
        self.assertEqual(action['context']['default_complaint_id'], complaint.id,
                         "Action drop wizard context is incorrect")

    def test_action_drop(self):
        complaint = self.complaint_model.create({
            'partner_id': self.partner.id,
            'type': self.default_type_id.id,
            'description': self.complaint_description
        })
        # Create drop wizard
        drop_wizard = self.drop_wizard_model.create({
            'complaint_id': complaint.id,
            'drop_reason_id': self.drop_reason.id,
            'drop_reason_notes': 'Duplicate entry'
        })

        # Perform drop action
        complaint.action_drop(drop_wizard.drop_reason_id, drop_wizard.drop_reason_notes)

        self.assertTrue(complaint.dropped, "Complaint is not marked as dropped")
        self.assertEqual(complaint.drop_reason_id, drop_wizard.drop_reason_id, "Drop reason ID is not set correctly")
        self.assertEqual(complaint.drop_reason_notes, drop_wizard.drop_reason_notes,
                         "Drop reason notes are not set correctly")
