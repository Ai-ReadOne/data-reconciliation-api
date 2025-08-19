from django.test import SimpleTestCase
import io
from .csv_parser import CSVParser


class CSVParserTests(SimpleTestCase):
    def test_clean_value_strips_and_lowercases(self):
        self.assertEqual(CSVParser.clean_value("  HelloWorld  "), "helloworld")

    def test_clean_value_returns_non_str(self):
        self.assertEqual(CSVParser.clean_value(123), 123)

    def test_clean_value_parses_date_iso(self):
        self.assertEqual(CSVParser.clean_value("2024-08-15"), "2024-08-15")

    def test_clean_value_invalid_date_returns_lowercased(self):
        self.assertEqual(CSVParser.clean_value("NotADate"), "notadate")

    def test_clean_data_normalizes(self):
        rows = [{"Name": " Alice ", "Date": "01/01/2025"}]
        result = CSVParser.clean_data(rows)
        self.assertEqual(result, [{"Name": "alice", "Date": "2025-01-01"}])

    def test_read_csv_parses_and_cleans(self):
        csv_bytes = io.BytesIO(
            b"Name,Date,Score\n Alice ,2024-08-15, 90 \n"
        )
        result = CSVParser.read_csv(csv_bytes)
        self.assertIn("data", result)
        self.assertIn("field_names", result)
        self.assertEqual(result["field_names"], ["Name", "Date", "Score"])
        self.assertEqual(result["data"], [
            {"Name": "alice", "Date": "2024-08-15", "Score": "90"}
        ])
