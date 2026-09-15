# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    islr_concept_id = fields.Many2one(
        comodel_name="islr.wh.concept",
        string="ISLR Concept",
        help="Default ISLR concept copied to sale/purchase and invoice lines.",
    )
