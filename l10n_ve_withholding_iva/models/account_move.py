# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    wh_iva_id = fields.Many2one(
        comodel_name="account.wh.iva",
        string="VAT Withholding Voucher",
        copy=False,
        readonly=True,
    )

    def action_generate_wh_iva(self):
        self.ensure_one()
        if self.wh_iva_id:
            raise UserError(_("VAT Withholding Voucher already exists for this move."))
        if self.move_type not in ["out_invoice", "in_invoice", "out_refund", "in_refund"]:
            raise UserError(_("Only invoices and refunds can generate VAT Withholdings."))
        if self.state != "posted":
            raise UserError(_("Post the invoice before generating the VAT withholding."))

        voucher = self.env["account.wh.iva"].create({
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "currency_id": self.company_id.currency_id.id,
            "type": self.move_type,
            "date": self.invoice_date or fields.Date.context_today(self),
            "journal_id": self.company_id.wh_iva_journal_id.id,
            "line_ids": [(0, 0, {"move_id": self.id})],
        })
        voucher.line_ids.action_recompute_from_move()
        self.wh_iva_id = voucher.id
        self._l10n_ve_refresh_wh_state()
        return {
            "name": _("VAT Withholding Voucher"),
            "type": "ir.actions.act_window",
            "res_model": "account.wh.iva",
            "res_id": voucher.id,
            "view_mode": "form",
            "target": "current",
        }
