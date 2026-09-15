# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    wh_src_subject = fields.Boolean(
        string="SRC Withholding Subject",
        help="Public-contract supplier subject to Compromiso de Responsabilidad Social.",
    )
    wh_src_rate = fields.Float(string="SRC Withholding Rate (%)")

    @api.onchange("wh_src_subject")
    def _onchange_wh_src_subject(self):
        if self.wh_src_subject and not self.wh_src_rate:
            self.wh_src_rate = self.env.company.wh_src_rate or 5.0
        if not self.wh_src_subject:
            self.wh_src_rate = 0.0
