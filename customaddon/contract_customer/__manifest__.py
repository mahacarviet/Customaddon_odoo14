# -*- coding: utf-8 -*-
{
    'name': "Management Contract Customer",

    'summary': """
        This Module will help users manage contracts for each order in Module Sales easily.""",

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
    'depends': ['base', 'sale_management', 'product', 'stock', 'mail', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/cron_job_payment.xml',
        # 'wizard/create_contract_wizard_view.xml',
        'views/res_partner_inherit_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/contract_customer_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
