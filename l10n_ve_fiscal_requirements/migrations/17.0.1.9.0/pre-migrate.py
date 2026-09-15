# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Runs before dependent modules (muni) reload their XML.


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1 FROM information_schema.tables
         WHERE table_name = 'ir_model_data'
        """
    )
    if not cr.fetchone():
        return
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
