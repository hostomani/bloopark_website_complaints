# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class WebsiteComplaintDropWizard(models.TransientModel):
    _name = 'website.complaint.drop.wizard'
    _description = 'Website Complaint Drop Wizard'

    complaint_id = fields.Many2one('website.complaint')
    drop_reason_id = fields.Many2one('website.complaint.drop.reason')
    note_required = fields.Boolean(related='drop_reason_id.note_required')
    drop_reason_notes = fields.Text()

    @api.onchange('drop_reason')
    def onchange_drop_reason(self):
        self.ensure_one()
        drop_reason = self.env['website.complaint.drop.reason'].search([
            ('id', '=', int(self.drop_reason))
        ])
        if drop_reason:
            self.note_required = drop_reason.note_required
        self.note_required = False

    def create(self, vals_list):
        recs = super(WebsiteComplaintDropWizard, self).create(vals_list)
        for rec in recs:
            rec.complaint_id.action_drop(rec.drop_reason_id, rec.drop_reason_notes)
        return recs
