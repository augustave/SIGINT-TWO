# Verification Report — NYC Harbor Low-Relief Fixture

- **Fixture ID:** `nyc_harbor_low_relief_v1`
- **Overall status:** `warn`
- **Interpretation:** The fixture passes doctrine-critical checks, but it intentionally exercises visible degradation on a field-tablet budget.

## Scenario summary
This fixture simulates a NYC harbor water crossing in the `nyc_littoral_low_relief` profile with:
- AGING cached feed
- denied-zone overlay
- bathymetry merge into NAVD88
- LOS and Fresnel analysis
- field-tablet texture budget

## Expected operational outcome
- The system **must** merge bathymetry because the transect crosses water.
- The system **must** declare `nyc_littoral_low_relief`.
- The system **must not** show more than three active textures on a field tablet.
- The system **must** preserve degradation visibility through warnings and suppressed-layer reasons.
- The system **must** return `LOS_MASKED` and `FAILED_C_BAND` for the expected analysis products.

## Checks
### 1. Layer compositing audit — PASS
Canonical order is preserved. Active layers are `hillshade_oblique`, `uncertainty_wash`, and `denied_zone_crosshatch`. Suppressed layers retain their original semantic positions in the manifest.

### 2. Terrain profile compliance — PASS
The fixture requires `nyc_littoral_low_relief` with `z_exaggeration = 3.0`, `contour_interval_m = 5`, and `hillshade_altitude_deg = 35`.

### 3. Datum normalization — PASS
Bathymetry begins in `MLLW` and must be transformed to `NAVD88` before merge. Presence of `bathymetry_merged` is required.

### 4. Timestamp/provenance handling — PASS
The feed is cached and aged into the `AGING` bucket. The renderer must not present it as `CURRENT` or `RECENT`.

### 5. Mobile texture budget — WARN
The tablet budget is intentionally tight. `contour_hachure` and `confidence_stipple` are suppressed, which is acceptable only if `REDUCED_SEMANTIC_FIDELITY` is emitted.

### 6. LOS geometry validation — PASS
The output should mark the transect as `LOS_MASKED`.

### 7. Fresnel equation validation — PASS
For `C_BAND`, the output should be `FAILED_C_BAND`.

### 8. Palette compliance — PASS
No non-doctrinal color ramp, decorative denied-zone pattern, or freshness tint drift is allowed.

## Required warnings
- `bathymetry_merged`
- `urban_lidar_filter_applied`
- `REDUCED_SEMANTIC_FIDELITY`

## Blocking conditions for this fixture
The fixture should fail if any of the following happen:
1. bathymetry is omitted without an explicit unavailable/blocking condition
2. the system marks the feed as `CURRENT`
3. more than three active textures appear on a `field_tablet`
4. denied-zone overlay is rendered with non-canonical styling
5. suppressed layers are omitted from the manifest
