# -*- coding: utf-8 -*-
{
    'name': "Shopify Odoo App",

    'summary': """
        This module will help users to manage shop in Shopify by Odoo""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'sale_management', 'product', 'stock', 'account', 'website_sale'],

    # always loaded
    'data': [
        'security/shopify_security.xml',
        'security/ir.model.access.csv',
        'data/cron_job_shopify.xml',
        'views/s_app_view.xml',
        'views/s_shop_view.xml',
        'views/s_sp_app_view.xml',
        'views/s_discount_view.xml',
        'views/product_template_inherit_view.xml',
        'views/account_move_inherit_view.xml',
        'views/s_fetch_view.xml',
        'views/s_fetch_product_view.xml',
        'views/menu_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
