from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CSVFileUploadSerializer

class CSVFileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CSVFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "Files uploaded successfully."}, 
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)