# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_model_data
           SET noupdate = TRUE
         WHERE module = 'l10n_ve_withholding_muni'
           AND model = 'l10n.ve.muni.activity'
        """
    )
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
         WHERE table_name = 'l10n_ve_muni_activity'
           AND column_name = 'municipality_id'
        """
    )
    if cr.fetchone():
        cr.execute(
            """
            ALTER TABLE l10n_ve_muni_activity
            ALTER COLUMN municipality_id DROP NOT NULL
            """
        )
