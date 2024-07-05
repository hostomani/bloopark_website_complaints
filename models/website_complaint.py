# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class WebsiteComplaint(models.Model):
    _name = 'website.complaint'
    _description = 'Website Complaint'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_stage_id(self):
        default_stage = self.env['website.complaint.stage'].search([
            ('default', '=', True)
        ], limit=1).id
        return default_stage

    @api.model
    def _get_default_type_id(self):
        default_type = self.env['website.complaint.type'].search([
            ('default', '=', True)
        ], limit=1).id
        return default_type

    name = fields.Char(compute='_compute_complaint_name')
    contact_name = fields.Char(compute='_compute_contact_name')
    partner_id = fields.Many2one('res.partner')
    user_id = fields.Many2one('res.users')
    
    stage_id = fields.Many2one(
        'website.complaint.stage', ondelete='restrict', default=_get_default_stage_id,
        group_expand='_read_group_stage_ids', tracking=True, copy=False)

    # Pipeline management
    priority = fields.Selection(related='type.priority')

    type = fields.Many2one('website.complaint.type', ondelete='restrict', default=_get_default_type_id)
    drop_reason_id = fields.Many2one('website.complaint.drop.reason')
    drop_reason_notes = fields.Text()
    dropped = fields.Boolean(default=False)
    solved = fields.Boolean(default=False)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    description = fields.Text()

    action_plan = fields.Text()

    @api.depends('partner_id')
    def _compute_complaint_name(self):
        for complaint in self:
            if not complaint.name and complaint.partner_id and complaint.partner_id.name:
                complaint.name = _("%s's complaint") % complaint.partner_id.name

    @api.depends('partner_id')
    def _compute_contact_name(self):
        """ compute the new values when partner_id has changed """
        for complaint in self:
            complaint.update(complaint.prepare_contact_name_from_partner())

    def prepare_contact_name_from_partner(self):
        contact_name = '' if self.partner_id.is_company or not self.partner_id else self.partner_id.name
        return {'contact_name': contact_name if not self.contact_name else ''}

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Always display all stages """
        return stages.search([], order=order)

    def action_drop_wizard(self):
        self.ensure_one()
        return {
            'name': _("Drop complaint"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_ref': 'view_website_complaint_drop_wizard_form',
            'res_model': 'website.complaint.drop.wizard',
            'context': {
                'default_complaint_id': self.id
            },
            'target': 'new',
        }

    def action_drop(self, drop_reason_id, drop_reason_notes):
        for rec in self:
            rec.write({
                'dropped': True,
                'drop_reason_id': drop_reason_id.id,
                'drop_reason_notes': drop_reason_notes
            })
            # Send email notification
            template = self.env.ref('bloopark_website_complaints.email_template_complaint_closed_notification')
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_solve(self):
        for rec in self:
            rec.solved = True
            # Send email notification
            template = self.env.ref('bloopark_website_complaints.email_template_complaint_closed_notification')
            if template:
                template.send_mail(rec.id, force_send=True)

    @api.model_create_multi
    def create(self, vals_list):
        self.get_user_with_least_complaints()
        complaints = super(WebsiteComplaint, self).create(vals_list)
        for complaint in complaints:
            complaint.assign_user()
            complaint.message_subscribe(partner_ids=[complaint.partner_id.id])
            # Send email notification
            template = self.env.ref('bloopark_website_complaints.email_template_complaint_registered_notification')
            if template:
                template.send_mail(complaint.id, force_send=True)
        return complaints

    @api.model
    def get_user_with_least_complaints(self):
        # Get the group
        group = self.env.ref('base.group_user')
        if not group:
            return None

        # Get users from the group
        user_ids = group.users.ids

        if not user_ids:
            return None

        # Group complaints by user in order to find user with
        # least complaints to maintain equal complaint distribution
        # e.g  [{'user_id': (6, 'Marc Demo'), 'user_id_count': 1, '__domain': [('user_id', '!=', False)]}]
        # Group complaints by user_id and filter by users in the group
        grouped_complaints = self.env['website.complaint'].read_group(
            domain=[('user_id', 'in', user_ids)],
            fields=['user_id'],
            groupby=['user_id']
        )
        _logger.info(f'====================== {grouped_complaints}')
        if not grouped_complaints:
            return user_ids[0]

        grouped_complaints_user_ids = list(map(lambda x: x.get('user_id')[0], grouped_complaints))

        for id in user_ids:
            if id not in grouped_complaints_user_ids:
                return id

        min_complaint_user = min(grouped_complaints, key=lambda x: x['user_id_count'])
        return min_complaint_user.get('user_id')[0]

    def assign_user(self):
        for rec in self:
            rec.user_id = self.get_user_with_least_complaints()
            rec.message_subscribe(partner_ids=[rec.user_id.partner_id.id])

