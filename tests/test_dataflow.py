from pathlib import Path

import pandas as pd

from dataflow import build_report, export_table, merge_tables


def test_merge_and_dedupe(tmp_path: Path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"

    a.write_text(
        "Name,Email,City\n"
        " Alice ,alice@example.com,Prague\n"
        "Bob,bob@example.com,Brno\n",
        encoding="utf-8",
    )
    b.write_text(
        "Name,Email,City\n"
        "Alice Smith,alice@example.com,Prague\n"
        "Carol,carol@example.com,Ostrava\n",
        encoding="utf-8",
    )

    result = merge_tables([a, b], dedupe_key="email")

    assert len(result) == 3
    assert result.loc[result["email"] == "alice@example.com", "name"].iloc[0] == "Alice Smith"


def test_report():
    df = pd.DataFrame({"name": ["A", "B"], "email": ["a@x.com", None]})
    report = build_report(df)

    assert report["rows"] == 2
    assert report["missing_values"] == {"email": 1}


def test_json_export(tmp_path: Path):
    df = pd.DataFrame({"name": ["A"], "value": [1]})
    output = tmp_path / "out.json"

    export_table(df, output)

    assert output.exists()
    assert '"name":"A"' in output.read_text(encoding="utf-8").replace(" ", "")
