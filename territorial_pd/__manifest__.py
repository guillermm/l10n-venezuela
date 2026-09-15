# Copyright 2020-2025 SINAPSYS GLOBAL SA, MASTERCORE SAS
# Copyright 2026 Guillermo Montoya
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Venezuelan Municipalities and Parishes",
    "summary": "Political division of Venezuela: states, municipalities and parishes",
    "version": "17.0.1.2.0",
    "category": "Localization",
    "author": "SINAPSYS GLOBAL SA, MASTERCORE SAS, Guillermo Montoya",
    "maintainer": "Guillermo Montoya",
    "maintainers": [
        "guillermm",
        "odoo-mastercore",
    ],
    "website": "https://github.com/odoo-mastercore/odoo-venezuela",
    "license": "LGPL-3",
    "depends": [
        "base",
        "contacts",
    ],
    "pre_init_hook": "pre_init_hook",
    "data": [
        "security/ir.model.access.csv",
        "data/res.country.csv",
        "data/res.country.state.csv",
        "data/res.country.state.municipality.csv",
        "data/res.country.state.municipality.parish.csv",
        "views/res_country_state_municipality_views.xml",
        "views/res_country_state_municipality_parish_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
