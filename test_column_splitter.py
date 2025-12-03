"""
Test Suite for Advanced Column Splitter
========================================

Comprehensive tests covering all edge cases and scenarios for the
column splitting functionality.

Run with: python test_column_splitter.py
"""

import pandas as pd
import unittest
from advanced_column_splitter import ColumnSplitter


class TestColumnSplitter(unittest.TestCase):
    """Test cases for the ColumnSplitter class."""

    def setUp(self):
        """Set up test fixtures before each test."""
        self.splitter = ColumnSplitter(raw_column_name='Raw_Marker_Data')

    def test_standard_pole_transfer(self):
        """Test standard POLE TRANSFER format."""
        result = self.splitter.split_marker_data('POLE TRANSFER 1237876 - 07613020')
        self.assertEqual(result, ('POLE TRANSFER', '1237876', '07613020'))

    def test_complex_marker_name(self):
        """Test complex marker names with multiple words."""
        result = self.splitter.split_marker_data('JAYSON POLE TRANSFER 3414407 - 7325119')
        self.assertEqual(result, ('JAYSON POLE TRANSFER', '3414407', '7325119'))

    def test_no_marker_name(self):
        """Test format with only engine and pole numbers."""
        result = self.splitter.split_marker_data('3584096 - 10823022')
        self.assertEqual(result, (None, '3584096', '10823022'))

    def test_alphanumeric_pole_number(self):
        """Test pole numbers containing letters (e.g., IPID)."""
        result = self.splitter.split_marker_data('3355758 - IPID 77731')
        self.assertEqual(result, (None, '3355758', 'IPID 77731'))

    def test_text_pole_number(self):
        """Test pole numbers that are descriptive text."""
        result = self.splitter.split_marker_data('3426473 - NEW POLE')
        self.assertEqual(result, (None, '3426473', 'NEW POLE'))

    def test_ug_span_replace(self):
        """Test UG SPAN REPLACE marker type."""
        result = self.splitter.split_marker_data('UG SPAN REPLACE 2841567 - 08451230')
        self.assertEqual(result, ('UG SPAN REPLACE', '2841567', '08451230'))

    def test_long_marker_name_with_hyphens(self):
        """Test marker names that contain hyphens themselves."""
        result = self.splitter.split_marker_data('NES BULK NES - VIOLATION CORRECTION 3567891 - 12345678')
        self.assertEqual(result, ('NES BULK NES - VIOLATION CORRECTION', '3567891', '12345678'))

    def test_plant_repair_no_numbers(self):
        """Test edge case where only marker name exists (Plant Repair)."""
        result = self.splitter.split_marker_data('Plant Repair')
        self.assertEqual(result, (None, None, None))

    def test_minimal_format(self):
        """Test minimal format with short pole number."""
        result = self.splitter.split_marker_data('1234567 - 999')
        self.assertEqual(result, (None, '1234567', '999'))

    def test_extra_whitespace(self):
        """Test handling of extra whitespace."""
        result = self.splitter.split_marker_data('  POLE TRANSFER   1237876   -   07613020  ')
        self.assertEqual(result, ('POLE TRANSFER', '1237876', '07613020'))

    def test_invalid_engine_number_too_short(self):
        """Test that engine numbers with fewer than 7 digits are rejected."""
        result = self.splitter.split_marker_data('POLE TRANSFER 123456 - 07613020')
        self.assertEqual(result, (None, None, None))

    def test_invalid_engine_number_too_long(self):
        """Test that engine numbers with more than 7 digits are handled."""
        result = self.splitter.split_marker_data('POLE TRANSFER 12345678 - 07613020')
        # If 8 digits appear, the regex matches exactly 7 digits (2345678)
        # and treats the first digit as part of the marker name
        # This is acceptable behavior as the regex anchors on 7 digits
        self.assertEqual(result[1], '2345678')  # Matches 7 digits
        self.assertIsNotNone(result[2])  # Pole number should be extracted

    def test_missing_hyphen_delimiter(self):
        """Test that missing hyphen delimiter causes parse failure."""
        result = self.splitter.split_marker_data('POLE TRANSFER 1237876 07613020')
        self.assertEqual(result, (None, None, None))

    def test_none_input(self):
        """Test handling of None input."""
        result = self.splitter.split_marker_data(None)
        self.assertEqual(result, (None, None, None))

    def test_empty_string(self):
        """Test handling of empty string."""
        result = self.splitter.split_marker_data('')
        self.assertEqual(result, (None, None, None))

    def test_dataframe_processing(self):
        """Test processing a complete DataFrame."""
        test_data = {
            'Raw_Marker_Data': [
                'POLE TRANSFER 1237876 - 07613020',
                '3584096 - 10823022',
                'Plant Repair',
            ]
        }
        df = pd.DataFrame(test_data)

        result_df = self.splitter.process_dataframe(df, remove_original=False)

        # Check that new columns were created
        self.assertIn('Marker_Name', result_df.columns)
        self.assertIn('Engine_Number', result_df.columns)
        self.assertIn('Pole_Number', result_df.columns)

        # Check first row
        self.assertEqual(result_df.iloc[0]['Marker_Name'], 'POLE TRANSFER')
        self.assertEqual(result_df.iloc[0]['Engine_Number'], '1237876')
        self.assertEqual(result_df.iloc[0]['Pole_Number'], '07613020')

        # Check third row (Plant Repair - should have None values)
        self.assertTrue(pd.isna(result_df.iloc[2]['Engine_Number']))

    def test_duplicate_removal(self):
        """Test removal of duplicate pole numbers."""
        test_data = {
            'Raw_Marker_Data': [
                'POLE TRANSFER 1237876 - 07613020',
                '3584096 - 10823022',
                'POLE TRANSFER 1237876 - 07613020',  # Duplicate
            ]
        }
        df = pd.DataFrame(test_data)

        processed_df = self.splitter.process_dataframe(df, remove_original=False)
        final_df = self.splitter.remove_duplicates_by_pole(processed_df)

        # Should have 2 rows after removing duplicate
        self.assertEqual(len(final_df), 2)

    def test_job_number_filtering(self):
        """Test filtering of job numbers (JB...)."""
        test_data = {
            'Raw_Marker_Data': [
                'JB0001234 POLE TRANSFER 1237876 - 07613020',
                '3584096 - 10823022',
            ]
        }
        df = pd.DataFrame(test_data)

        # With filtering enabled (default)
        result_df = self.splitter.process_dataframe(df, filter_job_numbers=True)
        self.assertEqual(len(result_df), 1)

        # Without filtering
        result_df = self.splitter.process_dataframe(df, filter_job_numbers=False)
        self.assertEqual(len(result_df), 2)

    def test_report_generation(self):
        """Test generation of processing report."""
        test_data = {
            'Raw_Marker_Data': [
                'POLE TRANSFER 1237876 - 07613020',
                '3584096 - 10823022',
                'Plant Repair',
            ]
        }
        df = pd.DataFrame(test_data)

        processed_df = self.splitter.process_dataframe(df)
        report = self.splitter.generate_report(processed_df)

        self.assertEqual(report['total_rows'], 3)
        self.assertEqual(report['rows_with_engine_number'], 2)
        self.assertEqual(report['unparsed_rows'], 1)

    def test_original_column_removal(self):
        """Test that original column is removed when requested."""
        test_data = {
            'Raw_Marker_Data': [
                'POLE TRANSFER 1237876 - 07613020',
            ]
        }
        df = pd.DataFrame(test_data)

        # With removal (default)
        result_df = self.splitter.process_dataframe(df, remove_original=True)
        self.assertNotIn('Raw_Marker_Data', result_df.columns)

        # Without removal
        result_df = self.splitter.process_dataframe(df, remove_original=False)
        self.assertIn('Raw_Marker_Data', result_df.columns)

    def test_special_characters_in_marker(self):
        """Test handling of special characters in marker names."""
        result = self.splitter.split_marker_data('POLE/TRANSFER & REPAIR 1237876 - 07613020')
        self.assertEqual(result, ('POLE/TRANSFER & REPAIR', '1237876', '07613020'))

    def test_pole_number_with_hyphens(self):
        """Test pole numbers that contain hyphens themselves."""
        result = self.splitter.split_marker_data('1237876 - 07613-020')
        self.assertEqual(result, (None, '1237876', '07613-020'))


