# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    wh_muni_journal_id = fields.Many2one("account.journal", string="Municipal Withholding Journal")
    wh_muni_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Municipal Withholding Account",
        check_company=True,
        help="7-digit VEN-NIF: 2104003 (Impuesto Municipal por Pagar).",
    )
