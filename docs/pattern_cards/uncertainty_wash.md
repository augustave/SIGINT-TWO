# Pattern Card — Uncertainty Wash

> Wash color/opacity encodes **feed age**. Older = more saturated. CURRENT shows nothing — fresh data is unmarked.

## Mapping

| `feed_age_tier` | Time window | Visual | Operator should infer |
|---|---|---|---|
| `CURRENT` | < 30 min | <img src="../patterns/uncertainty_wash_current.svg" width="140"/> | Live or near-live. No wash. |
| `RECENT` | 30 min – 2 h | <img src="../patterns/uncertainty_wash_recent.svg" width="140"/> | Slightly aged but actionable. |
| `AGING` | 2 – 6 h | <img src="../patterns/uncertainty_wash_aging.svg" width="140"/> | Use with awareness; verify before high-stakes decisions. |
| `STALE` | 6 – 24 h | <img src="../patterns/uncertainty_wash_stale.svg" width="140"/> | Reference only. Do not treat as live. |
| `HISTORICAL` | > 24 h | <img src="../patterns/uncertainty_wash_historical.svg" width="140"/> | Archival. Never act on this as current state. |

## Doctrine rules

- Rendered as **layer 5** (blend: `normal`).
- **Hard stop:** A feed with no `timestamp_utc` is **never** assigned `CURRENT` or `RECENT`. It is forced to `STALE` plus a hard warning, or — if the request is safety-relevant (LOS / Fresnel) — the entire output is **blocked** with `FEED_FRESHNESS_UNDEFINED`.
- Wash colors live **only** in the orange→red family. Decorative palettes (blue, green, purple) are prohibited.
- Tier thresholds are **not configurable** by the renderer at run time — they are doctrine.

## Tokens reference

[`tokens.json`](../../sigint_terrain_bundle/tokens.json) → `palettes.uncertainty_wash_orange_red_family.tiers`.
