# Copyright 2020-2025 SINAPSYS GLOBAL SA, MASTERCORE SAS
# Copyright 2026 Guillermo Montoya
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
# Address fields adapted from l10n_ve_base 16.0
# (odoo-mastercore/odoo-venezuela), authors SINAPSYS GLOBAL SA and MASTERCORE SAS.

import ast

from odoo import api, fields, models

_ADDRESS_SEARCH_ONLY = {
    "state_id",
    "city_id",
    "municipality_id",
    "parish_id",
}
_NO_CREATE_OPTIONS = {
    "no_open": True,
    "no_create": True,
    "no_create_edit": True,
    "no_quick_create": True,
}


class ResPartner(models.Model):
    _inherit = "res.partner"

    municipality_id = fields.Many2one(
        comodel_name="res.country.state.municipality",
        string="Municipality",
        ondelete="restrict",
        domain="[('state_id', '=', state_id)]",
    )
    parish_id = fields.Many2one(
        comodel_name="res.country.state.municipality.parish",
        string="Parish",
        ondelete="restrict",
        domain="[('municipality_id', '=', municipality_id)]",
    )

    @api.onchange("state_id")
    def _onchange_state_id_territorial(self):
        if self.municipality_id and self.municipality_id.state_id != self.state_id:
            self.municipality_id = False
            self.parish_id = False

    @api.onchange("municipality_id")
    def _onchange_municipality_id_territorial(self):
        if self.parish_id and self.parish_id.municipality_id != self.municipality_id:
            self.parish_id = False
        if self.municipality_id and self.municipality_id.state_id:
            self.state_id = self.municipality_id.state_id
            if self.municipality_id.state_id.country_id:
                self.country_id = self.municipality_id.state_id.country_id

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        """Only the contact address block: search city/state/municipality/parish."""
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type != "form":
            return arch, view
        address_fields = arch.xpath(
            "//div[contains(@class, 'o_address_format')]//field[@name]"
        )
        for node in address_fields:
            if node.get("name") not in _ADDRESS_SEARCH_ONLY:
                continue
            try:
                current = ast.literal_eval(node.get("options") or "{}")
            except (ValueError, SyntaxError):
                current = {}
            if not isinstance(current, dict):
                current = {}
            current.update(_NO_CREATE_OPTIONS)
            node.set("options", str(current))
        return arch, view
