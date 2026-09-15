# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    l10n_ve_igtf_available = fields.Boolean(related="journal_id.l10n_ve_igtf_enabled")
    l10n_ve_igtf_apply = fields.Boolean(string="Apply IGTF", copy=False)
    l10n_ve_igtf_rate = fields.Float(
        string="IGTF Rate (%)",
        default=lambda self: self.env.company.l10n_ve_igtf_rate,
    )
    l10n_ve_igtf_amount = fields.Monetary(
        string="IGTF Amount",
        currency_field="currency_id",
        compute="_compute_l10n_ve_igtf_amount",
        store=True,
    )

    @api.onchange("company_id", "journal_id")
    def _onchange_l10n_ve_igtf_defaults(self):
        if self.company_id:
            self.l10n_ve_igtf_rate = self.company_id.l10n_ve_igtf_rate
        if self.journal_id:
            self.l10n_ve_igtf_apply = bool(self.journal_id.l10n_ve_igtf_enabled)

    @api.depends("amount", "currency_id", "l10n_ve_igtf_apply", "l10n_ve_igtf_rate")
    def _compute_l10n_ve_igtf_amount(self):
        for payment in self:
            amount = payment.amount * payment.l10n_ve_igtf_rate / 100.0 if payment.l10n_ve_igtf_apply else 0.0
            payment.l10n_ve_igtf_amount = payment.currency_id.round(amount) if payment.currency_id else amount

    def _l10n_ve_validate_igtf(self):
        self.ensure_one()
        if not self.l10n_ve_igtf_available:
            raise UserError(_("Enable IGTF on the payment journal first."))
        if self.l10n_ve_igtf_rate <= 0:
            raise UserError(_("The IGTF rate must be greater than zero."))
        if self.payment_type == "outbound":
            if not self.company_id.l10n_ve_igtf_expense_account_id:
                raise UserError(_("Configure the IGTF expense account first."))
            return
        if not self.company_id.l10n_ve_igtf_perception_agent:
            raise UserError(_("The company must be an IGTF perception agent for incoming payments."))
        if (
            self.company_id.l10n_ve_igtf_perception_agent_date
            and self.date < self.company_id.l10n_ve_igtf_perception_agent_date
        ):
            raise UserError(_("The payment date is before the IGTF perception designation date."))
        if not self.company_id.l10n_ve_igtf_perception_account_id:
            raise UserError(_("Configure the IGTF perception account first."))

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        lines = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals,
            force_balance=force_balance,
        )
        if not self.l10n_ve_igtf_apply or self.currency_id.is_zero(self.l10n_ve_igtf_amount):
            return lines
        self._l10n_ve_validate_igtf()
        account = (
            self.company_id.l10n_ve_igtf_expense_account_id
            if self.payment_type == "outbound"
            else self.company_id.l10n_ve_igtf_perception_account_id
        )
        # Extra cash movement: vendor payments pay IGTF on top; inbound collections receive it.
        igtf_amount_currency = self.l10n_ve_igtf_amount if self.payment_type == "outbound" else -self.l10n_ve_igtf_amount
        igtf_balance = self.currency_id._convert(
            igtf_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_account = self.outstanding_account_id
        for line in lines:
            if liquidity_account and line.get("account_id") == liquidity_account.id:
                line["amount_currency"] = line.get("amount_currency", 0.0) - igtf_amount_currency
                line["balance"] = line.get("balance", 0.0) - igtf_balance
                break
        lines.append({
            "name": _("IGTF %s%%") % self.l10n_ve_igtf_rate,
            "date_maturity": self.date,
            "partner_id": self.partner_id.id,
            "account_id": account.id,
            "currency_id": self.currency_id.id,
            "amount_currency": igtf_amount_currency,
            "balance": igtf_balance,
        })
        return lines
