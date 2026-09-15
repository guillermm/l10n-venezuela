# Copyright 2026 Guillermo Montoya
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.l10n_ve_withholding_islr.models.islr_seniat_catalog import SENIAT_ISLR_CATALOG
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestIslrCatalog(TransactionCase):
    def _concept(self, xmlid):
        return self.env.ref("l10n_ve_withholding_islr.%s" % xmlid)

    def test_catalog_codes_are_unique(self):
        codes = [rate[1] for item in SENIAT_ISLR_CATALOG for rate in item[4]]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertGreaterEqual(len(codes), 60)

    def test_honorarios_official_codes(self):
        concept = self._concept("concept_honorarios_prof")
        self.assertEqual(concept.code, "002")
        self.assertEqual(concept.get_rate_for_person("pnre").code, "002")
        self.assertEqual(concept.get_rate_for_person("pnnr").code, "003")
        self.assertEqual(concept.get_rate_for_person("pjdo").code, "004")
        pnre = concept.get_rate_for_person("pnre")
        self.assertAlmostEqual(pnre.wh_percentage, 3.0)
        self.assertAlmostEqual(pnre.subtract_ut, 83.3334)
        pnnr = concept.get_rate_for_person("pnnr")
        self.assertAlmostEqual(pnnr.base_percentage, 90.0)
        self.assertAlmostEqual(pnnr.wh_percentage, 34.0)
        self.assertAlmostEqual(concept.get_rate_for_person("pjdo").wh_percentage, 5.0)

    def test_obras_fletes_and_lease_codes(self):
        obras = self._concept("concept_servicios_gen")
        self.assertEqual(obras.code, "053")
        self.assertEqual(obras.get_rate_for_person("pnre").code, "053")
        self.assertEqual(obras.get_rate_for_person("pnnr").code, "054")
        self.assertEqual(obras.get_rate_for_person("pjdo").code, "055")
        self.assertAlmostEqual(obras.get_rate_for_person("pnre").subtract_ut, 83.3334)

        fletes = self._concept("concept_fletes")
        self.assertEqual(fletes.get_rate_for_person("pnre").code, "071")
        self.assertEqual(fletes.get_rate_for_person("pjdo").code, "072")

        lease = self._concept("concept_arrendamiento_inmueble")
        self.assertEqual(lease.get_rate_for_person("pnre").code, "057")
        self.assertEqual(lease.get_rate_for_person("pnnr").code, "058")
        self.assertEqual(lease.get_rate_for_person("pjdo").code, "059")

    def test_seeded_xmlids_were_corrected(self):
        """Former seed 003/012/024/016 must not keep the wrong meaning."""
        self.assertNotEqual(self._concept("concept_honorarios_prof").code, "003")
        self.assertNotEqual(self._concept("concept_servicios_gen").code, "012")
        self.assertNotEqual(self._concept("concept_fletes").code, "024")
        self.assertNotEqual(self._concept("concept_arrendamiento_inmueble").code, "016")
        self.assertEqual(self._concept("concept_hprof_clinicas").code, "012")
        self.assertEqual(
            self._concept("concept_comisiones_inmuebles").get_rate_for_person("pjdo").code,
            "016",
        )
