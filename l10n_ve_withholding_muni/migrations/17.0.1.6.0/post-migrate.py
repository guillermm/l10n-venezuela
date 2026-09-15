# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["l10n.ve.muni.activity"]._l10n_ve_bind_activities_to_territorial()
    env["res.partner"]._l10n_ve_bind_wh_municipality_to_territorial()
