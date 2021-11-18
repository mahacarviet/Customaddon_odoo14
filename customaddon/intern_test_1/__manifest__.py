# -*- coding: utf-8 -*-
{
    'name': "intern_test_1",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

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
    'depends': ['base', 'sale_management', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security_data.xml',
        'views/res_partner_inherit_view_form.xml',
        'views/sale_order_inherit_view_form.xml',
        'views/sale_view_inherit_view_form.xml',
        'wizard/add_discount_code_customer_wizard_view.xml',
        'views/show_up_in_my_cart_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
