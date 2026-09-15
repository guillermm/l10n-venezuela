# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class WizardInvoiceNroCtrl(models.TransientModel):
    _name = "wizard.invoice.nro.ctrl"
    _description = "Assign Control Number"

    nro_ctrl = fields.Char(string="Control Number", required=True)

    def action_assign_nro_ctrl(self):
        self.ensure_one()
        active_id = self.env.context.get("active_id")
        if not active_id:
            return True
        move = self.env["account.move"].browse(active_id)
        if move.nro_ctrl and move.state == "posted":
            raise UserError(
                _("Posted invoice %s already has control number %s.")
                % (move.display_name, move.nro_ctrl)
            )
        move.with_context(l10n_ve_allow_nro_ctrl=True).write({"nro_ctrl": self.nro_ctrl})
        return True
