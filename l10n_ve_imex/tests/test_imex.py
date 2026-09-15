# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.l10n_ve_fiscal_requirements.tests.common import L10nVeSetupMixin
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestImex(L10nVeSetupMixin, AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls._l10n_ve_setup()
        purchase_tax = cls.company_data["default_tax_purchase"]
        tax_group = cls.env["account.tax.group"].create({
            "name": "IVA VE imex",
            "country_id": cls.ve_country.id,
        })
        cls.tax = purchase_tax.copy({"name": "IVA 16% imex", "amount": 16.0})
        cls.tax.write({
            "country_id": cls.ve_country.id,
            "tax_group_id": tax_group.id,
            "appl_type": "general",
        })
        cls.supplier = cls._create_ve_partner(
            "Importador",
            "J403187649",
            wh_iva_rate=75.0,
            wh_iva_agent=True,
        )

    def test_import_in_book_and_iva_txt(self):
        bill = self._create_vendor_bill(
            self.supplier,
            amount=1000.0,
            taxes=self.tax,
            nro_ctrl="00-80000001",
            ref="FAC-IMP-1",
        )
        declaration = self.env["customs.declaration"].create({
            "name": "C86-2025-001",
            "expediente": "EXP-99086-1",
            "date": "2025-09-01",
            "declaration_type": "dua",
            "move_ids": [(6, 0, bill.ids)],
        })
        declaration.action_confirm()
        self.assertEqual(bill.customs_declaration_id, declaration)

        book = self.env["fiscal.book"].create({
            "name": "Libro importación",
            "type": "purchase",
            "date_start": "2025-09-01",
            "date_end": "2025-09-30",
        })
        book.action_update_book()
        line = book.line_ids.filtered(lambda rec: rec.move_id == bill)
        self.assertEqual(line.doc_type, "05")
        self.assertEqual(line.customs_number, "C86-2025-001")
        self.assertEqual(line.expediente, "EXP-99086-1")

        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=bill.ids,
        ).create({"payment_date": "2025-09-01"})
        wizard._create_payments()
        txt_wizard = self.env["generate.txt.wh.iva"].create({
            "date_start": "2025-09-01",
            "date_end": "2025-09-15",
        })
        txt_wizard.action_generate_txt()
        row = base64.b64decode(txt_wizard.txt_file).decode("latin-1").strip().split("\r\n")[0]
        cols = row.split("\t")
        self.assertEqual(cols[4], "05")
        self.assertEqual(cols[6], "C86-2025-001")
        self.assertEqual(cols[15], "EXP-99086-1")
