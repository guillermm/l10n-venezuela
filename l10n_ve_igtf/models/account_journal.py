# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_ve_igtf_enabled = fields.Boolean(
        string="Apply IGTF",
        help="Enable IGTF on payments registered through this journal (foreign currency / crypto).",
    )
