# Copyright 2020-2025 SINAPSYS GLOBAL SA, MASTERCORE SAS
# Copyright 2026 Guillermo Montoya
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
# Territorial models and catalog taken from territorial_pd 16.0
# (odoo-mastercore/odoo-venezuela), authors SINAPSYS GLOBAL SA and MASTERCORE SAS.

from odoo import fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    nationality = fields.Char(
        string="Nationality",
        help="Gentilicio of the country (Mastercore territorial_pd).",
    )


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    municipality_ids = fields.One2many(
        comodel_name="res.country.state.municipality",
        inverse_name="state_id",
        string="Municipalities",
    )


class ResCountryStateMunicipality(models.Model):
    _name = "res.country.state.municipality"
    _description = "Municipality"
    _order = "name"

    name = fields.Char(string="Municipality", required=True)
    code = fields.Char(string="Code", required=True)
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="State",
        required=True,
        ondelete="restrict",
        index=True,
    )
    parish_ids = fields.One2many(
        comodel_name="res.country.state.municipality.parish",
        inverse_name="municipality_id",
        string="Parishes",
    )


class ResCountryStateMunicipalityParish(models.Model):
    _name = "res.country.state.municipality.parish"
    _description = "Parish"
    _order = "name"

    name = fields.Char(string="Parish", required=True)
    code = fields.Char(string="Code", required=True)
    municipality_id = fields.Many2one(
        comodel_name="res.country.state.municipality",
        string="Municipality",
        required=True,
        ondelete="restrict",
        index=True,
    )
