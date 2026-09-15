# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSalePurchaseIslr(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        cls.concept = cls.env["islr.wh.concept"].search([], limit=1)
        if not cls.concept:
            raise AssertionError("ISLR SENIAT catalog must be loaded")
        cls.product = cls.env["product.product"].create({
            "name": "Servicio con ISLR",
            "type": "service",
            "list_price": 1000.0,
            "islr_concept_id": cls.concept.id,
            "taxes_id": [(6, 0, [])],
            "supplier_taxes_id": [(6, 0, [])],
        })
        cls.customer = cls._create_ve_partner("Cliente ISLR", "V123456781")
        cls.supplier = cls._create_ve_partner("Proveedor ISLR", "J403187649")

    def test_sale_line_copies_product_concept(self):
        order = self.env["sale.order"].create({
            "partner_id": self.customer.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": 1000.0,
            })],
        })
        self.assertEqual(order.order_line.islr_concept_id, self.concept)

    def test_purchase_line_copies_product_concept(self):
        order = self.env["purchase.order"].create({
            "partner_id": self.supplier.id,
            "order_line": [(0, 0, {
                "product_id": self.product.id,
                "product_qty": 1,
                "price_unit": 1000.0,
            })],
        })
        self.assertEqual(order.order_line.islr_concept_id, self.concept)
