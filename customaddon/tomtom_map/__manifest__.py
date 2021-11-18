# -*- coding: utf-8 -*-
{
    'name': "Tomtom Map Integration Odoo",

    'summary': """
        Calculate Route in Odoo""",
    'sequence': 10,
    'description': """
        Tomtom Map with API by Python Http Request
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'account', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/calculate_route_wizard_view.xml',
        'views/res_partner_inherit_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
