import uuid
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from data_reconciler.processor import DataReconciler

from .models import CSVDataReport
from .serializers import CSVDataReportSerializer
from .csv_parser import CSVParser
from data_reconciler.report_formatter.html_generator import HTMLReportGenerator
from data_reconciler.report_formatter.csv_generator import CSVReportGenerator


class CSVReconciliationViewSet(viewsets.ViewSet):
    """
    Handles CSV file uploads for reconciliation and report retrieval.
    """

    def create(self, request):
        serializer = CSVDataReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.id = uuid.uuid4()
            csv_upload = serializer.save()

            source_data = CSVParser.read_csv(serializer.validated_data["source_file"])
            target_data = CSVParser.read_csv(serializer.validated_data["target_file"])
            index = serializer.data['unique_fields'].split(',')

            reconciliation_result = DataReconciler.reconcile(
                source_data.get("data"), 
                target_data.get("data"),
                index
            )
            csv_upload.report = reconciliation_result
            csv_upload.status = "completed"
            csv_upload.save(update_fields=["report", "status"])

            return Response(
                {"job_id": csv_upload.id},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["get"], url_name="get-report")
    def json(self, request, pk=None):
        try:
            report  = CSVDataReport.objects.get(id=pk)
        except CSVDataReport.DoesNotExist:
            return HttpResponse({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(report.report, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"], url_name="get-report-in-csv")
    def csv(self, request, pk=None):
        try:
            report = CSVDataReport.objects.get(id=pk)
        except CSVDataReport.DoesNotExist:
            return HttpResponse({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        if not report.report:
            return HttpResponse("Report data is not available.", status=status.HTTP_204_NO_CONTENT, content_type='text/csv')

        try:
            csv_content = CSVReportGenerator.generate_csv(report.report)
            response = HttpResponse(csv_content, content_type='text/csv', status=status.HTTP_200_OK)
            response['Content-Disposition'] = f'attachment; filename="reconciliation_report_{pk}.csv"'
            return response
        except Exception as e:
            return HttpResponse({"error": f"Error generating CSV report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=["get"], url_name="get-report-in-html")
    def html(self, request, pk=None):
        try:
            report = CSVDataReport.objects.get(id=pk)
        except CSVDataReport.DoesNotExist:
            return HttpResponse({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        if not report.report:
            html_content = "<html><body><h1>Report Not Generated</h1><p>The report data is not available for this job.</p></body></html>"
            return HttpResponse(html_content, status=status.HTTP_200_OK, content_type='text/html')

        try:
            html_content = HTMLReportGenerator.generate_html(report.report)
            return HttpResponse(html_content, status=status.HTTP_200_OK, content_type='text/html')
        except Exception as e:
            return HttpResponse({"error": f"Error generating HTML report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
