# -*- coding: utf-8 -*-
{
    'name': "marcos_branding",

    'summary': """
        Add marcos branding""",

    'description': """
        TODO
    """,

    'author': "Marcos Organizador de Negocios SRL",
    'website': "http://marcos.do",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'disable_openerp_online'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'templates.xml',
        'templates.xml',
        'models_view.xml'
    ],
    'qweb': ['static/src/xml/marcos_branding.xml'],
    'demo': [

    ],
}