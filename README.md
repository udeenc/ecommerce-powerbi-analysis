# E-Commerce Analytics with Power BI

An end-to-end e-commerce analytics project using Power BI.

## Project Objective

The objective of this project is to analyze e-commerce transaction data and build an interactive Power BI dashboard to understand:

- Sales performance
- Revenue and profit trends
- Product performance
- Customer behavior
- Order patterns
- Payment behavior
- Delivery performance

## Tech Stack

- Power BI
- Power Query
- DAX
- Git & GitHub

## Project Structure

```text
data/
├── raw/
└── processed/

docs/
├── data-dictionary.md
├── data-model.md
└── insights.md

powerbi/
scripts/
└── data-cleaning/

```

## Data Profiling

Run with Python 3.10 or later; no third-party packages are required:

```powershell
py scripts/data-cleaning/profile_data.py
```

The script recursively profiles every CSV in `data/raw/`, prints column-level
results, and writes `data/processed/data-profile.json` (ignored by Git). Defaults
are relative to the repository, independent of your working directory. Use
`--input-dir` and `--output` to override them; output inside the input directory
or `data/raw/` is rejected. Source files are read only.

Reports include row/column counts, column names, inferred types, null counts and
percentages, duplicate rows beyond the first occurrence, and candidate primary
keys. All records are examined. Empty or whitespace-only fields are null;
literal `NA`, `NULL`, and `NaN` are retained as strings. Types are inferred without
converting values, and leading-zero integer codes remain strings. Duplicate and
key comparisons use exact parsed values, including whitespace.

Key discovery checks all single columns and pairs, excluding pairs with an
already-unique component. Larger composite keys are not searched. Candidates
describe observed uniqueness and require business validation. Empty datasets
have no candidate keys and report zero null percentages. Malformed datasets are
reported separately, other files continue, and the process exits nonzero if any
file fails. Exact duplicate/key tracking uses memory proportional to distinct
rows and surviving key candidates.

Relationship validation checks orders to customers; order items to orders,
products, and sellers; payments and reviews to orders; and product categories
to the category translation table. The console and JSON report include child
row counts, distinct non-null foreign keys, matched/unmatched distinct keys,
match percentages, and up to five sorted unmatched values. Null foreign-key
rows are counted separately and excluded from the distinct-key denominator.
The percentage is null when there are no non-null child keys.

Expected parent keys are checked for uniqueness and nulls; duplicate non-null
key counts represent occurrences beyond the first. A valid primary key must
be unique and non-null. An empty parent passes these checks vacuously, so its
row count must also be considered. Values are compared exactly without cleaning.
These checks reuse keys collected during profiling. Missing or failed datasets
and missing required columns produce validation errors and a nonzero exit code.
Detected unmatched keys or invalid parent keys are findings in the report and
do not themselves change the exit code. Expected filenames are relative to the
input directory, as listed in the script's relationship definitions.

## Dataset

Dataset source: Kaggle
Detailed dataset information will be documented during the data profiling stage.

## Project Status

🚧 In Development
Current stage: Project initialization and data profiling.
