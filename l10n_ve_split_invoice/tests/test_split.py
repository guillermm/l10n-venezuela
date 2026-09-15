# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSplitInvoice(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        cls.company.lines_invoice = 1
        cls.customer = cls._create_ve_partner("Cliente Split", "V123456781")

    def test_overflow_lines_move_to_draft_invoice(self):
        revenue = self.company_data["default_account_revenue"]
        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.customer.id,
            "invoice_date": "2025-09-01",
            "nro_ctrl": "00-51000001",
            "invoice_line_ids": [
                (0, 0, {"name": "Linea 1", "quantity": 1, "price_unit": 100.0, "account_id": revenue.id}),
                (0, 0, {"name": "Linea 2", "quantity": 1, "price_unit": 50.0, "account_id": revenue.id}),
            ],
        })
        move.action_post()
        extra = self.env["account.move"].search([("split_parent_id", "=", move.id)])
        self.assertEqual(len(extra), 1)
        self.assertEqual(extra.state, "draft")
        self.assertEqual(len(move._l10n_ve_invoice_lines()), 1)
        self.assertEqual(len(extra._l10n_ve_invoice_lines()), 1)
