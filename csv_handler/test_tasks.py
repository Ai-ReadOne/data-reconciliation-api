from django.test import TestCase
from unittest.mock import patch, MagicMock
from .tasks import reconcile_csv_files
from .models import CSVDataReport


class ReconcileCSVFilesTaskTests(TestCase):
    def setUp(self):
        self.report = CSVDataReport.objects.create(
            source_file="dummy_source.csv",
            target_file="dummy_target.csv",
            unique_fields="id",
            status="pending",
            report={}
        )

    def test_report_not_found(self):
        result = reconcile_csv_files(9999)  # Non-existent ID
        self.assertEqual(result, "Report with id 9999 not found.")

    @patch("csv_handler.csv_parser.CSVParser.read_csv")
    @patch("data_reconciler.processor.DataReconciler")
    def test_successful_reconciliation(self, mock_reconcile, mock_read_csv):
        mock_read_csv.side_effect = [
            {"data": [{"id": "1", "name": "alice"}]},
            {"data": [{"id": "1", "name": "alice"}]},
        ]
        mock_reconcile.return_value = {"discrepancies": []}

        reconcile_csv_files(self.report.id)

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "completed")
        self.assertEqual(self.report.report["discrepancies"], [])

    @patch("csv_handler.csv_parser.CSVParser.read_csv")
    def test_reconciliation_failure_sets_failed_status(self, mock_read_csv):
        mock_read_csv.side_effect = Exception("Bad CSV")

        with self.assertRaises(Exception):
            reconcile_csv_files(self.report.id)

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "failed")
