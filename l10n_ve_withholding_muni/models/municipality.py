# Copyright 2011-2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

LEGACY_MUNICIPALITY_XMLID = {
    "libertador (caracas)": "territorial_pd.municipio_101",
    "libertador": "territorial_pd.municipio_101",
    "chacao": "territorial_pd.municipio_1418",
}

class L10nVeMuniActivity(models.Model):
    _name = "l10n.ve.muni.activity"
    _description = "Municipal Withholding Activity"
    _order = "municipality_id, name"
    _rec_names_search = ["name", "municipality_id", "state_id"]

    name = fields.Char(string="Economic Activity", required=True)
    municipality_id = fields.Many2one(
        comodel_name="res.country.state.municipality",
        string="Municipality",
        ondelete="set null",
        index=True,
    )
    state_id = fields.Many2one(
        related="municipality_id.state_id",
        store=True,
        string="State",
    )
    rate = fields.Float(string="Withholding Rate (%)", required=True)
    active = fields.Boolean(default=True)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name or ""
            extra = []
            if rec.municipality_id:
                extra.append(rec.municipality_id.name)
            if rec.state_id:
                extra.append(rec.state_id.name)
            if rec.rate:
                extra.append("%.2f%%" % rec.rate)
            if extra:
                name = "%s (%s)" % (name, " · ".join(extra))
            result.append((rec.id, name))
        return result

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        if name:
            records = self.search(
                [
                    "|",
                    "|",
                    "|",
                    ("name", operator, name),
                    ("municipality_id.name", operator, name),
                    ("state_id.name", operator, name),
                    ("municipality_id.code", operator, name),
                ]
                + args,
                limit=limit,
            )
            return records.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)

    @api.model
    def _l10n_ve_territorial_municipality(self, name):
        if not name:
            return self.env["res.country.state.municipality"]
        clean = " ".join(name.strip().split())
        xmlid = LEGACY_MUNICIPALITY_XMLID.get(clean.lower())
        if xmlid:
            record = self.env.ref(xmlid, raise_if_not_found=False)
            if record:
                return record
        short = clean.split("(")[0].strip()
        xmlid = LEGACY_MUNICIPALITY_XMLID.get(short.lower())
        if xmlid:
            record = self.env.ref(xmlid, raise_if_not_found=False)
            if record:
                return record
        Municipality = self.env["res.country.state.municipality"]
        matches = Municipality.search([("name", "=ilike", clean)])
        if not matches and short != clean:
            matches = Municipality.search([("name", "=ilike", short)])
        if len(matches) > 1 and "caracas" in clean.lower():
            capital = matches.filtered(lambda rec: rec.code == "101")
            if capital:
                return capital[:1]
        return matches[:1]

    @api.model
    def _l10n_ve_ensure_demo_activities(self):
        """Create demo activities only when the xmlid does not exist yet."""
        specs = (
            ("activity_libertador_services", "territorial_pd.municipio_101", "Servicios profesionales", 3.0),
            ("activity_chacao_services", "territorial_pd.municipio_1418", "Servicios profesionales", 2.0),
        )
        Imd = self.env["ir.model.data"]
        for xmlid, mun_xmlid, name, rate in specs:
            if self.env.ref("l10n_ve_withholding_muni.%s" % xmlid, raise_if_not_found=False):
                continue
            municipality = self.env.ref(mun_xmlid, raise_if_not_found=False)
            if not municipality:
                continue
            activity = self.create({
                "name": name,
                "municipality_id": municipality.id,
                "rate": rate,
            })
            Imd._update_xmlids([{
                "xml_id": "l10n_ve_withholding_muni.%s" % xmlid,
                "record": activity,
                "noupdate": True,
            }])

    @api.model
    def _l10n_ve_bind_activities_to_territorial(self):
        """Fill empty municipality links. Never overwrite a set municipality."""
        for xmlid, mun_xmlid in (
            ("l10n_ve_withholding_muni.activity_libertador_services", "territorial_pd.municipio_101"),
            ("l10n_ve_withholding_muni.activity_chacao_services", "territorial_pd.municipio_1418"),
        ):
            activity = self.env.ref(xmlid, raise_if_not_found=False)
            municipality = self.env.ref(mun_xmlid, raise_if_not_found=False)
            if activity and municipality and not activity.municipality_id:
                activity.municipality_id = municipality.id
        self.env.cr.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'l10n_ve_muni_activity'
              AND column_name = 'l10n_ve_muni_legacy'
            """
        )
        if not self.env.cr.fetchone():
            return
        self.env.cr.execute(
            """
            SELECT id, l10n_ve_muni_legacy FROM l10n_ve_muni_activity
            WHERE municipality_id IS NULL AND l10n_ve_muni_legacy IS NOT NULL
            """
        )
        for activity_id, legacy_name in self.env.cr.fetchall():
            municipality = self._l10n_ve_territorial_municipality(legacy_name)
            if municipality:
                self.browse(activity_id).municipality_id = municipality.id


class ResCountryStateMunicipality(models.Model):
    _inherit = "res.country.state.municipality"

    muni_activity_ids = fields.One2many(
        comodel_name="l10n.ve.muni.activity",
        inverse_name="municipality_id",
        string="Municipal Withholding Activities",
    )
