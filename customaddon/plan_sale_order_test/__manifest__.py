# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Plan Sale Order',
    'version': '0.1',
    'category': 'Uncategorized',
    'summary': """
        Create and validate plan of sale orders
    """,
    'description': """
        Create and validate plan of sale orders
    """,

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'mail', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_data.xml',
        'wizard/create_plan_wizard_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/plan_sale_order_view.xml',
    ],
    'demo': [
    ],
    'application': True,
    'installable': True,
}
