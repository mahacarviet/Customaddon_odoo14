# -*- coding: utf-8 -*-
{
    'name': "Wix Integration",

    'summary': """
        Sync Database From Wix To Odoo 
    """,
    'sequence': 10,
    'description': """
        Sync Database From Wix To Odoo 
    """,

    'author': "iamkien",
    'website': "https://magenest.com/vi/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wix_product_view.xml',
        'views/infor_seller_wix_view.xml',
        'views/infor_app_wix_view.xml',
        'views/infor_business_wix_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
