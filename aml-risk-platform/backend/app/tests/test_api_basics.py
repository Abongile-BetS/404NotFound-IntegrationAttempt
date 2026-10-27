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

# Load application settings only after installing test-only environment values.
from app.main import app, lifespan  # noqa: E402
from app.shared.auth.dependencies import get_current_user  # noqa: E402


class ApiBasicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        app.dependency_overrides[get_current_user] = lambda: {"sub": "test-user"}

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        app.dependency_overrides.pop(get_current_user, None)
        _test_environment.stop()

    def get_without_authentication(self, path):
        dependency_override = app.dependency_overrides.pop(get_current_user)
        try:
            return self.client.get(path)
        finally:
            app.dependency_overrides[get_current_user] = dependency_override

    def test_health_response_has_request_and_security_headers(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["x-request-id"])
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")

    def test_api_list_rejects_out_of_range_page_size(self):
        response = self.client.get("/api/v1/customers?limit=501")

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_intelligence_routes_require_authentication(self):
        response = self.get_without_authentication("/api/v1/intelligence/modules")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["www-authenticate"], "Bearer")

    def test_business_routes_require_authentication(self):
        response = self.get_without_authentication("/api/v1/customers")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["www-authenticate"], "Bearer")


class DatabaseLifespanTests(unittest.IsolatedAsyncioTestCase):
    async def test_shutdown_disposes_database_engine(self):
        with patch("app.main.dispose_engine") as dispose_engine:
            async with lifespan(app):
                pass

        dispose_engine.assert_called_once_with()
