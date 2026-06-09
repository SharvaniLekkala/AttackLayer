import unittest
from unittest.mock import MagicMock, patch

from app.api.admin import clear_databases


class AdminResetTest(unittest.TestCase):
    @patch("app.api.admin.reset_memory_collection")
    @patch("app.api.admin.SessionLocal")
    def test_clear_databases_clears_sql_and_chroma(self, session_local, reset_chroma):
        db = MagicMock()
        session_local.return_value = db

        result = clear_databases()

        self.assertEqual(result["status"], "cleared")
        self.assertEqual(db.query.call_count, 10)
        self.assertEqual(db.commit.call_count, 1)
        reset_chroma.assert_called_once_with()
        db.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
