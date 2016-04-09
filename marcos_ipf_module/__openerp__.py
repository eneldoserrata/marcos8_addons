# -*- coding: utf-8 -*-
{
    'name': "marcos_ipf_module",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'account', "mail", "auth_signup"],

    # always loaded
    'data': [
        'security/marcos_ipf_module.xml',
        'security/ir.model.access.csv',
        'templates.xml',
        'models_view.xml',
        'wizard/book_generator_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}