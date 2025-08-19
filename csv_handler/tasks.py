from celery import shared_task
from .models import CSVDataReport
from .csv_parser import CSVParser
from data_reconciler.processor import DataReconciler


@shared_task
def reconcile_csv_files(job_id):
    """
    Celery task to perform CSV data reconciliation in the background.
    """
    try:
        report_data = CSVDataReport.objects.get(id=job_id)
    except CSVDataReport.DoesNotExist:
        return f"Report with id {job_id} not found."

    try:
        source_data = CSVParser.read_csv(report_data.source_file)
        target_data = CSVParser.read_csv(report_data.target_file)
        index = report_data.unique_fields.split(',')

        reconciliation_result = DataReconciler.reconcile(
            source_data.get("data"),
            target_data.get("data"),
            index
        )

        report_data.report = reconciliation_result
        report_data.status = 'completed'
        report_data.save(update_fields=['report', 'status'])
    except Exception:
        report_data.status = 'failed'
        report_data.save(update_fields=['report', 'status'])
        raise
