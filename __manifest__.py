# -*- coding: utf-8 -*-
{
    'name': "OrderLine PriceList",

    'summary': "This module facilitates the selection of pricelists and ensures the application of the appropriate pricelists to products in sales orders.",

    'description': """
This module facilitates the selection of pricelists and ensures the application of the appropriate pricelists to products in sales orders.
    """,

    'author': "NIZAMUDHEEN MJ",
    'website': "https://github.com/am-niz",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/price_list_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    "application": True,
    "sequence": -92,
}

