# -*- coding: utf-8 -*-
{
    'name': "Quản lý trường học 1",

    'summary': """
        Module quản lý trường học.""",

    'description': """
        Module này sẽ giúp cho nhà trường quản lý được các hoạt động của trường một cách thuận tiện và dễ dàng hơn.
    """,

    'author': "Bui Quoc Viet",
    'website': "https://github.com/mahacarviet",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/phan_chia_quyen.xml',
        'security/ir.model.access.csv',
        'views/ly_do_tu_choi.xml',
        # 'views/templates.xml',
        'views/main_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
