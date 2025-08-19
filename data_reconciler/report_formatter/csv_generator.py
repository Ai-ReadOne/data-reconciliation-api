import csv
import io
from typing import List, Dict, Any


class CSVReportGenerator:
    """
    Generates a CSV report from a reconciliation result JSON object.
    """

    @staticmethod
    def _generate_csv_from_records(records: List[Dict[str, Any]], title: str) -> str:
        """Generates a CSV formatted string for a list of records with a section title."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Section title
        writer.writerow([title])

        if not records:
            writer.writerow(["None"])
        else:
            headers = list(records[0].keys())
            writer.writerow(headers)
            for record in records:
                writer.writerow([record.get(header, "") for header in headers])

        writer.writerow([])  # Add blank line for separation
        return output.getvalue()

    @staticmethod
    def _generate_discrepancies_csv(discrepancies: List[Dict[str, Any]]) -> str:
        """Generates a CSV formatted string for discrepancies."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Section title
        writer.writerow(["Discrepancies"])

        if not discrepancies:
            writer.writerow(["None"])
        else:
            headers = ["Key", "Field", "Source Value", "Target Value"]
            writer.writerow(headers)

            for item in discrepancies:
                key = ", ".join(map(str, item.get("key", [])))
                differences = item.get("differences", {})

                for field, values in differences.items():
                    source_val = values.get("source", "")
                    target_val = values.get("target", "")
                    writer.writerow([key, field, source_val, target_val])

        writer.writerow([])  # Add blank line for separation
        return output.getvalue()

    @classmethod
    def generate_csv(cls, report_data: Dict[str, Any]) -> str:
        """
        Generates a full CSV report from the reconciliation data.
        """
        discrepancies_csv = cls._generate_discrepancies_csv(
            report_data.get("discrepancies", [])
        )

        missing_in_target_csv = cls._generate_csv_from_records(
            report_data.get("missing_in_target", []),
            "Missing in Target (Present in Source)"
        )

        missing_in_source_csv = cls._generate_csv_from_records(
            report_data.get("missing_in_source", []),
            "Missing in Source (Present in Target)"
        )

        # Combine all sections
        full_csv = f"{discrepancies_csv}{missing_in_target_csv}{missing_in_source_csv}"
        return full_csv
