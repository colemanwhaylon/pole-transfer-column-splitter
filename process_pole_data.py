"""
Practical Script for Processing Pole Transfer Data from CSV/Excel Files
========================================================================

This script provides a command-line interface for processing pole transfer
data files with the advanced column splitter.

Usage:
    python process_pole_data.py input.csv output.csv
    python process_pole_data.py input.xlsx output.xlsx --sheet "Sheet1"

Features:
- Automatic file format detection (CSV/Excel)
- Column name auto-detection
- Comprehensive error handling and validation
- Progress reporting
- Backup creation before processing

Author: Max's Automation Team
Date: 2025-12-03
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from advanced_column_splitter import ColumnSplitter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataFileProcessor:
    """
    Handles reading, processing, and writing pole transfer data files.
    """

    # Common column names that might contain the raw marker data
    POSSIBLE_COLUMN_NAMES = [
        'Raw_Marker_Data',
        'Area Section Marker / Installation plan',
        'Marker Data',
        'Marker',
        'Installation Plan',
        'Raw Data',
    ]

    def __init__(self):
        """Initialize the processor."""
        self.splitter = None

    def detect_column_name(self, df: pd.DataFrame) -> str:
        """
        Auto-detect which column contains the raw marker data.

        Args:
            df: Input DataFrame

        Returns:
            Name of the detected column

        Raises:
            ValueError: If no matching column is found
        """
        # First, try exact matches
        for col_name in self.POSSIBLE_COLUMN_NAMES:
            if col_name in df.columns:
                logger.info(f"Found marker column: '{col_name}'")
                return col_name

        # Then try partial matches (case-insensitive)
        for col_name in df.columns:
            col_lower = col_name.lower()
            if any(keyword in col_lower for keyword in ['marker', 'installation', 'raw']):
                logger.info(f"Detected marker column by keyword match: '{col_name}'")
                return col_name

        # If still not found, show available columns
        logger.error("Could not detect marker column. Available columns:")
        for col in df.columns:
            logger.error(f"  - {col}")

        raise ValueError(
            "Could not auto-detect marker column. Please specify with --column parameter."
        )

    def validate_input_data(self, df: pd.DataFrame, column_name: str) -> bool:
        """
        Validate the input data before processing.

        Args:
            df: Input DataFrame
            column_name: Name of the raw marker column

        Returns:
            True if validation passes

        Raises:
            ValueError: If validation fails
        """
        # Check if DataFrame is empty
        if len(df) == 0:
            raise ValueError("Input file is empty")

        # Check if specified column exists
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in input file")

        # Check if column has any non-null values
        non_null_count = df[column_name].notna().sum()
        if non_null_count == 0:
            raise ValueError(f"Column '{column_name}' has no data")

        logger.info(f"Validation passed: {len(df)} rows, {non_null_count} non-null values")
        return True

    def create_backup(self, file_path: Path) -> Path:
        """
        Create a backup of the original file.

        Args:
            file_path: Path to the file to backup

        Returns:
            Path to the backup file
        """
        if not file_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"

        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
            return None

    def read_file(self, file_path: Path, sheet_name: str = None) -> pd.DataFrame:
        """
        Read data from CSV or Excel file.

        Args:
            file_path: Path to input file
            sheet_name: Sheet name for Excel files (optional)

        Returns:
            DataFrame containing the data

        Raises:
            ValueError: If file format is not supported
        """
        logger.info(f"Reading file: {file_path}")

        suffix = file_path.suffix.lower()

        try:
            if suffix == '.csv':
                df = pd.read_csv(file_path)
            elif suffix in ['.xlsx', '.xls']:
                if sheet_name:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

            logger.info(f"Successfully read {len(df)} rows, {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise

    def write_file(self, df: pd.DataFrame, file_path: Path, sheet_name: str = 'Processed Data'):
        """
        Write DataFrame to CSV or Excel file.

        Args:
            df: DataFrame to write
            file_path: Output file path
            sheet_name: Sheet name for Excel files
        """
        logger.info(f"Writing output to: {file_path}")

        suffix = file_path.suffix.lower()

        try:
            if suffix == '.csv':
                df.to_csv(file_path, index=False)
            elif suffix in ['.xlsx', '.xls']:
                df.to_excel(file_path, sheet_name=sheet_name, index=False)
            else:
                raise ValueError(f"Unsupported output format: {suffix}")

            logger.info(f"Successfully wrote {len(df)} rows to {file_path}")

        except Exception as e:
            logger.error(f"Error writing file: {e}")
            raise

    def process_file(self,
                    input_path: str,
                    output_path: str,
                    column_name: str = None,
                    sheet_name: str = None,
                    remove_original: bool = True,
                    remove_duplicates: bool = True,
                    filter_job_numbers: bool = True,
                    create_backup: bool = True) -> dict:
        """
        Complete processing pipeline for a pole transfer data file.

        Args:
            input_path: Path to input file
            output_path: Path to output file
            column_name: Name of raw marker column (auto-detected if None)
            sheet_name: Sheet name for Excel files
            remove_original: Remove original raw column after splitting
            remove_duplicates: Remove duplicate pole numbers
            filter_job_numbers: Filter out job numbers (JB...)
            create_backup: Create backup of output file if it exists

        Returns:
            Dictionary containing processing statistics
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        # Validate input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Create backup of output file if it exists
        if create_backup and output_path.exists():
            self.create_backup(output_path)

        # Read input file
        df = self.read_file(input_path, sheet_name)

        # Detect column name if not specified
        if column_name is None:
            column_name = self.detect_column_name(df)

        # Validate input data
        self.validate_input_data(df, column_name)

        # Initialize splitter with detected column name
        self.splitter = ColumnSplitter(raw_column_name=column_name)

        # Process the data
        logger.info("Starting column splitting...")
        processed_df = self.splitter.process_dataframe(
            df,
            remove_original=remove_original,
            filter_job_numbers=filter_job_numbers
        )

        # Remove duplicates if requested
        if remove_duplicates:
            logger.info("Removing duplicate pole numbers...")
            processed_df = self.splitter.remove_duplicates_by_pole(processed_df)

        # Generate report
        report = self.splitter.generate_report(processed_df)

        # Write output file
        self.write_file(processed_df, output_path, sheet_name='Processed Data')

        # Add file info to report
        report['input_file'] = str(input_path)
        report['output_file'] = str(output_path)
        report['input_rows'] = len(df)
        report['output_rows'] = len(processed_df)

        return report


