from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CSVFileUploadSerializer
from .csv_parser import CSVParser
from data_reconciler.processor import DataReconciler


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
            index = serializer.data['unique_fields'].split(',')
            print(index)


            reconciliation_result = DataReconciler.reconcile(
                source_data.get("data"), 
                target_data.get("data"),
                index
            )

            return Response(
                {
                    "message": "Files uploaded and normalized successfully.",
                    "reconciliation_result": reconciliation_result,
                },
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)