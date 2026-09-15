# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountWhIslrDocLine(models.Model):
    _name = "account.wh.islr.doc.line"
    _description = "ISLR Withholding Document Line"

    islr_doc_id = fields.Many2one(
        comodel_name="account.wh.islr.doc",
        string="Voucher",
        ondelete="cascade",
        required=True,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        required=True,
        domain="[('partner_id', '=', parent.partner_id), ('move_type', 'in', ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'))]",
    )
    concept_id = fields.Many2one(
        comodel_name="islr.wh.concept",
        string="ISLR Concept",
        required=True,
    )
    seniat_code = fields.Char(
        string="SENIAT Code",
        size=3,
        help="Official 3-digit code of the rate that matches the partner type.",
    )
    base_amount = fields.Monetary(
        string="Base Amount",
        currency_field="currency_id",
        required=True,
    )
    wh_percentage = fields.Float(
        string="Retention Rate (%)",
        default=2.0,
    )
    subtract_amount = fields.Monetary(
        string="Subtraction Amount",
        currency_field="currency_id",
        default=0.0,
    )
    amount_ret = fields.Monetary(
        string="Withheld ISLR",
        compute="_compute_amount_ret",
        store=True,
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        related="islr_doc_id.currency_id",
        store=True,
    )

    @api.depends("base_amount", "wh_percentage", "subtract_amount")
    def _compute_amount_ret(self):
        for line in self:
            calc = (line.base_amount * (line.wh_percentage / 100.0)) - line.subtract_amount
            line.amount_ret = max(calc, 0.0)

    def _prepare_rate_values(self):
        self.ensure_one()
        values = {
            "base_amount": self.move_id._l10n_ve_taxable_untaxed() if self.move_id else 0.0,
            "wh_percentage": self.wh_percentage,
            "subtract_amount": 0.0,
            "seniat_code": self.seniat_code or False,
        }
        if not (self.move_id and self.concept_id and self.islr_doc_id.partner_id):
            return values
        person_type = self.islr_doc_id.partner_id.person_type or "pjdo"
        rate = self.concept_id.get_rate_for_person(person_type)
        if not rate:
            return values
        values["seniat_code"] = rate.code
        base_pct = rate.base_percentage or 100.0
        move = self.move_id
        date = self.islr_doc_id.date or fields.Date.context_today(self)
        company = self.islr_doc_id.company_id
        currency = self.islr_doc_id.currency_id or company.currency_id
        base = move._l10n_ve_taxable_untaxed()
        if move.currency_id and currency and move.currency_id != currency:
            base = move.currency_id._convert(base, currency, company, date)
        values["base_amount"] = base * (base_pct / 100.0)
        values["wh_percentage"] = rate.wh_percentage
        if rate.subtract_ut > 0:
            ut_val = self.env["l10n.ut"].get_amount_ut(date)
            subtract_ves = rate.subtract_ut * ut_val * (rate.wh_percentage / 100.0)
            ves = self.env["l10n.ut"].get_ves_currency()
            values["subtract_amount"] = (
                ves._convert(subtract_ves, currency, company, date)
                if ves and currency and ves != currency
                else subtract_ves
            )
        return values

    def action_recompute_from_move(self):
        for line in self:
            line.write(line._prepare_rate_values())
        return True

    @api.onchange("move_id", "concept_id")
    def _onchange_concept_or_move(self):
        if self.move_id:
            values = self._prepare_rate_values()
            self.base_amount = values["base_amount"]
            self.wh_percentage = values["wh_percentage"]
            self.subtract_amount = values["subtract_amount"]
            self.seniat_code = values.get("seniat_code") or False
