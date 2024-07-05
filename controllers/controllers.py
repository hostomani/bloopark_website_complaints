# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID, _, _lt
from odoo.http import request, route, Response
from werkzeug.exceptions import BadRequest

from odoo.addons.website.controllers.form import WebsiteForm
import logging
import json
_logger = logging.getLogger(__name__)


class WebsiteSaleForm(WebsiteForm):

    @http.route('/website/form/website.complaint', type='http', auth="public", methods=['POST'], website=True)
    def website_form_complaints(self, **kwargs):
        required_fields = ['name', 'email', 'phone', 'type', 'description']
        if not all([kwargs.get(field) for field in required_fields]):
            raise BadRequest('Missing required fields!')

        complaint_types = request.env['website.complaint.type'].with_user(SUPERUSER_ID)
        compliant_type = complaint_types.search([
            ('id', '=', int(kwargs.get('type')))
        ])
        if not compliant_type:
            raise BadRequest('Invalid complaint type!')

        partners = request.env['res.partner'].with_user(SUPERUSER_ID)
        partner = partners.search([
            ('email', '=', kwargs.get('email'))
        ])
        if not partner:
            partner = partners.create({
                'name': kwargs.get('name'),
                'email': kwargs.get('email'),
                'phone': kwargs.get('phone')
            })

        complaints = request.env['website.complaint'].with_user(SUPERUSER_ID)
        complaint = complaints.create({
            'contact_name': kwargs.get('name'),
            'partner_id': partner.id,
            'type': compliant_type.id,
        })
        return json.dumps({'id': complaint.id})



