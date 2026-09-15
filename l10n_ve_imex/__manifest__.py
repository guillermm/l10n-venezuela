# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Imex (Import and Export Customs Declaration)",
    "version": "17.0.1.1.0",
    "category": "Localization",
    "author": "Tecvemar/Vauxoo",
    "maintainer": "Guillermo Montoya",
    "maintainers": [
        "guillermm",
    ],
    "website": "http://vauxoo.com",
    "license": "AGPL-3",
    "depends": [
        "account",
        "l10n_ve_fiscal_requirements",
        "l10n_ve_fiscal_book",
        "l10n_ve_withholding_iva",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/imex_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
