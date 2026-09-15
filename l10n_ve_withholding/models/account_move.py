# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    wh_state = fields.Selection(
        selection=[
            ("no_withheld", "Not Withheld"),
            ("partially_withheld", "Partially Withheld"),
            ("withheld", "Withheld"),
        ],
        string="Withholding State",
        default="no_withheld",
        copy=False,
        help="State of withholdings applied to this invoice",
    )

    def _l10n_ve_refresh_wh_state(self):
        """Recompute withholding state from the installed withholding modules."""
        for move in self:
            flags = []
            if "wh_iva_id" in move._fields and move.wh_iva_id:
                flags.append(move.wh_iva_id.state in ("confirmed", "done"))
            if "wh_islr_doc_id" in move._fields and move.wh_islr_doc_id:
                flags.append(move.wh_islr_doc_id.state in ("confirmed", "done"))
            if "wh_muni_id" in move._fields and move.wh_muni_id:
                flags.append(move.wh_muni_id.state in ("done",))
            if "wh_src_id" in move._fields and move.wh_src_id:
                flags.append(move.wh_src_id.state in ("done",))
            applied = sum(1 for flag in flags if flag)
            if not flags or not applied:
                move.wh_state = "no_withheld"
            elif applied == len(flags) and applied > 1:
                move.wh_state = "withheld"
            elif applied:
                move.wh_state = "partially_withheld" if len(flags) > 1 else "withheld"
            else:
                move.wh_state = "no_withheld"
