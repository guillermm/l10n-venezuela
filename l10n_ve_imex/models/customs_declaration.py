# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomsDeclaration(models.Model):
    _name = "customs.declaration"
    _description = "Customs Declaration (Forma 86 / DUA / DVI)"
    _order = "date desc, name desc"
    _check_company_auto = True

    name = fields.Char(
        string="Form 86 / C-80 / C-81",
        required=True,
        help="Customs form number used as document number in SENIAT IVA TXT (tipo 05).",
    )
    expediente = fields.Char(
        string="Expediente / Confrontación",
        help="Import control number for column 16 of the SENIAT IVA TXT (99035/99086).",
    )
    date = fields.Date(string="Declaration Date", required=True, default=fields.Date.context_today)
    date_liq = fields.Date(string="Liquidation Date")
    declaration_type = fields.Selection(
        [("dua", "DUA / Import (F86)"), ("dvi", "DVI / Export")],
        string="Type",
        default="dua",
        required=True,
    )
    customs_code = fields.Char(string="Customs Office Code")
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Broker / Partner")
    amount_total = fields.Monetary(string="Declared Amount")
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="customs_declaration_id",
        string="Invoices",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Confirmed"), ("cancel", "Cancelled")],
        default="draft",
        required=True,
    )
    notes = fields.Text()

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique(name, company_id)",
            "The customs form number must be unique per company.",
        ),
    ]

    @api.constrains("move_ids", "declaration_type")
    def _check_moves(self):
        for rec in self:
            if rec.declaration_type == "dua" and rec.move_ids.filtered(
                lambda move: move.move_type not in ("in_invoice", "in_refund")
            ):
                raise ValidationError(_("Import declarations can only be linked to vendor bills or refunds."))

    def action_confirm(self):
        for rec in self:
            if not rec.move_ids:
                raise ValidationError(_("Link at least one invoice before confirming the customs declaration."))
            rec.state = "done"

    def action_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancel"})
