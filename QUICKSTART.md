# Quick Start Guide

Get started with the Advanced Column Splitter in 5 minutes!

## Installation (1 minute)

```bash
# Install required library
pip install pandas openpyxl
```

## Basic Usage (2 minutes)

### Option 1: Command Line (Easiest)

```bash
# Process your CSV file
python process_pole_data.py your_data.csv output.csv

# Process Excel file
python process_pole_data.py your_data.xlsx output.xlsx
```

### Option 2: Python Script

```python
from advanced_column_splitter import ColumnSplitter
import pandas as pd

# Load data
df = pd.read_csv('your_data.csv')

# Initialize and process
splitter = ColumnSplitter(raw_column_name='Raw_Marker_Data')
result = splitter.process_dataframe(df)

# Remove duplicates
result = splitter.remove_duplicates_by_pole(result)

# Save
result.to_csv('output.csv', index=False)
```

## Test It (2 minutes)

### Run the demo:
```bash
python advanced_column_splitter.py
```

### Run tests:
```bash
python test_column_splitter.py
```

## What It Does

**Input:**
```
POLE TRANSFER 1237876 - 07613020
```

**Output:**
| Marker_Name | Engine_Number | Pole_Number |
|-------------|---------------|-------------|
| POLE TRANSFER | 1237876 | 07613020 |

## Common Commands

```bash
# Basic processing
python process_pole_data.py input.csv output.csv

# Keep original column
python process_pole_data.py input.csv output.csv --keep-original

# Don't remove duplicates
python process_pole_data.py input.csv output.csv --no-dedupe

# Specify column name manually
python process_pole_data.py input.csv output.csv --column "Area Section Marker / Installation plan"

# Excel with specific sheet
python process_pole_data.py data.xlsx out.xlsx --sheet "Sheet1"
```

## Troubleshooting

**"Column not found"**
→ Use `--column "YourColumnName"` to specify manually

**"No data extracted"**
→ Check that Engine Numbers are exactly 7 digits and there's a hyphen delimiter

**"Import error"**
→ Run `pip install pandas openpyxl`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [test_column_splitter.py](test_column_splitter.py) for examples
- Check the edge cases in the test suite

## Need Help?

1. Run the tests to see if everything works: `python test_column_splitter.py`
2. Check the example output in the demo: `python advanced_column_splitter.py`
3. Review the README.md for detailed troubleshooting

That's it! You're ready to process pole transfer data. 🚀
