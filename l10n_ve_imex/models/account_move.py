# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    customs_declaration_id = fields.Many2one(
        comodel_name="customs.declaration",
        string="Customs Declaration (F86)",
        copy=False,
        check_company=True,
        help="Form 86 / DUA. Marks the invoice as an import (SENIAT document type 05).",
    )
    l10n_ve_expediente = fields.Char(
        related="customs_declaration_id.expediente",
        string="Import Expediente",
    )
