"""
Advanced Column Splitting for Pole Transfer Data
=================================================

This module handles the complex task of splitting raw marker data into three
distinct fields: Marker Name, Engine Number, and Pole Number.

Key Constraints:
- Engine Number: Always exactly 7 digits
- Pole Number: Variable length (numeric or alphanumeric)
- Marker Name: Variable text (e.g., "POLE TRANSFER", "Plant Repair")
- Format: [Marker Name] [Engine Number] - [Pole Number]

Author: Max's Automation Team
Date: 2025-12-03
"""

import pandas as pd
import re
from typing import Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ColumnSplitter:
    """
    Handles advanced column splitting using regex patterns to separate
    conjoined marker, engine, and pole number data.
    """

    # Primary pattern: Captures Marker Name + 7-digit Engine Number + Pole Number
    PRIMARY_PATTERN = r"^(.*?)\s*(\d{7})\s*-\s*([0-9a-zA-Z\s-]+)$"

    # Alternative pattern: For cases where marker name is missing
    NO_MARKER_PATTERN = r"^(\d{7})\s*-\s*([0-9a-zA-Z\s-]+)$"

    # Pattern for detecting job numbers that should be filtered
    JOB_NUMBER_PATTERN = r"JB\d+"

    def __init__(self, raw_column_name: str = 'Raw_Marker_Data'):
        """
        Initialize the ColumnSplitter.

        Args:
            raw_column_name: Name of the column containing raw marker data
        """
        self.raw_column_name = raw_column_name
        self.primary_regex = re.compile(self.PRIMARY_PATTERN)
        self.no_marker_regex = re.compile(self.NO_MARKER_PATTERN)
        self.job_number_regex = re.compile(self.JOB_NUMBER_PATTERN)

    def split_marker_data(self, raw_text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Split a single raw marker data string into its components.

        Args:
            raw_text: Raw string containing marker, engine, and pole data

        Returns:
            Tuple of (marker_name, engine_number, pole_number)
            Returns (None, None, None) if parsing fails
        """
        if pd.isna(raw_text) or not isinstance(raw_text, str):
            return (None, None, None)

        # Clean the input
        raw_text = raw_text.strip()

        # Try primary pattern first (with marker name)
        match = self.primary_regex.match(raw_text)
        if match:
            marker_name = match.group(1).strip()
            engine_number = match.group(2)
            pole_number = match.group(3).strip()

            # If marker name is empty, set it to None
            marker_name = marker_name if marker_name else None

            return (marker_name, engine_number, pole_number)

        # Try alternative pattern (without marker name)
        match = self.no_marker_regex.match(raw_text)
        if match:
            engine_number = match.group(1)
            pole_number = match.group(2).strip()
            return (None, engine_number, pole_number)

        # If no pattern matches, log and return None values
        logger.warning(f"Could not parse: '{raw_text}'")
        return (None, None, None)

    def process_dataframe(self, df: pd.DataFrame,
                         remove_original: bool = True,
                         filter_job_numbers: bool = True) -> pd.DataFrame:
        """
        Process an entire DataFrame, splitting the raw marker column.

        Args:
            df: Input DataFrame containing raw marker data
            remove_original: Whether to delete the original raw column after splitting
            filter_job_numbers: Whether to exclude rows with job numbers (JB...)

        Returns:
            DataFrame with new columns: Marker_Name, Engine_Number, Pole_Number
        """
        if self.raw_column_name not in df.columns:
            raise ValueError(f"Column '{self.raw_column_name}' not found in DataFrame")

        logger.info(f"Processing {len(df)} rows...")

        # Create a copy to avoid modifying the original
        result_df = df.copy()

        # Optional: Filter out job numbers if requested
        if filter_job_numbers:
            original_count = len(result_df)
            result_df = result_df[~result_df[self.raw_column_name].astype(str).str.contains(
                self.JOB_NUMBER_PATTERN, regex=True, na=False
            )]
            filtered_count = original_count - len(result_df)
            if filtered_count > 0:
                logger.info(f"Filtered out {filtered_count} rows containing job numbers")

        # Apply the splitting logic to each row
        split_data = result_df[self.raw_column_name].apply(self.split_marker_data)

        # Unpack the tuples into separate columns
        result_df[['Marker_Name', 'Engine_Number', 'Pole_Number']] = pd.DataFrame(
            split_data.tolist(),
            index=result_df.index
        )

        # Count successful extractions
        successful = result_df['Engine_Number'].notna().sum()
        failed = len(result_df) - successful

        logger.info(f"Successfully split {successful} rows")
        if failed > 0:
            logger.warning(f"Failed to split {failed} rows (likely Plant Repair or other small jobs)")

        # Remove the original column if requested
        if remove_original:
            result_df = result_df.drop(columns=[self.raw_column_name])
            logger.info(f"Removed original column: {self.raw_column_name}")

        return result_df

    def remove_duplicates_by_pole(self, df: pd.DataFrame,
                                  keep: str = 'first') -> pd.DataFrame:
        """
        Remove duplicate entries based on Pole Number.

        Args:
            df: DataFrame with Pole_Number column
            keep: Which duplicate to keep ('first', 'last', or False to drop all)

        Returns:
            DataFrame with duplicates removed
        """
        if 'Pole_Number' not in df.columns:
            raise ValueError("Pole_Number column not found")

        original_count = len(df)

        # Remove duplicates based on Pole Number (ignoring NaN values)
        result_df = df.drop_duplicates(subset=['Pole_Number'], keep=keep)

        removed_count = original_count - len(result_df)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate pole numbers")

        return result_df

    def generate_report(self, df: pd.DataFrame) -> dict:
        """
        Generate a summary report of the splitting results.

        Args:
            df: Processed DataFrame

        Returns:
            Dictionary containing statistics
        """
        report = {
            'total_rows': len(df),
            'rows_with_marker_name': df['Marker_Name'].notna().sum(),
            'rows_with_engine_number': df['Engine_Number'].notna().sum(),
            'rows_with_pole_number': df['Pole_Number'].notna().sum(),
            'unique_markers': df['Marker_Name'].nunique(),
            'unique_engine_numbers': df['Engine_Number'].nunique(),
            'unique_pole_numbers': df['Pole_Number'].nunique(),
        }

        # Count rows that failed to parse (no engine number extracted)
        report['unparsed_rows'] = len(df) - report['rows_with_engine_number']

        return report


def main():
    """
    Main function demonstrating usage of the ColumnSplitter.
    """
    # Example data based on the requirements
    sample_data = {
        'Raw_Marker_Data': [
            'POLE TRANSFER 1237876 - 07613020',
            '3584096 - 10823022',
            'JAYSON POLE TRANSFER 3414407 - 7325119',
            '3355758 - IPID 77731',
            '3426473 - NEW POLE',
            'UG SPAN REPLACE 2841567 - 08451230',
            'NES BULK NES - VIOLATION CORRECTION 3567891 - 12345678',
            'Plant Repair',  # Edge case: no engine/pole number
            '1234567 - 999',  # Minimal case
            'POLE TRANSFER 1237876 - 07613020',  # Duplicate
        ]
    }

    # Create DataFrame
    df = pd.DataFrame(sample_data)

    print("=" * 80)
    print("ORIGINAL DATA")
    print("=" * 80)
    print(df)
    print()

    # Initialize splitter
    splitter = ColumnSplitter(raw_column_name='Raw_Marker_Data')

    # Process the DataFrame
    processed_df = splitter.process_dataframe(
        df,
        remove_original=False,  # Keep original for comparison
        filter_job_numbers=True
    )

    print("=" * 80)
    print("AFTER COLUMN SPLITTING")
    print("=" * 80)
    print(processed_df)
    print()

    # Remove duplicates
    final_df = splitter.remove_duplicates_by_pole(processed_df)

    print("=" * 80)
    print("AFTER DUPLICATE REMOVAL")
    print("=" * 80)
    print(final_df)
    print()

    # Generate report
    report = splitter.generate_report(final_df)

    print("=" * 80)
    print("PROCESSING REPORT")
    print("=" * 80)
    for key, value in report.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print()


if __name__ == "__main__":
    main()
