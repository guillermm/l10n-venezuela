# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    l10n_ve_islr_concept_id = fields.Many2one(
        comodel_name="islr.wh.concept",
        string="Concepto ISLR",
        compute="_compute_l10n_ve_islr_concept_id",
        store=True,
        readonly=False,
    )
    l10n_ve_islr_amount = fields.Monetary(
        string="Retención ISLR",
        currency_field="currency_id",
        compute="_compute_l10n_ve_islr_amount",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id", "payment_type", "partner_type", "line_ids")
    def _compute_l10n_ve_islr_concept_id(self):
        for wizard in self:
            concept = False
            if wizard.payment_type == "outbound" and wizard.partner_type == "supplier":
                concept = wizard.partner_id.islr_concept_id
                if not concept:
                    moves = wizard._l10n_ve_wh_moves()
                    concept = moves[:1].islr_concept_id or moves.invoice_line_ids.mapped("islr_concept_id")[:1]
            wizard.l10n_ve_islr_concept_id = concept

    @api.depends("l10n_ve_islr_concept_id", "amount", "currency_id", "partner_id", "line_ids")
    def _compute_l10n_ve_islr_amount(self):
        for wizard in self:
            wizard.l10n_ve_islr_amount = wizard._l10n_ve_get_islr_amount()

    def _l10n_ve_get_islr_amount(self):
        self.ensure_one()
        if (
            self.payment_type != "outbound"
            or self.partner_type != "supplier"
            or not self.l10n_ve_islr_concept_id
            or not self._l10n_ve_wh_edit_mode()
        ):
            return 0.0
        person_type = self.partner_id.person_type or "pjdo"
        rate = self.l10n_ve_islr_concept_id.get_rate_for_person(person_type)
        if not rate:
            return 0.0
        moves = self._l10n_ve_wh_moves().filtered(
            lambda move: move.move_type in ("in_invoice", "in_refund")
        )
        date = self.payment_date or fields.Date.context_today(self)
        base = 0.0
        for move in moves:
            sign = 1 if move.move_type == "in_invoice" else -1
            move_base = move._l10n_ve_taxable_untaxed() * ((rate.base_percentage or 100.0) / 100.0)
            if move.currency_id and self.currency_id and move.currency_id != self.currency_id:
                move_base = move.currency_id._convert(
                    move_base, self.currency_id, self.company_id, date
                )
            base += sign * move_base
        if base <= 0:
            return 0.0
        subtract = 0.0
        if rate.subtract_ut:
            ut_val = self.env["l10n.ut"].get_amount_ut(date)
            subtract_ves = rate.subtract_ut * ut_val * (rate.wh_percentage / 100.0)
            ves = self.env["l10n.ut"].get_ves_currency()
            subtract = (
                ves._convert(subtract_ves, self.currency_id, self.company_id, date)
                if ves and self.currency_id and ves != self.currency_id
                else subtract_ves
            )
        return self.currency_id.round(max(base * (rate.wh_percentage / 100.0) - subtract, 0.0))

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        if (
            self._l10n_ve_wh_edit_mode()
            and self.payment_type == "outbound"
            and self.l10n_ve_islr_amount
        ):
            account = self.company_id.wh_islr_account_id
            if not account:
                raise UserError(_("Configure the ISLR Withholding Account in Company Settings."))
            self._l10n_ve_append_wh_writeoff(
                payment_vals,
                self.l10n_ve_islr_amount,
                account,
                _("ISLR withholding %s") % (self.l10n_ve_islr_concept_id.display_name,),
            )
        return payment_vals

    def _create_payments(self):
        payments = super()._create_payments()
        if (
            self._l10n_ve_wh_edit_mode()
            and self.payment_type == "outbound"
            and self.l10n_ve_islr_amount
            and self.l10n_ve_islr_concept_id
        ):
            self._l10n_ve_create_islr_voucher(payments)
        return payments

    def _l10n_ve_create_islr_voucher(self, payments):
        self.ensure_one()
        moves = self._l10n_ve_wh_moves().filtered(
            lambda move: move.move_type in ("in_invoice", "in_refund") and not move.wh_islr_doc_id
        )
        if not moves:
            return
        voucher = self.env["account.wh.islr.doc"].create({
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "currency_id": self.currency_id.id,
            "type": moves[:1].move_type,
            "date": self.payment_date,
            "journal_id": self.company_id.wh_islr_journal_id.id,
            "payment_id": payments[:1].id,
            "line_ids": [(0, 0, {
                "move_id": move.id,
                "concept_id": self.l10n_ve_islr_concept_id.id,
                "base_amount": move._l10n_ve_taxable_untaxed(),
            }) for move in moves],
        })
        voucher.line_ids.action_recompute_from_move()
        voucher.action_confirm()
        voucher.action_done()
        moves.write({"wh_islr_doc_id": voucher.id})
        moves._l10n_ve_refresh_wh_state()
        return voucher
