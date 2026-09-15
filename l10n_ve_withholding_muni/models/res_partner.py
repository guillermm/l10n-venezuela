# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    muni_activity_id = fields.Many2one(
        comodel_name="l10n.ve.muni.activity",
        string="Municipal Activity",
        domain="['|', ('municipality_id', '=', municipality_id), ('municipality_id', '=', False)]",
    )
    wh_muni_rate = fields.Float(string="Municipal Withholding Rate (%)")

    @api.onchange("municipality_id")
    def _onchange_municipality_id_wh(self):
        activity = self.muni_activity_id
        if (
            activity
            and activity.municipality_id
            and self.municipality_id
            and activity.municipality_id != self.municipality_id
        ):
            self.muni_activity_id = False

    @api.onchange("muni_activity_id")
    def _onchange_muni_activity_id(self):
        if self.muni_activity_id:
            self.wh_muni_rate = self.muni_activity_id.rate
            self.municipality_id = self.muni_activity_id.municipality_id
            if self.municipality_id.state_id:
                self.state_id = self.municipality_id.state_id
                if self.municipality_id.state_id.country_id:
                    self.country_id = self.municipality_id.state_id.country_id

    @api.model
    def _l10n_ve_bind_wh_municipality_to_territorial(self):
        Activity = self.env["l10n.ve.muni.activity"]
        partners = self.sudo().search([
            ("muni_activity_id", "!=", False),
            ("municipality_id", "=", False),
        ])
        for partner in partners:
            municipality = partner.muni_activity_id.municipality_id
            if municipality:
                partner.municipality_id = municipality.id
        self.env.cr.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'res_partner' AND column_name = 'l10n_ve_wh_muni_legacy'
            """
        )
        if not self.env.cr.fetchone():
            return
        self.env.cr.execute(
            """
            SELECT id, l10n_ve_wh_muni_legacy FROM res_partner
            WHERE municipality_id IS NULL AND l10n_ve_wh_muni_legacy IS NOT NULL
            """
        )
        for partner_id, legacy_name in self.env.cr.fetchall():
            municipality = Activity._l10n_ve_territorial_municipality(legacy_name)
            if municipality:
                self.browse(partner_id).municipality_id = municipality.id
