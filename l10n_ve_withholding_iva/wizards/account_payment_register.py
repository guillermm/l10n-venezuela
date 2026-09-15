# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    l10n_ve_iva_wh_amount = fields.Monetary(
        string="IVA a Retener",
        currency_field="currency_id",
        compute="_compute_l10n_ve_iva_wh_amount",
        store=True,
        readonly=False,
    )
    l10n_ve_iva_wh_received_amount = fields.Monetary(
        string="IVA Retenido por el Cliente",
        currency_field="currency_id",
        default=0.0,
    )
    l10n_ve_iva_wh_voucher_number = fields.Char(
        string="N° Comprobante Recibido",
    )

    @api.depends("line_ids", "amount", "currency_id", "payment_date", "partner_id", "company_id")
    def _compute_l10n_ve_iva_wh_amount(self):
        for wizard in self:
            wizard.l10n_ve_iva_wh_amount = wizard._l10n_ve_get_iva_wh_amount()

    def _l10n_ve_get_iva_wh_amount(self):
        self.ensure_one()
        if (
            self.payment_type != "outbound"
            or self.partner_type != "supplier"
            or not self._l10n_ve_wh_edit_mode()
        ):
            return 0.0
        partner = self.partner_id.commercial_partner_id
        rate = partner.wh_iva_rate or 0.0
        if not rate:
            return 0.0
        moves = self._l10n_ve_wh_moves().filtered(
            lambda move: move.move_type in ("in_invoice", "in_refund")
        )
        company_currency = self.company_id.currency_id
        tax_total = 0.0
        for move in moves:
            sign = -1.0 if move.move_type == "in_refund" else 1.0
            tax = sum(abs(line.balance) for line in move.line_ids.filtered("tax_line_id"))
            tax_total += sign * tax
        if company_currency.compare_amounts(tax_total, 0.0) <= 0:
            return 0.0
        date = self.payment_date or fields.Date.context_today(self)
        tax_wc = company_currency._convert(tax_total, self.currency_id, self.company_id, date)
        return self.currency_id.round(tax_wc * rate / 100.0)

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        if not self._l10n_ve_wh_edit_mode():
            return payment_vals
        received = self.l10n_ve_iva_wh_received_amount
        if self.payment_type == "inbound" and self.partner_type == "customer" and received:
            account = self.company_id.wh_iva_received_account_id or self.company_id.wh_iva_account_id
            if not account:
                raise UserError(
                    _("Configure the VAT withholding account (received) in Company Settings.")
                )
            if not self.l10n_ve_iva_wh_voucher_number:
                raise UserError(_("Indicate the 14-digit received VAT withholding voucher number."))
            self._l10n_ve_append_wh_writeoff(
                payment_vals,
                received,
                account,
                _("VAT withholding received %s") % self.l10n_ve_iva_wh_voucher_number,
            )
            return payment_vals
        if self.l10n_ve_iva_wh_amount:
            account = self.company_id.wh_iva_account_id
            if not account:
                raise UserError(_("Configure the VAT Withholding Account in Company Settings."))
            partner = self.partner_id.commercial_partner_id
            if not partner.vat:
                raise UserError(_("Partner %s has no RIF; VAT withholding cannot be applied.") % partner.display_name)
            self._l10n_ve_append_wh_writeoff(
                payment_vals,
                self.l10n_ve_iva_wh_amount,
                account,
                _("VAT withholding %s%% %s") % (partner.wh_iva_rate or 0, partner.name),
            )
        return payment_vals

    def _create_payments(self):
        payments = super()._create_payments()
        if (
            self._l10n_ve_wh_edit_mode()
            and self.payment_type == "outbound"
            and self.l10n_ve_iva_wh_amount
        ):
            self._l10n_ve_create_iva_wh_voucher(payments)
        return payments

    def _l10n_ve_create_iva_wh_voucher(self, payments):
        self.ensure_one()
        moves = self._l10n_ve_wh_moves().filtered(
            lambda move: move.move_type in ("in_invoice", "in_refund") and not move.wh_iva_id
        )
        if not moves:
            return
        voucher = self.env["account.wh.iva"].create({
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "currency_id": self.company_id.currency_id.id,
            "type": moves[:1].move_type,
            "date": self.payment_date,
            "journal_id": self.company_id.wh_iva_journal_id.id,
            "payment_id": payments[:1].id,
            "line_ids": [(0, 0, {"move_id": move.id}) for move in moves],
        })
        voucher.line_ids.action_recompute_from_move()
        voucher.action_confirm()
        voucher.action_done()
        moves.write({"wh_iva_id": voucher.id})
        moves._l10n_ve_refresh_wh_state()
        return voucher
