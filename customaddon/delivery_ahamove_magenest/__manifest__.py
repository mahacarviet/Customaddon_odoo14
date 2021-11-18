{
    "name": "AhaMove Express",
    "summary": """Integration App In Odoo With Delivery In Company AhaMove"
               Developed by Magenest JSC """,
    "version": "13.0.1.0.0",
    "category": "Extra Tools",
    "website": "http://www.magenest.com",
    "author": "Magenest",
    "license": "OPL-1",
    "data": [
        'security/ir.model.access.csv',
        "views/config_delivery_carrier_form.xml",
        "views/ahamove_seller_view.xml",
    ],
    "depends": [
        "base",
        "web",
        'hr',
        'delivery',
    ],
    'images': ['static/images/icon.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'images': ['static/description/ahamove_background.png'],

}
