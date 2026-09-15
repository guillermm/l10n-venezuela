# Copyright 2023 Luis Pinzón
# Copyright 2026 Anderson Armeya
# Copyright 2026 andyengit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Currency Rate Provider BCV",
    "summary": "OCA version for BCV scrapping rates",
    "version": "17.0.1.1.3",
    "development_status": "Beta",
    "category": "Financial Management/Configuration",
    "website": "https://github.com/OCA/l10n-venezuela",
    "author": "Luis Pinzón, Anderson Armeya, andyengit, "
    "Odoo Community Association (OCA)",
    "maintainers": [
        "lapinzon",
        "andyengit",
        "guillermm",
    ],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "currency_rate_update",
    ],
    "data": [
        "views/views.xml",
    ],
}
