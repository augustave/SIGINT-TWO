# SIGINT Terrain Rendering Engine — v2.0

> A deterministic compiler that transforms terrain elevation, telemetry freshness, provenance, and denied-space geometry into audit-friendly tactical 2D/3D outputs. **The system acts like a compiler, not a stylist.**

---

## What This Is

This repository is a **specification bundle** — not a runtime. It is the complete, machine-checkable design contract for a SIGINT terrain rendering engine that downstream coding agents (or human implementors) can build against without inventing layer rules, field names, or fallback behavior.

The bundle treats **rendering as evidence handling**. Every visible mark on the screen must answer a tactical question. Texture, tone, contour, and wash are operational encodings — never cosmetic effects.

### Why this design exists

Most terrain rendering systems collapse operational meaning into visual taste. Stipple becomes "decoration." Crosshatch becomes "pattern fill." Color becomes a palette choice. The result: feed freshness, provenance, and denial semantics drift between screens and device classes, and operators stop trusting what they see.

This bundle locks down those semantics. The renderer is required to fail loudly when trust state is uncertain, rather than render something pretty and ambiguous.

---

## Repository Layout

```
sigint_terrain_bundle/
├── PRD.yaml                                    # Product requirements (scope, personas, success metrics)
├── SKILL.md                                    # Full doctrine: invariants, layer order, profiles, output modes
├── SWARM.md                                    # Multi-agent topology and coordination protocol
├── common-schema.yaml                          # JSON Schema Draft 2020-12 contracts
├── conformance/
│   ├── README.md                               # Conformance kit overview
│   ├── sample_render_state_manifest.json       # Canonical example manifest
│   └── sample_verification_report.md           # Canonical example verification report
└── fixtures/
    ├── nyc_harbor_low_relief/                  # Happy-path fixture (warn status)
    │   ├── input.json
    │   ├── expected_manifest.json
    │   ├── expected_warnings.json
    │   ├── expected_verification.json
    │   └── expected_verification.md
    └── missing_timestamp_los_blocked/          # Hard-stop fixture (blocked status)
        ├── input.json
        ├── expected_manifest.json
        ├── expected_warnings.json
        ├── expected_verification.json
        └── expected_verification.md
```

---

## Core Doctrine

### Invariants

| Invariant | Meaning |
|---|---|
| **Texture Is Meaning** | Grain = provenance/confidence. Hatching = slope severity. Crosshatch = denied/contested area. Wash = data age. None of these are decorative. |
| **Compositing Is Law** | The 7-layer canonical order is fixed and semantically meaningful. Reordering is a doctrine violation. |
| **Terrain Must Be Honest** | All elevation rendering must declare datum, source class, and z-exaggeration. No silent assumptions. |
| **Degradation Must Be Visible** | Performance fallback is allowed; silent semantic loss is not. Every suppressed layer must carry a reason. |

### Canonical Layer Order

| # | Layer | Blend Mode | Opacity |
|---|---|---|---|
| 1 | Base imagery / neutral substrate | normal | 100% |
| 2 | DEM hillshade | overlay | 55–65% |
| 3 | Contour or hachure slope overlay | multiply | 100% |
| 4 | Confidence stipple | screen | variable by provenance |
| 5 | Uncertainty wash | normal | variable by age tier |
| 6 | Denied-zone crosshatch | normal | 100% |
| 7 | Scan-line overlay | normal | 4%, live feeds only |

### Feed Age Tiers

| Tier | Age window | Visual treatment |
|---|---|---|
| `CURRENT` | < 30 min | No wash |
| `RECENT` | 30 min – 2 hr | Light orange wash |
| `AGING` | 2 hr – 6 hr | Medium orange wash |
| `STALE` | 6 hr – 24 hr | Heavy red-orange wash |
| `HISTORICAL` | > 24 hr | Saturated wash + badge |

> **Hard rule:** A feed with no timestamp **never** becomes `CURRENT` or `RECENT`. It is forced to `STALE` plus a hard warning, or — if the request is safety-relevant (e.g. LOS/Fresnel) — the entire output is **blocked**.

