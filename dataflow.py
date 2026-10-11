from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import pandas as pd


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [
        str(col).strip().lower().replace(" ", "_").replace("-", "_")
        for col in out.columns
    ]
    return out


def _clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return out


def load_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported input format: {path.suffix}")

    return _clean_strings(_normalize_columns(df))


def merge_tables(paths: Iterable[str | Path], dedupe_key: str | None = None) -> pd.DataFrame:
    frames = [load_table(path) for path in paths]
    if not frames:
        raise ValueError("At least one input file is required.")

    merged = pd.concat(frames, ignore_index=True, sort=False)

    if dedupe_key:
        key = dedupe_key.strip().lower().replace(" ", "_").replace("-", "_")
        if key not in merged.columns:
            raise ValueError(f"Dedupe key '{key}' not found in merged columns.")
        merged = merged.drop_duplicates(subset=[key], keep="last")
    else:
        merged = merged.drop_duplicates()

    return merged.reset_index(drop=True)


def build_report(df: pd.DataFrame) -> dict:
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "missing_values": {
            col: int(count)
            for col, count in df.isna().sum().items()
            if int(count) > 0
        },
        "duplicate_rows": int(df.duplicated().sum()),
    }


def export_table(df: pd.DataFrame, output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    suffix = output.suffix.lower()

    if suffix == ".csv":
        df.to_csv(output, index=False)
    elif suffix == ".xlsx":
        df.to_excel(output, index=False)
    elif suffix == ".json":
        df.to_json(output, orient="records", indent=2, force_ascii=False)
    else:
        raise ValueError("Output must be .csv, .xlsx, or .json")

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge and clean CSV/Excel files, remove duplicates, and export clean data."
    )
    parser.add_argument("inputs", nargs="+", help="Input .csv/.xlsx files")
    parser.add_argument("-o", "--output", required=True, help="Output .csv/.xlsx/.json file")
    parser.add_argument("--dedupe-key", help="Column used to remove duplicates (example: email)")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    merged = merge_tables(args.inputs, args.dedupe_key)
    export_table(merged, args.output)
    report = build_report(merged)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Processed {len(args.inputs)} file(s)")
    print(f"Result: {len(merged)} rows, {len(merged.columns)} columns")
    print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()
