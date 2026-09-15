# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import re
from xml.etree import ElementTree as ET

from odoo import _, fields, models
from odoo.exceptions import UserError

RIF_PATTERN = re.compile(r"^[VEJPG]\d{9}$")


class GenerateXmlWhIslr(models.TransientModel):
    _name = "generate.xml.wh.islr"
    _description = "Generate XML File for SENIAT (ISLR)"

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.context_today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.context_today)
    xml_filename = fields.Char(string="File Name", default="retencion_islr_seniat.xml")
    xml_file = fields.Binary(string="XML File", readonly=True)
    state = fields.Selection([("draft", "Draft"), ("done", "Done")], default="draft")

    def _format_rif(self, vat, owner_name):
        rif = re.sub(r"[^A-Za-z0-9]", "", vat or "").upper()
        if rif.startswith("VE"):
            rif = rif[2:]
        if not RIF_PATTERN.match(rif):
            raise UserError(
                _("The RIF of %s is not valid for SENIAT XML (letter V/E/J/P/G + 9 digits).")
                % owner_name
            )
        return rif

    def _invoice_number(self, move):
        digits = re.sub(r"\D", "", (move.supplier_invoice_number or move.ref or move.name or ""))
        return digits[-10:] if digits else "0"

    def _control_number(self, move):
        digits = re.sub(r"\D", "", move.nro_ctrl or "")
        return digits[-8:] if digits else "NA"

    def action_generate_xml(self):
        self.ensure_one()
        company = self.env.company
        vouchers = self.env["account.wh.islr.doc"].search([
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("state", "in", ["confirmed", "done"]),
            ("type", "in", ["in_invoice", "in_refund"]),
            ("company_id", "=", company.id),
        ])
        period_str = self.date_start.strftime("%Y%m")
        rif_agente = self._format_rif(company.partner_id.vat, company.display_name)
        root = ET.Element("RelacionRetencionesISLR", RifAgente=rif_agente, Periodo=period_str)
        ut = self.env["l10n.ut"]

        if not vouchers:
            last_day = fields.Date.end_of(self.date_start.replace(day=1), "month")
            det = ET.SubElement(root, "DetalleRetencion")
            ET.SubElement(det, "RifRetenido").text = rif_agente
            ET.SubElement(det, "NumeroFactura").text = "0"
            ET.SubElement(det, "NumeroControl").text = "NA"
            ET.SubElement(det, "FechaOperacion").text = last_day.strftime("%d/%m/%Y")
            ET.SubElement(det, "CodigoConcepto").text = "000"
            ET.SubElement(det, "MontoOperacion").text = "0.00"
            ET.SubElement(det, "PorcentajeRetencion").text = "0.00"
        for voucher in vouchers:
            partner_vat = self._format_rif(voucher.partner_id.vat, voucher.partner_id.display_name)
            for line in voucher.line_ids:
                move = line.move_id
                person_type = voucher.partner_id.person_type or "pjdo"
                seniat_rate = line.concept_id.get_rate_for_person(person_type)
                code = (line.seniat_code or seniat_rate.code or "").strip()
                if not code or code == "000":
                    raise UserError(
                        _("Voucher %s has no SENIAT code for concept %s and person type %s.")
                        % (voucher.name, line.concept_id.display_name, person_type.upper())
                    )
                base_ves = ut.amount_to_ves(line.base_amount, voucher.currency_id, voucher.date, company)
                rate = 0.0 if voucher.currency_id.is_zero(line.amount_ret) else line.wh_percentage
                det = ET.SubElement(root, "DetalleRetencion")
                ET.SubElement(det, "RifRetenido").text = partner_vat
                ET.SubElement(det, "NumeroFactura").text = self._invoice_number(move)
                ET.SubElement(det, "NumeroControl").text = self._control_number(move)
                ET.SubElement(det, "FechaOperacion").text = (
                    voucher.date or move.invoice_date or fields.Date.context_today(self)
                ).strftime("%d/%m/%Y")
                ET.SubElement(det, "CodigoConcepto").text = code
                ET.SubElement(det, "MontoOperacion").text = f"{base_ves:.2f}"
                ET.SubElement(det, "PorcentajeRetencion").text = f"{rate:.2f}"

        xml_bytes = ET.tostring(root, encoding="ISO-8859-1", xml_declaration=True)
        self.write({
            "xml_file": base64.b64encode(xml_bytes),
            "xml_filename": f"ISLR_{rif_agente}_{period_str}.xml",
            "state": "done",
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "generate.xml.wh.islr",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
