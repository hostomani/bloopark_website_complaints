# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WebsiteComplaintDropReason(models.Model):
    _name = 'website.complaint.drop.reason'
    _description = 'Website Complaint Drop Reason'

    name = fields.Char(required=True)
    note_required = fields.Boolean()

