# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    islr_concept_id = fields.Many2one(
        comodel_name="islr.wh.concept",
        string="ISLR Concept",
    )

    @api.model_create_multi
    def create(self, vals_list):
        Product = self.env["product.product"]
        for vals in vals_list:
            if not vals.get("islr_concept_id") and vals.get("product_id"):
                product = Product.browse(vals["product_id"])
                if product.islr_concept_id:
                    vals["islr_concept_id"] = product.islr_concept_id.id
        return super().create(vals_list)

    @api.onchange("product_id")
    def _onchange_product_id_islr_concept(self):
        if self.product_id and self.product_id.islr_concept_id:
            self.islr_concept_id = self.product_id.islr_concept_id

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self.islr_concept_id:
            res["islr_concept_id"] = self.islr_concept_id.id
        return res
