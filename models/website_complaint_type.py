# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class WebsiteComplaintType(models.Model):
    _name = 'website.complaint.type'
    _description = 'Website Complaint Type'

    name = fields.Char(required=True)
    default = fields.Boolean(default=False)
    priority = fields.Selection(
        AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=AVAILABLE_PRIORITIES[0][0])

    @api.model_create_multi
    def create(self, vals_list):
        # Check if multiple values has default checked, we are checking this early on to not make database queries
        values_with_default_checked = list(filter(lambda val: val.get('default'), vals_list))
        if len(values_with_default_checked) > 1:
            raise exceptions.ValidationError(_('Only one default type is allowed'))

        # In case only one value has default checked, check if there is a default type
        default_type = self.search([
            ('default', '=', True)
        ], limit=1)
        if default_type and values_with_default_checked:
            raise exceptions.ValidationError(_('Only one default type is allowed'))

        return super(WebsiteComplaintType, self).create(vals_list)

    def unlink(self):
        default_included = self.filtered(lambda rec: rec.default)
        if default_included:
            raise exceptions.ValidationError(_('Default record can not be deleted!'))
        return super(WebsiteComplaintType, self).unlink()

    def write(self, vals):
        # Check if multiple values has default checked, we are checking this early on to not make database queries
        values_with_default_checked = list(filter(lambda value: vals.get('default'), vals))
        if len(values_with_default_checked) > 1:
            raise exceptions.ValidationError(_('Only one default type is allowed'))

        # In case only one value has default checked, check if there is a default type
        default_type = self.search([
            ('default', '=', True)
        ], limit=1)
        if default_type and values_with_default_checked:
            raise exceptions.ValidationError(_('Only one default type is allowed'))

        return super(WebsiteComplaintType, self).write(vals)

    def set_default(self):
        self.ensure_one()
        recs = self.search([])
        recs.write({
            'default': False
        })
        self.default = True

