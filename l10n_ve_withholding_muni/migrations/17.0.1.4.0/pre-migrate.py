# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def _territorial_id(cr, xmlid_name):
    cr.execute(
        """
        SELECT res_id FROM ir_model_data
         WHERE module = 'territorial_pd'
           AND name = %s
           AND model = 'res.country.state.municipality'
        """,
        (xmlid_name,),
    )
    row = cr.fetchone()
    return row[0] if row else None


def _column_exists(cr, table, column):
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
         WHERE table_name = %s AND column_name = %s
        """,
        (table, column),
    )
    return bool(cr.fetchone())


def migrate(cr, version):
    """Keep existing activities; only fill empty municipality links."""
    cr.execute(
        """
        UPDATE ir_model_data
           SET noupdate = TRUE
         WHERE module = 'l10n_ve_withholding_muni'
           AND name IN ('activity_libertador_services', 'activity_chacao_services')
        """
    )
    if not _column_exists(cr, "l10n_ve_muni_activity", "municipality_id"):
        return
    cr.execute(
        """
        ALTER TABLE l10n_ve_muni_activity
        ALTER COLUMN municipality_id DROP NOT NULL
        """
    )
    libertador = _territorial_id(cr, "municipio_101")
    chacao = _territorial_id(cr, "municipio_1418")
    pairs = (
        ("activity_libertador_services", libertador),
        ("activity_chacao_services", chacao),
    )
    for act_name, mun_id in pairs:
        if not mun_id:
            continue
        cr.execute(
            """
            UPDATE l10n_ve_muni_activity AS activity
               SET municipality_id = %s
              FROM ir_model_data AS imd
             WHERE imd.module = 'l10n_ve_withholding_muni'
               AND imd.name = %s
               AND imd.model = 'l10n.ve.muni.activity'
               AND imd.res_id = activity.id
               AND activity.municipality_id IS NULL
            """,
            (mun_id, act_name),
        )
    if _column_exists(cr, "l10n_ve_muni_activity", "l10n_ve_muni_legacy"):
        cr.execute(
            """
            UPDATE l10n_ve_muni_activity AS activity
               SET municipality_id = municipality.id
              FROM res_country_state_municipality AS municipality
             WHERE activity.municipality_id IS NULL
               AND activity.l10n_ve_muni_legacy IS NOT NULL
               AND municipality.name ILIKE activity.l10n_ve_muni_legacy
            """
        )
