from rest_framework import serializers
from .models import CSVDataReport


def validate_is_csv(file):
    """
    Validator to check if the uploaded file is a CSV by checking its extension and content type.
    """
    
    if not file.name.lower().endswith(".csv"):
        raise serializers.ValidationError("File must have a .csv extension.")

    if file.content_type not in ("application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text/csv"):
        raise serializers.ValidationError(
            f"Unsupported file content type '{file.content_type}'. Must be one of \
            ('application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv')."
        )


class CSVDataReportSerializer(serializers.ModelSerializer):    
    """Handles the validation for source and target CSV file uploads."""

    source_file = serializers.FileField(
        required=True,
        validators=[validate_is_csv],
        help_text="The source CSV file for reconciliation.",
    )
    target_file = serializers.FileField(
        required=True, 
        validators=[validate_is_csv], 
        help_text="The target CSV file for reconciliation."
    )
    unique_fields = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="comma separated list of unique columns that should be used to identify individual records"
    )

    class Meta:
        model = CSVDataReport
        fields = ['unique_fields', 'source_file', 'target_file']

class ListCSVDataReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVDataReport
        fields = ['id', 'created_at', 'updated_at', 'status']