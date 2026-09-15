# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import io
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import xlsxwriter

MONTHS_ES = (
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)


class FiscalBook(models.Model):
    _name = "fiscal.book"
    _description = "Venezuelan Fiscal Book"
    _order = "date_start desc, type"
    _check_company_auto = True

    name = fields.Char(string="Description", required=True)
    type = fields.Selection(
        selection=[("purchase", "Purchase Book"), ("sale", "Sale Book")],
        string="Book Type",
        required=True,
        default="purchase",
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
        copy=False,
    )
    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.context_today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.context_today)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    article_number = fields.Char(
        string="RLIVA Article",
        compute="_compute_article_number",
        help="Art. 75 purchase / Art. 76 sale (Art. 78 if fiscal printer).",
    )
    period_label = fields.Char(string="Period", compute="_compute_period_label")
    line_ids = fields.One2many(
        comodel_name="fiscal.book.line",
        inverse_name="fb_id",
        string="Fiscal Book Lines",
        copy=True,
    )
    tax_ids = fields.One2many(
        comodel_name="fiscal.book.taxes",
        inverse_name="fb_id",
        string="Tax Summary",
    )
    total_amount = fields.Float(string="Total Operations", compute="_compute_book_totals", store=True)
    total_exempt = fields.Float(string="Total Exempt", compute="_compute_book_totals", store=True)
    total_sdcf = fields.Float(string="Total SDCF", compute="_compute_book_totals", store=True)
    total_base_general = fields.Float(string="Base General (16%)", compute="_compute_book_totals", store=True)
    total_tax_general = fields.Float(string="Tax General (16%)", compute="_compute_book_totals", store=True)
    total_base_reduced = fields.Float(string="Base Reduced (8%)", compute="_compute_book_totals", store=True)
    total_tax_reduced = fields.Float(string="Tax Reduced (8%)", compute="_compute_book_totals", store=True)
    total_base_additional = fields.Float(string="Base Additional (31%)", compute="_compute_book_totals", store=True)
    total_tax_additional = fields.Float(string="Tax Additional (31%)", compute="_compute_book_totals", store=True)
    total_vat_withheld = fields.Float(string="Total VAT Withheld", compute="_compute_book_totals", store=True)

    @api.depends("type", "company_id.printer_fiscal")
    def _compute_article_number(self):
        for rec in self:
            if rec.type == "purchase":
                rec.article_number = "75"
            elif rec.company_id.printer_fiscal:
                rec.article_number = "78"
            else:
                rec.article_number = "76"

    @api.depends("date_start")
    def _compute_period_label(self):
        for rec in self:
            if rec.date_start:
                rec.period_label = "Correspondiente al mes de %s del año %s" % (
                    MONTHS_ES[rec.date_start.month - 1],
                    rec.date_start.year,
                )
            else:
                rec.period_label = ""

    @api.depends(
        "line_ids.total_amount",
        "line_ids.exempt_amount",
        "line_ids.sdcf_amount",
        "line_ids.base_general",
        "line_ids.tax_general",
        "line_ids.base_reduced",
        "line_ids.tax_reduced",
        "line_ids.base_additional",
        "line_ids.tax_additional",
        "line_ids.vat_withheld",
    )
    def _compute_book_totals(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped("total_amount"))
            rec.total_exempt = sum(rec.line_ids.mapped("exempt_amount"))
            rec.total_sdcf = sum(rec.line_ids.mapped("sdcf_amount"))
            rec.total_base_general = sum(rec.line_ids.mapped("base_general"))
            rec.total_tax_general = sum(rec.line_ids.mapped("tax_general"))
            rec.total_base_reduced = sum(rec.line_ids.mapped("base_reduced"))
            rec.total_tax_reduced = sum(rec.line_ids.mapped("tax_reduced"))
            rec.total_base_additional = sum(rec.line_ids.mapped("base_additional"))
            rec.total_tax_additional = sum(rec.line_ids.mapped("tax_additional"))
            rec.total_vat_withheld = sum(rec.line_ids.mapped("vat_withheld"))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(_("The start date must be before the end date."))

    @api.constrains("date_start", "date_end", "type", "company_id", "state")
    def _check_unique_period(self):
        for rec in self:
            if rec.state == "cancel":
                continue
            overlap = self.search([
                ("id", "!=", rec.id),
                ("company_id", "=", rec.company_id.id),
                ("type", "=", rec.type),
                ("state", "!=", "cancel"),
                ("date_start", "<=", rec.date_end),
                ("date_end", ">=", rec.date_start),
            ], limit=1)
            if overlap:
                raise ValidationError(
                    _("There is already a %s fiscal book (%s) covering this period.")
                    % (dict(self._fields["type"].selection).get(rec.type), overlap.name)
                )

    def _l10n_ve_doc_date(self, move):
        return move.date_document or move.invoice_date or move.date

    def _l10n_ve_doc_type(self, move):
        if move.move_type in ("in_refund", "out_refund"):
            return "03"
        if "customs_declaration_id" in move._fields and move.customs_declaration_id:
            return "05"
        if "debit_origin_id" in move._fields and move.debit_origin_id:
            return "02"
        return "01"

    def _l10n_ve_invoice_number(self, move):
        if move.move_type in ("in_invoice", "in_refund"):
            return move.supplier_invoice_number or move.ref or move.name
        return move.invoice_printer or move.name or ""

    def _l10n_ve_affected_number(self, move):
        origin = move.reversed_entry_id
        if "debit_origin_id" in move._fields and move.debit_origin_id:
            origin = move.debit_origin_id
        if not origin:
            return ""
        return self._l10n_ve_invoice_number(origin)

    def _l10n_ve_move_types(self):
        self.ensure_one()
        if self.type == "purchase":
            return ["in_invoice", "in_refund"]
        return ["out_invoice", "out_refund"]

    def _l10n_ve_to_ves(self, amount, currency, date, company):
        return self.env["l10n.ut"].amount_to_ves(amount, currency, date, company)

    def _l10n_ve_classify_move(self, move):
        """Return aliquot buckets in VES for one invoice (credit notes negative)."""
        self.ensure_one()
        sign = -1 if move.move_type in ("in_refund", "out_refund") else 1
        date = self._l10n_ve_doc_date(move)
        company = move.company_id
        company_cur = company.currency_id
        to_ves_company = lambda amount: self._l10n_ve_to_ves(amount, company_cur, date, company) * sign
        values = {
            "total_amount": to_ves_company(abs(move.amount_total_signed)),
            "exempt_amount": 0.0,
            "sdcf_amount": 0.0,
            "base_general": 0.0,
            "tax_general": 0.0,
            "base_reduced": 0.0,
            "tax_reduced": 0.0,
            "base_additional": 0.0,
            "tax_additional": 0.0,
        }
        for line in move.line_ids.filtered(lambda rec: rec.tax_line_id):
            tax = line.tax_line_id
            t_amt = to_ves_company(abs(line.balance))
            t_base = to_ves_company(line.tax_base_amount or 0.0)
            appl = tax.appl_type
            if appl == "general" or (not appl and abs(tax.amount - 16) < 0.1):
                values["base_general"] += t_base
                values["tax_general"] += t_amt
            elif appl == "reducido" or (not appl and abs(tax.amount - 8) < 0.1):
                values["base_reduced"] += t_base
                values["tax_reduced"] += t_amt
            elif appl == "adicional" or (not appl and abs(tax.amount - 31) < 0.1):
                values["base_additional"] += t_base
                values["tax_additional"] += t_amt
            elif appl == "sdcf":
                values["sdcf_amount"] += t_base
            elif appl == "exento" or not tax.amount:
                values["exempt_amount"] += t_base
        igtf_lines = move.invoice_line_ids.filtered(
            lambda rec: rec.display_type == "product" and getattr(rec, "l10n_ve_igtf_line", False)
        )
        igtf_amount = sum(abs(line.balance) for line in igtf_lines)
        if igtf_amount:
            values["total_amount"] -= to_ves_company(igtf_amount)
        untaxed = sum(
            abs(line.balance)
            for line in move.invoice_line_ids.filtered(
                lambda rec: rec.display_type == "product"
                and not rec.tax_ids
                and not getattr(rec, "l10n_ve_igtf_line", False)
            )
        )
        values["exempt_amount"] += to_ves_company(untaxed)
        return values

    def _l10n_ve_line_vals(self, move, rank, withholding_only=False):
        self.ensure_one()
        values = self._l10n_ve_classify_move(move) if not withholding_only else {
            "total_amount": 0.0,
            "exempt_amount": 0.0,
            "sdcf_amount": 0.0,
            "base_general": 0.0,
            "tax_general": 0.0,
            "base_reduced": 0.0,
            "tax_reduced": 0.0,
            "base_additional": 0.0,
            "tax_additional": 0.0,
        }
        values.update({
            "rank": rank,
            "move_id": move.id,
            "partner_id": move.partner_id.id,
            "partner_vat": move.partner_id.vat or "",
            "doc_date": self._l10n_ve_doc_date(move),
            "invoice_number": self._l10n_ve_invoice_number(move),
            "nro_ctrl": move.nro_ctrl or "",
            "affected_number": self._l10n_ve_affected_number(move),
            "doc_type": self._l10n_ve_doc_type(move),
            "withholding_only": withholding_only,
            "is_adjustment": False,
            "expediente": "",
            "customs_number": "",
            "vat_withheld": 0.0,
            "voucher_number": "",
        })
        declaration = move.customs_declaration_id if "customs_declaration_id" in move._fields else False
        if declaration:
            values["expediente"] = declaration.expediente or declaration.name or ""
            values["customs_number"] = declaration.name or ""
        return values

    def _l10n_ve_apply_withholding(self, values, move, voucher=None):
        if voucher is None:
            voucher = move.wh_iva_id if "wh_iva_id" in move._fields else False
        if not voucher or voucher.state not in ("confirmed", "done"):
            return values
        if not (self.date_start <= voucher.date <= self.date_end):
            return values
        sign = -1 if move.move_type in ("in_refund", "out_refund") else 1
        amount = sum(
            voucher.line_ids.filtered(lambda line: line.move_id == move).mapped("amount_ret")
        )
        if not amount:
            amount = voucher.total_ret_amount
        if not amount:
            return values
        values["vat_withheld"] = self._l10n_ve_to_ves(
            amount,
            voucher.currency_id,
            voucher.date,
            move.company_id,
        ) * sign
        values["voucher_number"] = voucher.name or ""
        return values

    def _l10n_ve_adjustment_line_vals(self, rank):
        """Include posted VAT write-offs of this period in the book totals."""
        self.ensure_one()
        lines = []
        if "vat.write.off" not in self.env:
            return lines, rank
        writeoffs = self.env["vat.write.off"].search([
            ("company_id", "=", self.company_id.id),
            ("state", "=", "done"),
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("move_id", "!=", False),
        ])

        def _matches_book(rec):
            if rec.purchase_book_id == self or rec.sale_book_id == self:
                return True
            if rec.purchase_book_id or rec.sale_book_id:
                return False
            return self.type == "purchase"

        writeoffs = writeoffs.filtered(_matches_book)
        for writeoff in writeoffs:
            if not writeoff.move_id:
                continue
            amount = self._l10n_ve_to_ves(
                writeoff.amount,
                writeoff.company_id.currency_id,
                writeoff.date,
                writeoff.company_id,
            )
            lines.append((0, 0, {
                "rank": rank,
                "move_id": writeoff.move_id.id,
                "partner_id": writeoff.company_id.partner_id.id,
                "partner_vat": writeoff.company_id.partner_id.vat or "",
                "doc_date": writeoff.date,
                "invoice_number": writeoff.name,
                "nro_ctrl": "",
                "affected_number": "",
                "doc_type": "04",
                "withholding_only": False,
                "is_adjustment": True,
                "expediente": "",
                "customs_number": "",
                "total_amount": 0.0,
                "exempt_amount": 0.0,
                "sdcf_amount": 0.0,
                "base_general": 0.0,
                "tax_general": -amount,
                "base_reduced": 0.0,
                "tax_reduced": 0.0,
                "base_additional": 0.0,
                "tax_additional": 0.0,
                "vat_withheld": 0.0,
                "voucher_number": "",
            }))
            rank += 1
        return lines, rank

    def _l10n_ve_refresh_tax_summary(self):
        self.ensure_one()
        self.tax_ids.unlink()
        mapping = (
            ("exento", self.total_exempt, 0.0),
            ("sdcf", self.total_sdcf, 0.0),
            ("general", self.total_base_general, self.total_tax_general),
            ("reducido", self.total_base_reduced, self.total_tax_reduced),
            ("adicional", self.total_base_additional, self.total_tax_additional),
        )
        self.write({
            "tax_ids": [
                (0, 0, {"appl_type": appl, "base_amount": base, "tax_amount": tax})
                for appl, base, tax in mapping
                if base or tax
            ]
        })

    def action_update_book(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft fiscal books can be regenerated."))
        self.line_ids.unlink()
        move_types = self._l10n_ve_move_types()
        all_moves = self.env["account.move"].search([
            ("state", "=", "posted"),
            ("move_type", "in", move_types),
            ("company_id", "=", self.company_id.id),
            ("sin_cred", "=", False),
        ], order="invoice_date asc, name asc")
        period_moves = all_moves.filtered(
            lambda move: self.date_start <= self._l10n_ve_doc_date(move) <= self.date_end
        )
        rank = 1
        lines = []
        added = self.env["account.move"]
        for move in period_moves:
            vals = self._l10n_ve_line_vals(move, rank)
            self._l10n_ve_apply_withholding(vals, move)
            lines.append((0, 0, vals))
            added |= move
            rank += 1
        vouchers = self.env["account.wh.iva"].search([
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("state", "in", ["confirmed", "done"]),
            ("type", "in", move_types),
            ("company_id", "=", self.company_id.id),
        ])
        for voucher in vouchers:
            for wh_line in voucher.line_ids:
                move = wh_line.move_id
                if not move or move in added or move.sin_cred or move.state != "posted":
                    continue
                vals = self._l10n_ve_line_vals(move, rank, withholding_only=True)
                self._l10n_ve_apply_withholding(vals, move, voucher=voucher)
                if not vals["vat_withheld"]:
                    continue
                lines.append((0, 0, vals))
                added |= move
                rank += 1
        extra, rank = self._l10n_ve_adjustment_line_vals(rank)
        lines.extend(extra)
        self.write({"line_ids": lines})
        self.flush_recordset()
        self._l10n_ve_refresh_tax_summary()
        return True

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                rec.action_update_book()
            rec.write({"state": "confirmed"})

    def action_done(self):
        self.write({"state": "done"})

    def action_draft(self):
        locked = self.filtered(lambda rec: rec.state == "done")
        if locked and not self.env.context.get("l10n_ve_unlock_book"):
            raise UserError(
                _("Posted fiscal books lock the period. Ask an accounting manager to reopen them.")
            )
        self.write({"state": "draft"})

    def action_cancel(self):
        if self.filtered(lambda rec: rec.state == "done"):
            raise UserError(_("A posted fiscal book cannot be cancelled. Reopen it first."))
        self.write({"state": "cancel"})

    def action_export_xlsx(self):
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_("xlsxwriter is not available on this Odoo installation."))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet(_("Fiscal Book"))
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 1})
        text_fmt = workbook.add_format({"border": 1})
        date_fmt = workbook.add_format({"border": 1, "num_format": "yyyy-mm-dd"})
        number_fmt = workbook.add_format({"border": 1, "num_format": "#,##0.00"})
        title_fmt = workbook.add_format({"bold": True, "font_size": 14})

        headers = [
            _("N°"),
            _("Date"),
            _("RIF / CI"),
            _("Partner"),
            _("Doc Type"),
            _("Invoice Number"),
            _("Control Number"),
            _("Affected Document"),
            _("Form 86 / Expediente"),
            _("Total Amount"),
            _("Exempt Amount"),
            _("SDCF Amount"),
            _("Base General"),
            _("Tax General"),
            _("Base Reduced"),
            _("Tax Reduced"),
            _("Base Additional"),
            _("Tax Additional"),
            _("VAT Withheld"),
            _("Withholding Voucher"),
        ]
        sheet.merge_range(0, 0, 0, 6, self.name or _("Fiscal Book"), title_fmt)
        sheet.write(1, 0, dict(self._fields["type"].selection).get(self.type, self.type))
        sheet.write(1, 1, self.period_label or "")
        sheet.write(2, 0, self.company_id.name or "")
        sheet.write(2, 1, self.company_id.partner_id.vat or "")

        for col, title in enumerate(headers):
            sheet.write(4, col, title, header_fmt)
            sheet.set_column(col, col, 16)

        for row, line in enumerate(self.line_ids, start=5):
            values = [
                line.rank,
                line.doc_date,
                line.partner_vat or "",
                line.partner_id.name or "",
                line.doc_type or "",
                line.invoice_number or "",
                line.nro_ctrl or "",
                line.affected_number or "",
                " / ".join(part for part in (line.customs_number, line.expediente) if part),
                line.total_amount,
                line.exempt_amount,
                line.sdcf_amount,
                line.base_general,
                line.tax_general,
                line.base_reduced,
                line.tax_reduced,
                line.base_additional,
                line.tax_additional,
                line.vat_withheld,
                line.voucher_number or "",
            ]
            for col, value in enumerate(values):
                if col == 1 and value:
                    sheet.write(row, col, value.strftime("%Y-%m-%d"), date_fmt)
                elif col >= 9 and col <= 18:
                    sheet.write_number(row, col, value or 0.0, number_fmt)
                else:
                    sheet.write(row, col, value if value is not None else "", text_fmt)

        totals_row = 5 + len(self.line_ids)
        sheet.write(totals_row, 0, _("Totals"), header_fmt)
        totals = [
            self.total_amount,
            self.total_exempt,
            self.total_sdcf,
            self.total_base_general,
            self.total_tax_general,
            self.total_base_reduced,
            self.total_tax_reduced,
            self.total_base_additional,
            self.total_tax_additional,
            self.total_vat_withheld,
        ]
        for offset, value in enumerate(totals):
            sheet.write_number(totals_row, 9 + offset, value or 0.0, number_fmt)

        workbook.close()
        filename = "%s.xlsx" % re.sub(r"[^\w\-.]+", "_", self.name or "libro_fiscal")
        attachment = self.env["ir.attachment"].create({
            "name": filename,
            "type": "binary",
            "datas": base64.b64encode(output.getvalue()),
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }
