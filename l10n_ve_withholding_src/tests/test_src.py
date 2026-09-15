# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSrcWithholding(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        cls.company.wh_src_rate = 5.0
        cls.supplier = cls._create_ve_partner(
            "Contratista SRC",
            "J403187649",
            wh_src_subject=True,
            wh_src_rate=5.0,
        )

    def test_src_default_five_percent_on_payment(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            nro_ctrl="00-70000001",
            ref="FAC-SRC-1",
        )
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({"payment_date": "2025-09-01"})
        self.assertAlmostEqual(wizard.l10n_ve_src_wh_amount, 50.0, places=2)
        wizard._create_payments()
        self.assertTrue(bill.wh_src_id)
        self.assertAlmostEqual(bill.wh_src_id.wh_rate, 5.0, places=2)
        self.assertTrue(bill.currency_id.is_zero(bill.amount_residual))
