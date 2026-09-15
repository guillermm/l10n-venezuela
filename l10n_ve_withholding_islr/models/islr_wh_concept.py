# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from .islr_seniat_catalog import SENIAT_ISLR_CATALOG


class IslrWhConcept(models.Model):
    _name = "islr.wh.concept"
    _description = "ISLR Withholding Concept"
    _order = "code, name"

    name = fields.Char(string="Concept Name", required=True)
    code = fields.Char(
        string="Main SENIAT Code",
        required=True,
        help="Reference code (usually the PNRE / most used SENIAT code). "
        "The XML uses the code of the rate that matches the partner type.",
    )
    withholding_rate_ids = fields.One2many(
        comodel_name="islr.wh.rates",
        inverse_name="concept_id",
        string="Rates Breakdown",
    )

    def name_get(self):
        return [(rec.id, "[%s] %s" % (rec.code or "", rec.name or "")) for rec in self]

    def get_rate_for_person(self, person_type):
        self.ensure_one()
        person_type = person_type or "pjdo"
        return self.withholding_rate_ids.filtered(lambda rec: rec.person_type == person_type)[:1]

    @api.model
    def _l10n_ve_load_seniat_catalog(self):
        """Load / refresh official SENIAT ISLR concepts and per-type codes."""
        Imd = self.env["ir.model.data"]
        Rate = self.env["islr.wh.rates"]
        all_codes = [rate[1] for item in SENIAT_ISLR_CATALOG for rate in item[4]]
        if len(all_codes) != len(set(all_codes)):
            raise ValueError("Duplicated SENIAT ISLR concept codes in the catalog.")
        for xmlid, name, code, nature, rates in SENIAT_ISLR_CATALOG:
            xml_name = "l10n_ve_withholding_islr.%s" % xmlid
            concept = self.env.ref(xml_name, raise_if_not_found=False)
            vals = {"name": name, "code": code}
            if concept:
                concept.write(vals)
            else:
                concept = self.create(vals)
                Imd._update_xmlids([{
                    "xml_id": xml_name,
                    "record": concept,
                    "noupdate": False,
                }])
            keep_ids = []
            for person_type, seniat_code, base_pct, wh_pct, subtract_ut in rates:
                rate = Rate.search([("code", "=", seniat_code)], limit=1)
                if not rate:
                    rate = concept.withholding_rate_ids.filtered(
                        lambda rec, ptype=person_type: rec.person_type == ptype
                    )[:1]
                rate_vals = {
                    "concept_id": concept.id,
                    "person_type": person_type,
                    "nature": nature,
                    "code": seniat_code,
                    "base_percentage": base_pct,
                    "wh_percentage": wh_pct,
                    "subtract_ut": subtract_ut,
                }
                if rate:
                    rate.write(rate_vals)
                else:
                    rate = Rate.create(rate_vals)
                    Imd._update_xmlids([{
                        "xml_id": "l10n_ve_withholding_islr.rate_islr_%s" % seniat_code,
                        "record": rate,
                        "noupdate": False,
                    }])
                keep_ids.append(rate.id)
            concept.withholding_rate_ids.filtered(lambda rec: rec.id not in keep_ids).unlink()
        return True