### Terrain Profiles

| Profile | Use case | Notable parameters |
|---|---|---|
| `standard_regional` | General regional viewport | z-exaggeration by zoom table, 10 m contour interval, 45° hillshade altitude |
| `nyc_littoral_low_relief` | NYC harbor / low-relief coastal | z-exaggeration 3.0, 5 m contours, 35° altitude, mandatory bathymetry merge if water crossed |
| `alpine_high_delta_z` | High-relief mountain terrain | z-exaggeration clamped 1.0–1.5, contours over hillshade microtexture |
| `urban_canyon_lidar` | Dense urban LiDAR contexts | Bare-earth DEM preferred; LOS requires building-contamination warning if DSM used |

### Device Classes & Degradation

| Device | Texture budget | Degradation behavior |
|---|---|---|
| `desktop_analyst` | Full 7-layer stack | 2D + profile + optional 3D |
| `field_tablet` | Max 3 simultaneous textures | **Semantic suppressions first** (scan_line on non-live), then **performance suppressions** in priority order: stipple → contour → wash. Always emit `REDUCED_SEMANTIC_FIDELITY`. |
| `degraded_edge_device` | Hillshade + 1 operational overlay | Suppress 3D. Emit degraded-state badge. |

---

## Multi-Agent Architecture

The renderer is decomposed into 10 cooperating agents (see [SWARM.md](sigint_terrain_bundle/SWARM.md)):

```
┌─────────────────────────┐
│   RenderOrchestrator    │  ← entry point; owns the run, merges outputs
└────────────┬────────────┘
             │
   ┌─────────┼──────────────────────────────┐
   ▼         ▼                              ▼
TerrainProfile  DatumNormalization   TerrainInterpretation
   Agent          Agent                 Agent
                                          │
            ┌─────────────────────────────┼─────────────────────────┐
            ▼ (parallelizable)            ▼                         ▼
       TelemetryState              ThreatOverlay              LOSFresnel
          Agent                       Agent                     Agent
            └─────────────────────────────┼─────────────────────────┘
                                          ▼
                              LayerCompilation
                                  Agent
                                          │
                                          ▼
                              Verification → Packaging
                                  Agent      Agent
```

Steps 5, 6, and 7 (Telemetry, Threat, LOS/Fresnel) have no inter-dependencies and may run concurrently.

**Error propagation:** Blocking errors halt downstream dependents immediately. Non-blocking warnings accumulate into the manifest. The PackagingAgent must include all warnings even in `blocked` outputs — a blocked package is still a valid, reproducible artifact explaining the block.

---

## Output Contract

Every successful run produces a reproducible package:

```
/layers/*                      # Compiled layer assets
/patterns/*                    # SVG / shader patterns
/shaders/*                     # GLSL or equivalent
/profiles/*                    # Selected terrain profile parameters
/render_state_manifest.json    # Authoritative state record
/verification_report.md        # Human-readable pass/fail report
```

### `render_state_manifest.json` shape

```json
{
  "terrain_profile": "nyc_littoral_low_relief",
  "vertical_datum": "NAVD88",
  "water_crossing": true,
  "z_exaggeration": 3.0,
  "device_budget": "field_tablet",
  "layers_active": [ /* layer_spec[] */ ],
  "layers_suppressed": [ /* suppressed_layer_spec[] — reason required */ ],
  "warnings": [ "bathymetry_merged", "REDUCED_SEMANTIC_FIDELITY" ],
  "analysis_products": {
    "elevation_profile": true,
    "los_check": "LOS_MASKED",
    "fresnel_check": "FAILED_C_BAND",
    "terrain_3d": false
  }
}
```

Validated end-to-end against [`common-schema.yaml`](sigint_terrain_bundle/common-schema.yaml).

---

## Conformance Kit

The repository ships with two acceptance fixtures that any compliant implementation must reproduce exactly.

### Fixture 1 — `nyc_harbor_low_relief`

A field-tablet renderer requesting LOS + Fresnel across a harbor crossing with bathymetric merge required and aging telemetry. Tests:

