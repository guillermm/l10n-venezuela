# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import calendar
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class GenerateTxtWhIva(models.TransientModel):
    _name = "generate.txt.wh.iva"
    _description = "Generate TXT File for SENIAT (IVA)"

    date_start = fields.Date(string="Start Date", required=True, default=lambda self: self._default_date_start())
    date_end = fields.Date(string="End Date", required=True, default=lambda self: self._default_date_end())
    txt_filename = fields.Char(string="File Name", default="retencion_iva_seniat.txt")
    txt_file = fields.Binary(string="TXT File", readonly=True)
    state = fields.Selection([("draft", "Draft"), ("done", "Done")], default="draft")

    @api.model
    def _default_date_start(self):
        today = fields.Date.context_today(self)
        return today.replace(day=1) if today.day <= 15 else today.replace(day=16)

    @api.model
    def _default_date_end(self):
        today = fields.Date.context_today(self)
        if today.day <= 15:
            return today.replace(day=15)
        return today.replace(day=calendar.monthrange(today.year, today.month)[1])

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for wizard in self:
            if wizard.date_start > wizard.date_end:
                raise ValidationError(_("The start date must be before the end date."))

    def _sanitize(self, value, size=20):
        return re.sub(r"[\t\r\n]", " ", value or "").strip()[:size]

    def action_generate_txt(self):
        self.ensure_one()
        company = self.env.company
        vouchers = self.env["account.wh.iva"].search([
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("state", "in", ["confirmed", "done"]),
            ("type", "in", ["in_invoice", "in_refund"]),
            ("company_id", "=", company.id),
        ])
        if not vouchers:
            raise UserError(_("No confirmed VAT Withholding vouchers found for the selected date range."))

        ut = self.env["l10n.ut"]
        company_vat = re.sub(r"[^A-Z0-9]", "", (company.partner_id.vat or "").upper())
        lines = []
        for voucher in vouchers:
            partner_vat = re.sub(r"[^A-Z0-9]", "", (voucher.partner_id.vat or "").upper())
            period = (voucher.date or self.date_start).strftime("%Y%m")
            for row in voucher._l10n_ve_get_report_lines():
                doc_date = row["date"]
                if not doc_date:
                    raise UserError(
                        _("Invoice %s has no document date; it cannot be exported to SENIAT.")
                        % (row["move"].display_name)
                    )
                to_ves = lambda amount, conv_date=doc_date: ut.amount_to_ves(
                    amount, voucher.currency_id, conv_date, company
                )
                columns = [
                    company_vat,
                    period,
                    doc_date.strftime("%Y-%m-%d"),
                    "C",
                    row["doc_type"],
                    partner_vat,
                    self._sanitize(row["doc_number"]) or "0",
                    self._sanitize(row["control_number"]) or "0",
                    f"{to_ves(abs(row['total'])):.2f}",
                    f"{to_ves(abs(row['base'])):.2f}",
                    f"{to_ves(abs(row['withheld']), voucher.date):.2f}",
                    self._sanitize(row["affected"]) or "0",
                    voucher.name or "",
                    f"{to_ves(abs(row['exempt'])):.2f}",
                    f"{row['rate']:.2f}",
                    self._sanitize(row.get("expediente") or "0", 15),
                ]
                lines.append("\t".join(columns))

        txt_content = "\r\n".join(lines)
        self.write({
            "txt_file": base64.b64encode(txt_content.encode("latin-1", errors="replace")),
            "txt_filename": f"IVA_{company_vat}_{self.date_start.strftime('%Y%m')}.txt",
            "state": "done",
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "generate.txt.wh.iva",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
