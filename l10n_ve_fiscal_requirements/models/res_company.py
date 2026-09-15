# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import calendar

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .l10n_ve_account_codes import (
    ACCOUNT_CODE_DIGITS,
    ACCOUNT_CODES,
    COMPANY_ACCOUNT_FIELDS,
)


class ResCompany(models.Model):
    _inherit = "res.company"

    jour_id = fields.Many2one(
        comodel_name="account.journal",
        string="Damaged Invoices Journal",
        check_company=True,
        help="Default journal for damaged/void invoices",
    )
    acc_id = fields.Many2one(
        comodel_name="account.account",
        string="Damaged Invoices Account",
        check_company=True,
        help="Default account used for damaged/void invoices",
    )
    printer_fiscal = fields.Boolean(
        string="Manages Fiscal Printer",
        help="Indicates that the company operates a fiscal printer",
    )
    l10n_ve_account_code_digits = fields.Integer(
        string="Account Code Digits",
        default=ACCOUNT_CODE_DIGITS,
        help="Odoo 17 / VEN-NIF uses 7-digit account codes. "
        "Master/19.0 uses 6 digits with the same 4-digit groups.",
    )

    def _l10n_ve_find_account(self, *codes, prefixes=()):
        """Return the first company account matching a 7-digit code or prefix."""
        self.ensure_one()
        Account = self.env["account.account"]
        domain_company = [("company_id", "=", self.id), ("deprecated", "=", False)]
        for code in codes:
            if not code:
                continue
            account = Account.search(domain_company + [("code", "=", code)], limit=1)
            if account:
                return account
        for prefix in prefixes:
            account = Account.search(
                domain_company + [("code", "=like", "%s%%" % prefix)],
                order="code",
                limit=1,
            )
            if account:
                return account
        return Account

    def _l10n_ve_account(self, key):
        self.ensure_one()
        return self._l10n_ve_find_account(*ACCOUNT_CODES.get(key, ()))

    def _l10n_ve_fill_missing_accounts(self):
        """Fill empty fiscal accounts from the official 7-digit chart."""
        companies = self or self.search([])
        for company in companies:
            vals = {}
            for fname, key in COMPANY_ACCOUNT_FIELDS:
                if fname not in company._fields or company[fname]:
                    continue
                account = company._l10n_ve_account(key)
                if account:
                    vals[fname] = account.id
            if vals:
                company.write(vals)
        return True

    @api.model
    def _l10n_ve_setup_bolivar_currency(self):
        """Use current VES (symbol Bs), not obsolete VEF (Bs.F)."""
        ves = self.env.ref("base.VES", raise_if_not_found=False)
        vef = self.env.ref("base.VEF", raise_if_not_found=False)
        ve = self.env.ref("base.ve", raise_if_not_found=False)
        if not ves:
            return True
        ves.sudo().write(
            {
                "active": True,
                "symbol": "Bs",
                "full_name": "Venezuelan bolívar soberano",
                "position": "after",
                "rounding": 0.01,
                "currency_unit_label": False,
                "currency_subunit_label": False,
            }
        )
        if ve and ve.currency_id != ves:
            ve.sudo().write({"currency_id": ves.id})
        if not vef or vef == ves:
            return True
        companies = self.env["res.company"].sudo().search([("currency_id", "=", vef.id)])
        for company in companies:
            company._l10n_ve_switch_company_currency(vef, ves)
        if not self.env["res.company"].sudo().search_count(
            [("currency_id", "=", vef.id)]
        ):
            vef.sudo().write({"active": False})
        return True

    def _l10n_ve_switch_company_currency(self, old_currency, new_currency):
        """Point the company to VES. VEF and VES are the same bolívar (1:1)."""
        self.ensure_one()
        if self.currency_id != old_currency or old_currency == new_currency:
            return
        if self.root_id._existing_accounting():
            self.env.cr.execute(
                """
                UPDATE res_company
                   SET currency_id = %s
                 WHERE id = %s AND currency_id = %s
                """,
                (new_currency.id, self.id, old_currency.id),
            )
        else:
            self.write({"currency_id": new_currency.id})
        self.invalidate_recordset(["currency_id"])
        self.env.cr.execute(
            """
            UPDATE account_move
               SET currency_id = %s
             WHERE company_id = %s AND currency_id = %s
            """,
            (new_currency.id, self.id, old_currency.id),
        )
        self.env.cr.execute(
            """
            UPDATE account_move_line
               SET currency_id = %s
             WHERE company_id = %s AND currency_id = %s
            """,
            (new_currency.id, self.id, old_currency.id),
        )
        self.env.cr.execute(
            """
            UPDATE account_journal
               SET currency_id = %s
             WHERE company_id = %s AND currency_id = %s
            """,
            (new_currency.id, self.id, old_currency.id),
        )
        self.env.cr.execute(
            """
            UPDATE account_account
               SET currency_id = %s
             WHERE company_id = %s AND currency_id = %s
            """,
            (new_currency.id, self.id, old_currency.id),
        )
        self.env["account.move"].invalidate_model(["currency_id"])
        self.env["account.move.line"].invalidate_model(["currency_id"])
        self.env["account.journal"].invalidate_model(["currency_id"])
        self.env["account.account"].invalidate_model(["currency_id"])

    def _l10n_ve_find_iva_16(self, type_tax_use):
        """Return the general 16% IVA tax used as company default."""
        self.ensure_one()
        taxes = self.env["account.tax"].search(
            [
                ("company_id", "=", self.id),
                ("type_tax_use", "=", type_tax_use),
                ("amount_type", "=", "percent"),
                ("appl_type", "=", "general"),
            ]
        )
        taxes = taxes.filtered(lambda tax: abs(tax.amount - 16.0) < 0.1)
        if not taxes:
            return self.env["account.tax"]
        suffix = "tax1sale" if type_tax_use == "sale" else "tax1purchase"
        xmlids = taxes.get_external_id()
        for tax in taxes:
            if (xmlids.get(tax.id) or "").endswith(suffix):
                return tax
        named = taxes.filtered(
            lambda tax: (tax.name or "").strip().upper().replace(" ", "")
            in ("IVA16%", "16%")
        )
        return named[:1] or taxes.sorted("id")[:1]

    def _l10n_ve_set_default_iva_taxes(self):
        """Use IVA 16% as Accounting default for sales and purchases."""
        ve = self.env.ref("base.ve", raise_if_not_found=False)
        companies = self or self.search([])
        if ve:
            companies = companies.filtered(
                lambda company: company.country_id == ve
                or company.account_fiscal_country_id == ve
            )
        for company in companies:
            vals = {}
            for fname, tax_use in (
                ("account_sale_tax_id", "sale"),
                ("account_purchase_tax_id", "purchase"),
            ):
                if fname not in company._fields:
                    continue
                iva16 = company._l10n_ve_find_iva_16(tax_use)
                if iva16 and company[fname] != iva16:
                    vals[fname] = iva16.id
            if vals:
                company.write(vals)
        return True

    @api.model
    def _l10n_ve_default_account_id(self, key):
        account = self.env.company._l10n_ve_account(key)
        return account.id if account else False

    def _l10n_ve_next_nro_ctrl(self, seq_date=None):
        """Return the next sales control number for this company."""
        self.ensure_one()
        seq_date = fields.Date.to_date(seq_date) or fields.Date.context_today(self)
        sequence = self.env["ir.sequence"].sudo().search(
            [("code", "=", "l10n.ve.nro.ctrl"), ("company_id", "=", self.id)],
            limit=1,
        )
        if not sequence:
            sequence = self.env["ir.sequence"].sudo().create(
                {
                    "name": _("Control Number (%s)", self.name),
                    "code": "l10n.ve.nro.ctrl",
                    "padding": 8,
                    "implementation": "no_gap",
                    "use_date_range": True,
                    "company_id": self.id,
                }
            )
        range_model = self.env["ir.sequence.date_range"].sudo()
        if not range_model.search_count(
            [
                ("sequence_id", "=", sequence.id),
                ("date_from", "<=", seq_date),
                ("date_to", ">=", seq_date),
            ]
        ):
            last_day = calendar.monthrange(seq_date.year, seq_date.month)[1]
            range_model.create(
                {
                    "sequence_id": sequence.id,
                    "date_from": seq_date.replace(day=1),
                    "date_to": seq_date.replace(day=last_day),
                }
            )
        number = sequence.next_by_id(sequence_date=seq_date)
        if not number:
            raise UserError(
                _("Could not generate a control number for company %s.") % self.display_name
            )
        return number
