# -*- coding: utf-8 -*-
{
    'name': "Odoo Hubspot Connector",
    'summary': """
            Odoo Hubspot Connector provides the opportunity to import contacts and companies from Hubspot to ODOO.
            """,
    'description': """
       Odoo is a fully integrated suite of business modules that encompass the traditional ERP functionality.
        Odoo Hubspot Connector provides the opportunity to import contacts and companies from Hubspot to ODOO.
    """,
    'author': "Techloyce",
    'website': "http://www.techloyce.com",
    'category': 'sale',
    'price': 299,
    "license": "OPL-1",
    'currency': 'USD',
    'version': '13.0.0.2.0',
    'depends': ['base', 'crm', 'helpdesk', 'sale_management'],
    'images': [
        'static/description/banner.gif',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hubspotwizard.xml',
        'views/views.xml',
        # 'views/companyone2manymodels.xml',
        # 'views/dealone2manymodels.xml',
        # 'views/ticketone2manymodels.xml',
        # 'views/contactone2manymodels.xml',
        'views/logs.xml'
    ],
}
