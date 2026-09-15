# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import calendar

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountWhIslrDoc(models.Model):
    _name = "account.wh.islr.doc"
    _description = "ISLR Withholding Document"
    _order = "date desc, name desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True

    name = fields.Char(
        string="Voucher Number",
        required=True,
        copy=False,
        default="/",
        tracking=True,
        help="Correlative number of ISLR Withholding Voucher",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Posted"),
            ("cancel", "Cancelled"),
        ],
        string="State",
        default="draft",
        tracking=True,
    )
    type = fields.Selection(
        selection=[
            ("in_invoice", "Vendor Bill"),
            ("out_invoice", "Customer Invoice"),
            ("in_refund", "Vendor Refund"),
            ("out_refund", "Customer Refund"),
        ],
        string="Type",
        default="in_invoice",
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        check_company=True,
        default=lambda self: self.env.company.wh_islr_journal_id,
    )
    payment_id = fields.Many2one(
        comodel_name="account.payment",
        string="Payment",
        copy=False,
        check_company=True,
        readonly=True,
    )
    date = fields.Date(
        string="Date of Voucher",
        required=True,
        default=fields.Date.context_today,
    )
    period_date = fields.Date(
        string="Fiscal Period Date",
        default=fields.Date.context_today,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Accounting Entry",
        copy=False,
        readonly=True,
        check_company=True,
    )
    line_ids = fields.One2many(
        comodel_name="account.wh.islr.doc.line",
        inverse_name="islr_doc_id",
        string="Withholding Lines",
        copy=True,
    )
    total_base_amount = fields.Monetary(
        string="Total Base",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_ret_amount = fields.Monetary(
        string="Total ISLR Retained",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("line_ids.base_amount", "line_ids.amount_ret")
    def _compute_totals(self):
        for rec in self:
            rec.total_base_amount = sum(rec.line_ids.mapped("base_amount"))
            rec.total_ret_amount = sum(rec.line_ids.mapped("amount_ret"))

    def _l10n_ve_next_number(self, seq_date=None, company=None):
        company = company or self.env.company
        seq_date = fields.Date.to_date(seq_date) or fields.Date.context_today(self)
        sequence = self.env["ir.sequence"].sudo().search(
            [("code", "=", "account.wh.islr.doc"), ("company_id", "=", company.id)],
            limit=1,
        )
        if not sequence:
            sequence = self.env["ir.sequence"].sudo().search(
                [("code", "=", "account.wh.islr.doc"), ("company_id", "=", False)],
                limit=1,
            )
        if not sequence:
            sequence = self.env["ir.sequence"].sudo().create(
                {
                    "name": _("ISLR Withholding Voucher (%s)", company.name),
                    "code": "account.wh.islr.doc",
                    "prefix": "%(year)s%(month)s",
                    "padding": 8,
                    "implementation": "no_gap",
                    "use_date_range": True,
                    "company_id": company.id,
                }
            )
        range_model = self.env["ir.sequence.date_range"].sudo()
        if not range_model.search_count(
            [
                ("sequence_id", "=", sequence.id),
                ("date_from", "<=", seq_date),
                ("date_to", ">=", seq_date),
            ]
        ):
            last_day = calendar.monthrange(seq_date.year, seq_date.month)[1]
            range_model.create(
                {
                    "sequence_id": sequence.id,
                    "date_from": seq_date.replace(day=1),
                    "date_to": seq_date.replace(day=last_day),
                }
            )
        return sequence.next_by_id(sequence_date=seq_date)

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("Cannot confirm voucher without lines."))
            rec.line_ids.action_recompute_from_move()
            if rec.name == "/" or not rec.name:
                rec.name = rec._l10n_ve_next_number(rec.date, rec.company_id)
            rec.write({"state": "confirmed"})
            rec.line_ids.move_id._l10n_ve_refresh_wh_state()

    def _l10n_ve_cancel_entry(self):
        for rec in self:
            move = rec.move_id
            if not move:
                continue
            if move.state == "posted":
                try:
                    move.button_draft()
                    move.button_cancel()
                except UserError:
                    move._reverse_moves(
                        default_values_list=[{"ref": _("Reversal of %s") % rec.name}],
                        cancel=True,
                    )
            elif move.state == "draft":
                move.button_cancel()

    def action_done(self):
        for rec in self:
            if rec.payment_id:
                rec.write({"state": "done"})
                rec.line_ids.move_id._l10n_ve_refresh_wh_state()
                continue
            if rec.type in ["in_invoice", "in_refund"] and not rec.move_id:
                if not rec.journal_id:
                    raise UserError(
                        _("Please configure the default ISLR Withholding Journal in Company Settings.")
                    )
                partner_acc = rec.partner_id.property_account_payable_id.id
                wh_acc = rec.company_id.wh_islr_account_id.id
                if not wh_acc:
                    raise UserError(
                        _("Please configure default ISLR Withholding Account in Company Settings.")
                    )
                amount = rec.total_ret_amount
                lines = [
                    (0, 0, {
                        "name": _("ISLR Retention %s") % rec.name,
                        "partner_id": rec.partner_id.id,
                        "account_id": partner_acc,
                        "debit": amount if rec.type == "in_invoice" else 0.0,
                        "credit": amount if rec.type == "in_refund" else 0.0,
                    }),
                    (0, 0, {
                        "name": _("ISLR Retention %s") % rec.name,
                        "partner_id": rec.partner_id.id,
                        "account_id": wh_acc,
                        "debit": amount if rec.type == "in_refund" else 0.0,
                        "credit": amount if rec.type == "in_invoice" else 0.0,
                    }),
                ]
                move = self.env["account.move"].create({
                    "journal_id": rec.journal_id.id,
                    "date": rec.date,
                    "ref": rec.name,
                    "company_id": rec.company_id.id,
                    "move_type": "entry",
                    "line_ids": lines,
                })
                move.action_post()
                rec.move_id = move.id
            rec.write({"state": "done"})
            rec.line_ids.move_id._l10n_ve_refresh_wh_state()

    def action_cancel(self):
        for rec in self:
            rec._l10n_ve_cancel_entry()
            rec.write({"state": "cancel"})
            rec.line_ids.move_id._l10n_ve_refresh_wh_state()

    def action_draft(self):
        for rec in self:
            rec.write({"state": "draft"})
            rec.line_ids.move_id._l10n_ve_refresh_wh_state()
