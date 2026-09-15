# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    l10n_ve_igtf_available = fields.Boolean(related="journal_id.l10n_ve_igtf_enabled")
    l10n_ve_igtf_apply = fields.Boolean(string="Apply IGTF")
    l10n_ve_igtf_rate = fields.Float(string="IGTF Rate (%)")
    l10n_ve_igtf_amount = fields.Monetary(
        string="IGTF Amount",
        currency_field="currency_id",
        compute="_compute_l10n_ve_igtf_amount",
    )

    def _l10n_ve_igtf_already_on_bills(self):
        moves = self.env["account.move"]
        if self.env.context.get("active_model") == "account.move":
            moves = self.env["account.move"].browse(self.env.context.get("active_ids") or [])
        if "line_ids" in self._fields and self.line_ids:
            moves |= self.line_ids.move_id
        return any(move.l10n_ve_igtf_apply for move in moves)

    @api.onchange("journal_id", "company_id")
    def _onchange_l10n_ve_igtf_defaults(self):
        already = self._l10n_ve_igtf_already_on_bills()
        self.l10n_ve_igtf_apply = bool(self.journal_id.l10n_ve_igtf_enabled) and not already
        self.l10n_ve_igtf_rate = self.company_id.l10n_ve_igtf_rate

    @api.depends("amount", "currency_id", "l10n_ve_igtf_apply", "l10n_ve_igtf_rate")
    def _compute_l10n_ve_igtf_amount(self):
        for wizard in self:
            amount = wizard.amount * wizard.l10n_ve_igtf_rate / 100.0 if wizard.l10n_ve_igtf_apply else 0.0
            wizard.l10n_ve_igtf_amount = wizard.currency_id.round(amount) if wizard.currency_id else amount

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super()._create_payment_vals_from_wizard(batch_result)
        vals.update({
            "l10n_ve_igtf_apply": self.l10n_ve_igtf_apply,
            "l10n_ve_igtf_rate": self.l10n_ve_igtf_rate,
        })
        return vals

    def _create_payment_vals_from_batch(self, batch_result):
        vals = super()._create_payment_vals_from_batch(batch_result)
        vals.update({
            "l10n_ve_igtf_apply": self.l10n_ve_igtf_apply,
            "l10n_ve_igtf_rate": self.l10n_ve_igtf_rate,
        })
        return vals

    def action_create_payments(self):
        if self.l10n_ve_igtf_apply:
            if not self.journal_id.l10n_ve_igtf_enabled:
                raise UserError(_("Enable IGTF on the payment journal first."))
            if self.l10n_ve_igtf_rate <= 0:
                raise UserError(_("The IGTF rate must be greater than zero."))
        return super().action_create_payments()
