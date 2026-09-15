# Copyright 2020-2025 SINAPSYS GLOBAL SA, MASTERCORE SAS
# Copyright 2026 Guillermo Montoya
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from . import models


def pre_init_hook(env_or_cr, registry=None):
    """Free res.partner.municipality_id if municipal withholding already used it."""
    cr = env_or_cr.cr if hasattr(env_or_cr, "cr") else env_or_cr
    cr.execute(
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'l10n_ve_municipality'
        """
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'res_partner' AND column_name = 'municipality_id'
        """
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'res_partner' AND column_name = 'wh_municipality_id'
        """
    )
    if cr.fetchone():
        return
    cr.execute(
        "ALTER TABLE res_partner RENAME COLUMN municipality_id TO wh_municipality_id"
    )
