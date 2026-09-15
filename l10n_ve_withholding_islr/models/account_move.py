# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    wh_islr_doc_id = fields.Many2one(
        comodel_name="account.wh.islr.doc",
        string="ISLR Withholding Voucher",
        copy=False,
        readonly=True,
    )
    islr_concept_id = fields.Many2one(
        comodel_name="islr.wh.concept",
        string="Default ISLR Concept",
    )

    def _l10n_ve_get_islr_concept(self):
        self.ensure_one()
        if self.islr_concept_id:
            return self.islr_concept_id
        line_concept = self.invoice_line_ids.mapped("islr_concept_id")[:1]
        if line_concept:
            return line_concept
        partner_concept = self.partner_id.islr_concept_id
        if partner_concept:
            return partner_concept
        return self.env["islr.wh.concept"]

    def action_generate_wh_islr(self):
        self.ensure_one()
        if self.wh_islr_doc_id:
            raise UserError(_("ISLR Withholding Voucher already exists for this move."))
        if self.move_type not in ["out_invoice", "in_invoice", "out_refund", "in_refund"]:
            raise UserError(_("Only invoices and refunds can generate ISLR Withholdings."))
        if self.state != "posted":
            raise UserError(_("Post the invoice before generating the ISLR withholding."))
        concept = self._l10n_ve_get_islr_concept()
        if not concept:
            raise UserError(_("Select an ISLR concept on the invoice, its lines or the partner."))
        voucher = self.env["account.wh.islr.doc"].create({
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "currency_id": self.company_id.currency_id.id,
            "type": self.move_type,
            "date": self.invoice_date or fields.Date.context_today(self),
            "journal_id": self.company_id.wh_islr_journal_id.id,
            "line_ids": [(0, 0, {
                "move_id": self.id,
                "concept_id": concept.id,
                "base_amount": self._l10n_ve_taxable_untaxed(),
            })],
        })
        voucher.line_ids.action_recompute_from_move()
        self.wh_islr_doc_id = voucher.id
        self._l10n_ve_refresh_wh_state()
        return {
            "name": _("ISLR Withholding Voucher"),
            "type": "ir.actions.act_window",
            "res_model": "account.wh.islr.doc",
            "res_id": voucher.id,
            "view_mode": "form",
            "target": "current",
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    islr_concept_id = fields.Many2one(
        comodel_name="islr.wh.concept",
        string="ISLR Concept",
    )

    def _l10n_ve_default_islr_concept(self, product):
        return product.islr_concept_id.id if product and product.islr_concept_id else False

    @api.model_create_multi
    def create(self, vals_list):
        Product = self.env["product.product"]
        for vals in vals_list:
            if not vals.get("islr_concept_id") and vals.get("product_id"):
                concept_id = self._l10n_ve_default_islr_concept(Product.browse(vals["product_id"]))
                if concept_id:
                    vals["islr_concept_id"] = concept_id
        return super().create(vals_list)

    @api.onchange("product_id")
    def _onchange_product_id_islr_concept(self):
        if self.product_id and self.product_id.islr_concept_id:
            self.islr_concept_id = self.product_id.islr_concept_id
