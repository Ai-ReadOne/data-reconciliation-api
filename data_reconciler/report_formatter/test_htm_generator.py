import unittest

from .html_generator import HTMLReportGenerator


class TestHTMLReportGenerator(unittest.TestCase):
    # ---------- Helpers ----------
    def _minimal_report(self):
        return {
            "discrepancies": [],
            "missing_in_target": [],
            "missing_in_source": [],
        }

    # ---------- generate_html: structure ----------

    def test_generate_html_empty_sections_render_none(self):
        html_doc = HTMLReportGenerator.generate_html(self._minimal_report())
        # Discrepancies
        self.assertIn("<h2>Discrepancies</h2>", html_doc)
        self.assertIn("<p>None</p>", html_doc)
        # Missing in target
        self.assertIn("Missing in Target (Present in Source)", html_doc)
        # Missing in source
        self.assertIn("Missing in Source (Present in Target)", html_doc)

    # ---------- Discrepancies table ----------
    
    def test_discrepancies_none(self):
        frag = HTMLReportGenerator._generate_discrepancies_table([])
        self.assertIn("<h2>Discrepancies</h2>", frag)
        self.assertIn("<p>None</p>", frag)

    def test_discrepancies_single_item_single_field(self):
        data = [
            {
                "key": ["id=1"],
                "differences": {
                    "amount": {"source": 100, "target": 90}
                },
            }
        ]
        frag = HTMLReportGenerator._generate_discrepancies_table(data)
        # Headers
        self.assertIn("<th>Key</th>", frag)
        self.assertIn("<th>Field</th>", frag)
        self.assertIn("<th>Source Value</th>", frag)
        self.assertIn("<th>Target Value</th>", frag)
        # Content
        self.assertIn("<td>id=1</td>", frag)
        self.assertIn("<td>amount</td>", frag)
        self.assertIn("<td>100</td>", frag)
        self.assertIn("<td>90</td>", frag)

    def test_discrepancies_multiple_fields_multiple_keys(self):
        data = [
            {
                "key": ["user:42", "date:2024-01-01"],
                "differences": {
                    "name": {"source": "Alice", "target": "Alicia"},
                    "active": {"source": True, "target": False},
                },
            }
        ]
        frag = HTMLReportGenerator._generate_discrepancies_table(data)
        # Key is joined by comma + space
        self.assertIn("<td>user:42, date:2024-01-01</td>", frag)
        # Each field generates a row
        self.assertIn("<td>name</td>", frag)
        self.assertIn("<td>Alice</td>", frag)
        self.assertIn("<td>Alicia</td>", frag)
        self.assertIn("<td>active</td>", frag)
        self.assertIn("<td>True</td>", frag)
        self.assertIn("<td>False</td>", frag)

    def test_discrepancies_missing_differences_dict(self):
        data = [{"key": ["k1"], "differences": {}}]
        frag = HTMLReportGenerator._generate_discrepancies_table(data)
        # Empty differences => no rows within tbody
        self.assertIn("<tbody>", frag)
        # Ensure the tbody exists but contains no <tr> with data
        tbody = frag.split("<tbody>")[1].split("</tbody>")[0]
        self.assertNotIn("<tr>", tbody)

    # ---------- _generate_table_from_records ----------
    def test_table_from_records_none(self):
        frag = HTMLReportGenerator._generate_table_from_records([], "Missing in Target (Present in Source)")
        self.assertIn("<h2>Missing in Target (Present in Source)</h2>", frag)
        self.assertIn("<p>None</p>", frag)

    def test_table_from_records_single_row(self):
        rows = [{"id": 1, "name": "Alice"}]
        frag = HTMLReportGenerator._generate_table_from_records(rows, "Missing in Target (Present in Source)")
        # Headers from first record's keys
        self.assertIn("<th>id</th>", frag)
        self.assertIn("<th>name</th>", frag)
        # Data
        self.assertIn("<td>1</td>", frag)
        self.assertIn("<td>Alice</td>", frag)

    def test_table_from_records_mixed_keys_uses_first_record_headers(self):
        rows = [
            {"id": 1, "name": "Alice"},          # headers taken from here
            {"id": 2, "email": "alice@x.com"},   # "email" should not appear as a header
        ]
        frag = HTMLReportGenerator._generate_table_from_records(rows, "Title")
        # Only id and name headers
        self.assertIn("<th>id</th>", frag)
        self.assertIn("<th>name</th>", frag)
        self.assertNotIn("<th>email</th>", frag)
        # Second row should fill missing "name" with empty string
        # We expect a row containing <td>2</td> and an empty <td></td> for name
        self.assertIn("<td>2</td>", frag)
        # At least one empty cell for missing key
        self.assertIn("<td></td>", frag)

    def test_table_from_records_non_string_values_and_none(self):
        rows = [{"a": None, "b": 123, "c": 45.6, "d": True, "e": False}]
        frag = HTMLReportGenerator._generate_table_from_records(rows, "Title")
        # Make sure values turn into strings
        self.assertIn("<td>None</td>", frag)
        self.assertIn("<td>123</td>", frag)
        self.assertIn("<td>45.6</td>", frag)
        self.assertIn("<td>True</td>", frag)
        self.assertIn("<td>False</td>", frag)

    # ---------- Escaping ----------
    def test_escaping_in_headers_and_values(self):
        rows = [{"x<y": "a&b", "danger": "<script>alert(\"x\")</script>"}]
        frag = HTMLReportGenerator._generate_table_from_records(rows, 'Title "with" & <chars>')
        # Title is escaped
        self.assertIn("<h2>Title &quot;with&quot; &amp; &lt;chars&gt;</h2>", frag)
        # Header is escaped
        self.assertIn("<th>x&lt;y</th>", frag)
        self.assertIn("<th>danger</th>", frag)
        # Values are escaped
        self.assertIn("<td>a&amp;b</td>", frag)
        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", frag)
        # Ensure no raw <script> survives
        self.assertNotIn("<script>", frag)

    def test_escaping_in_discrepancies(self):
        data = [
            {
                "key": ["id<1>", "a&b"],
                "differences": {
                    "field<1>": {"source": "<x>", "target": "\"y\" & 'z'"},
                },
            }
        ]
        frag = HTMLReportGenerator._generate_discrepancies_table(data)
        # Key escaped and joined
        self.assertIn("<td>id&lt;1&gt;, a&amp;b</td>", frag)
        # Field escaped
        self.assertIn("<td>field&lt;1&gt;</td>", frag)
        # Values escaped
        self.assertIn("<td>&lt;x&gt;</td>", frag)
        self.assertIn("<td>&quot;y&quot; &amp; &#x27;z&#x27;</td>", frag)

    # ---------- End-to-end with populated data ----------
    def test_generate_html_with_full_data(self):
        report = {
            "discrepancies": [
                {
                    "key": ["id:1"],
                    "differences": {
                        "amount": {"source": 10, "target": 15},
                        "status": {"source": "open", "target": "closed"},
                    },
                }
            ],
            "missing_in_target": [
                {"id": 2, "name": "MissingThere"}
            ],
            "missing_in_source": [
                {"id": 3, "name": "MissingHere"}
            ],
        }
        html_doc = HTMLReportGenerator.generate_html(report)
        # Discrepancies
        self.assertIn("<td>id:1</td>", html_doc)
        self.assertIn("<td>amount</td>", html_doc)
        self.assertIn("<td>10</td>", html_doc)
        self.assertIn("<td>15</td>", html_doc)
        self.assertIn("<td>status</td>", html_doc)
        self.assertIn("<td>open</td>", html_doc)
        self.assertIn("<td>closed</td>", html_doc)
        # Missing in target
        self.assertIn("Missing in Target (Present in Source)", html_doc)
        self.assertIn("<td>2</td>", html_doc)
        self.assertIn("<td>MissingThere</td>", html_doc)
        # Missing in source
        self.assertIn("Missing in Source (Present in Target)", html_doc)
        self.assertIn("<td>3</td>", html_doc)
        self.assertIn("<td>MissingHere</td>", html_doc)

    # ---------- Robustness ----------
    def test_generate_html_handles_missing_top_level_keys(self):
        # Only discrepancies key provided
        html_doc = HTMLReportGenerator.generate_html({"discrepancies": []})
        self.assertIn("<h2>Discrepancies</h2>", html_doc)
        self.assertIn("Missing in Target (Present in Source)", html_doc)
        self.assertIn("Missing in Source (Present in Target)", html_doc)

    def test_generate_html_never_unescapes_user_content(self):
        # Make sure dangerous content stays escaped in the final page
        report = {
            "discrepancies": [
                {"key": ["<b>bold</b>"], "differences": {"f": {"source": "<img>", "target": "<svg>"}}}
            ],
            "missing_in_target": [{"h1": "<h1>"}],
            "missing_in_source": [{"script": "<script>bad()</script>"}],
        }
        html_doc = HTMLReportGenerator.generate_html(report)
        self.assertNotIn("<script>bad()</script>", html_doc)
        self.assertIn("&lt;script&gt;bad()&lt;/script&gt;", html_doc)
        self.assertIn("&lt;img&gt;", html_doc)
        self.assertIn("&lt;svg&gt;", html_doc)
        self.assertIn("&lt;h1&gt;", html_doc)
        # Ensure no unexpected unescaped HTML user data appears
        # (sanity: the doc must still have our own structural tags)
        self.assertIn("<table", html_doc)


if __name__ == "__main__":
    unittest.main()
