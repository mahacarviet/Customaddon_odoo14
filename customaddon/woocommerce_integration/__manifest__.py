# -*- coding: utf-8 -*-
{
    'name': "WooCommerce Integration Odoo",
    'summary': """Connection WooCommerce With Odoo""",
    'sequence': 15,
    'description': """
        Following are the steps to use this module effectively:
        1) Put in the KEY and SECRET in the connection menu.
        2) Click Sync Button on the list.
        3) Orders, Customers and Products will be Imported from WooCommerce to Odoo.
        Data will be displayed on the WooCommerce Connector App as well as the odoo modules.
        
        More updates will be pushed frequently. Contributors are invited and appreciated.
        This is a free module and for more information contact on WhatsApp +923340239555.
    """,
    'author': "Magenest",
    'website': "https://magenest.com/en/",
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'product', 'website_sale', 'mail', 'stock'],
    'images': ['static/description/banner.png'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/cron_job_woocommerce.xml',
        'views/woocommerce_seller_view.xml',
        'views/woocommerce_category_view.xml',
        'views/product_template_inherit_view.xml',
        'views/sale_order_inherit_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
