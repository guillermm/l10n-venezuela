# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class VatWriteOff(models.Model):
    _name = "vat.write.off"
    _description = "VAT Write Off"
    _check_company_auto = True

    name = fields.Char(string="Reference", required=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    purchase_book_id = fields.Many2one("fiscal.book", string="Purchase Book", domain="[('type', '=', 'purchase')]")
    sale_book_id = fields.Many2one("fiscal.book", string="Sale Book", domain="[('type', '=', 'sale')]")
    journal_id = fields.Many2one("account.journal", string="Journal")
    debit_account_id = fields.Many2one("account.account", string="Debit Account", check_company=True)
    credit_account_id = fields.Many2one("account.account", string="Credit Account", check_company=True)
    amount = fields.Float(string="Amount to Write Off", required=True)
    reason = fields.Text(string="Reason")
    move_id = fields.Many2one("account.move", string="Accounting Entry", copy=False, readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Posted"), ("cancel", "Cancelled")],
        default="draft",
    )

    def action_post(self):
        for rec in self:
            if rec.move_id:
                rec.state = "done"
                continue
            if not rec.journal_id:
                raise UserError(_("Select a journal to post the VAT write-off."))
            if rec.amount <= 0:
                raise UserError(_("The write-off amount must be greater than zero."))
            debit_account = rec.debit_account_id or rec.journal_id.default_account_id
            credit_account = rec.credit_account_id
            if not debit_account or not credit_account:
                raise UserError(_("Select the debit and credit accounts for the VAT write-off."))
            if debit_account == credit_account:
                raise UserError(_("The debit and credit accounts must be different."))
            move = self.env["account.move"].create({
                "journal_id": rec.journal_id.id,
                "date": rec.date,
                "ref": rec.name,
                "company_id": rec.company_id.id,
                "move_type": "entry",
                "line_ids": [
                    (0, 0, {"name": rec.name, "account_id": debit_account.id, "debit": rec.amount}),
                    (0, 0, {"name": rec.name, "account_id": credit_account.id, "credit": rec.amount}),
                ],
            })
            move.action_post()
            rec.move_id = move.id
            rec.state = "done"
            books = rec.purchase_book_id | rec.sale_book_id
            books.filtered(lambda book: book.state == "draft").action_update_book()

    def action_cancel(self):
        for rec in self:
            if rec.move_id and rec.move_id.state == "posted":
                rec.move_id.button_draft()
                rec.move_id.button_cancel()
            rec.state = "cancel"
