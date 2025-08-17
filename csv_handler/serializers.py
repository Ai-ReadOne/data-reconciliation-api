from rest_framework import serializers


def validate_is_csv(file):
    """
    Validator to check if the uploaded file is a CSV by checking its extension and content type.
    """
    
    if not file.name.lower().endswith(".csv"):
        raise serializers.ValidationError("File must have a .csv extension.")

    if file.content_type != "text/csv" and file.content_type != "application/vnd.ms-excel":
        raise serializers.ValidationError(
            f"Unsupported file content type '{file.content_type}'. Must be 'text/csv'."
        )


class CSVFileUploadSerializer(serializers.Serializer):
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