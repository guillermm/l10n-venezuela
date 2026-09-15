# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountWhMuni(models.Model):
    _name = "account.wh.muni"
    _description = "Municipal Withholding Voucher"
    _order = "date desc, name desc"
    _check_company_auto = True

    name = fields.Char(string="Voucher Number", required=True, copy=False, default="/")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Posted"), ("cancel", "Cancelled")],
        string="State",
        default="draft",
    )
    move_id = fields.Many2one(comodel_name="account.move", string="Invoice", required=True)
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        default=lambda self: self.env.company.wh_muni_journal_id,
    )
    payment_id = fields.Many2one(comodel_name="account.payment", copy=False)
    wh_rate = fields.Float(string="Rate (%)", default=0.0)
    amount_base = fields.Float(string="Base Amount")
    amount_total_ret = fields.Float(string="Total Withheld Amount", compute="_compute_amount", store=True)
    accounting_move_id = fields.Many2one(comodel_name="account.move", copy=False, readonly=True)

    @api.depends("amount_base", "wh_rate")
    def _compute_amount(self):
        for rec in self:
            rec.amount_total_ret = rec.amount_base * (rec.wh_rate / 100.0)

    @api.onchange("move_id")
    def _onchange_move_id(self):
        if self.move_id:
            self.partner_id = self.move_id.partner_id
            self.amount_base = self.move_id._l10n_ve_taxable_untaxed()
            self.wh_rate = self.move_id.partner_id.wh_muni_rate or self.wh_rate

    def action_confirm(self):
        for rec in self:
            if rec.name == "/" or not rec.name:
                rec.name = self.env["ir.sequence"].next_by_code("account.wh.muni") or rec.id
            if rec.amount_total_ret <= 0:
                raise ValidationError(_("Municipal withholding amount must be greater than zero."))
            account = rec.company_id.wh_muni_account_id
            if rec.payment_id:
                rec.state = "done"
                if rec.move_id:
                    rec.move_id.wh_muni_id = rec.id
                    rec.move_id._l10n_ve_refresh_wh_state()
                continue
            if rec.journal_id and account and not rec.accounting_move_id:
                move = self.env["account.move"].create({
                    "journal_id": rec.journal_id.id,
                    "date": rec.date,
                    "ref": rec.name,
                    "company_id": rec.company_id.id,
                    "move_type": "entry",
                    "line_ids": [
                        (0, 0, {
                            "name": _("Municipal withholding %s") % rec.name,
                            "partner_id": rec.partner_id.id,
                            "account_id": rec.partner_id.property_account_payable_id.id,
                            "debit": rec.amount_total_ret,
                        }),
                        (0, 0, {
                            "name": _("Municipal withholding %s") % rec.name,
                            "partner_id": rec.partner_id.id,
                            "account_id": account.id,
                            "credit": rec.amount_total_ret,
                        }),
                    ],
                })
                move.action_post()
                rec.accounting_move_id = move.id
            rec.state = "done"
            if rec.move_id:
                rec.move_id.wh_muni_id = rec.id
                rec.move_id._l10n_ve_refresh_wh_state()

    def action_cancel(self):
        for rec in self:
            if rec.accounting_move_id and rec.accounting_move_id.state == "posted":
                rec.accounting_move_id.button_draft()
                rec.accounting_move_id.button_cancel()
            rec.state = "cancel"
            if rec.move_id:
                rec.move_id._l10n_ve_refresh_wh_state()
