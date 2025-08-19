from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from .models import CSVDataReport
from .serializers import CSVDataReportSerializer, ListCSVDataReportSerializer


class CSVDataReportSerializerTests(TestCase):
    def setUp(self):
        self.valid_csv_file = SimpleUploadedFile(
            "test.csv",
            b"id,name\n1,Alice\n2,Bob",
            content_type="text/csv"
        )
        self.valid_csv_file_2 = SimpleUploadedFile(
            "test2.csv",
            b"id,name\n3,Charlie\n4,David",
            content_type="text/csv"
        )

    def test_valid_serializer_creates_report(self):
        """Serializer should validate and create a CSVDataReport instance."""
        data = {
            "unique_fields": "id",
            "source_file": self.valid_csv_file,
            "target_file": self.valid_csv_file_2,
        }
        serializer = CSVDataReportSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()
        self.assertIsInstance(report, CSVDataReport)
        self.assertEqual(report.unique_fields, "id")
        self.assertEqual(report.status, "processing")

    def test_invalid_extension_raises_error(self):
        """Should reject non-CSV file extensions."""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"Not a CSV",
            content_type="text/csv"  # content type valid but extension invalid
        )
        data = {
            "unique_fields": "id",
            "source_file": invalid_file,
            "target_file": self.valid_csv_file_2,
        }
        serializer = CSVDataReportSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("File must have a .csv extension.", str(serializer.errors))

    def test_invalid_content_type_raises_error(self):
        """Should reject invalid MIME types even if extension is .csv."""
        invalid_file = SimpleUploadedFile(
            "data.csv",
            b"1,2,3",
            content_type="application/pdf"  # invalid MIME type
        )
        data = {
            "unique_fields": "id",
            "source_file": invalid_file,
            "target_file": self.valid_csv_file_2,
        }
        serializer = CSVDataReportSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Unsupported file content type", str(serializer.errors))

    def test_missing_unique_fields(self):
        """unique_fields must be required and non-blank."""
        data = {
            "unique_fields": "",
            "source_file": self.valid_csv_file,
            "target_file": self.valid_csv_file_2,
        }
        serializer = CSVDataReportSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("unique_fields", serializer.errors)


class ListCSVDataReportSerializerTests(TestCase):
    def test_serializes_expected_fields(self):
        """List serializer should return only id, created_at, updated_at, and status."""
        report = CSVDataReport.objects.create(
            unique_fields="id",
            source_file=SimpleUploadedFile("source.csv", b"id\n1", content_type="text/csv"),
            target_file=SimpleUploadedFile("target.csv", b"id\n1", content_type="text/csv"),
        )
        serializer = ListCSVDataReportSerializer(report)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("status", data)
        self.assertEqual(len(data.keys()), 4)
