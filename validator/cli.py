"""
adtr-validate: check ADTR records against the v0.1 schema.

Usage:
    adtr-validate record.json
    adtr-validate records/*.json --format json
    adtr-validate --stdin < record.json
"""

import argparse
import json
import sys
from pathlib import Path

from .validate import validate_record, ValidationResult


def main():
    p = argparse.ArgumentParser(
        prog="adtr-validate",
        description="Validate ADTR record files against the schema.",
    )
    p.add_argument("files", nargs="*", help="ADTR JSON files to validate")
    p.add_argument("--stdin", action="store_true", help="read one record from stdin")
    p.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="output format (default: text)",
    )
    p.add_argument("--schema", type=str, default=None, help="custom schema path")
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = p.parse_args()

    # TODO: --quiet flag to suppress warnings
    if not args.files and not args.stdin:
        p.print_help()
        sys.exit(1)

    results: list[ValidationResult] = []

    if args.stdin:
        try:
            rec = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(f"bad json on stdin: {exc}", file=sys.stderr)
            sys.exit(2)
        r = validate_record(rec, schema_path=args.schema)
        r.source = "<stdin>"
        results.append(r)
    else:
        for fp in args.files:
            fpath = Path(fp)
            if not fpath.exists():
                print(f"not found: {fp}", file=sys.stderr)
                continue
            try:
                with open(fpath) as fh:
                    rec = json.load(fh)
            except json.JSONDecodeError as exc:
                print(f"bad json in {fp}: {exc}", file=sys.stderr)
                continue

            r = validate_record(rec, schema_path=args.schema)
            r.source = str(fpath)
            results.append(r)

    rc = 0
    if args.format == "json":
        print(json.dumps([r.to_dict() for r in results], indent=2))
        rc = 0 if all(r.valid for r in results) else 1
    else:
        for r in results:
            tag = "PASS" if r.valid else "FAIL"
            print(f"[{tag}] {r.source}")
            for e in r.errors:
                print(f"  {e}")
            for w in r.warnings:
                print(f"  (warn) {w}")
            if not r.valid:
                rc = 1

    sys.exit(rc)


if __name__ == "__main__":
    main()
