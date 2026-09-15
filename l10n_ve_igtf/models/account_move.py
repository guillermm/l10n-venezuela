# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ve_igtf_apply = fields.Boolean(
        string="Apply IGTF",
        copy=False,
        help="Adds an IGTF expense line on this vendor bill and increases the residual. "
        "Do not apply IGTF again when paying this bill.",
    )
    l10n_ve_igtf_rate = fields.Float(
        string="IGTF Rate (%)",
        default=lambda self: self.env.company.l10n_ve_igtf_rate,
    )
    l10n_ve_igtf_amount = fields.Monetary(
        string="IGTF Amount",
        currency_field="currency_id",
        compute="_compute_l10n_ve_igtf_amount",
        store=True,
    )

    @api.onchange("company_id")
    def _onchange_l10n_ve_igtf_company(self):
        if self.company_id:
            self.l10n_ve_igtf_rate = self.company_id.l10n_ve_igtf_rate

    def _l10n_ve_igtf_taxable_base(self):
        self.ensure_one()
        lines = self.invoice_line_ids.filtered(
            lambda line: line.display_type == "product" and not line.l10n_ve_igtf_line
        )
        return sum(lines.mapped("price_total"))

    @api.depends(
        "invoice_line_ids.price_total",
        "invoice_line_ids.l10n_ve_igtf_line",
        "l10n_ve_igtf_apply",
        "l10n_ve_igtf_rate",
        "currency_id",
    )
    def _compute_l10n_ve_igtf_amount(self):
        for move in self:
            if not move.l10n_ve_igtf_apply or move.move_type not in ("in_invoice", "in_refund"):
                move.l10n_ve_igtf_amount = 0.0
                continue
            amount = move._l10n_ve_igtf_taxable_base() * move.l10n_ve_igtf_rate / 100.0
            move.l10n_ve_igtf_amount = move.currency_id.round(amount) if move.currency_id else amount

    def _l10n_ve_sync_igtf_invoice_line(self):
        for move in self:
            if move.move_type not in ("in_invoice", "in_refund") or move.state != "draft":
                continue
            existing = move.invoice_line_ids.filtered(lambda line: line.l10n_ve_igtf_line)
            if not move.l10n_ve_igtf_apply:
                existing.unlink()
                continue
            if move.l10n_ve_igtf_rate <= 0:
                raise UserError(_("The IGTF rate must be greater than zero."))
            account = move.company_id.l10n_ve_igtf_expense_account_id
            if not account:
                raise UserError(_("Configure the IGTF expense account first."))
            amount = move.l10n_ve_igtf_amount
            if move.currency_id.is_zero(amount):
                existing.unlink()
                continue
            vals = {
                "name": _("IGTF %s%%") % move.l10n_ve_igtf_rate,
                "quantity": 1,
                "price_unit": amount,
                "account_id": account.id,
                "tax_ids": [(6, 0, [])],
                "l10n_ve_igtf_line": True,
            }
            if existing:
                existing[:1].write(vals)
                existing[1:].unlink()
            else:
                move.write({"invoice_line_ids": [(0, 0, vals)]})

    def _post(self, soft=True):
        self._l10n_ve_sync_igtf_invoice_line()
        return super()._post(soft=soft)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_ve_igtf_line = fields.Boolean(string="IGTF Line", copy=False)
