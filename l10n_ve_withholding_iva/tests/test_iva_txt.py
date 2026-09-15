# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestIvaTxt(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        purchase_tax = cls.company_data["default_tax_purchase"]
        tax_group = cls.env["account.tax.group"].create({
            "name": "IVA VE test",
            "country_id": cls.ve_country.id,
        })
        cls.tax = purchase_tax.copy({
            "name": "IVA 16% test",
            "amount": 16.0,
        })
        cls.tax.write({
            "country_id": cls.ve_country.id,
            "tax_group_id": tax_group.id,
            "appl_type": "general",
        })
        cls.supplier = cls._create_ve_partner(
            "Proveedor IVA",
            "J555555554",
            person_type="pjdo",
            wh_iva_rate=75.0,
            wh_iva_agent=True,
        )

    def test_iva_withholding_and_txt_columns(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            taxes=self.tax,
            nro_ctrl="00-30000001",
            ref="FAC-IVA-1",
        )
        self.assertAlmostEqual(bill.amount_tax, 160.0, places=2)

        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({"payment_date": "2025-09-01"})
        self.assertAlmostEqual(wizard.l10n_ve_iva_wh_amount, 120.0, places=2)
        wizard._create_payments()

        voucher = bill.wh_iva_id
        self.assertTrue(voucher)
        self.assertEqual(voucher.state, "done")
        self.assertAlmostEqual(voucher.total_ret_amount, 120.0, places=2)
        self.assertTrue(bill.currency_id.is_zero(bill.amount_residual))
        self.assertIn(bill.payment_state, ("paid", "in_payment"))

        txt_wizard = self.env["generate.txt.wh.iva"].create({
            "date_start": "2025-09-01",
            "date_end": "2025-09-15",
        })
        txt_wizard.action_generate_txt()
        content = base64.b64decode(txt_wizard.txt_file).decode("latin-1")
        row = content.strip().split("\r\n")[0]
        cols = row.split("\t")
        self.assertEqual(len(cols), 16)
        self.assertEqual(cols[0], "J000000000")
        self.assertEqual(cols[1], "202509")
        self.assertEqual(cols[2], "2025-09-01")
        self.assertEqual(cols[3], "C")
        self.assertEqual(cols[4], "01")
        self.assertEqual(cols[5], "J555555554")
        self.assertEqual(cols[6], "FAC-IVA-1")
        self.assertEqual(cols[7], "00-30000001")
        self.assertEqual(cols[14], "16.00")
