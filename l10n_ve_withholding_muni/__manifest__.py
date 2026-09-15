# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Local Withholding Venezuelan Laws (Municipal Withholdings)",
    "version": "17.0.1.8.0",
    "category": "Localization",
    "author": "Vauxoo",
    "maintainer": "Guillermo Montoya",
    "maintainers": [
        "guillermm",
    ],
    "website": "http://vauxoo.com",
    "license": "AGPL-3",
    "depends": [
        "account",
        "l10n_ve_fiscal_requirements",
        "l10n_ve_withholding",
        "territorial_pd",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/municipality_views.xml",
        "views/wh_muni_views.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/account_payment_register_views.xml",
        "views/menu_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "application": False,
}
