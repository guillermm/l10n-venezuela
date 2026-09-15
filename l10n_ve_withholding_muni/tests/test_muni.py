# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestMunicipalWithholding(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        activity = cls.env.ref("l10n_ve_withholding_muni.activity_libertador_services", raise_if_not_found=False)
        extra = {"wh_muni_rate": 3.0}
        if activity:
            extra.update({
                "municipality_id": activity.municipality_id.id,
                "state_id": activity.municipality_id.state_id.id,
                "muni_activity_id": activity.id,
                "wh_muni_rate": activity.rate,
            })
        cls.supplier = cls._create_ve_partner("Proveedor Muni", "J403187649", **extra)

    def test_activity_uses_territorial_municipality(self):
        activity = self.env.ref("l10n_ve_withholding_muni.activity_libertador_services")
        libertador = self.env.ref("territorial_pd.municipio_101")
        self.assertEqual(activity.municipality_id, libertador)
        self.assertEqual(activity.municipality_id._name, "res.country.state.municipality")

    def test_activity_sets_rate_and_payment_withholds(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            nro_ctrl="00-60000001",
            ref="FAC-MUNI-1",
        )
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({"payment_date": "2025-09-01"})
        expected = bill.currency_id.round(bill.amount_untaxed * self.supplier.wh_muni_rate / 100.0)
        self.assertAlmostEqual(wizard.l10n_ve_muni_wh_amount, expected, places=2)
        wizard._create_payments()
        self.assertTrue(bill.wh_muni_id)
        self.assertTrue(bill.currency_id.is_zero(bill.amount_residual))
