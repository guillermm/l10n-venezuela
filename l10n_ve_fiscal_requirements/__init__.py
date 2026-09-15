# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api

from . import models
from . import wizards


def post_init_hook(env_or_cr, registry=None):
    env = env_or_cr if registry is None else api.Environment(env_or_cr, SUPERUSER_ID, {})
    env["res.company"]._l10n_ve_setup_bolivar_currency()
    env["res.company"]._l10n_ve_fill_missing_accounts()
    env["account.tax"]._l10n_ve_assign_appl_type()
    env["res.partner"]._l10n_ve_setup_identification_types()