- Terrain profile inference and override
- Bathymetric merge with NAVD88 datum normalization
- Field-tablet 3-texture budget enforcement (suppresses stipple + contour, semantically suppresses scan_line)
- Required warnings: `bathymetry_merged`, `urban_lidar_filter_applied`, `REDUCED_SEMANTIC_FIDELITY`
- Expected verification status: **`warn`**

### Fixture 2 — `missing_timestamp_los_blocked`

A safety-relevant LOS request against a feed with no `timestamp_utc`. Tests the most critical hard-stop in the spec:

- LOS computation **blocked** (not degraded)
- `los_check` result forced to `UNKNOWN`
- `FEED_FRESHNESS_UNDEFINED` warning emitted
- No `CURRENT` or `RECENT` tier permitted
- Expected verification status: **`blocked`**

---

## Local Validation

Validate the schema and fixtures with Python:

```bash
pip install pyyaml jsonschema

python3 - <<'EOF'
import yaml, json
from jsonschema import Draft202012Validator

with open("sigint_terrain_bundle/common-schema.yaml") as f:
    schema = yaml.safe_load(f)

manifest_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$defs": schema["$defs"],
    **schema["$defs"]["render_state_manifest"]
}

for path in [
    "sigint_terrain_bundle/conformance/sample_render_state_manifest.json",
    "sigint_terrain_bundle/fixtures/nyc_harbor_low_relief/expected_manifest.json",
    "sigint_terrain_bundle/fixtures/missing_timestamp_los_blocked/expected_manifest.json",
]:
    with open(path) as f:
        instance = json.load(f)
    errors = list(Draft202012Validator(manifest_schema).iter_errors(instance))
    print(f"{'PASS' if not errors else 'FAIL'} {path}")
    for e in errors:
        print(f"  - {e.message}")
EOF
```

Expected output: `PASS` on all three.

---

## Acceptance Gates

A render is valid only if **all** of the following are true:

1. Layer order matches the canonical 7-layer stack
2. No illegal palette is used (no rainbow hypsometric, no decorative denied-zone patterns)
3. Timestamp-less feeds are not displayed as `CURRENT` or `RECENT`
4. Water-crossing profiles use bathymetric fill or explicitly mark `bathymetry_unavailable`
5. 3D mode respects terrain profile and device budget
6. Output manifest explains every suppressed or degraded layer with a `reason`

---

## Failure Modes (Hard Stops)

| Condition | Required behavior |
|---|---|
| Sensor timestamps absent in safety-relevant view | `[BLOCKED: feed freshness undefined. CURRENT/RECENT prohibited.]` |
| LiDAR rooftop contamination in LOS mode | Switch to bare-earth DEM or emit `LOS_UNSAFE_DSM_CONTAMINATION` |
| Bathymetry missing for harbor-crossing transect | Block bathymetric fill, emit `BATHYMETRY_REQUIRED_FOR_WATER_CROSSING` |
| Fresnel request without declared frequency class | Reject request at validation |
| Device cannot sustain required blend modes | Reduced-fidelity package with `REDUCED_SEMANTIC_FIDELITY` warning |

---

## Versioning

- **Bundle version:** 2.0.0
- **Schema version:** 1.1.0 (Draft 2020-12)
- **Status:** active

---

## Implementing Against This Bundle

A coding agent or human implementor should:

1. **Read in order:** `SKILL.md` → `PRD.yaml` → `SWARM.md` → `common-schema.yaml`
2. **Treat the schema as authoritative.** If doctrine and schema disagree, the schema wins (and the disagreement is a bug — file an issue).
3. **Run both conformance fixtures.** A renderer that passes only the happy-path fixture has not implemented the hard-stop semantics.
4. **Never invent fields.** All cross-agent state flows through types defined in `common-schema.yaml` (`additionalProperties: false` is enforced everywhere).
5. **Fail loud.** When in doubt, emit a warning and suppress, rather than render something pretty and ambiguous.

---

## License

Specification bundle. No code; no runtime. Treat as a build target.
