# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Tiki Integration',
    'version': '1.1',
    'summary': '',
    'sequence': 10,
    'description': """
    Tiki Integration with API by Python Http Request
    """,
    'category': 'Uncategorized',
    'website': '#',
    'depends': ['base', 'sale_management', 'product', 'website_sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_job_tiki.xml',
        'wizard/connect_to_shop_wizard.xml',
        'views/product_template_inherit.xml',
        'views/tiki_seller_view.xml',
        # 'views/assets_backend.xml',
    ],
    'demo': [
    ],
     #  'qweb': [
     #      'static/src/xml/template.xml',
     # ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
