import uuid
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import CSVDataReport
from .serializers import CSVDataReportSerializer, ListCSVDataReportSerializer
from data_reconciler.report_formatter.html_generator import HTMLReportGenerator
from data_reconciler.report_formatter.csv_generator import CSVReportGenerator
from .tasks import reconcile_csv_files


class CSVReconciliationViewSet(viewsets.ViewSet):
    """
    Handles CSV file uploads for reconciliation and report retrieval.
    """

    def create(self, request):
        serializer = CSVDataReportSerializer(data=request.data)
        if serializer.is_valid():
            csv_upload = serializer.save()

            # Trigger the background task
            reconcile_csv_files.delay(str(csv_upload.id))

            return Response(
                {"job_id": csv_upload.id, "status": "processing"},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"], url_path="", url_name="list-reports")
    def get(self, request):
        reports = CSVDataReport.objects.all()
        serializer = ListCSVDataReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_name="get-report")
    def json(self, request, pk=None):
        try:
            uuid.UUID(pk)
        except ValueError:
            return Response({"error": "job_id must be a valid UUID format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report  = CSVDataReport.objects.get(id=pk)
        except CSVDataReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if report.status != 'completed':
            return Response({"status": report.status}, status=status.HTTP_200_OK)
        
        if not report.report:
            return Response({"message": "No descripancy found in both datasets."}, status=status.HTTP_200_OK)
        return Response(report.report, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"], url_name="get-report-in-csv")
    def csv(self, request, pk=None):
        try:
            uuid.UUID(pk)
        except ValueError:
            return Response({"error": "job_id must be a valid UUID format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = CSVDataReport.objects.get(id=pk)
        except CSVDataReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        if report.status != 'completed':
            return Response({"status": report.status}, status=status.HTTP_200_OK)
        
        if not report.report:
            return Response({"message": "No descripancy found in both datasets."}, status=status.HTTP_200_OK)

        try:
            csv_content = CSVReportGenerator.generate_csv(report.report)
            response = HttpResponse(csv_content, content_type='text/csv', status=status.HTTP_200_OK)
            response['Content-Disposition'] = f'attachment; filename="reconciliation_report_{pk}.csv"'
            return response
        except Exception as e:
            return Response({"error": f"Error generating CSV report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=["get"], url_name="get-report-in-html")
    def html(self, request, pk =None):
        try:
            uuid.UUID(pk)
        except ValueError:
            return Response({"error": "job_id must be a valid UUID format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = CSVDataReport.objects.get(id=pk)
        except CSVDataReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        if report.status != 'completed':
            return Response({"status": report.status}, status=status.HTTP_200_OK)
        
        if not report.report:
            return Response({"message": "No descripancy found in both datasets."}, status=status.HTTP_200_OK)

        try:
            html_content = HTMLReportGenerator.generate_html(report.report)
            return HttpResponse(html_content, status=status.HTTP_200_OK, content_type='text/html')
        except Exception as e:
            return Response({"error": f"Error generating HTML report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
