# -*- coding: utf-8 -*-
{
    'name': "sita_payment_integration",

    'summary': """
        MPGS Integration
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "SITA-EGYPT",
    'website': "https://www.sita-egypt.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'website', 'board'],

    # always loaded
    'data': [
        'views/record_rules.xml',

        'security/ir.model.access.csv',
        # 'security/sita_pay_secruity.xml',

        'data/transaction_sequence.xml',
        'views/account_manager_view.xml',
        'views/transaction_view.xml',
        'views/client_order_view.xml',
        'views/home.xml',
        'views/transaction_actions.xml',
        # 'views/dashboard.xml',
        'views/dashboard_owl.xml',
        'templates/website_view_inherit.xml',
        'reports/transaction_single_report.xml',
        'templates/footer.xml',
        'templates/header.xml',
        'templates/home_qnb.xml',
        'templates/home_nbe.xml',
        'templates/home_kashier.xml',
        'templates/home_aaib.xml',
        'templates/payment_done.xml',
        'templates/payment_pending.xml',
        'templates/payment_failed.xml',
        'templates/session_failed.xml',
        'templates/link_expire.xml',
        'templates/home_fawry.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "qweb": [
        'static/src/xml/base_templates.xml',
    ],
    "assets": {
        "web.assets_backend": [

            "sita_payment_integration/static/src/components/**/*.js",
            "sita_payment_integration/static/src/components/**/*.xml",
            'https://www.gstatic.com/charts/loader.js',
            'sita_payment_integration/static/styles/sita_pay.css'
        ]
    },

    # 'web.assets_frontend': [
    # "https://test-nbe.gateway.mastercard.com/static/checkout/checkout.min.js"

    # 'mbi/static/src/js/mbi_admission_request.js',
    # 'mbi/static/src/js/admission.js',

    # ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'images': ['static/description/icon.png'],
}
