import unittest

import pandas as pd

from evals.executar_avaliacao import validar_resultado


class EvaluationResultTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "required_tables": ["EMPLOYEES"],
            "expected_columns": ["EMPLOYEE_ID", "LAST_NAME"],
            "expected_rows": [[101, "Yang"], [200, "Whalen"]],
        }

    def test_result_comparison_ignores_row_order_and_extra_columns(self):
        dataframe = pd.DataFrame(
            [
                {"EMPLOYEE_ID": 200, "LAST_NAME": "Whalen", "SALARY": 4400},
                {"EMPLOYEE_ID": 101, "LAST_NAME": "Yang", "SALARY": 17000},
            ]
        )

        failures = validar_resultado(
            self.case,
            "SELECT EMPLOYEE_ID, LAST_NAME, SALARY FROM EMPLOYEES",
            dataframe,
        )

        self.assertEqual(failures["failures"], [])
        self.assertTrue(failures["rows_match"])
        self.assertTrue(failures["columns_exact"])

    def test_result_comparison_reports_wrong_rows(self):
        dataframe = pd.DataFrame(
            [{"EMPLOYEE_ID": 101, "LAST_NAME": "Wrong"}]
        )

        failures = validar_resultado(
            self.case,
            "SELECT EMPLOYEE_ID, LAST_NAME FROM EMPLOYEES",
            dataframe,
        )

        self.assertTrue(
            any("Resultado diferente" in failure for failure in failures["failures"])
        )

    def test_result_comparison_requires_expected_tables_and_columns(self):
        dataframe = pd.DataFrame([{"EMPLOYEE_ID": 101}])

        failures = validar_resultado(
            self.case,
            "SELECT EMPLOYEE_ID FROM JOBS",
            dataframe,
        )

        self.assertTrue(
            any(
                "Tabelas esperadas ausentes" in failure
                for failure in failures["failures"]
            )
        )
        self.assertTrue(
            any(
                "Colunas esperadas ausentes" in failure
                for failure in failures["failures"]
            )
        )

    def test_allowed_alias_can_match_values_but_fails_exact_output_contract(self):
        case = {
            "required_tables": ["EMPLOYEES"],
            "expected_columns": ["AVG_SALARY"],
            "column_aliases": {"AVG_SALARY": ["AVG_SALARIAL"]},
            "expected_rows": [[7500]],
        }
        dataframe = pd.DataFrame([{"AVG_SALARIAL": 7500.0}])

        validation = validar_resultado(
            case, "SELECT AVG(SALARY) AS AVG_SALARIAL FROM EMPLOYEES", dataframe
        )

        self.assertTrue(validation["rows_match"])
        self.assertFalse(validation["columns_exact"])
        self.assertTrue(validation["failures"])


if __name__ == "__main__":
    unittest.main()