def print_report(report: dict):
    """
    Print a formatted processing report.

    Args:
        report: Report dictionary from process_file
    """
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"\nInput File:  {report['input_file']}")
    print(f"Output File: {report['output_file']}")
    print(f"\nRows Processed: {report['input_rows']} → {report['output_rows']}")
    print(f"Rows Filtered: {report['input_rows'] - report['output_rows']}")
    print(f"\nSuccessfully Parsed:")
    print(f"  - Rows with Engine Number: {report['rows_with_engine_number']}")
    print(f"  - Rows with Marker Name:   {report['rows_with_marker_name']}")
    print(f"  - Rows with Pole Number:   {report['rows_with_pole_number']}")
    print(f"\nUnique Values:")
    print(f"  - Unique Markers:        {report['unique_markers']}")
    print(f"  - Unique Engine Numbers: {report['unique_engine_numbers']}")
    print(f"  - Unique Pole Numbers:   {report['unique_pole_numbers']}")
    print(f"\nUnparsed Rows: {report['unparsed_rows']}")
    print("=" * 80 + "\n")


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Process pole transfer data files with advanced column splitting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.csv output.csv
  %(prog)s data.xlsx processed.xlsx --sheet "Sheet1"
  %(prog)s input.csv output.csv --column "Area Section Marker / Installation plan"
  %(prog)s input.csv output.csv --keep-original --no-dedupe
        """
    )

    parser.add_argument('input', type=str, help='Input file path (CSV or Excel)')
    parser.add_argument('output', type=str, help='Output file path (CSV or Excel)')
    parser.add_argument('--column', type=str, help='Name of raw marker column (auto-detected if omitted)')
    parser.add_argument('--sheet', type=str, help='Sheet name for Excel files')
    parser.add_argument('--keep-original', action='store_true', help='Keep original raw column')
    parser.add_argument('--no-dedupe', action='store_true', help='Do not remove duplicate pole numbers')
    parser.add_argument('--keep-job-numbers', action='store_true', help='Keep rows with job numbers (JB...)')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup of existing output file')

    args = parser.parse_args()

    try:
        processor = DataFileProcessor()

        report = processor.process_file(
            input_path=args.input,
            output_path=args.output,
            column_name=args.column,
            sheet_name=args.sheet,
            remove_original=not args.keep_original,
            remove_duplicates=not args.no_dedupe,
            filter_job_numbers=not args.keep_job_numbers,
            create_backup=not args.no_backup
        )

        print_report(report)

        return 0

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
