# Copyright 2020-2025 SINAPSYS GLOBAL SA, MASTERCORE SAS
# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Taken from l10n_ve_base 16.0 (odoo-mastercore/odoo-venezuela).

from odoo import fields, models


class L10nVeResponsibilityType(models.Model):
    _name = "l10n_ve.responsibility.type"
    _description = "SENIAT Responsibility Type"
    _order = "sequence, name"

    name = fields.Char(required=True, index=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The responsibility type name must be unique."),
        ("code_uniq", "unique(code)", "The responsibility type code must be unique."),
    ]
