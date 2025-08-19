import uuid
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import CSVDataReport
from .serializers import CSVDataReportSerializer, ListCSVDataReportSerializer
from data_reconciler.report_formatter.html_generator import HTMLReportGenerator
from data_reconciler.report_formatter.csv_generator import CSVReportGenerator
from .tasks import reconcile_csv_files

@extend_schema_view(
    create=extend_schema(
        summary="Submit new CSV files for reconciliation",
        description="Public endpoint to create a new user account. No authentication is required.",
        request=CSVDataReportSerializer,
        responses={
            202: {"job_id": "UUID", "status": "processing"},
            400: dict,
        },
        auth=[],
    ),
   
    list=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
@extend_schema(tags=["CSV-datasets"])
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
    
    @extend_schema(
        summary="get list of all submitted reconciliation jobs",
        description="get list of all submitted reconciliation jobs, returning their status and id",
        responses={
            200: ListCSVDataReportSerializer,
            400: {"description": "Invalid input job_id."},
            500: {"description": "unexpected error"},
        
        },
        auth=[],
    )
    @action(detail=False, methods=["get"], url_path="", url_name="list-reports")
    def get(self, request):
        reports = CSVDataReport.objects.all()
        serializer = ListCSVDataReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(
        summary="Views the reconciliation report for a specific job in JSON format",
        responses={
            201: "returns a json report",
            400: {"description": "Invalid input job_id."},
            500: {"description": "unexpected error"},
        
        },
        auth=[],
    )
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
    

    @extend_schema(
        summary="Views the reconciliation report for a specific job in CSV format",
        responses={
            201: "returns a CSV report with content-type text/csv",
            400: {"description": "Invalid input job_id."},
            500: {"description": "unexpected error"},
        
        },
        auth=[],
    )
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
        
    
    @extend_schema(
        summary="Views the reconciliation report for a specific job as an HTML page",
        responses={
            201: "returns an HTML report with content-type text/html",
            400: {"description": "Invalid input job_id."},
            500: {"description": "unexpected error"},
        
        },
        auth=[],
    )
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
        
