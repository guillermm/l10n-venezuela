# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    split_parent_id = fields.Many2one(
        comodel_name="account.move",
        string="Split Parent Invoice",
        copy=False,
    )

    def _l10n_ve_invoice_lines(self):
        self.ensure_one()
        return self.invoice_line_ids.filtered(lambda line: line.display_type == "product")

    def _l10n_ve_prepare_split_line_vals(self, line):
        vals = {
            "name": line.name,
            "product_id": line.product_id.id,
            "product_uom_id": line.product_uom_id.id,
            "quantity": line.quantity,
            "price_unit": line.price_unit,
            "discount": line.discount,
            "tax_ids": [(6, 0, line.tax_ids.ids)],
            "account_id": line.account_id.id,
        }
        if "islr_concept_id" in line._fields:
            vals["islr_concept_id"] = line.islr_concept_id.id
        return vals

    def split_invoice(self):
        """Copy overflowing product lines into a new draft invoice."""
        for move in self:
            limit = move.company_id.lines_invoice
            if limit < 1 or move.move_type not in ("out_invoice", "out_refund"):
                continue
            product_lines = move._l10n_ve_invoice_lines()
            if len(product_lines) <= limit:
                continue
            extra_lines = product_lines[limit:]
            new_move = self.env["account.move"].create({
                "move_type": move.move_type,
                "partner_id": move.partner_id.id,
                "journal_id": move.journal_id.id,
                "invoice_date": move.invoice_date,
                "date": move.date,
                "currency_id": move.currency_id.id,
                "company_id": move.company_id.id,
                "split_parent_id": move.id,
                "invoice_line_ids": [
                    (0, 0, self._l10n_ve_prepare_split_line_vals(line))
                    for line in extra_lines
                ],
            })
            extra_lines.with_context(check_move_validity=False).unlink()
            move.message_post(body=_("Split invoice created: %s") % new_move.display_name)
        return True

    def _post(self, soft=True):
        self.filtered(lambda move: move.state == "draft").split_invoice()
        return super()._post(soft=soft)
