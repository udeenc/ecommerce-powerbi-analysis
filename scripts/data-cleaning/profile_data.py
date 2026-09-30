"""Profile CSVs without changing source data (Python 3.10+, standard library)."""

import argparse
import csv
from datetime import datetime
from itertools import combinations
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
RELATIONSHIPS = [
    ("olist_orders_dataset.csv", "customer_id", "olist_customers_dataset.csv", "customer_id"),
    ("olist_order_items_dataset.csv", "order_id", "olist_orders_dataset.csv", "order_id"),
    ("olist_order_items_dataset.csv", "product_id", "olist_products_dataset.csv", "product_id"),
    ("olist_order_items_dataset.csv", "seller_id", "olist_sellers_dataset.csv", "seller_id"),
    ("olist_order_payments_dataset.csv", "order_id", "olist_orders_dataset.csv", "order_id"),
    ("olist_order_reviews_dataset.csv", "order_id", "olist_orders_dataset.csv", "order_id"),
    ("olist_products_dataset.csv", "product_category_name",
     "product_category_name_translation.csv", "product_category_name"),
]
INTEGER = re.compile(r"[+-]?(?:0|[1-9][0-9]*)\Z")
NUMBER = re.compile(r"[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+|[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}(?:[ T].*)?\Z")


def infer_type(value):
    """Infer conservative types; preserve leading-zero codes as strings."""
    if value.lower() in {"true", "false"}:
        return "boolean"
    if INTEGER.fullmatch(value):
        return "integer"
    if NUMBER.fullmatch(value):
        if re.fullmatch(r"[+-]?0[0-9]+", value):
            return "string"
        return "decimal"
    if ISO_DATE.fullmatch(value):
        try:
            datetime.fromisoformat(value)
            return "date" if len(value) == 10 else "datetime"
        except ValueError:
            pass
    return "string"


def merge_type(current, new):
    if current == "null" or current == new:
        return new
    if {current, new} <= {"integer", "decimal"}:
        return "decimal"
    if {current, new} <= {"date", "datetime"}:
        return "datetime"
    return "string"


def profile_csv(path, key_columns=(), key_index=None):
    """Use every record; count duplicates beyond their first occurrence.

    Candidate keys are minimal unique, non-null singles and pairs. Values are
    compared exactly as read; only empty/whitespace-only fields count as null.
    Memory usage grows with the number of distinct rows and surviving keys.
    """
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        names = next(reader, [])
        if not names or any(not name.strip() for name in names):
            raise ValueError("missing or blank column names")
        if len(set(names)) != len(names):
            raise ValueError("duplicate column names")
        width = len(names)
        tracked = {name: set() for name in key_columns if name in names}
        nulls = [0] * width
        types = ["null"] * width
        keys = {indices: set() for size in (1, 2)
                for indices in combinations(range(width), size)}
        seen_rows = set()
        rows = duplicates = 0
        for row in reader:
            if len(row) != width:
                raise ValueError(f"line {reader.line_num}: expected {width} fields, got {len(row)}")
            rows += 1
            values = tuple(row)
            if values in seen_rows:
                duplicates += 1
            else:
                seen_rows.add(values)
            missing = [not value.strip() for value in row]
            for index, value in enumerate(row):
                if missing[index]:
                    nulls[index] += 1
                elif types[index] != "string":
                    types[index] = merge_type(types[index], infer_type(value))
                if names[index] in tracked and not missing[index]:
                    tracked[names[index]].add(value)
            for indices in list(keys):
                key = tuple(row[index] for index in indices)
                if any(missing[index] for index in indices) or key in keys[indices]:
                    del keys[indices]
                else:
                    keys[indices].add(key)
        candidates = [indices for indices in keys if rows and not any(
            set(other) < set(indices) for other in keys)]
        if key_index is not None:
            key_index.update(tracked)
        return {
            "row_count": rows,
            "column_count": width,
            "duplicate_row_count": duplicates,
            "candidate_primary_keys": [[names[index] for index in key] for key in candidates],
            "columns": [
                {"name": name, "inferred_type": types[index],
                 "null_count": nulls[index],
                 "null_percentage": round(nulls[index] * 100 / rows, 4) if rows else 0.0}
                for index, name in enumerate(names)
            ],
        }


