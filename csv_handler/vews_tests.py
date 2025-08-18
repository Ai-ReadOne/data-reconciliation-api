from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

class CSVFileUploadViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('csv-file-upload')
        self.dummy_csv = b"col1,col2\nval1,val2\n"
        self.source_file = SimpleUploadedFile("source.csv", self.dummy_csv, content_type="text/csv")
        self.target_file = SimpleUploadedFile("target.csv", self.dummy_csv, content_type="text/csv")
        self.dummy_txt = b"not,a,csv\nfile,content\n"

    def test_upload_both_files_success(self):
        response = self.client.post(
            self.url,
            {'source_file': self.source_file, 'target_file': self.target_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('message', response.data)

    def test_upload_missing_source_file(self):
        response = self.client.post(
            self.url,
            {'target_file': self.target_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)

    def test_upload_missing_target_file(self):
        response = self.client.post(
            self.url,
            {'source_file': self.source_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_file', response.data)

    def test_upload_no_files(self):
        response = self.client.post(self.url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)
        self.assertIn('target_file', response.data)

    def test_upload_non_csv_extension(self):
        source_file = SimpleUploadedFile("source.txt", self.dummy_csv, content_type="text/csv")
        target_file = SimpleUploadedFile("target.csv", self.dummy_csv, content_type="text/csv")
        response = self.client.post(
            self.url,
            {'source_file': source_file, 'target_file': target_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)
        self.assertIn('.csv extension', str(response.data['source_file']))

    def test_upload_non_csv_content_type(self):
        source_file = SimpleUploadedFile("source.csv", self.dummy_csv, content_type="text/plain")
        target_file = SimpleUploadedFile("target.csv", self.dummy_csv, content_type="text/csv")
        response = self.client.post(
            self.url,
            {'source_file': source_file, 'target_file': target_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)
        self.assertIn('Unsupported file content type', str(response.data['source_file']))

    def test_upload_both_files_invalid(self):
        source_file = SimpleUploadedFile("source.txt", self.dummy_txt, content_type="text/plain")
        target_file = SimpleUploadedFile("target.txt", self.dummy_txt, content_type="text/plain")
        response = self.client.post(
            self.url,
            {'source_file': source_file, 'target_file': target_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source_file', response.data)
        self.assertIn('target_file', response.data)