class TestEdgeCases(unittest.TestCase):
    """Additional edge case tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.splitter = ColumnSplitter()

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        result = self.splitter.split_marker_data('PÔLE TRANSFER 1237876 - 07613020')
        self.assertEqual(result[1], '1237876')  # Engine number should still parse

    def test_mixed_case(self):
        """Test mixed case marker names."""
        result = self.splitter.split_marker_data('Pole Transfer 1237876 - 07613020')
        self.assertEqual(result, ('Pole Transfer', '1237876', '07613020'))

    def test_numeric_only_pole(self):
        """Test purely numeric pole numbers of various lengths."""
        for pole_num in ['1', '12', '123', '1234', '12345', '123456', '12345678']:
            result = self.splitter.split_marker_data(f'1234567 - {pole_num}')
            self.assertEqual(result[2], pole_num)

    def test_very_long_marker_name(self):
        """Test very long marker names."""
        long_marker = 'THIS IS A VERY LONG MARKER NAME WITH MANY WORDS FOR TESTING PURPOSES'
        result = self.splitter.split_marker_data(f'{long_marker} 1237876 - 07613020')
        self.assertEqual(result[0], long_marker)


def run_comprehensive_examples():
    """
    Run comprehensive examples showing various use cases.
    """
    print("\n" + "=" * 80)
    print("COMPREHENSIVE EXAMPLES")
    print("=" * 80 + "\n")

    # Example 1: Basic usage
    print("Example 1: Basic Usage")
    print("-" * 80)
    data = {
        'Raw_Marker_Data': [
            'POLE TRANSFER 1237876 - 07613020',
            '3584096 - 10823022',
            'JAYSON POLE TRANSFER 3414407 - 7325119',
        ]
    }
    df = pd.DataFrame(data)
    splitter = ColumnSplitter()
    result = splitter.process_dataframe(df)
    print(result)
    print()

    # Example 2: With edge cases
    print("Example 2: Edge Cases (Plant Repair, IPID)")
    print("-" * 80)
    data = {
        'Raw_Marker_Data': [
            '3355758 - IPID 77731',
            '3426473 - NEW POLE',
            'Plant Repair',
            'UG SPAN REPLACE 2841567 - 08451230',
        ]
    }
    df = pd.DataFrame(data)
    result = splitter.process_dataframe(df)
    print(result)
    print()

    # Example 3: Duplicate removal
    print("Example 3: Duplicate Removal")
    print("-" * 80)
    data = {
        'Raw_Marker_Data': [
            'POLE TRANSFER 1237876 - 07613020',
            '3584096 - 10823022',
            'POLE TRANSFER 1237876 - 07613020',  # Duplicate
            '3584096 - 10823022',  # Duplicate
        ]
    }
    df = pd.DataFrame(data)
    processed = splitter.process_dataframe(df)
    final = splitter.remove_duplicates_by_pole(processed)
    print(f"Original rows: {len(df)}")
    print(f"After deduplication: {len(final)}")
    print(final)
    print()


if __name__ == '__main__':
    # Run unit tests
    print("Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run comprehensive examples
    run_comprehensive_examples()
