from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from .models import CSVDataReport


class CSVFileUploadViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('csv-reconciliation-list')
        self.list_url = reverse('csv-reconciliation-list-reports')
        self.dummy_csv = b"col1,col2\nval1,val2\n"
        self.source_file = SimpleUploadedFile("source.csv", self.dummy_csv, content_type="text/csv")
        self.target_file = SimpleUploadedFile("target.csv", self.dummy_csv, content_type="text/csv")
        self.dummy_txt = b"not,a,csv\nfile,content\n"

    # ---------- Upload Tests (create) ----------
    def test_upload_missing_source_file(self):
        response = self.client.post(
            self.url,
            {'target_file': self.target_file, "unique_fields": "col1,col2"},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)

    def test_upload_missing_target_file(self):
        response = self.client.post(
            self.url,
            {'source_file': self.source_file, "unique_fields": "col1,col2"},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_file', response.data)

    def test_upload_no_files(self):
        response = self.client.post(self.url, {"unique_fields": "col1,col2"}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)
        self.assertIn('target_file', response.data)

    def test_upload_non_csv_extension(self):
        source_file = SimpleUploadedFile("source.txt", self.dummy_csv, content_type="text/csv")
        response = self.client.post(
            self.url,
            {'source_file': source_file, 'target_file': self.target_file, "unique_fields": "col1,col2"},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)

    def test_upload_non_csv_content_type(self):
        source_file = SimpleUploadedFile("source.csv", self.dummy_csv, content_type="text/plain")
        response = self.client.post(
            self.url,
            {'source_file': source_file, 'target_file': self.target_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)

    def test_upload_both_files_invalid(self):
        source_file = SimpleUploadedFile("source.txt", self.dummy_txt, content_type="text/plain")
        target_file = SimpleUploadedFile("target.txt", self.dummy_txt, content_type="text/plain")
        response = self.client.post(
            self.url,
            {'source_file': source_file, 'target_file': target_file, "unique_fields": "col1,col2"},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)
        self.assertIn('target_file', response.data)

    def test_upload_missing_unique_fields(self):
        response = self.client.post(
            self.url,
            {'source_file': self.source_file, 'target_file': self.target_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('unique_fields', response.data)

    def test_upload_both_files_success(self):
        response = self.client.post(
            self.url,
            {'source_file': self.source_file, 'target_file': self.target_file, "unique_fields": "col1,col2"},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('status', response.data)

    # ---------- List Reports ----------
    def test_list_reports(self):
        CSVDataReport.objects.create(status="processing")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    # ---------- JSON Report ----------
    def test_json_invalid_uuid(self):
        response = self.client.get(reverse("csv-reconciliation-get-report", args=["not-a-uuid"]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_json_not_found(self):
        import uuid
        response = self.client.get(reverse("csv-reconciliation-get-report", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_json_processing_status(self):
        report = CSVDataReport.objects.create(status="processing")
        response = self.client.get(reverse("csv-reconciliation-get-report", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "processing")

    def test_json_no_discrepancy(self):
        report = CSVDataReport.objects.create(status="completed", report={})
        response = self.client.get(reverse("csv-reconciliation-get-report", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_json_with_report(self):
        report = CSVDataReport.objects.create(status="completed", report={"diff": "found"})
        response = self.client.get(reverse("csv-reconciliation-get-report", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("diff", response.data)

    # ---------- CSV Report ----------
    def test_csv_invalid_uuid(self):
        response = self.client.get(reverse("csv-reconciliation-get-report-in-csv", args=["bad-uuid"]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_csv_not_found(self):
        import uuid
        response = self.client.get(reverse("csv-reconciliation-get-report-in-csv", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_csv_processing_status(self):
        report = CSVDataReport.objects.create(status="processing")
        response = self.client.get(reverse("csv-reconciliation-get-report-in-csv", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "processing")

    def test_csv_no_discrepancy(self):
        report = CSVDataReport.objects.create(status="completed", report={})
        response = self.client.get(reverse("csv-reconciliation-get-report-in-csv", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_csv_with_report(self):
        report = CSVDataReport.objects.create(status="completed", report={"diff": "found"})
        response = self.client.get(reverse("csv-reconciliation-get-report-in-csv", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get("Content-Type"), "text/csv")

    @patch("data_reconciler.report_formatter.csv_generator.CSVReportGenerator.generate_csv", side_effect=Exception("CSV error"))
    def test_csv_generation_error(self, mock_gen):
        report = CSVDataReport.objects.create(status="completed", report={"diff": "found"})
        response = self.client.get(reverse("csv-reconciliation-get-report-in-csv", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    # ---------- HTML Report ----------
    def test_html_invalid_uuid(self):
        response = self.client.get(reverse("csv-reconciliation-get-report-in-html", args=["bad-uuid"]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_html_not_found(self):
        import uuid
        response = self.client.get(reverse("csv-reconciliation-get-report-in-html", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_html_processing_status(self):
        report = CSVDataReport.objects.create(status="processing")
        response = self.client.get(reverse("csv-reconciliation-get-report-in-html", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "processing")

    def test_html_no_discrepancy(self):
        report = CSVDataReport.objects.create(status="completed", report={})
        response = self.client.get(reverse("csv-reconciliation-get-report-in-html", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_html_with_report(self):
        report = CSVDataReport.objects.create(status="completed", report={"diff": "found"})
        response = self.client.get(reverse("csv-reconciliation-get-report-in-html", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get("Content-Type"), "text/html")

    @patch("data_reconciler.report_formatter.html_generator.HTMLReportGenerator.generate_html", side_effect=Exception("HTML error"))
    def test_html_generation_error(self, mock_gen):
        report = CSVDataReport.objects.create(status="completed", report={"diff": "found"})
        response = self.client.get(reverse("csv-reconciliation-get-report-in-html", args=[report.id]))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
