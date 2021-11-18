# -*- coding: utf-8 -*-

{
    'name': "Advanced Portal User",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Magenest",
    'website': "http://www.magenest.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'hr_attendance', 'hr_holidays', 'hr_payroll', 'hr_contract', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/css_loader.xml',
        'views/attendance_template.xml',
        'views/leave_template.xml',
        'views/over_time_template.xml',
        'views/payroll_template.xml',
        'views/order_template.xml',
        'views/res_config_settings.xml',
        'views/attendance_views_inherit.xml',
        'views/portal_user_menu.xml',
        'views/portal_user_nav_menu.xml',
        'views/over_time_views.xml',
        'views/portal_employee.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
