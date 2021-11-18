# -*- coding: utf-8 -*-
{
    'name': "advanced_quotation_approval",

    'summary': """Quotation approve by sales,accountant, CEO before sent to customer""",

    'description': """
        Quotation approve by sales,accountant, CEO before sent to customer
    """,

    'author': "Magenest",
    'website': "https://magenest.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/res_group_data.xml',
        'views/sale_order_view.xml',
        'views/user_need_approve_view.xml',
    ],
}
