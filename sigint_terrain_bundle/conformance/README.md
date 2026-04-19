# SIGINT Terrain Conformance Kit

This kit turns the rendering bundle from a specification into a build target.

## Why this exists
A coding agent can read `SKILL.md`, `SWARM.md`, `PRD.yaml`, and `common-schema.yaml` and still make subtle semantic mistakes. These fixtures reduce that drift by providing one doctrine-heavy, machine-checkable scenario.

## Included artifacts
- `sample_render_state_manifest.json` — canonical example manifest
- `sample_verification_report.md` — canonical example verification report
- `fixtures/nyc_harbor_low_relief/input.json` — scenario input payload
- `fixtures/nyc_harbor_low_relief/expected_manifest.json` — expected manifest for the scenario
- `fixtures/nyc_harbor_low_relief/expected_warnings.json` — required warning set and rationale
- `fixtures/nyc_harbor_low_relief/expected_verification.json` — structured verification result
- `fixtures/nyc_harbor_low_relief/expected_verification.md` — human-readable verification report

## What this fixture tests
- terrain profile override and compliance
- bathymetry merge with datum normalization
- feed aging / uncertainty wash behavior
- denied-zone overlay semantics
- field-tablet degradation ladder
- LOS and first Fresnel zone output logging

## Pass criteria
A renderer passes this fixture only if:
1. `nyc_littoral_low_relief` is selected and logged
2. vertical datum ends as `NAVD88`
3. bathymetry merge is declared for the water crossing
4. no more than three textures are active for `field_tablet`
5. suppressed layers remain present in the manifest with reasons
6. warnings include all required doctrinal signals
7. verification status remains `warn` rather than `fail` or silent `pass`

## Second Fixture: missing_timestamp_los_blocked

Located at `fixtures/missing_timestamp_los_blocked/`. Exercises the highest-priority failure mode: a safety-relevant LOS request against a feed with no timestamp.

Pass criteria:
1. `overall_status` is `blocked`
2. `los_check` result is `UNKNOWN`
3. `FEED_FRESHNESS_UNDEFINED` is present in `warnings`
4. No `CURRENT` or `RECENT` tier appears in the manifest
5. All suppressed layers carry `reason` fields
6. `blocking_errors` is non-empty
