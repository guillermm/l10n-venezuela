# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    wh_muni_id = fields.Many2one("account.wh.muni", string="Municipal Withholding", copy=False)
