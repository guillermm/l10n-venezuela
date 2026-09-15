# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import calendar

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountWhIva(models.Model):
    _name = "account.wh.iva"
    _description = "VAT Withholding Voucher"
    _order = "date desc, name desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True

    name = fields.Char(
        string="Voucher Number",
        required=True,
        copy=False,
        default="/",
        tracking=True,
        help="Correlative number of VAT Withholding Voucher (YYYYMMXXXXXXXX)",
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
        default=lambda self: self.env.company.wh_iva_journal_id,
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
        help="Date used to compute the tax period (month/year)",
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Accounting Entry",
        copy=False,
        readonly=True,
        check_company=True,
    )
    line_ids = fields.One2many(
        comodel_name="account.wh.iva.line",
        inverse_name="wh_iva_id",
        string="Withholding Lines",
        copy=True,
    )
    total_tax_amount = fields.Monetary(
        string="Total Base Tax",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_ret_amount = fields.Monetary(
        string="Total Retained Amount",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_exempt_amount = fields.Monetary(
        string="Total Exempt",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("line_ids.tax_amount", "line_ids.amount_ret", "line_ids.exempt_amount")
    def _compute_totals(self):
        for rec in self:
            rec.total_tax_amount = sum(rec.line_ids.mapped("tax_amount"))
            rec.total_ret_amount = sum(rec.line_ids.mapped("amount_ret"))
            rec.total_exempt_amount = sum(rec.line_ids.mapped("exempt_amount"))

    def _l10n_ve_next_number(self, seq_date=None, company=None):
        company = company or self.env.company
        seq_date = fields.Date.to_date(seq_date) or fields.Date.context_today(self)
        sequence = self.env["ir.sequence"].sudo().search(
            [("code", "=", "account.wh.iva"), ("company_id", "=", company.id)],
            limit=1,
        )
        if not sequence:
            sequence = self.env["ir.sequence"].sudo().search(
                [("code", "=", "account.wh.iva"), ("company_id", "=", False)],
                limit=1,
            )
        if not sequence:
            sequence = self.env["ir.sequence"].sudo().create(
                {
                    "name": _("VAT Withholding Voucher (%s)", company.name),
                    "code": "account.wh.iva",
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
            rec.line_ids.move_id.write({"wh_iva_id": rec.id})
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
                        _("Please configure the default VAT Withholding Journal in Company Settings.")
                    )
                partner_acc = rec.partner_id.property_account_payable_id.id
                wh_acc = rec.company_id.wh_iva_account_id.id
                if not wh_acc:
                    raise UserError(
                        _("Please configure default VAT Withholding Account in Company Settings.")
                    )
                amount = rec.total_ret_amount
                lines = [
                    (0, 0, {
                        "name": _("VAT Retention %s") % rec.name,
                        "partner_id": rec.partner_id.id,
                        "account_id": partner_acc,
                        "debit": amount if rec.type == "in_invoice" else 0.0,
                        "credit": amount if rec.type == "in_refund" else 0.0,
                    }),
                    (0, 0, {
                        "name": _("VAT Retention %s") % rec.name,
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

    def _l10n_ve_doc_type(self, move):
        if move.move_type in ("in_refund", "out_refund"):
            return "03"
        if "customs_declaration_id" in move._fields and move.customs_declaration_id:
            return "05"
        if "debit_origin_id" in move._fields and move.debit_origin_id:
            return "02"
        return "01"

    def _l10n_ve_txt_doc_number(self, move):
        declaration = move.customs_declaration_id if "customs_declaration_id" in move._fields else False
        if declaration:
            return declaration.name or ""
        return move.supplier_invoice_number or move.ref or move.name or ""

    def _l10n_ve_txt_expediente(self, move):
        declaration = move.customs_declaration_id if "customs_declaration_id" in move._fields else False
        if not declaration:
            return "0"
        return (declaration.expediente or declaration.name or "0")[:15]

    def _l10n_ve_get_report_lines(self):
        """One TXT/PDF row per document and legal VAT rate."""
        self.ensure_one()
        rows = []
        for line in self.line_ids:
            move = line.move_id
            sign = -1.0 if move.move_type in ("in_refund", "out_refund") else 1.0
            common = {
                "move": move,
                "doc_type": self._l10n_ve_doc_type(move),
                "doc_number": self._l10n_ve_txt_doc_number(move),
                "control_number": move.nro_ctrl or "",
                "expediente": self._l10n_ve_txt_expediente(move),
                "affected": (
                    move.reversed_entry_id.supplier_invoice_number
                    or move.reversed_entry_id.ref
                    or move.reversed_entry_id.name
                    or ""
                ),
                "date": move.invoice_date or move.date_document or move.date or self.date,
                "total": sign * abs(move.amount_total),
            }
            tax_lines = line.tax_line_ids
            if not tax_lines:
                rows.append({
                    **common,
                    "base": sign * line.base_amount,
                    "exempt": sign * line.exempt_amount,
                    "tax": sign * line.tax_amount,
                    "rate": 0.0,
                    "withheld": sign * line.amount_ret,
                })
                continue
            remaining = line.amount_ret
            last_index = len(tax_lines) - 1
            for index, tax_line in enumerate(tax_lines):
                withheld = remaining if index == last_index else tax_line.amount_ret
                remaining -= withheld
                rate = 0.0
                if tax_line.base_amount:
                    rate = round(tax_line.tax_amount / tax_line.base_amount * 100.0, 2)
                elif tax_line.tax_id:
                    rate = tax_line.tax_id.amount
                rows.append({
                    **common,
                    "base": sign * tax_line.base_amount,
                    "exempt": sign * line.exempt_amount if index == 0 else 0.0,
                    "tax": sign * tax_line.tax_amount,
                    "rate": rate,
                    "withheld": sign * withheld,
                })
        return rows
