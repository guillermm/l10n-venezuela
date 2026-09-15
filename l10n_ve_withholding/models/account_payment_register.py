# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _l10n_ve_wh_edit_mode(self):
        self.ensure_one()
        if not self.can_edit_wizard:
            return False
        batches = self._get_batches()
        if not batches:
            return False
        return len(batches[0]["lines"]) == 1 or self.group_payment

    def _l10n_ve_wh_moves(self):
        self.ensure_one()
        return self.line_ids.move_id.filtered(
            lambda move: move.is_invoice(include_receipts=True) and move.state == "posted"
        )

    def _l10n_ve_append_wh_writeoff(self, payment_vals, amount, account, label):
        """Reduce the payment cash amount and add a withholding write-off line."""
        self.ensure_one()
        if not account or self.currency_id.is_zero(amount):
            return payment_vals
        if self.currency_id.compare_amounts(amount, payment_vals["amount"]) >= 0:
            raise UserError(
                _(
                    "The withholding (%(wh)s) cannot be greater than or equal to the "
                    "payment amount (%(amount)s)."
                )
                % {"wh": amount, "amount": payment_vals["amount"]}
            )
        payment_vals["amount"] -= amount
        write_off_amount_currency = amount if self.payment_type == "inbound" else -amount
        payment_vals.setdefault("write_off_line_vals", []).append(
            {
                "name": label,
                "account_id": account.id,
                "partner_id": self.partner_id.commercial_partner_id.id,
                "currency_id": self.currency_id.id,
                "amount_currency": write_off_amount_currency,
                "balance": self.currency_id._convert(
                    write_off_amount_currency,
                    self.company_id.currency_id,
                    self.company_id,
                    self.payment_date,
                ),
            }
        )
        return payment_vals
