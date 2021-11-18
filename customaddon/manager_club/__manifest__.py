# -*- coding: utf-8 -*-
{
    'name': "manager_club",

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
    'depends': ['base', 'badge_menu'],

    # always loaded
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/footballer_view.xml',
        'views/coach_view.xml',
        'views/team_club_view.xml',
        'views/training_center_view.xml',
        'wizard/transfer_footballer_wizard_view.xml',
        'wizard/transfer_coach_wizard_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
