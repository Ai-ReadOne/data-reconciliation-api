import uuid
from django.db import models


def upload_directory_path(instance, filename):
    return f'csv_datasets/{instance.id}/{filename}'

class CSVDataReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_file = models.FileField(upload_to=upload_directory_path)
    target_file = models.FileField(upload_to=upload_directory_path)
    unique_fields = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10, 
            choices=[
            ('processing', 'Processing'), 
            ('completed', 'Completed'), 
            ('failed', 'Failed')
        ]
    )
    report = models.JSONField(null=True, blank=True)