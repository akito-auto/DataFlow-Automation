# DataFlow Automation

A small Python automation tool for cleaning, merging and exporting CSV/Excel datasets.

## What it does

- Reads multiple CSV or Excel files
- Normalizes column names
- Trims whitespace from text fields
- Merges datasets with different columns
- Removes duplicate rows
- Supports deduplication by a chosen key such as `email` or `id`
- Exports to CSV, Excel or JSON
- Generates a simple JSON quality report

## Installation

```bash
pip install -r requirements.txt
```

## Example

```bash
python dataflow.py data/customers_a.csv data/customers_b.csv \
  --dedupe-key email \
  --output output/merged_customers.xlsx \
  --report output/report.json
```

## Example result

Input:

- `customers_a.csv` — 4 rows
- `customers_b.csv` — 4 rows

After merge + deduplication by email:

- 6 unique customers
- normalized columns
- latest duplicate record retained
- output ready for Excel/CRM/import workflows

## Why this project matters

Small businesses often receive data from different sources with inconsistent columns,
duplicate records and formatting problems. DataFlow turns that repetitive manual cleanup
into a reproducible command-line workflow.

## Tech

- Python
- Pandas
- OpenPyXL
- Pytest

## Tests

```bash
pytest -q
```

## Possible extensions

- GUI
- scheduled folder processing
- configurable validation rules
- Google Sheets integration
- automatic email reports
