import os
import unittest
from unittest.mock import patch

import certifi

from app.core import database as db


class DatabaseTests(unittest.TestCase):
    def test_uses_explicit_ca_bundle_for_tls_verification(self):
        settings = {
            "MYSQL_HOST": "example.mysql.database.azure.com",
            "MYSQL_DATABASE": "test_db",
            "MYSQL_USER": "test_user",
            "MYSQL_PASSWORD": "test_password",
        }
        with patch.dict(os.environ, settings, clear=True), patch.object(db, "_pool", None), patch.object(db, "MySQLConnectionPool") as pool:
            db.connect()

        self.assertEqual(pool.call_args.kwargs["ssl_ca"], certifi.where())
        self.assertTrue(pool.call_args.kwargs["ssl_verify_cert"])
        self.assertTrue(pool.call_args.kwargs["ssl_verify_identity"])
