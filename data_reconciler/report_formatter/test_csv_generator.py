import csv
import io
from .csv_generator import CSVReportGenerator


class TestCSVReportGenerator:
    def test_generate_csv_from_records_empty(self):
        records = []
        result = CSVReportGenerator._generate_csv_from_records(records, "Test Section")
        expected = "Test Section\r\nNone\r\n\r\n"
        assert result == expected

    def test_generate_csv_from_records_with_data(self):
        records = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = CSVReportGenerator._generate_csv_from_records(records, "Users")
        expected_lines = [
            ["Users"],
            ["id", "name"],
            ["1", "Alice"],
            ["2", "Bob"],
            [],
        ]

        reader = csv.reader(io.StringIO(result))
        assert list(reader) == expected_lines

    def test_generate_csv_from_records_with_missing_keys(self):
        records = [
            {"id": 1, "name": "Alice"},
            {"id": 2},  # missing "name"
        ]
        result = CSVReportGenerator._generate_csv_from_records(records, "Users")
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)

        # Header must include both "id" and "name"
        assert rows[1] == ["id", "name"]
        # Missing key should render as empty string
        assert rows[3] == ["2", ""]

    def test_generate_discrepancies_csv_empty(self):
        discrepancies = []
        result = CSVReportGenerator._generate_discrepancies_csv(discrepancies)
        expected = "Discrepancies\r\nNone\r\n\r\n"
        assert result == expected

    def test_generate_discrepancies_csv_with_data(self):
        discrepancies = [
            {
                "key": [1],
                "differences": {
                    "amount": {"source": 100, "target": 90},
                    "status": {"source": "paid", "target": "pending"},
                },
            }
        ]

        result = CSVReportGenerator._generate_discrepancies_csv(discrepancies)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)

        assert rows[0] == ["Discrepancies"]
        assert rows[1] == ["Key", "Field", "Source Value", "Target Value"]
        assert ["1", "amount", "100", "90"] in rows
        assert ["1", "status", "paid", "pending"] in rows

    def test_generate_discrepancies_with_multiple_keys(self):
        discrepancies = [
            {
                "key": [1, "order_42"],
                "differences": {
                    "price": {"source": 200, "target": 210},
                },
            }
        ]

        result = CSVReportGenerator._generate_discrepancies_csv(discrepancies)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)

        # Keys should be joined with comma
        assert rows[2][0] == "1, order_42"
        assert rows[2][1:] == ["price", "200", "210"]

    def test_generate_csv_full_report_all_sections(self):
        report_data = {
            "discrepancies": [
                {
                    "key": [101],
                    "differences": {
                        "quantity": {"source": 5, "target": 3},
                    },
                }
            ],
            "missing_in_target": [{"id": 1, "value": "X"}],
            "missing_in_source": [{"id": 2, "value": "Y"}],
        }

        full_csv = CSVReportGenerator.generate_csv(report_data)
        reader = csv.reader(io.StringIO(full_csv))
        rows = list(reader)

        # Ensure all sections are included
        assert "Discrepancies" in rows[0]
        assert "Missing in Target (Present in Source)" in full_csv
        assert "Missing in Source (Present in Target)" in full_csv

    def test_csv_handles_commas_and_special_chars(self):
        records = [
            {"id": 1, "desc": "Item, with comma"},
            {"id": 2, "desc": "Line\nBreak"},
            {"id": 3, "desc": 'Quoted "text"'},
        ]
        result = CSVReportGenerator._generate_csv_from_records(records, "Specials")

        reader = csv.reader(io.StringIO(result))
        rows = list(reader)

        # Check preservation of special values
        assert rows[2] == ["1", "Item, with comma"]
        assert rows[3] == ["2", "Line\nBreak"]
        assert rows[4] == ["3", 'Quoted "text"']
