# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class WizardFiscalBook(models.TransientModel):
    _name = "wizard.fiscal.book"
    _description = "Fiscal Book Generator Wizard"

    type = fields.Selection(
        [("purchase", "Purchase Book"), ("sale", "Sale Book")],
        string="Book Type",
        required=True,
        default="purchase",
    )
    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.context_today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.context_today)

    def action_create_book(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise UserError(_("The start date must be before the end date."))
        book = self.env["fiscal.book"].search([
            ("company_id", "=", self.env.company.id),
            ("type", "=", self.type),
            ("date_start", "=", self.date_start),
            ("date_end", "=", self.date_end),
            ("state", "!=", "cancel"),
        ], limit=1)
        if book and book.state != "draft":
            raise UserError(
                _("Fiscal book %s already exists for this period and is not in draft.")
                % book.name
            )
        if not book:
            title = "%s - %s" % (
                _("Libro de Compras") if self.type == "purchase" else _("Libro de Ventas"),
                self.date_start.strftime("%m/%Y"),
            )
            book = self.env["fiscal.book"].create({
                "name": title,
                "type": self.type,
                "date_start": self.date_start,
                "date_end": self.date_end,
            })
        book.action_update_book()
        return {
            "type": "ir.actions.act_window",
            "res_model": "fiscal.book",
            "res_id": book.id,
            "view_mode": "form",
            "target": "current",
        }
