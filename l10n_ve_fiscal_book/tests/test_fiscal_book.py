# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestFiscalBook(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        purchase_tax = cls.company_data["default_tax_purchase"]
        tax_group = cls.env["account.tax.group"].create({
            "name": "IVA VE book",
            "country_id": cls.ve_country.id,
        })
        cls.tax = purchase_tax.copy({
            "name": "IVA 16% book",
            "amount": 16.0,
        })
        cls.tax.write({
            "country_id": cls.ve_country.id,
            "tax_group_id": tax_group.id,
            "appl_type": "general",
        })
        cls.supplier = cls._create_ve_partner(
            "Proveedor Libro",
            "J403187649",
            wh_iva_rate=75.0,
            wh_iva_agent=True,
        )

    def _ves(self, amount, date="2025-09-01"):
        return self.env["l10n.ut"].amount_to_ves(
            amount, self.company.currency_id, date, self.company
        )

    def _create_book(self, book_type="purchase", start="2025-09-01", end="2025-09-30"):
        book = self.env["fiscal.book"].create({
            "name": "Libro %s %s" % (book_type, start),
            "type": book_type,
            "date_start": start,
            "date_end": end,
        })
        book.action_update_book()
        return book

    def test_purchase_book_classifies_general_aliquot(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            taxes=self.tax,
            nro_ctrl="00-40000001",
            ref="FAC-LIB-1",
        )
        book = self._create_book()
        self.assertEqual(len(book.line_ids), 1)
        line = book.line_ids
        self.assertEqual(line.doc_type, "01")
        self.assertEqual(line.invoice_number, "FAC-LIB-1")
        self.assertAlmostEqual(line.base_general, self._ves(1000.0), places=2)
        self.assertAlmostEqual(line.tax_general, self._ves(160.0), places=2)
        self.assertAlmostEqual(book.total_base_general, self._ves(1000.0), places=2)
        self.assertTrue(book.tax_ids.filtered(lambda rec: rec.appl_type == "general"))

    def test_credit_note_is_negative_and_keeps_affected_number(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            taxes=self.tax,
            nro_ctrl="00-40000002",
            ref="FAC-LIB-2",
        )
        refund = self.env["account.move"].create({
            "move_type": "in_refund",
            "partner_id": self.supplier.id,
            "invoice_date": "2025-09-10",
            "invoice_date_due": "2025-09-15",
            "nro_ctrl": "00-40000003",
            "supplier_invoice_number": "NC-LIB-2",
            "reversed_entry_id": bill.id,
            "invoice_line_ids": [(0, 0, {
                "name": "Devolución",
                "quantity": 1,
                "price_unit": 1000.0,
                "account_id": self.company_data["default_account_expense"].id,
                "tax_ids": [(6, 0, self.tax.ids)],
            })],
        })
        refund.action_post()
        book = self._create_book()
        nc = book.line_ids.filtered(lambda rec: rec.move_id == refund)
        self.assertEqual(nc.doc_type, "03")
        self.assertEqual(nc.affected_number, "FAC-LIB-2")
        self.assertAlmostEqual(nc.base_general, -self._ves(1000.0), places=2)
        self.assertAlmostEqual(nc.tax_general, -self._ves(160.0), places=2)

    def _confirm_iva_voucher(self, bill, date=None):
        bill.action_generate_wh_iva()
        voucher = bill.wh_iva_id
        if date:
            voucher.write({"date": date})
        voucher.action_confirm()
        self.assertTrue(voucher.total_ret_amount, "VAT withholding voucher must have a retained amount")
        return voucher

    def test_withholding_follows_voucher_period(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            taxes=self.tax,
            nro_ctrl="00-40000004",
            ref="FAC-LIB-3",
        )
        voucher = self._confirm_iva_voucher(bill, date="2025-10-05")
        september = self._create_book(start="2025-09-01", end="2025-09-30")
        self.assertEqual(len(september.line_ids), 1)
        self.assertFalse(september.line_ids.withholding_only)
        self.assertAlmostEqual(september.line_ids.vat_withheld, 0.0, places=2)
        october = self._create_book(start="2025-10-01", end="2025-10-31")
        self.assertEqual(len(october.line_ids), 1)
        self.assertTrue(october.line_ids.withholding_only)
        self.assertAlmostEqual(
            october.line_ids.vat_withheld,
            self._ves(voucher.total_ret_amount, "2025-10-05"),
            places=2,
        )

    def test_same_period_withholding_stays_on_invoice_line(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            taxes=self.tax,
            nro_ctrl="00-40000006",
            ref="FAC-LIB-4",
        )
        voucher = self._confirm_iva_voucher(bill)
        book = self._create_book()
        self.assertEqual(len(book.line_ids), 1)
        self.assertFalse(book.line_ids.withholding_only)
        self.assertTrue(book.line_ids.voucher_number)
        self.assertAlmostEqual(
            book.line_ids.vat_withheld,
            self._ves(voucher.total_ret_amount),
            places=2,
        )

    def test_sale_book_classifies_general_aliquot(self):
        sale_tax = self.company_data["default_tax_sale"].copy({
            "name": "IVA 16% sale book",
            "amount": 16.0,
        })
        tax_group = self.env["account.tax.group"].create({
            "name": "IVA VE sale book",
            "country_id": self.ve_country.id,
        })
        sale_tax.write({
            "country_id": self.ve_country.id,
            "tax_group_id": tax_group.id,
            "appl_type": "general",
        })
        customer = self._create_ve_partner("Cliente Libro", "V123456781")
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": customer.id,
            "invoice_date": "2025-09-01",
            "invoice_date_due": "2025-09-15",
            "nro_ctrl": "00-50000001",
            "invoice_line_ids": [(0, 0, {
                "name": "Servicio",
                "quantity": 1,
                "price_unit": 1000.0,
                "account_id": self.company_data["default_account_revenue"].id,
                "tax_ids": [(6, 0, sale_tax.ids)],
            })],
        })
        invoice.action_post()
        book = self._create_book(book_type="sale")
        self.assertEqual(len(book.line_ids), 1)
        self.assertEqual(book.article_number, "76")
        self.assertAlmostEqual(book.line_ids.base_general, self._ves(1000.0), places=2)
        self.assertAlmostEqual(book.line_ids.tax_general, self._ves(160.0), places=2)

    def test_wizard_reuses_draft_book(self):
        first = self._create_book()
        action = self.env["wizard.fiscal.book"].create({
            "type": "purchase",
            "date_start": "2025-09-01",
            "date_end": "2025-09-30",
        }).action_create_book()
        self.assertEqual(action["res_id"], first.id)

    def test_posted_book_locks_period(self):
        book = self._create_book()
        book.action_confirm()
        book.action_done()
        with self.assertRaises(UserError):
            self._create_vendor_bill(
                self.supplier,
                amount=100.0,
                taxes=self.tax,
                nro_ctrl="00-40000005",
                ref="FAC-LOCK",
            )
        book.with_context(l10n_ve_unlock_book=True).action_draft()
        move = self._create_vendor_bill(
            self.supplier,
            amount=100.0,
            taxes=self.tax,
            nro_ctrl="00-40000005",
            ref="FAC-LOCK",
        )
        self.assertEqual(move.state, "posted")

    def test_export_xlsx_has_content(self):
        self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            taxes=self.tax,
            nro_ctrl="00-40000007",
            ref="FAC-XLSX-1",
        )
        book = self._create_book()
        action = book.action_export_xlsx()
        self.assertEqual(action["type"], "ir.actions.act_url")
        attachment_id = int(action["url"].split("/web/content/")[1].split("?")[0])
        attachment = self.env["ir.attachment"].browse(attachment_id)
        self.assertTrue(attachment.datas)
        self.assertGreater(len(base64.b64decode(attachment.datas)), 100)
        self.assertIn(".xlsx", attachment.name)

    def test_overlapping_books_are_rejected(self):
        self._create_book()
        with self.assertRaises(ValidationError):
            self.env["fiscal.book"].create({
                "name": "Duplicado",
                "type": "purchase",
                "date_start": "2025-09-15",
                "date_end": "2025-10-15",
            })
