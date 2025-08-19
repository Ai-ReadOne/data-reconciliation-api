import html
from typing import List, Dict, Any

class HTMLReportGenerator:
    """
    Generates an HTML report from a reconciliation result JSON object.
    """

    @staticmethod
    def _generate_table_from_records(records: List[Dict[str, Any]], title: str) -> str:
        """Generates an HTML table for a list of records (e.g., missing items)."""
       
        if not records:
            return f"<h2>{html.escape(title)}</h2><p>None</p>"

        headers = records[0].keys()
        header_html = "".join(f"<th>{html.escape(str(header))}</th>" for header in headers)

        rows_html = ""
        for record in records:
            row_data = "".join(f"<td>{html.escape(str(record.get(header, '')))}</td>" for header in headers)
            rows_html += f"<tr>{row_data}</tr>"

        return f"""
        <h2>{html.escape(title)}</h2>
        <table border="1">
            <thead>
                <tr>{header_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """

    @staticmethod
    def _generate_discrepancies_table(discrepancies: List[Dict[str, Any]]) -> str:
        """Generates a detailed HTML table for discrepancies."""
        if not discrepancies:
            return "<h2>Discrepancies</h2><p>None</p>"

        headers = ["Key", "Field", "Source Value", "Target Value"]
        header_html = "".join(f"<th>{header}</th>" for header in headers)

        rows_html = ""
        for item in discrepancies:
            key = ", ".join(map(str, item.get("key", [])))
            for field, values in item.get("differences", {}).items():
                source_val = values.get("source", "")
                target_val = values.get("target", "")
                rows_html += f"""
                <tr>
                    <td>{html.escape(key)}</td>
                    <td>{html.escape(field)}</td>
                    <td>{html.escape(str(source_val))}</td>
                    <td>{html.escape(str(target_val))}</td>
                </tr>
                """

        return f"""
            <h2>Discrepancies</h2>
            <table border="1">
                <thead>
                    <tr>{header_html}</tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        """

    @classmethod
    def generate_html(cls, report_data: Dict[str, Any]) -> str:
        """
        Generates a full HTML report from the reconciliation data.
        """
        style = """
        <style>
            body { font-family: sans-serif; margin: 2em; }
            table { border-collapse: collapse; margin-bottom: 20px; width: 100%; }
            th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
            th { background-color: #f2f2f2; }
            h1, h2 { color: #333; }
        </style>
        """
        discrepancies_html = cls._generate_discrepancies_table(report_data.get("discrepancies", []))
        missing_in_target_html = cls._generate_table_from_records(report_data.get("missing_in_target", []), "Missing in Target (Present in Source)")
        missing_in_source_html = cls._generate_table_from_records(report_data.get("missing_in_source", []), "Missing in Source (Present in Target)")

        return f"""<!DOCTYPE html />
                    <html>
                        <head>
                            <title>Reconciliation Report</title>
                            {style}
                        </head>
                        <body>
                            <h1>Reconciliation Report</h1>
                                {discrepancies_html}
                                {missing_in_target_html}
                                {missing_in_source_html}
                        </body>
                    </html>
                """