def validate_relationships(datasets, key_indexes):
    """Compare exact non-null keys; report missing inputs instead of guessing."""
    parents = {}
    relationships = []
    for child_file, child_column, parent_file, parent_column in RELATIONSHIPS:
        parent_name = f"{parent_file}.{parent_column}"
        if parent_name not in parents:
            parent_profile = datasets.get(parent_file)
            parent_keys = key_indexes.get(parent_file, {}).get(parent_column)
            if parent_profile is None or parent_keys is None:
                parents[parent_name] = {"status": "error", "error": "Parent dataset or column unavailable."}
            else:
                column = next(c for c in parent_profile["columns"] if c["name"] == parent_column)
                nulls = column["null_count"]
                duplicates = parent_profile["row_count"] - nulls - len(parent_keys)
                parents[parent_name] = {
                    "status": "ok",
                    "row_count": parent_profile["row_count"],
                    "distinct_non_null_keys": len(parent_keys),
                    "null_key_rows": nulls,
                    "duplicate_non_null_key_rows": duplicates,
                    "is_unique": duplicates == 0 and nulls <= 1,
                    "is_valid_primary_key": duplicates == 0 and nulls == 0,
                }
        result = {
            "child_dataset": child_file, "child_column": child_column,
            "parent_dataset": parent_file, "parent_column": parent_column,
        }
        child_profile = datasets.get(child_file)
        child_keys = key_indexes.get(child_file, {}).get(child_column)
        if child_profile is None or child_keys is None or parents[parent_name]["status"] == "error":
            result.update(status="error", error="Required dataset or column unavailable; see dataset errors.")
        else:
            parent_keys = key_indexes[parent_file][parent_column]
            unmatched = child_keys - parent_keys
            matched = len(child_keys) - len(unmatched)
            column = next(c for c in child_profile["columns"] if c["name"] == child_column)
            result.update(
                status="ok",
                child_row_count=child_profile["row_count"],
                null_foreign_key_rows=column["null_count"],
                distinct_foreign_key_values=len(child_keys),
                matched_distinct_keys=matched,
                unmatched_distinct_keys=len(unmatched),
                match_percentage=round(100 * matched / len(child_keys), 4) if child_keys else None,
                unmatched_key_sample=sorted(unmatched)[:5],
                parent_key_is_valid=parents[parent_name]["is_valid_primary_key"],
            )
        relationships.append(result)
    return parents, relationships


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/data-profile.json")
    args = parser.parse_args()
    source_dir = args.input_dir.resolve()
    output = args.output.resolve()
    for protected in (source_dir, (ROOT / "data/raw").resolve()):
        if output == protected or protected in output.parents:
            parser.error("output must be outside the input directory and data/raw")
    files = sorted(path for path in source_dir.rglob("*")
                   if path.is_file() and path.suffix.lower() == ".csv")
    if not files:
        parser.error(f"no CSV files found in {source_dir}")
    report = {
        "methodology": {
            "nulls": "Empty or whitespace-only fields; literal NA, NULL and NaN remain strings.",
            "types": "Inferred from all non-null values; no source values are converted.",
            "duplicates": "Exact parsed rows beyond the first occurrence, including null fields.",
            "keys": "Minimal unique non-null single columns and pairs; no larger combinations. "
                    "Observed uniqueness is not a guarantee of a business key.",
            "relationships": "Exact non-null key comparisons. Match percentage = matched distinct "
                             "keys / distinct non-null child keys * 100; null when denominator is zero. "
                             "Null child rows are counted separately. Samples are sorted, at most five keys.",
            "parent_keys": "Uniqueness treats nulls as one value; a valid primary key must also have "
                           "no nulls. Duplicate non-null key rows count occurrences beyond the first. "
                           "Empty parents satisfy these checks vacuously; row counts are reported.",
        },
        "datasets": {},
        "errors": {},
    }
    required_columns = {}
    for child_file, child_column, parent_file, parent_column in RELATIONSHIPS:
        required_columns.setdefault(child_file, set()).add(child_column)
        required_columns.setdefault(parent_file, set()).add(parent_column)
    key_indexes = {}
    for path in files:
        name = path.relative_to(source_dir).as_posix()
        try:
            key_index = {}
            result = profile_csv(path, required_columns.get(name, ()), key_index)
        except (OSError, UnicodeError, csv.Error, ValueError) as exc:
            report["errors"][name] = str(exc)
            print(f"ERROR {name}: {exc}", file=sys.stderr)
            continue
        report["datasets"][name] = result
        key_indexes[name] = key_index
        print(f"\n{name}: {result['row_count']:,} rows, {result['column_count']} columns; "
              f"{result['duplicate_row_count']:,} duplicate rows")
        print("Candidate keys: " + (", ".join(" + ".join(key) for key in
              result["candidate_primary_keys"]) or "none among singles and pairs"))
        for column in result["columns"]:
            print(f"  {column['name']}: {column['inferred_type']}; "
                  f"nulls={column['null_count']:,} ({column['null_percentage']:.4f}%)")
    parents, relationships = validate_relationships(report["datasets"], key_indexes)
    report["parent_keys"] = parents
    report["relationships"] = relationships
    print("\nParent key validation:")
    for name, result in parents.items():
        print(f"  {name}: {json.dumps(result)}")
    print("\nRelationship validation:")
    for result in relationships:
        print(json.dumps(result))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nReport: {output}")
    return 1 if report["errors"] or any(r["status"] == "error" for r in relationships) else 0


if __name__ == "__main__":
    sys.exit(main())
