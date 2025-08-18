import csv
from typing import List, Dict, IO, Any
from datetime import datetime

class CSVParser:
    """
    Utility class for reading, and cleaning (nomralizing) CSV data.
    """

    @classmethod
    def read_csv(cls, file_obj: IO) -> Dict[str, List]:
        """
        Reads a CSV file-like object and returns a list of dictionaries.
        """
        file_obj.seek(0)
        decoded = (line.decode('utf-8') for line in file_obj)
        reader = csv.DictReader(decoded)
        data = [row for row in reader]
        field_names = reader.fieldnames
        return dict(data=cls.clean_data(data), field_names=list(field_names))

    @staticmethod
    def clean_value(value: str) -> str:
        """
        Normalize a single value: strip spaces, lowercase, and standardize date formats.
        """
        if not isinstance(value, str):
            return value
        value = value.strip()

        # Try to parse as date (ISO or common formats)
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return value.lower()  

    @classmethod
    def clean_data(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize a list of rows.
        """
        for row in data:
            for key, value in row.items():
                row[key] = cls.clean_value(value)
        return data


    