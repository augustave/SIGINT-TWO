#!/usr/bin/env python3
"""SIGINT Terrain Bundle conformance validator.

Run from repo root:
    python3 scripts/validate.py

Exits 0 if every check passes, 1 otherwise.

Checks:
  1. common-schema.yaml is a well-formed Draft 2020-12 schema.
  2. Every fixture's expected_manifest.json validates against render_state_manifest.
  3. Every fixture's expected_verification.json validates against verification_report.
  4. The sample manifest validates.
  5. Every fixture's required warnings (declared in expected_warnings.json) appear in the manifest.
  6. Hard-stop fixtures (those whose verification has overall_status: blocked) actually carry that status.
  7. A synthetic suppressed-layer-without-reason is correctly rejected (proves the schema enforces it).
"""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, SchemaError

REPO = Path(__file__).resolve().parent.parent
BUNDLE = REPO / "sigint_terrain_bundle"
SCHEMA_PATH = BUNDLE / "common-schema.yaml"
FIXTURES_DIR = BUNDLE / "fixtures"
SAMPLE_MANIFEST = BUNDLE / "conformance" / "sample_render_state_manifest.json"

PASS = "PASS"
FAIL = "FAIL"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return yaml.safe_load(f)


def subschema(schema, defname):
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": schema["$defs"],
        **schema["$defs"][defname],
    }


def validate_instance(instance, sub):
    return list(Draft202012Validator(sub).iter_errors(instance))


def main():
    failures = []
    print("== SIGINT Terrain Bundle conformance validation ==\n")

    # Check 1: schema is well-formed
    schema = load_schema()
    try:
        Draft202012Validator.check_schema(schema)
        print(f"{PASS}  schema well-formed (Draft 2020-12)")
    except SchemaError as e:
        print(f"{FAIL}  schema invalid: {e.message}")
        failures.append("schema")
        return 1

    manifest_schema = subschema(schema, "render_state_manifest")
    verification_schema = subschema(schema, "verification_report")

    # Check 2: sample manifest
    with open(SAMPLE_MANIFEST) as f:
        sample = json.load(f)
    errors = validate_instance(sample, manifest_schema)
    if errors:
        print(f"{FAIL}  conformance/sample_render_state_manifest.json:")
        for e in errors:
            print(f"      - {e.message} @ {list(e.absolute_path)}")
        failures.append("sample_manifest")
    else:
        print(f"{PASS}  conformance/sample_render_state_manifest.json validates")

    # Check 3 + 5 + 6: per-fixture
    for fixture_dir in sorted(p for p in FIXTURES_DIR.iterdir() if p.is_dir()):
        name = fixture_dir.name
        manifest_path = fixture_dir / "expected_manifest.json"
        verification_path = fixture_dir / "expected_verification.json"
        warnings_path = fixture_dir / "expected_warnings.json"

        # manifest
        with open(manifest_path) as f:
            manifest = json.load(f)
        errs = validate_instance(manifest, manifest_schema)
        if errs:
            print(f"{FAIL}  fixtures/{name}/expected_manifest.json:")
            for e in errs:
                print(f"      - {e.message} @ {list(e.absolute_path)}")
            failures.append(f"{name}_manifest")
        else:
            print(f"{PASS}  fixtures/{name}/expected_manifest.json validates")

        # verification
        with open(verification_path) as f:
            verification = json.load(f)
        errs = validate_instance(verification, verification_schema)
        if errs:
            print(f"{FAIL}  fixtures/{name}/expected_verification.json:")
            for e in errs:
                print(f"      - {e.message} @ {list(e.absolute_path)}")
            failures.append(f"{name}_verification")
        else:
            print(f"{PASS}  fixtures/{name}/expected_verification.json validates")

        # required warnings present
        with open(warnings_path) as f:
            warnings_decl = json.load(f)
        if isinstance(warnings_decl, list):
            required_codes = [w["code"] for w in warnings_decl if "code" in w]
        else:
            required_codes = warnings_decl.get("required_warnings", [])
        manifest_warnings = manifest.get("warnings", [])
        missing = [c for c in required_codes if c not in manifest_warnings]
        if missing:
            print(f"{FAIL}  fixtures/{name}: required warnings missing from manifest: {missing}")
            failures.append(f"{name}_warnings")
        else:
            print(f"{PASS}  fixtures/{name}: all required warnings present in manifest")

        # blocked-status fixture coherence
        if "blocked" in name or verification.get("overall_status") == "blocked":
            if verification.get("overall_status") != "blocked":
                print(f"{FAIL}  fixtures/{name}: name suggests blocked, but overall_status={verification.get('overall_status')}")
                failures.append(f"{name}_blocked_status")
            else:
                print(f"{PASS}  fixtures/{name}: blocked-status coherence")

    # Check 7: synthetic negative — suppressed layer without reason must fail
    bad = {
        "terrain_profile": "nyc_littoral_low_relief",
        "vertical_datum": "NAVD88",
        "z_exaggeration": 3.0,
        "device_budget": "field_tablet",
        "layers_active": [],
        "layers_suppressed": [{"id": "contour_hachure", "blend": "multiply"}],
        "warnings": [],
        "analysis_products": {},
    }
    errs = validate_instance(bad, manifest_schema)
    if errs and any("reason" in e.message for e in errs):
        print(f"{PASS}  schema correctly rejects suppressed layer missing 'reason'")
    else:
        print(f"{FAIL}  schema did NOT reject suppressed layer missing 'reason' (regression)")
        failures.append("negative_test")

    print()
    if failures:
        print(f"=== {len(failures)} failure(s): {', '.join(failures)} ===")
        return 1
    print("=== all checks passed ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
