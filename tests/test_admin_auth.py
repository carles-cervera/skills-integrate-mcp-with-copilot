import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import src.app as app_module
import src.auth as auth_module


class AdminAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.teachers_file = Path(self.temp_dir.name) / "teachers.json"
        password = "a-long-test-password"
        self.teachers_file.write_text(
            json.dumps({
                "iterations": auth_module.PASSWORD_ITERATIONS,
                "teachers": {"staff": auth_module.create_password_record(password)},
            }),
            encoding="utf-8",
        )
        self.store_patch = patch.object(auth_module, "TEACHERS_FILE", self.teachers_file)
        self.store_patch.start()
        self.activities = copy.deepcopy(app_module.activities)
        self.client = TestClient(app_module.app)

    def tearDown(self):
        app_module.activities.clear()
        app_module.activities.update(self.activities)
        self.client.close()
        self.store_patch.stop()
        self.temp_dir.cleanup()

    def test_guest_can_view_activities_and_participants(self):
        response = self.client.get("/activities")

        self.assertEqual(response.status_code, 200)
        self.assertIn("michael@mergington.edu", response.json()["Chess Club"]["participants"])

    def test_guest_cannot_register_or_unregister(self):
        signup = self.client.post(
            "/activities/Chess Club/signup", params={"email": "new@mergington.edu"}
        )
        unregister = self.client.delete(
            "/activities/Chess Club/unregister", params={"email": "michael@mergington.edu"}
        )

        self.assertEqual(signup.status_code, 401)
        self.assertEqual(unregister.status_code, 401)

    def test_teacher_can_register_and_unregister(self):
        login = self.client.post(
            "/auth/login",
            json={"username": "staff", "password": "a-long-test-password"},
        )
        self.assertEqual(login.status_code, 200)

        signup = self.client.post(
            "/activities/Chess Club/signup", params={"email": "new@mergington.edu"}
        )
        unregister = self.client.delete(
            "/activities/Chess Club/unregister", params={"email": "new@mergington.edu"}
        )

        self.assertEqual(signup.status_code, 200)
        self.assertEqual(unregister.status_code, 200)

    def test_invalid_login_is_rejected(self):
        response = self.client.post(
            "/auth/login", json={"username": "staff", "password": "wrong-password"}
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()