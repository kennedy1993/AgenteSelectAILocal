import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class DatabaseReadOnlyTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "hr_oracle.db"
        self.db_path_patch = patch.object(database, "DB_PATH", self.database_path)
        self.db_path_patch.start()
        database.inicializar_banco()

    def tearDown(self):
        self.db_path_patch.stop()
        self.temp_dir.cleanup()

    def test_select_returns_seeded_employees(self):
        result = database.executar_consulta_sql(
            "SELECT FIRST_NAME, LAST_NAME FROM EMPLOYEES ORDER BY EMPLOYEE_ID"
        )

        self.assertEqual(len(result), 8)
        self.assertEqual(result.iloc[0].tolist(), ["Neena", "Yang"])

    def test_mutating_statements_are_rejected(self):
        statements = (
            "DELETE FROM EMPLOYEES",
            "UPDATE EMPLOYEES SET SALARY = 0",
            "INSERT INTO EMPLOYEES VALUES (999, 'A', 'B', 'AB', '2024-01-01', 'IT_PROG', 1, 60)",
            "DROP TABLE EMPLOYEES",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                with self.assertRaisesRegex(ValueError, "Apenas consultas de leitura"):
                    database.executar_consulta_sql(statement)

    def test_non_select_statements_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nao e um SELECT valido"):
            database.executar_consulta_sql("CREATE TABLE forbidden (id INTEGER)")

    def test_database_is_opened_with_read_only_uri(self):
        sqlite_connect = sqlite3.connect
        with patch("database.sqlite3.connect", wraps=sqlite_connect) as connect_spy:
            database.executar_consulta_sql("SELECT COUNT(*) FROM EMPLOYEES")

        args, kwargs = connect_spy.call_args
        self.assertTrue(kwargs["uri"])
        self.assertTrue(args[0].endswith("?mode=ro"))


if __name__ == "__main__":
    unittest.main()
