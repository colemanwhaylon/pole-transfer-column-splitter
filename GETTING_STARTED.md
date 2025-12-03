# Getting Started - Step by Step

## 🎯 Goal
Split raw marker data into three columns (Marker Name, Engine Number, Pole Number) with **yellow highlighting** in Excel output.

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install pandas openpyxl
```

### Step 2: Test with Sample Data (1 minute)

```bash
python process_with_highlighting.py example_sample_data.csv example_output.xlsx
```

### Step 3: Open the Excel File

Open `example_output.xlsx` and you'll see:
- ✅ Three new columns: **Marker_Name**, **Engine_Number**, **Pole_Number**
- ✅ **Yellow background** on all three new columns
- ✅ Blue header row with white text
- ✅ Clean, professional formatting

## 🔧 Process Your Own Data

### For CSV Files:

```bash
python process_with_highlighting.py your_data.csv output.xlsx
```

### For Excel Files:

```bash
python process_with_highlighting.py your_data.xlsx output.xlsx --sheet "Sheet1"
```

### If Column Auto-Detection Fails:

```bash
python process_with_highlighting.py input.csv output.xlsx --column "Area Section Marker / Installation plan"
```

## 📋 What the Script Does

1. **Reads** your CSV or Excel file
2. **Detects** the column containing raw marker data
3. **Splits** each row into three parts using regex:
   - Marker Name (e.g., "POLE TRANSFER")
   - Engine Number (exactly 7 digits)
   - Pole Number (variable length)
4. **Removes** duplicate pole numbers (optional)
5. **Filters** job numbers like JB0001234 (optional)
6. **Creates** Excel file with **yellow highlighting** on new columns
7. **Reports** processing statistics

## 📊 Expected Input Format

Your raw data column should look like this:

```
POLE TRANSFER 1237876 - 07613020
3584096 - 10823022
JAYSON POLE TRANSFER 3414407 - 7325119
3355758 - IPID 77731
Plant Repair
```

**Pattern:** `[Marker Name] [7-digit Engine Number] - [Pole Number]`

## ✅ Expected Output

Three new columns with **yellow background**:

| Marker_Name | Engine_Number | Pole_Number |
|-------------|---------------|-------------|
| 🟨 POLE TRANSFER | 🟨 1237876 | 🟨 07613020 |
| 🟨 (empty) | 🟨 3584096 | 🟨 10823022 |
| 🟨 JAYSON POLE TRANSFER | 🟨 3414407 | 🟨 7325119 |
| 🟨 (empty) | 🟨 3355758 | 🟨 IPID 77731 |
| 🟨 (empty) | 🟨 (empty) | 🟨 (empty) |

## 🎛️ Command Options

### Basic Usage
```bash
python process_with_highlighting.py INPUT.csv OUTPUT.xlsx
```

### Keep Original Column
```bash
python process_with_highlighting.py input.csv output.xlsx --keep-original
```

### Don't Remove Duplicates
```bash
python process_with_highlighting.py input.csv output.xlsx --no-dedupe
```

### Keep Job Numbers (Don't Filter JB...)
```bash
python process_with_highlighting.py input.csv output.xlsx --keep-job-numbers
```

### Excel Input with Specific Sheet
```bash
python process_with_highlighting.py data.xlsx output.xlsx --sheet "Sheet1"
```

### Specify Column Name
```bash
python process_with_highlighting.py input.csv output.xlsx --column "Raw_Marker_Data"
```

## 🧪 Testing

### Run Unit Tests
```bash
python test_column_splitter.py
```

Expected: `26 tests - ALL PASSING ✅`

### Run Demo
```bash
python advanced_column_splitter.py
```

Expected: See processing output with example data

## 🚨 Troubleshooting

### "Module 'pandas' not found"
```bash
pip install pandas openpyxl
```

### "Column not found"
Use `--column` to specify the exact column name:
```bash
python process_with_highlighting.py input.csv output.xlsx --column "Your Column Name"
```

### "No data extracted"
Check that:
1. Engine Numbers are exactly 7 digits
2. There's a hyphen `-` between Engine and Pole numbers
3. Your data matches the expected format

### See Available Columns
If auto-detection fails, the script will show you available columns in the error message.

## 📁 File Structure

```
Max/
├── advanced_column_splitter.py       # Core splitting logic
├── process_with_highlighting.py      # ⭐ Main tool with Excel highlighting
├── process_pole_data.py              # Alternative tool (CSV/Excel output)
├── test_column_splitter.py           # Unit tests
├── example_sample_data.csv           # Sample input data
├── example_output.xlsx               # Sample output (with highlighting)
├── requirements.txt                  # Dependencies
├── README.md                         # Full documentation
├── QUICKSTART.md                     # Quick reference
├── SUMMARY.md                        # Project summary
└── GETTING_STARTED.md               # This file
```

## 🎓 Understanding the Output

When you run the highlighting tool, you'll see:

```
================================================================================
PROCESSING COMPLETE - NEW COLUMNS HIGHLIGHTED IN YELLOW
================================================================================

