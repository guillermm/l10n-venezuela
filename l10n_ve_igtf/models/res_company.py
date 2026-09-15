# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ve_igtf_rate = fields.Float(string="IGTF Rate (%)", default=3.0)
    l10n_ve_igtf_expense_account_id = fields.Many2one(
        comodel_name="account.account",
        string="IGTF Expense Account",
        check_company=True,
        help="7-digit VEN-NIF: 6601001 (Gasto por IGTF). Fallback: 9114001.",
    )
    l10n_ve_igtf_perception_account_id = fields.Many2one(
        comodel_name="account.account",
        string="IGTF Perception Account",
        check_company=True,
        help="7-digit VEN-NIF: 2103004 (IGTF Percibido por Enterar).",
    )
    l10n_ve_igtf_perception_agent = fields.Boolean(string="IGTF Perception Agent")
    l10n_ve_igtf_perception_agent_date = fields.Date(string="IGTF Agent Since")
