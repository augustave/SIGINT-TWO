---
title: SIGINT Terrain Rendering Engine
---

# SIGINT Terrain Rendering Engine

> A deterministic compiler that transforms terrain elevation, telemetry freshness, provenance, and denied-space geometry into audit-friendly tactical 2D/3D outputs. **The system acts like a compiler, not a stylist.**

This is the visual reference site. For the full specification, see the [repository](https://github.com/augustave/SIGINT-TWO) and [README](https://github.com/augustave/SIGINT-TWO/blob/main/README.md).

---

## The 7-Layer Canonical Stack

<img src="patterns/layer_stack.svg" width="480"/>

Layer order is **fixed** and **semantically ordered**. Reordering is a doctrine violation. → [Layer Stack pattern card](pattern_cards/layer_stack.md)

---

## Pattern Cards

Each card pairs a visual primitive with the doctrine that governs it.

### [Confidence Stipple](pattern_cards/confidence_stipple.md)

Grain density encodes provenance. Higher density = lower trust.

| High-res LiDAR | Medium | Interpolated | Synthetic |
|---|---|---|---|
| <img src="patterns/confidence_stipple_high_res_lidar.svg" width="120"/> | <img src="patterns/confidence_stipple_medium_confidence.svg" width="120"/> | <img src="patterns/confidence_stipple_interpolated.svg" width="120"/> | <img src="patterns/confidence_stipple_synthetic.svg" width="120"/> |

### [Uncertainty Wash](pattern_cards/uncertainty_wash.md)

Wash saturation encodes feed age. CURRENT shows nothing.

| CURRENT | RECENT | AGING | STALE | HISTORICAL |
|---|---|---|---|---|
| <img src="patterns/uncertainty_wash_current.svg" width="100"/> | <img src="patterns/uncertainty_wash_recent.svg" width="100"/> | <img src="patterns/uncertainty_wash_aging.svg" width="100"/> | <img src="patterns/uncertainty_wash_stale.svg" width="100"/> | <img src="patterns/uncertainty_wash_historical.svg" width="100"/> |

### [Slope Hachure](pattern_cards/slope_hachure.md)

Hachure spacing encodes slope severity.

| 5–15° | 15–30° | 30–45° | 45°+ |
|---|---|---|---|
| <img src="patterns/slope_hachure_slope_5_15.svg" width="120"/> | <img src="patterns/slope_hachure_slope_15_30.svg" width="120"/> | <img src="patterns/slope_hachure_slope_30_45.svg" width="120"/> | <img src="patterns/slope_hachure_slope_45_up.svg" width="120"/> |

### [Denied / Contested Zones](pattern_cards/denied_zones.md)

High-contrast crosshatch in the red family. Never feathered.

<img src="patterns/denied_zone_crosshatch.svg" width="280"/>

### Live Scan Lines (4% opacity)

Applied only to live ingest surfaces. Never to archived stills or analysis exports.

<img src="patterns/scan_line_overlay.svg" width="280"/>

### Tactical Hypsometric Bands (first 5 only)

The only permitted hypsometric palette. Rainbow ramps are prohibited.

<img src="patterns/tactical_hypso_first_5.svg" width="480"/>

---

## Core Doctrine

| Invariant | Meaning |
|---|---|
| **Texture Is Meaning** | Grain = provenance. Hatching = slope. Crosshatch = denied. Wash = age. None decorative. |
| **Compositing Is Law** | The 7-layer canonical order is fixed and semantically meaningful. |
| **Terrain Must Be Honest** | All elevation must declare datum, source class, and z-exaggeration. |
| **Degradation Must Be Visible** | Performance fallback is allowed; silent semantic loss is not. |

---

## Conformance

Two acceptance fixtures live in [`sigint_terrain_bundle/fixtures/`](https://github.com/augustave/SIGINT-TWO/tree/main/sigint_terrain_bundle/fixtures):

- **`nyc_harbor_low_relief`** — happy path with field-tablet degradation. Expected status: `warn`.
- **`missing_timestamp_los_blocked`** — hard stop. A safety-relevant LOS request against a timestamp-less feed → `blocked`.

Validate locally:

```bash
pip install pyyaml jsonschema
python3 scripts/validate.py
```

---

## Reference

- [Glossary](https://github.com/augustave/SIGINT-TWO/blob/main/GLOSSARY.md) — domain acronyms (SIGINT, NAVD88, Fresnel, DSM, EOIR, …)
- [SKILL.md](https://github.com/augustave/SIGINT-TWO/blob/main/sigint_terrain_bundle/SKILL.md) — full doctrine
- [PRD.yaml](https://github.com/augustave/SIGINT-TWO/blob/main/sigint_terrain_bundle/PRD.yaml) — product requirements
- [SWARM.md](https://github.com/augustave/SIGINT-TWO/blob/main/sigint_terrain_bundle/SWARM.md) — multi-agent topology
- [common-schema.yaml](https://github.com/augustave/SIGINT-TWO/blob/main/sigint_terrain_bundle/common-schema.yaml) — JSON Schema contracts

---

*Generated SVGs come from [`scripts/build_patterns.py`](https://github.com/augustave/SIGINT-TWO/blob/main/scripts/build_patterns.py) reading [`sigint_terrain_bundle/tokens.json`](https://github.com/augustave/SIGINT-TWO/blob/main/sigint_terrain_bundle/tokens.json). Single source of truth for the palette.*
