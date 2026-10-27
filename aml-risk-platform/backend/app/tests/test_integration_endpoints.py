import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

_test_environment = patch.dict(
    os.environ,
    {
        "POSTGRES_PASSWORD": "test-password",
        "KEYCLOAK_ISSUER": "http://localhost:8080/realms/aml-risk",
        "KEYCLOAK_JWKS_URL": (
            "http://localhost:8080/realms/aml-risk/protocol/openid-connect/certs"
        ),
        "KEYCLOAK_AUDIENCE": "aml-api",
        "DEV_AUTH_BYPASS": "false",
    },
)
_test_environment.start()

from app.main import app  # noqa: E402
from app.shared.auth.dependencies import get_current_user  # noqa: E402


class IntegrationEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "realm_access": {"roles": ["admin"]},
        }

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        app.dependency_overrides.pop(get_current_user, None)
        _test_environment.stop()

    def test_create_investigation_requires_title(self):
        response = self.client.post("/api/v1/investigations", json={})
        self.assertEqual(response.status_code, 422)

    def test_network_relationships_returns_rows(self):
        with patch(
            "app.modules.network_intelligence.api.network_intelligence_router.fetch_all"
        ) as fetch_all:
            fetch_all.return_value = [{"customer_id": "abc", "hops": 1}]
            response = self.client.get(
                "/api/v1/network/customers/abc/relationships?depth=2"
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["relationships"][0]["hops"], 1)

    def test_update_kyc_missing_customer_returns_404(self):
        with patch(
            "app.modules.kyc.infrastructure.kyc_repository.fetch_one", return_value=None
        ):
            response = self.client.patch(
                "/api/v1/kyc/missing", json={"verification_result": "APPROVED"}
            )
            self.assertEqual(response.status_code, 404)

    def test_update_screening_missing_returns_404(self):
        with patch(
            "app.modules.screening.infrastructure.screening_repository.fetch_one",
            return_value=None,
        ):
            response = self.client.patch(
                "/api/v1/screening/missing", json={"result": "CLEAR"}
            )
            self.assertEqual(response.status_code, 404)

    def test_update_rule_thresholds(self):
        response = self.client.put(
            "/api/v1/intelligence-engine/rules/AML-TXN-003/thresholds",
            json={"min_count": 5},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["thresholds"]["min_count"], 5)

    def test_update_rule_thresholds_unknown_returns_404(self):
        response = self.client.put(
            "/api/v1/intelligence-engine/rules/UNKNOWN/thresholds",
            json={"min_count": 5},
        )
        self.assertEqual(response.status_code, 404)

    def test_list_reports_empty(self):
        with patch(
            "app.modules.enterprise_extension.api_extension.fetch_all", return_value=[]
        ):
            response = self.client.get("/api/v1/intelligence-engine/reports/customer-1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["reports"], [])


if __name__ == "__main__":
    unittest.main()
