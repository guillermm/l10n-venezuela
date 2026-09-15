# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestIgtf(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        cls.journal = cls.company_data["default_journal_bank"]
        cls.journal.l10n_ve_igtf_enabled = True
        cls.company.l10n_ve_igtf_rate = 3.0
        cls.supplier = cls._create_ve_partner("Proveedor IGTF", "J403187649")

    def test_outbound_payment_adds_igtf_line(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            nro_ctrl="00-90000001",
            ref="FAC-IGTF-1",
        )
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({
            "payment_date": "2025-09-01",
            "journal_id": self.journal.id,
            "l10n_ve_igtf_apply": True,
            "l10n_ve_igtf_rate": 3.0,
        })
        expected = wizard.currency_id.round(wizard.amount * 3.0 / 100.0)
        self.assertAlmostEqual(wizard.l10n_ve_igtf_amount, expected, places=2)
        payments = wizard._create_payments()
        payment = payments[:1] if payments and hasattr(payments, "ids") else self.env["account.payment"].search([
            ("partner_id", "=", self.supplier.id),
        ], order="id desc", limit=1)
        self.assertTrue(payment.l10n_ve_igtf_apply)
        self.assertAlmostEqual(
            payment.l10n_ve_igtf_amount,
            payment.currency_id.round(payment.amount * payment.l10n_ve_igtf_rate / 100.0),
            places=2,
        )
        igtf_lines = payment.move_id.line_ids.filtered(
            lambda line: line.account_id == self.company.l10n_ve_igtf_expense_account_id
        )
        self.assertTrue(igtf_lines)

    def test_vendor_bill_igtf_increases_total(self):
        move = self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.supplier.id,
            "invoice_date": "2025-09-01",
            "invoice_date_due": "2025-09-15",
            "nro_ctrl": "00-90000002",
            "supplier_invoice_number": "FAC-IGTF-BILL",
            "invoice_line_ids": [(0, 0, {
                "name": "Servicio IGTF",
                "quantity": 1,
                "price_unit": 1000.0,
                "account_id": self.company_data["default_account_expense"].id,
                "tax_ids": [(6, 0, [])],
            })],
        })
        base_total = move.amount_total
        move.write({
            "l10n_ve_igtf_apply": True,
            "l10n_ve_igtf_rate": 3.0,
        })
        expected = move.currency_id.round(base_total * 3.0 / 100.0)
        self.assertAlmostEqual(move.l10n_ve_igtf_amount, expected, places=2)
        move.action_post()
        self.assertAlmostEqual(move.amount_total, base_total + expected, places=2)
        self.assertTrue(move.invoice_line_ids.filtered(lambda line: line.l10n_ve_igtf_line))

    def test_payment_wizard_skips_igtf_when_already_on_bill(self):
        move = self.env["account.move"].create({
            "move_type": "in_invoice",
            "partner_id": self.supplier.id,
            "invoice_date": "2025-09-01",
            "invoice_date_due": "2025-09-15",
            "nro_ctrl": "00-90000003",
            "supplier_invoice_number": "FAC-IGTF-SKIP",
            "l10n_ve_igtf_apply": True,
            "l10n_ve_igtf_rate": 3.0,
            "invoice_line_ids": [(0, 0, {
                "name": "Servicio IGTF",
                "quantity": 1,
                "price_unit": 1000.0,
                "account_id": self.company_data["default_account_expense"].id,
                "tax_ids": [(6, 0, [])],
            })],
        })
        move.action_post()
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=move.ids,
        ).create({
            "payment_date": "2025-09-01",
            "journal_id": self.journal.id,
        })
        wizard._onchange_l10n_ve_igtf_defaults()
        self.assertFalse(wizard.l10n_ve_igtf_apply)
