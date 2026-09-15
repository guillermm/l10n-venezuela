# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    lines_invoice = fields.Integer(
        string="Max Invoice Lines",
        default=0,
        help="Maximum invoice lines before the document is split. 0 disables splitting.",
    )
