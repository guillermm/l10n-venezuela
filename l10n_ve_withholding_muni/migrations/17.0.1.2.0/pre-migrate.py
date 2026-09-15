# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Keep ordinance municipality data when territorial_pd takes municipality_id."""
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
