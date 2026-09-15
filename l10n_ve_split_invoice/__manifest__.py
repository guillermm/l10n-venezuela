# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Split Invoices for Venezuela",
    "version": "17.0.1.1.0",
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
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
