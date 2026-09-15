# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestVatWriteOff(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()

    def test_write_off_appears_in_purchase_book(self):
        book = self.env["fiscal.book"].create({
            "name": "Libro ajuste",
            "type": "purchase",
            "date_start": "2025-09-01",
            "date_end": "2025-09-30",
        })
        writeoff = self.env["vat.write.off"].create({
            "name": "AJUSTE-CF-1",
            "date": "2025-09-10",
            "journal_id": self.company_data["default_journal_misc"].id,
            "debit_account_id": self.company_data["default_account_expense"].id,
            "credit_account_id": self.company_data["default_account_payable"].id,
            "amount": 100.0,
            "purchase_book_id": book.id,
        })
        writeoff.action_post()
        self.assertEqual(writeoff.state, "done")
        self.assertTrue(writeoff.move_id)
        book.invalidate_recordset()
        line = book.line_ids.filtered("is_adjustment")
        self.assertEqual(len(line), 1)
        self.assertEqual(line.doc_type, "04")
        self.assertAlmostEqual(line.tax_general, -self.env["l10n.ut"].amount_to_ves(
            100.0, self.company.currency_id, "2025-09-10", self.company
        ), places=2)
