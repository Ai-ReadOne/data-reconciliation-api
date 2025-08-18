from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CSVFileUploadSerializer
from .csv_parser import CSVParser

class CSVFileUploadView(APIView):
    """
    Handles POST requests for uploading and normalizing CSV files.
    """

    def post(self, request, *args, **kwargs):
        serializer = CSVFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            source_file = request.FILES['source_file']
            target_file = request.FILES['target_file']
            csv_engine = CSVParser()
            source_data = csv_engine.read_csv(source_file)
            target_data = csv_engine.read_csv(target_file)
            
            return Response(
                {
                    "message": "Files uploaded and normalized successfully.",
                    "normalized_source": source_data.get("data"),
                    "normalized_target": target_data.get("data"),
                    "field_names": set(source_data.get("field_names") + target_data.get("field_names"))
                },
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)