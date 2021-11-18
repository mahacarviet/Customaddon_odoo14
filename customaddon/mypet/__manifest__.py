# -*- coding: utf-8 -*-
{
    'name': "My pet - minhng.info",
    'summary': """My pet model""",
    'description': """Managing pet information""",
    'author': "minhng.info",
    'website': "https://minhng.info",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/my_pet_views.xml',
        'wizard/batch_update.xml',        
        'views/res_config_settings_views.xml',
    ],
    'qweb': [
        #'static/src/xml/*.xml',
        'static/src/xml/btn_tree_multi_update.xml', # <-- khai bao thua ke qweb vua hien thuc
    ],
    'installable': True,
    'application': True,
}
