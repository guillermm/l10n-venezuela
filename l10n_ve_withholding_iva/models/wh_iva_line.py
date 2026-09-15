# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountWhIvaLine(models.Model):
    _name = "account.wh.iva.line"
    _description = "VAT Withholding Voucher Line"

    wh_iva_id = fields.Many2one(
        comodel_name="account.wh.iva",
        string="Voucher",
        ondelete="cascade",
        required=True,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        required=True,
        domain="[('partner_id', '=', parent.partner_id), ('move_type', 'in', ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'))]",
    )
    tax_line_ids = fields.One2many(
        comodel_name="account.wh.iva.line.tax",
        inverse_name="wh_iva_line_id",
        string="Taxes Breakdown",
        copy=True,
    )
    base_amount = fields.Monetary(
        string="Base Amount",
        compute="_compute_line_totals",
        store=True,
        currency_field="currency_id",
    )
    tax_amount = fields.Monetary(
        string="Tax Amount",
        compute="_compute_line_totals",
        store=True,
        currency_field="currency_id",
    )
    amount_ret = fields.Monetary(
        string="Withheld Amount",
        compute="_compute_line_totals",
        store=True,
        currency_field="currency_id",
    )
    exempt_amount = fields.Monetary(
        string="Exempt Amount",
        compute="_compute_line_totals",
        store=True,
        currency_field="currency_id",
    )
    wh_rate = fields.Float(
        string="Retention Rate (%)",
        default=75.0,
    )
    currency_id = fields.Many2one(
        related="wh_iva_id.currency_id",
        store=True,
    )

    @api.depends(
        "tax_line_ids.base_amount",
        "tax_line_ids.tax_amount",
        "tax_line_ids.amount_ret",
        "tax_line_ids.is_exempt",
    )
    def _compute_line_totals(self):
        for line in self:
            taxable = line.tax_line_ids.filtered(lambda rec: not rec.is_exempt)
            exempt = line.tax_line_ids.filtered("is_exempt")
            line.base_amount = sum(taxable.mapped("base_amount"))
            line.tax_amount = sum(taxable.mapped("tax_amount"))
            line.amount_ret = sum(taxable.mapped("amount_ret"))
            line.exempt_amount = sum(exempt.mapped("base_amount"))

    def _prepare_tax_lines_vals(self):
        self.ensure_one()
        rate = self.wh_iva_id.partner_id.wh_iva_rate or 75.0
        vals = []
        move = self.move_id
        if not move:
            return rate, vals
        for tax_line in move.line_ids.filtered(lambda rec: rec.tax_line_id):
            tax = tax_line.tax_line_id
            is_exempt = tax.appl_type in ("exento", "sdcf") or not tax.amount
            base = tax_line.tax_base_amount or abs(tax_line.balance)
            tax_amt = 0.0 if is_exempt else abs(tax_line.balance)
            vals.append({
                "tax_id": tax.id,
                "base_amount": base,
                "tax_amount": tax_amt,
                "wh_rate": 0.0 if is_exempt else rate,
                "is_exempt": is_exempt,
            })
        for inv_line in move.invoice_line_ids.filtered(
            lambda rec: rec.display_type == "product"
            and not rec.tax_ids
            and not getattr(rec, "l10n_ve_igtf_line", False)
        ):
            vals.append({
                "base_amount": abs(inv_line.balance) or inv_line.price_subtotal,
                "tax_amount": 0.0,
                "wh_rate": 0.0,
                "is_exempt": True,
            })
        return rate, vals

    def action_recompute_from_move(self):
        for line in self:
            rate, vals = line._prepare_tax_lines_vals()
            line.tax_line_ids.unlink()
            line.write({
                "wh_rate": rate,
                "tax_line_ids": [(0, 0, val) for val in vals],
            })
        return True

    @api.onchange("move_id")
    def _onchange_move_id(self):
        if self.move_id:
            rate, vals = self._prepare_tax_lines_vals()
            self.wh_rate = rate
            self.tax_line_ids = [(5, 0, 0)] + [(0, 0, val) for val in vals]
