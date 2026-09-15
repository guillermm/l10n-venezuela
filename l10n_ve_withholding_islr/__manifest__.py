# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Management Withholding ISLR Venezuelan Laws",
    "version": "17.0.1.3.0",
    "category": "Localization",
    "author": "Vauxoo",
    "maintainer": "Guillermo Montoya",
    "maintainers": [
        "guillermm",
    ],
    "website": "https://www.odoo.com",
    "license": "AGPL-3",
    "depends": [
        "account",
        "product",
        "l10n_ve_fiscal_requirements",
        "l10n_ve_withholding",
    ],
        "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/islr_wh_concept_data.xml",
        "reports/report_wh_islr.xml",
        "wizards/generate_xml_views.xml",
        "views/islr_wh_concept_views.xml",
        "views/account_wh_islr_doc_views.xml",
        "views/account_move_views.xml",
        "views/account_payment_register_views.xml",
        "views/res_partner_views.xml",
        "views/product_views.xml",
        "views/res_company_views.xml",
        "views/menu_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "application": False,
}
