# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sendo Integration',
    'version': '1.1',
    'summary': 'Connection Sendo With Odoo',
    'sequence': 10,
    'description': """
    Sendo Integration with API by Python Http Request
    """,
    'category': 'Uncategorized',
    'website': '#',
    'depends': ['base', 'sale_management', 'product', 'website_sale', 'mail', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_job_sendo.xml',
        'views/sendo_seller_product_view.xml',
        'views/sendo_seller_view.xml',
        'wizard/sendo_cancel_reason_wizard_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/product_template_inherit.xml',
        'views/product_product_inherit_view.xml',
        'views/res_partner_inherit_view_form.xml',
        'views/sendo_cancel_reason_view.xml',
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
