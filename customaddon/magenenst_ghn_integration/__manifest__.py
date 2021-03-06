{
    'name': "GHN ",
    'summary': """Integration App In Odoo With Delivery In Company GHN""",
    'description': """ GHN API """,
    'author': "Magenest",
    'website': "http://magenest.com/",
    'sequence': '10',
    'images': ['static/description/ghn_background.png'],
    'category': 'Extra Tools',
    'version': '1.0',
    'depends': ['base', 'contacts', 'sale', 'delivery', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'data/ghn_cron_job.xml',
        'views/res_partner.xml',
        'views/delivery_carrier.xml',
        'views/res_company.xml',
        'views/sale_order_view.xml',
        'views/res_state_district_view.xml',
        'views/res_ward_view.xml',
        'views/stock_picking.xml',
        'views/res_config_settings_view.xml',
        'views/stock_warehouse.xml',
        'views/res_country_state.xml',
        'views/lunch_call_api.xml',
        'wizard/choose_delivery_carrier_view.xml',

    ],
    'demo': [
        'demo/demo_data.xml',
    ],         # only loaded in demonstration mode
    # 'css': ['static/src/css/crm.css'],
    # 'js': ['static/src/js/patient_ajax_2.js'],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}