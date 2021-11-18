# -*- coding: utf-8 -*-
{
    'name': "Lazada Integration",

    'summary': """
        Connection Lazada With Odoo""",

    'description': """
        Lazada Integration with API by Python Http Request
    """,

    'author': "Mahacarviet",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'product', 'website_sale', 'mail', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/views.xml',
        # 'views/views.xml',
        # 'views/views.xml',
        # 'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
