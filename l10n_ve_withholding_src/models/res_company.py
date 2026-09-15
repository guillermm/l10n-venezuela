# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    wh_src_journal_id = fields.Many2one("account.journal", string="SRC Withholding Journal")
    wh_src_rate = fields.Float(
        string="Default SRC Rate (%)",
        default=5.0,
        help="Legal default for public-sector contracts (Ley de Contrataciones Públicas).",
    )
    wh_src_account_id = fields.Many2one(
        comodel_name="account.account",
        string="SRC Withholding Account",
        check_company=True,
        help="7-digit VEN-NIF: 2104004 (Otros Impuestos y Contribuciones por Pagar).",
    )
