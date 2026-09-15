# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1 FROM information_schema.tables
         WHERE table_name = 'l10n_ve_muni_activity'
        """
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        UPDATE ir_model_data
           SET noupdate = TRUE
         WHERE module = 'l10n_ve_withholding_muni'
           AND model IN ('l10n.ve.muni.activity', 'l10n.ve.municipality')
        """
    )
    cr.execute(
        """
        SELECT conname FROM pg_constraint
         WHERE conrelid = 'l10n_ve_muni_activity'::regclass
           AND contype = 'f'
           AND conname ILIKE '%municipality_id%'
        """
    )
    for (conname,) in cr.fetchall():
        cr.execute(
            'ALTER TABLE l10n_ve_muni_activity DROP CONSTRAINT IF EXISTS "%s"'
            % conname
        )
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
         WHERE table_name = 'l10n_ve_muni_activity'
           AND column_name = 'municipality_id'
        """
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        ALTER TABLE l10n_ve_muni_activity
        ALTER COLUMN municipality_id DROP NOT NULL
        """
    )
    cr.execute(
        """
        SELECT 1 FROM information_schema.tables
         WHERE table_name = 'l10n_ve_municipality'
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
        return
    cr.execute(
        """
        SELECT 1 FROM information_schema.tables
         WHERE table_name = 'res_country_state_municipality'
        """
    )
    if cr.fetchone():
        cr.execute(
            """
            UPDATE l10n_ve_muni_activity AS activity
               SET municipality_id = NULL
             WHERE activity.municipality_id IS NOT NULL
               AND NOT EXISTS (
                    SELECT 1 FROM res_country_state_municipality AS municipality
                     WHERE municipality.id = activity.municipality_id
               )
            """
        )
