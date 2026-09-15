# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    l10n_ve_muni_wh_amount = fields.Monetary(
        string="Retención Municipal",
        currency_field="currency_id",
        compute="_compute_l10n_ve_muni_wh_amount",
        store=True,
        readonly=False,
    )

    @api.depends("line_ids", "amount", "currency_id", "payment_date", "partner_id")
    def _compute_l10n_ve_muni_wh_amount(self):
        for wizard in self:
            wizard.l10n_ve_muni_wh_amount = wizard._l10n_ve_get_muni_wh_amount()

    def _l10n_ve_get_muni_wh_amount(self):
        self.ensure_one()
        if (
            self.payment_type != "outbound"
            or self.partner_type != "supplier"
            or not self._l10n_ve_wh_edit_mode()
        ):
            return 0.0
        rate = self.partner_id.commercial_partner_id.wh_muni_rate or 0.0
        if not rate:
            return 0.0
        date = self.payment_date or fields.Date.context_today(self)
        base = 0.0
        for move in self._l10n_ve_wh_moves().filtered(
            lambda rec: rec.move_type in ("in_invoice", "in_refund") and not rec.wh_muni_id
        ):
            sign = 1 if move.move_type == "in_invoice" else -1
            amount = move._l10n_ve_taxable_untaxed()
            if move.currency_id != self.currency_id:
                amount = move.currency_id._convert(amount, self.currency_id, self.company_id, date)
            base += sign * amount
        if base <= 0:
            return 0.0
        return self.currency_id.round(base * rate / 100.0)

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        if self._l10n_ve_wh_edit_mode() and self.l10n_ve_muni_wh_amount:
            account = self.company_id.wh_muni_account_id
            if not account:
                raise UserError(_("Configure the municipal withholding account in Company Settings."))
            self._l10n_ve_append_wh_writeoff(
                payment_vals,
                self.l10n_ve_muni_wh_amount,
                account,
                _("Municipal withholding %s%%") % (self.partner_id.wh_muni_rate or 0),
            )
        return payment_vals

    def _create_payments(self):
        payments = super()._create_payments()
        if self._l10n_ve_wh_edit_mode() and self.payment_type == "outbound" and self.l10n_ve_muni_wh_amount:
            self._l10n_ve_create_muni_voucher(payments)
        return payments

    def _l10n_ve_create_muni_voucher(self, payments):
        self.ensure_one()
        moves = self._l10n_ve_wh_moves().filtered(
            lambda move: move.move_type in ("in_invoice", "in_refund") and not move.wh_muni_id
        )
        if not moves:
            return
        for move in moves:
            voucher = self.env["account.wh.muni"].create({
                "partner_id": self.partner_id.id,
                "company_id": self.company_id.id,
                "move_id": move.id,
                "date": self.payment_date,
                "wh_rate": self.partner_id.wh_muni_rate,
                "amount_base": move._l10n_ve_taxable_untaxed(),
                "journal_id": self.company_id.wh_muni_journal_id.id,
                "payment_id": payments[:1].id,
            })
            voucher.action_confirm()
        return True
