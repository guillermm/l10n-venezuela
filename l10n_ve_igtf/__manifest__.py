# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Venezuela IGTF",
    "summary": "IGTF on vendor bills and payments in foreign currency / crypto journals (Odoo 17)",
    "version": "17.0.1.2.0",
    "category": "Localization",
    "author": "Guillermo Montoya",
    "maintainer": "Guillermo Montoya",
    "maintainers": [
        "guillermm",
    ],
    "website": "https://github.com/OCA/l10n-venezuela",
    "license": "AGPL-3",
    "depends": [
        "account",
        "l10n_ve_fiscal_requirements",
        "l10n_ve_withholding",
    ],
    "data": [
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "views/account_payment_views.xml",
        "views/res_company_views.xml",
        "views/account_payment_register_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "application": False,
}