Input File:  example_sample_data.csv
Output File: example_output.xlsx

📊 Rows: 12 → 10
   Filtered: 2 rows

✅ Successfully Parsed:
   - Engine Numbers: 9
   - Marker Names:   5
   - Pole Numbers:   9

⚠️  Unparsed Rows: 1 (e.g., Plant Repair)

🎨 The following NEW columns are highlighted in YELLOW:
   - Marker_Name
   - Engine_Number
   - Pole_Number

================================================================================
✨ Open the Excel file to see the highlighted columns!
================================================================================
```

**What this means:**
- **12 → 10**: Started with 12 rows, ended with 10 (2 duplicates removed)
- **Engine Numbers: 9**: Successfully extracted 9 engine numbers
- **Unparsed Rows: 1**: 1 row couldn't be parsed (like "Plant Repair")
- **Yellow Highlighting**: The three new columns are highlighted in yellow

## 🔍 Edge Cases Handled

✅ **Missing Marker Name**: `3584096 - 10823022`
✅ **Complex Markers**: `NES BULK NES - VIOLATION CORRECTION 3567891 - 12345678`
✅ **Alphanumeric Pole Numbers**: `3355758 - IPID 77731`
✅ **Text Pole Numbers**: `3426473 - NEW POLE`
✅ **Plant Repair** (no numbers): Sets all fields to empty
✅ **Extra Whitespace**: Automatically trimmed
✅ **Special Characters**: Handled correctly

## 💡 Pro Tips

1. **Always check the output report** to see how many rows were parsed successfully
2. **Review unparsed rows** - they might need manual handling
3. **Keep backups** - The script creates automatic backups of existing output files
4. **Test on a small sample** before processing large datasets
5. **Open the Excel file** to visually verify the yellow highlighted columns

## 🚀 Next Steps

1. ✅ Test with sample data: `python process_with_highlighting.py example_sample_data.csv test.xlsx`
2. ✅ Open test.xlsx and verify yellow highlighting
3. ✅ Process your real data: `python process_with_highlighting.py your_data.csv output.xlsx`
4. ✅ Review the output and processing report
5. ✅ Integrate into your automation workflow

## 📞 Need More Help?

- **Quick commands**: See QUICKSTART.md
- **Full documentation**: See README.md
- **Technical details**: See SUMMARY.md
- **Troubleshooting**: See README.md Troubleshooting section

## 🎉 You're Ready!

That's it! You now have a complete solution for:
- ✅ Advanced column splitting (the "10% tough stuff")
- ✅ Duplicate removal (the "easy 90%")
- ✅ Visual verification (yellow highlighting)
- ✅ Production-ready code (tested and documented)

**Let's process some pole transfer data! ⚡**
