# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Shopify App',
    'version' : '1.1',
    'summary': 'Shopify App',
    'sequence': 5,
    'description': """
    """,
    'category': '',
    'website': '',
    'images' : [''],
    'depends' : ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/plan_data.xml',
        'views/shopify_controller.xml',
        'views/shopify_store_views.xml',
        # 'views/xero_account_views.xml',
        'views/shopify_xero_plans_views.xml',
        'views/shopify_xero_logs_views.xml',
        'views/res_config_settings_views.xml',
        'data/shopify_xero_cron.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'css': ['static/src/css/shopify_app.css'],
    'installable': True,
    'application': True,
    'auto_install': False,

}
