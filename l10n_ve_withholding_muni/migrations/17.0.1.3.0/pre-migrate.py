# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Keep names before municipality_id changes to territorial_pd."""
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
        WHERE table_name = 'l10n_ve_muni_activity' AND column_name = 'municipality_id'
        """
    )
    if cr.fetchone():
        cr.execute(
            """
            ALTER TABLE l10n_ve_muni_activity
            ADD COLUMN IF NOT EXISTS l10n_ve_muni_legacy varchar
            """
        )
        cr.execute(
            """
            UPDATE l10n_ve_muni_activity AS activity
               SET l10n_ve_muni_legacy = municipality.name
              FROM l10n_ve_municipality AS municipality
             WHERE activity.municipality_id = municipality.id
               AND activity.l10n_ve_muni_legacy IS NULL
            """
        )
        cr.execute("UPDATE l10n_ve_muni_activity SET municipality_id = NULL")
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'res_partner' AND column_name = 'wh_municipality_id'
        """
    )
    if cr.fetchone():
        cr.execute(
            """
            ALTER TABLE res_partner
            ADD COLUMN IF NOT EXISTS l10n_ve_wh_muni_legacy varchar
            """
        )
        cr.execute(
            """
            UPDATE res_partner AS partner
               SET l10n_ve_wh_muni_legacy = municipality.name
              FROM l10n_ve_municipality AS municipality
             WHERE partner.wh_municipality_id = municipality.id
               AND partner.l10n_ve_wh_muni_legacy IS NULL
            """
        )
