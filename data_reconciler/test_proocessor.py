import unittest
from .processor import DataReconciler 


class TestDataReconciler(unittest.TestCase):

    def setUp(self):
        # Sample data with single unique field 'id'
        self.source_data = [
            {"id": 1, "name": "Alice", "age": 25},
            {"id": 2, "name": "Bob", "age": 30},
            {"id": 3, "name": "Charlie", "age": 35},
        ]
        self.target_data = [
            {"id": 1, "name": "Alice", "age": 25},
            {"id": 2, "name": "Bob", "age": 31},  # Age differs here
            {"id": 4, "name": "David", "age": 40}, # Only in target
        ]

        # Data with multi-column unique keys
        self.source_multi_key = [
            {"country": "USA", "year": 2020, "population": 331},
            {"country": "USA", "year": 2021, "population": 333},
            {"country": "Canada", "year": 2020, "population": 38},
        ]
        self.target_multi_key = [
            {"country": "USA", "year": 2020, "population": 331},
            {"country": "USA", "year": 2021, "population": 334},  # Discrepancy here
            {"country": "Canada", "year": 2021, "population": 39}, # Only in target
        ]

        # Data with NaN values
        self.source_nan = [
            {"id": 1, "value": None},
            {"id": 2, "value": float('nan')},
            {"id": 3, "value": 100},
        ]
        self.target_nan = [
            {"id": 1, "value": None},
            {"id": 2, "value": float('nan')},
            {"id": 3, "value": 101},  # Discrepancy here
        ]

    def test_no_differences(self):
        # Identical datasets should return empty results
        result = DataReconciler.reconcile(
            self.source_data[:1],  # only first record
            self.source_data[:1],  # same record in target
            unique_fields=['id']
        )
        self.assertEqual(result['only_in_source'], [])
        self.assertEqual(result['only_in_target'], [])
        self.assertEqual(result['discrepancies'], [])

    def test_only_in_source_and_target(self):
        result = DataReconciler.reconcile(
            self.source_data,
            self.target_data,
            unique_fields=['id']
        )
        # id=3 only in source
        self.assertIn({'id': 3, 'name': 'Charlie', 'age': 35}, result['only_in_source'])
        # id=4 only in target
        self.assertIn({'id': 4, 'name': 'David', 'age': 40}, result['only_in_target'])

    def test_discrepancies(self):
        result = DataReconciler.reconcile(
            self.source_data,
            self.target_data,
            unique_fields=['id']
        )
        discrepancies = result['discrepancies']
        self.assertEqual(len(discrepancies), 1)
        diff = discrepancies[0]
        self.assertEqual(diff['key'], (2,))
        self.assertIn('age', diff['differences'])
        self.assertEqual(diff['differences']['age']['source'], 30)
        self.assertEqual(diff['differences']['age']['target'], 31)

    def test_multi_column_index(self):
        result = DataReconciler.reconcile(
            self.source_multi_key,
            self.target_multi_key,
            unique_fields=['country', 'year']
        )
        # Only in source: Canada 2020
        self.assertIn({'country': 'Canada', 'year': 2020, 'population': 38}, result['only_in_source'])
        # Only in target: Canada 2021
        self.assertIn({'country': 'Canada', 'year': 2021, 'population': 39}, result['only_in_target'])
        # Discrepancy on USA 2021 population
        self.assertEqual(len(result['discrepancies']), 1)
        discrepancy = result['discrepancies'][0]
        self.assertEqual(discrepancy['key'], ('USA', 2021))
        self.assertIn('population', discrepancy['differences'])
        self.assertEqual(discrepancy['differences']['population']['source'], 333)
        self.assertEqual(discrepancy['differences']['population']['target'], 334)

    def test_nan_handling(self):
        result = DataReconciler.reconcile(
            self.source_nan,
            self.target_nan,
            unique_fields=['id']
        )
        # Only one discrepancy on id=3 because None and NaN are treated equal if both null
        self.assertEqual(len(result['discrepancies']), 1)
        discrepancy = result['discrepancies'][0]
        self.assertEqual(discrepancy['key'], (3,))
        self.assertIn('value', discrepancy['differences'])
        self.assertEqual(discrepancy['differences']['value']['source'], 100)
        self.assertEqual(discrepancy['differences']['value']['target'], 101)

    def test_empty_datasets(self):
        DataReconciler.reconcile([], [], unique_fields=['id'])
        self.assertRaises(ValueError)

    def test_empty_source_dataset(self):
        DataReconciler.reconcile(self.source_multi_key, [], unique_fields=['id'])
        self.assertRaises(ValueError)

    def test_empty_target_dataset(self):
        DataReconciler.reconcile([], self.source_multi_key, unique_fields=['id'])
        self.assertRaises(ValueError)

    def test_empty_unique_fields(self):
        DataReconciler.reconcile(self.source_multi_key, self.source_multi_key, unique_fields=[])
        self.assertRaises(ValueError)

    def test_non_overlapping_indexes(self):
        source = [{'id': 1, 'val': 'a'}]
        target = [{'id': 2, 'val': 'b'}]
        result = DataReconciler.reconcile(source, target, unique_fields=['id'])
        self.assertEqual(len(result['only_in_source']), 1)
        self.assertEqual(len(result['only_in_target']), 1)
        self.assertEqual(result['discrepancies'], [])

if __name__ == '__main__':
    unittest.main()
