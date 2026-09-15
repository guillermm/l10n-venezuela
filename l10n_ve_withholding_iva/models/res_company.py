# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    wh_iva_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Default VAT Withholding Journal",
        check_company=True,
        help="Journal used to generate VAT withholding entries",
    )
    wh_iva_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Default VAT Withholding Account",
        check_company=True,
        help="7-digit VEN-NIF: 2103003 (Retenciones de IVA por Enterar). "
        "Fallback on the current official chart: 2172004.",
    )
    wh_iva_received_account_id = fields.Many2one(
        comodel_name="account.account",
        string="VAT Withholding Received Account",
        check_company=True,
        help="7-digit VEN-NIF: 1103002 (Retenciones de IVA Recibidas). "
        "Fallback on the current official chart: 1151003.",
    )
