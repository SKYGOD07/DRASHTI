# 08 — Hybrid Model Justification (for the Solution Presentation slide)

The brief explicitly permits: any single reference model, a hybrid, or a fully custom architecture — provided it addresses interoperability, security, scalability, analytics, and implementation requirements. DRASHTI is a **deliberate Model 1 + Model 2 hybrid**, architected so it can grow toward Model 3/4 without a rewrite.

## Why not just one model

- **Model 1 alone** gives visibility but no live video/analytics — fails the test scenario outright (can't trace a vehicle with zero video access).
- **Model 2 alone** gives live viewing/ANPR but no persistent asset inventory, GIS gap-analysis, or department-wide visibility — the registry is what makes onboarding, coverage reporting, and future scale credible.
- **Model 3 (federation middleware)** and **Model 4 (full central VMS)** are the right end-state for 80,000 cameras statewide, but building either from scratch in a week is not realistic and would sacrifice the working-demo requirement, which the rubric weighs heavily ("mock-ups... will not be considered").

## What we take from each model

| From | What we take | What we deliberately skip (for now) |
|---|---|---|
| **Model 1** | Central registry schema, GIS map, bulk/manual/API onboarding, gap-analysis, RBAC | N/A — this is fully built |
| **Model 2** | Direct RTSP/ONVIF feed integration without touching dept VMS, ANPR metadata generation, event tagging, searchable vehicle-movement records, video-wall grid | Full vendor-SDK coverage for every possible VMS brand — we support the open, standards-based protocols (RTSP/ONVIF) the brief itself calls out first |
| **Model 3** | The *architecture pattern* only: a pluggable `FeedAdapter` interface so a middleware/federation layer is an additive adapter, not a rewrite | Actual adapter implementations for specific vendor middleware — no such systems available to test against in a week |
| **Model 4** | The *scale-up narrative*: tiered storage, Kubernetes-based horizontal scaling, GPU inference batching — documented, not built | Centralized 24/7 recording/storage of all statewide feeds — out of scope and arguably undesirable at PoC stage (matches Model 2's own "no centralized storage of all video feeds" framing) |

## One-paragraph version for the pitch

*"We built a Model 1 registry-and-GIS backbone because you cannot manage 80,000 cameras you cannot see. On top of it we built Model 2's direct feed integration and ANPR analytics because visibility without live intelligence doesn't catch anyone. Every ingestion path is written as a swappable adapter — today it speaks RTSP and ONVIF directly to cameras; tomorrow the same interface can speak to a Model 3 federation layer or feed a Model 4 central VMS, without touching the registry, the AI pipeline, or a single line of frontend code. We didn't build the biggest possible system in a week — we built the smallest system that is honestly extensible to the biggest one."*
