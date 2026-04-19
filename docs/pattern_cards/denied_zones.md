# Pattern Card — Denied / Contested Zone Crosshatch

> Crosshatch encodes **denied, contested, blackout, fire-control, or degraded sensing zones**. High-contrast red family; never feathered.

## Visual

<img src="../patterns/denied_zone_crosshatch.svg" width="280"/>

## Doctrine rules

- Rendered as **layer 6** (blend: `normal`, opacity 100%).
- **Geometry must remain legible above hillshade and below live-track icons.**
- Stroke and fill are restricted to the **denied red family** (see [`tokens.json`](../../sigint_terrain_bundle/tokens.json) → `palettes.denied_red_family`).
- Crosshatch angle is **45°** by default, with optional perpendicular cross-stroke. No painterly variants.

## Prohibited

- Feathered or blurred edges (boundary clarity is operationally critical)
- Low-contrast alternatives (purple, gray, faint red)
- Decorative pattern fills (dots, waves, gradients)
- Animated denied zones (no flashing, no pulsing — distracts and delegitimizes)

## Why these rules

A denied zone is not a stylistic choice. An operator needs to know — instantly and without ambiguity — that crossing this boundary triggers an operational consequence. Crosshatch is the established convention; deviation costs lives.

## Tokens reference

[`tokens.json`](../../sigint_terrain_bundle/tokens.json) → `palettes.denied_red_family`.
