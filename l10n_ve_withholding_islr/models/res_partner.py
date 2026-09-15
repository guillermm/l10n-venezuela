# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    islr_concept_id = fields.Many2one(
        comodel_name="islr.wh.concept",
        string="Default ISLR Concept",
        help="Default income-tax withholding concept used on vendor bills and payments",
    )
