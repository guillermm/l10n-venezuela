# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_ve_fiscal_book_type(self):
        self.ensure_one()
        if self.move_type in ("in_invoice", "in_refund"):
            return "purchase"
        if self.move_type in ("out_invoice", "out_refund"):
            return "sale"
        return False

    def _l10n_ve_find_locked_book(self):
        self.ensure_one()
        book_type = self._l10n_ve_fiscal_book_type()
        if not book_type:
            return self.env["fiscal.book"]
        date = self.date_document or self.invoice_date or self.date
        if not date:
            return self.env["fiscal.book"]
        return self.env["fiscal.book"].search([
            ("company_id", "=", self.company_id.id),
            ("type", "=", book_type),
            ("state", "=", "done"),
            ("date_start", "<=", date),
            ("date_end", ">=", date),
        ], limit=1)

    def _l10n_ve_check_fiscal_book_lock(self):
        for move in self:
            if not move.is_invoice(include_receipts=True):
                continue
            book = move._l10n_ve_find_locked_book()
            if book:
                raise UserError(
                    _(
                        "Cannot post %(move)s: period %(start)s to %(end)s is locked by "
                        "fiscal book %(book)s."
                    )
                    % {
                        "move": move.display_name,
                        "start": book.date_start,
                        "end": book.date_end,
                        "book": book.name,
                    }
                )

    def _post(self, soft=True):
        self._l10n_ve_check_fiscal_book_lock()
        return super()._post(soft=soft)
