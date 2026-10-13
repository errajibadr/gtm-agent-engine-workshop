import copy
import unittest

from gtm_agent import data_service
from gtm_agent.gtm_records import PROSPECTS


class UpdateProspectInfoTest(unittest.TestCase):
    def setUp(self):
        self._prospects = copy.deepcopy(PROSPECTS)
        self._profiles = dict(data_service._PROFILES)
        self.pid = next(pid for pid, rec in PROSPECTS.items() if "Terraform" not in rec["tech_stack"])

    def tearDown(self):
        PROSPECTS.clear()
        PROSPECTS.update(self._prospects)
        data_service._PROFILES.clear()
        data_service._PROFILES.update(self._profiles)

    def test_added_technology_is_persisted(self):
        result = data_service.update_prospect_info(self.pid, "Terraform")
        self.assertTrue(result["updated"])
        self.assertIn("Terraform", result["tech_stack"])
        self.assertIn("Terraform", data_service.get_prospect_record(self.pid)["tech_stack"])

    def test_fetch_after_update_sees_technology(self):
        data_service.update_prospect_info(self.pid, "Terraform")
        self.assertIn("Terraform", data_service.fetch_tech_stack(self.pid))

    def test_cached_profile_does_not_serve_stale_stack(self):
        stale = {"prospect_id": self.pid, "tech_stack": list(PROSPECTS[self.pid]["tech_stack"])}
        data_service.save_profile_to_db(self.pid, stale)
        data_service.update_prospect_info(self.pid, "Terraform")
        cached = data_service.get_profile_from_db(self.pid)["prospect_profile"]
        self.assertTrue(cached is None or "Terraform" in cached["tech_stack"])

    def test_unknown_prospect_is_not_updated(self):
        result = data_service.update_prospect_info("LEAD-00000", "Terraform")
        self.assertEqual(result, {"updated": False, "found": False})
        self.assertNotIn("LEAD-00000", PROSPECTS)


if __name__ == "__main__":
    unittest.main()
