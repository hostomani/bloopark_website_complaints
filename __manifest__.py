# -*- coding: utf-8 -*-
{
    'name': "bloopark_website_complaints",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'website',
        'mail',
        'l10n_din5008'
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        # Website Data
        'data/website_data.xml',

        # Website Complaint Data
        'data/website_complaint.xml',
        'data/website_complaint_stage.xml',
        'data/website_complaint_type.xml',

        # Website Complaint Views
        'views/website_complaint.xml',
        'views/website_complaint_drop_reason.xml',
        'views/website_complaint_drop_wizard.xml',
        'views/website_complaint_stage.xml',
        'views/website_complaint_type.xml',

        # Website Complaint Actions
        'actions/website_complaint.xml',
        'actions/website_complaint_drop_reason.xml',
        'actions/website_complaint_stage.xml',
        'actions/website_complaint_type.xml',

        'reports/action_plan_report_template.xml',
        'reports/action_plan_report_action.xml',
        # Website Complaint Menu
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True
}

