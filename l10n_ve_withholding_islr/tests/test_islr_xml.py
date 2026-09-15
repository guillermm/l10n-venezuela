# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from xml.etree import ElementTree as ET

from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestIslrXml(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        cls.concept = cls.env.ref("l10n_ve_withholding_islr.concept_honorarios_prof")
        cls.supplier_pjdo = cls._create_ve_partner(
            "Honorarios PJDO",
            "J403187649",
            person_type="pjdo",
            islr_concept_id=cls.concept.id,
        )
        cls.supplier_pnre = cls._create_ve_partner(
            "Honorarios PNRE",
            "V123456781",
            person_type="pnre",
            islr_concept_id=cls.concept.id,
        )
        cls.supplier_pnnr = cls._create_ve_partner(
            "Honorarios PNNR",
            "E123456788",
            person_type="pnnr",
            islr_concept_id=cls.concept.id,
        )

    def _expected_pnre_amount(self, base):
        ut_val = self.env["l10n.ut"].get_amount_ut("2025-09-01")
        subtract_ves = 83.3334 * ut_val * 0.03
        ves = self.env["l10n.ut"].get_ves_currency()
        currency = self.company.currency_id
        subtract = subtract_ves
        if ves and currency and ves != currency:
            subtract = ves._convert(
                subtract_ves, currency, self.company, fields.Date.to_date("2025-09-01")
            )
        return currency.round(max(base * 0.03 - subtract, 0.0))

    def _create_voucher(self, partner, bill):
        voucher = self.env["account.wh.islr.doc"].create({
            "partner_id": partner.id,
            "company_id": self.company.id,
            "currency_id": self.company.currency_id.id,
            "type": "in_invoice",
            "date": "2025-09-01",
            "journal_id": self.company.wh_islr_journal_id.id,
            "line_ids": [(0, 0, {
                "move_id": bill.id,
                "concept_id": self.concept.id,
                "base_amount": bill.amount_untaxed,
            })],
        })
        voucher.line_ids.action_recompute_from_move()
        voucher.action_confirm()
        return voucher

    def _generate_xml(self):
        wizard = self.env["generate.xml.wh.islr"].create({
            "date_start": "2025-09-01",
            "date_end": "2025-09-30",
        })
        wizard.action_generate_xml()
        return ET.fromstring(base64.b64decode(wizard.xml_file))

    def test_pjdo_uses_code_004_and_five_percent(self):
        bill = self._create_vendor_bill(self.supplier_pjdo, amount=10000.0, nro_ctrl="00-20000001")
        voucher = self._create_voucher(self.supplier_pjdo, bill)
        line = voucher.line_ids
        self.assertEqual(line.seniat_code, "004")
        self.assertAlmostEqual(line.wh_percentage, 5.0)
        self.assertAlmostEqual(line.amount_ret, 500.0, places=2)

        root = self._generate_xml()
        det = root.find("DetalleRetencion")
        self.assertEqual(det.findtext("CodigoConcepto"), "004")
        self.assertEqual(det.findtext("PorcentajeRetencion"), "5.00")
        self.assertEqual(det.findtext("RifRetenido"), "J403187649")

    def test_pnnr_xml_uses_rate_code_not_concept_code(self):
        bill = self._create_vendor_bill(self.supplier_pnnr, amount=10000.0, nro_ctrl="00-20000002")
        voucher = self._create_voucher(self.supplier_pnnr, bill)
        self.assertEqual(self.concept.code, "002")
        self.assertEqual(voucher.line_ids.seniat_code, "003")
        root = self._generate_xml()
        self.assertEqual(root.find("DetalleRetencion").findtext("CodigoConcepto"), "003")

    def test_pnre_applies_ut_sustraendo(self):
        bill = self._create_vendor_bill(self.supplier_pnre, amount=10000.0, nro_ctrl="00-20000003")
        voucher = self._create_voucher(self.supplier_pnre, bill)
        line = voucher.line_ids
        self.assertEqual(line.seniat_code, "002")
        self.assertAlmostEqual(line.amount_ret, self._expected_pnre_amount(10000.0), places=2)
        self.assertGreater(line.subtract_amount, 0.0)

    def test_register_payment_creates_voucher(self):
        bill = self._create_vendor_bill(self.supplier_pjdo, amount=10000.0, nro_ctrl="00-20000004")
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({"payment_date": "2025-09-01"})
        self.assertAlmostEqual(wizard.l10n_ve_islr_amount, 500.0, places=2)
        wizard._create_payments()
        self.assertTrue(bill.wh_islr_doc_id)
        self.assertEqual(bill.wh_islr_doc_id.line_ids.seniat_code, "004")
        self.assertTrue(bill.currency_id.is_zero(bill.amount_residual))
        self.assertIn(bill.payment_state, ("paid", "in_payment"))
