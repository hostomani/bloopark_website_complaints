# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class WebsiteComplaintStage(models.Model):
    _name = 'website.complaint.stage'
    _description = 'Website Complaint Stage'

    name = fields.Char(required=True)
    description = fields.Char()
    default = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        # Check if multiple values has default checked, we are checking this early on to not make database queries
        values_with_default_checked = list(filter(lambda val: val.get('default'), vals_list))
        if len(values_with_default_checked) > 1:
            raise exceptions.ValidationError(_('Only one default stage is allowed'))

        # In case only one value has default checked, check if there is a default stage
        default_stage = self.search([
            ('default', '=', True)
        ], limit=1)
        if default_stage and values_with_default_checked:
            raise exceptions.ValidationError(_('Only one default stage is allowed'))

        return super(WebsiteComplaintStage, self).create(vals_list)

    def unlink(self):
        default_included = self.filtered(lambda rec: rec.default)
        if default_included:
            raise exceptions.ValidationError(_('Default record can not be deleted!'))
        return super(WebsiteComplaintStage, self).unlink()

    def write(self, vals):
        # Check if multiple values has default checked, we are checking this early on to not make database queries
        values_with_default_checked = list(filter(lambda value: vals.get('default'), vals))
        if len(values_with_default_checked) > 1:
            raise exceptions.ValidationError(_('Only one default stage is allowed'))

        # In case only one value has default checked, check if there is a default stage
        default_stage = self.search([
            ('default', '=', True)
        ], limit=1)
        if default_stage and values_with_default_checked:
            raise exceptions.ValidationError(_('Only one default stage is allowed'))
        
        return super(WebsiteComplaintStage, self).write(vals)

    def set_default(self):
        self.ensure_one()
        recs = self.search([])
        recs.write({
            'default': False
        })
        self.default = True

