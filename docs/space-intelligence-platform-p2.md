# Space Intelligence Platform — Functional Requirements  
### Signal • Change • Interstellar • Impact  

## Vision

This platform does not aim to display space data.

> It aims to **interpret the universe as a system** —  
filtering signals, identifying change, detecting the unusual,  
and connecting it to real-world meaning.

Each module answers a different layer of understanding:

| Layer | Question |
|------|--------|
| Signal vs Noise | What actually matters? |
| What Changed | What changed and why? |
| Interstellar Watch | What doesn’t belong? |
| Space → Earth Impact | So what? |

---

## 1. Signal vs Noise Engine (Signature Layer)

### 1.1 Purpose

To identify and surface **high-value, meaningful events** from large volumes of space data.

> “Out of everything happening in space right now… what actually matters?”

---

### 1.2 Functional Requirements

#### 1.2.1 Event Ingestion
- Ingest real-time data from:
  - NASA NEO datasets  
  - NOAA Space Weather  
  - Satellite tracking feeds  
- Normalize into unified event schema:
  - Event type (NEO, Solar, Orbital, Satellite)
  - Timestamp
  - Key parameters (velocity, magnitude, proximity, etc.)

---

#### 1.2.2 Signal Scoring Engine

Each event must be scored based on:

- **Rarity Score**
  - Frequency of similar events historically  

- **Deviation Score**
  - Distance from statistical baseline  

- **Impact Score**
  - Potential effect on Earth or systems  

- **Composite Signal Score**
  - Weighted aggregation of above  

---

#### 1.2.3 Classification

Events must be categorized:

- Routine  
- Elevated  
- Significant  
- Anomalous  

---

#### 1.2.4 Output

- Top N signals (configurable: 3–10)
- Ranked by Signal Score
- Real-time updates (5–15 min refresh)

---

### 1.3 UI / UX Requirements

- **Primary Panel: “What Matters Now”**
- Card-based display:
  - Event summary  
  - Signal level (color-coded)  
  - Quick explanation  

- Visual indicators:
  - Heat intensity (signal strength)
  - Pulsing animation for anomalies  

---

### 1.4 Content Layer (3 Registers)

- **Technical:** Raw metrics, scoring breakdown  
- **Popular Science:** What this event is  
- **My Perspective:** Why this stands out  

---

### 1.5 Success Criteria

- High shareability  
- Clear prioritization of events  
- Users understand significance in <10 seconds  

---

## 2. “What Changed?” Temporal Intelligence

### 2.1 Purpose

To detect and explain **changes over time**, not just current state.

> “What changed in the last 24 hours / 7 days?”

---

### 2.2 Functional Requirements

#### 2.2.1 Time Window Analysis
- Compare datasets across:
  - 24 hours  
  - 7 days  
  - Custom range  

---

#### 2.2.2 Change Detection

Identify:

- Increase in solar activity  
- New NEO entries  
- Orbital parameter changes  
- Satellite density variations  

---

#### 2.2.3 Delta Computation

For each metric:

- Absolute change  
- Percentage change  
- Direction (increase/decrease)

---

#### 2.2.4 Trend Classification

- Stable  
- Increasing  
- Decreasing  
- Volatile  

---

#### 2.2.5 Output

- Top changes ranked by magnitude + significance  
- Highlight “new events” vs “intensifying events”

---

### 2.3 UI / UX Requirements

- **Panel: “What Changed”**
- Delta visualizations:
  - Arrows (↑ ↓ →)  
  - Color-coded trends  
- Timeline slider  
- Before vs After comparison  

---

### 2.4 “Explain This Change” Layer

For each change:

- Generate explanation:
  - What changed  
  - Possible causes  
  - Why it matters  

---

### 2.5 Content Layer

- **Technical:** Time-series data  
- **Popular Science:** Explanation of change  
- **My Perspective:** Why this change matters  

---

### 2.6 Success Criteria

- Immediate clarity of change  
- Executive-friendly insights  
- Actionable interpretation  

---

## 3. Interstellar Watch

### 3.1 Purpose

To detect and analyze **objects that may originate outside our solar system**.

> “What doesn’t belong to our system?”

---

### 3.2 Functional Requirements

#### 3.2.1 Object Identification

Filter objects where:

- Orbital eccentricity > 1  
- High entry velocity  
- Non-periodic trajectory  

---

#### 3.2.2 Feature Extraction

For each candidate:

- Eccentricity  
- Velocity at perihelion  
- Inclination  
- Trajectory shape  

---

#### 3.2.3 Interstellar Scoring

Score based on:

- Probability of hyperbolic orbit  
- Velocity anomaly  
- Deviation from known object classes  

---

#### 3.2.4 Confidence Levels

- Low (uncertain)  
- Medium (possible)  
- High (likely interstellar)  

---

#### 3.2.5 Output

- Curated list of candidates  
- Deep-dive analysis for top events  

Reference benchmark:
- :contentReference[oaicite:0]{index=0}  

---

### 3.3 UI / UX Requirements

- Dedicated section: **“Interstellar Watch”**
- Orbit visualization:
  - Hyperbolic vs elliptical comparison  
- Highlight trajectory path  

---

### 3.4 Interpretation Layer

Each object must include:

- Why this could be interstellar  
- What makes it unusual  
- Confidence level  

---

### 3.5 Content Layer

- **Technical:** Orbital mechanics  
- **Popular Science:** What interstellar means  
- **My Perspective:** Why this matters  

---

### 3.6 Success Criteria

- Unique insights not widely available  
- High curiosity and engagement  
- Establish authority in niche  

---

## 4. Space → Earth Impact Layer

### 4.1 Purpose

To connect space events to **real-world consequences**.

> “So what?”

---

### 4.2 Functional Requirements

#### 4.2.1 Event Mapping

Map space events to Earth systems:

| Event | Impact |
|------|--------|
| Solar flare | GPS degradation |
| Geomagnetic storm | Power grid stress |
| Satellite congestion | Collision risk |
| Radiation burst | Aviation exposure |

---

#### 4.2.2 Impact Scoring

Score impact based on:

- Severity  
- Duration  
- Affected systems  
- Geographic scope  

---

#### 4.2.3 Industry Mapping

Map impacts to domains:

- Insurance  
- Aviation  
- Telecommunications  
- Energy  

---

#### 4.2.4 Output

- “Impact Summary” for each major event  
- Risk level (Low / Medium / High)  

---

### 4.3 UI / UX Requirements

- **Panel: “Why This Matters on Earth”**
- Visuals:
  - Earth overlays  
  - Affected regions  
- Impact icons (GPS, Power, Aviation)

---

### 4.4 Insight Layer

Each event must include:

- What systems are affected  
- Why it matters  
- Potential downstream effects  

---

### 4.5 Content Layer

- **Technical:** Impact pathways  
- **Popular Science:** Explanation  
- **My Perspective:** System-level analogy  

---

### 4.6 Success Criteria

- Bridges science → business  
- Relevant to executives  
- Drives real-world understanding  

---

## 5. Cross-Cutting Requirements

### 5.1 Data Credibility

All outputs must include:

- Source attribution (NASA, NOAA, ESA)  
- Timestamp  
- Data version  

---

### 5.2 Real-Time Behavior

- Refresh interval: 5–15 minutes  
- Graceful degradation if data unavailable  

---

### 5.3 Performance

- Page load < 3 seconds  
- Smooth animations (WebGL / GPU accelerated)

---

### 5.4 Visual Experience

- 3D visualizations where applicable  
- Subtle animations (not distracting)  
- Clean, high-contrast design  

---

### 5.5 Personal Perspective (Non-Negotiable)

Each module must include:

> A clearly visible “My Perspective” section

This is the differentiator.

---

## 6. Engineering Review Notes (added Apr 29, 2026)

The notes below capture review feedback against the requirements in
sections 1–5. They are intentionally pragmatic: where the requirements
are ambitious, these notes describe what it takes to make them
defensible and shippable.

### 6.1 Gaps to close before scoring is credible

#### 6.1.1 Historical baseline service is a prerequisite, not a feature

"Rarity" and "Deviation" are undefined without a multi-year corpus to
compare against. Build the baseline before the scoring engine:

- **NEO close approaches:** ingest JPL SBDB close-approach archive
  (~40 years).
- **Solar flares:** ingest NOAA SWPC GOES X-ray flux archive (back to
  ~1986, 1-min cadence).
- **Geomagnetic Kp:** ingest NOAA Kp archive (back to the 1930s).
- **Orbital congestion:** derive launch / decay rates per orbit regime
  from Space-Track GP + decay history.

Single output API: `percentile(event_type, metric, value) -> float`.
With this in place the scoring engine is ~50 lines and every
"Rarity 9/10" claim is auditable.

#### 6.1.2 Refactor the scoring axes

Replace `Rarity / Deviation / Impact` with three orthogonal axes:

| Axis | Definition |
|---|---|
| Magnitude | Size of the event on its own scale (M5.2 flare, 0.03 AU miss, Kp 7) |
| Surprise | How unexpected given recent context (Kp 7 in solar minimum is more surprising than at solar max) |
| Reach | Fraction of Earth systems / human activity plausibly affected |

`Magnitude` and `Surprise` are properties of the event itself.
`Reach` is the bridge into Section 4 — keep it here for ranking, but
let Section 4 own the *richer* impact narrative (see 6.1.3).

#### 6.1.3 Decide once: Signal Engine vs Impact Layer architecture

Two clean options. Pick one before implementing either module.

- **Option A (recommended):** Signal Engine scores `Magnitude + Surprise`
  only. Section 4 is a downstream *consumer* that adds impact
  context. The "Top 5 things that matter" composes
  `(signal × impact)` for display.
- **Option B:** Signal Engine owns the full composite including impact;
  Section 4 becomes a visualization layer over the same numbers.

Option A is more honest — "astronomically significant" and "affects
Earth systems" are genuinely different questions.

#### 6.1.4 Per-source refresh cadences (not a global 5–15 min)

Some sources are too fast for 15 min, others are too slow:

| Source | Cadence |
|---|---|
| NOAA SWPC GOES X-ray flux | 1 min (flares peak in <5 min) |
| NOAA Kp index | 3 hours |
| NASA NEO feed | daily (sometimes weekly) |
| Space-Track GP catalog | 2 hours (already cached) |

Document the cadences on the panel itself — that transparency is a
credibility cue.

#### 6.1.5 Define the `Anomalous` class boundary explicitly

Statistical thresholds keep the engine defensible:

| Class | Rule |
|---|---|
| Routine | <50th percentile |
| Elevated | 50–90th |
| Significant | 90–99th |
| Anomalous | >99th OR violates a structural assumption (e.g., `e > 1` for an asteroid) |

The "structural assumption" branch lets Section 3 (Interstellar Watch)
cleanly *consume* this engine — an interstellar object is, by
definition, an Anomalous event triggered by `eccentricity > 1`.

#### 6.1.6 Authoring workflow for "My Perspective"

The Personal Perspective layer is the moat, but the spec is silent on
how it is produced and maintained. Concrete proposal:

- Treat perspectives as a small CMS-backed corpus.
- One Markdown file per recurring event type
  (`solar_flare_M_class.md`, `neo_close_approach.md`,
  `geomagnetic_storm.md`) with placeholders.
- Truly novel events (Anomalous tier) get a manual override field and
  a "draft" badge until published.
- Show "Perspective: standing analysis" vs "Perspective: live
  commentary" labels — readers can see which is which.

#### 6.1.7 `Top N` should be fixed at 5, not user-configurable

A user-tunable N (3–10) trains readers to think "the engine knows the
top 10 but is hiding 7." Pick **5**, defend it editorially ("the human
attention budget is 5 things"), and stop. Top-N is a content
decision, not a setting.

---

### 6.2 What I'd add that isn't in the doc

1. **A "Quiet Day" state.** Most days *nothing* significant happens.
   The panel must handle this gracefully and *say so*: "The sky is
   quiet today. Kp 1.2, no flares above C-class, nearest NEO at 38 LD."
   If the panel always finds something "anomalous," the engine is
   broken. Quiet states are credibility.
2. **A "Why this is on the list" justification per card.** One short
   sentence stating the scoring rationale: *"Significant: largest
   flare in 47 days (M5.2)"*. This is what separates an analyst from
   a feed.
3. **An audit trail / "How was this scored?" expander.** For each
   card, allow drill-down into the raw sub-scores plus a small
   sparkline of the metric over the last N days. This is where the
   Technical register lives.
4. **Subscribable feeds (low effort, high leverage):**
   - `/api/signals.json` — JSON feed of the current top-N
   - `/api/signals.atom` — Atom feed for syndication
   - Astronomy enthusiasts, journalists, and educators will syndicate
     this; it becomes a citation source. Cost: ~30 lines of Flask.
5. **"Standing watch" cards.** Some signals (e.g., 3I/Atlas this
   year) deserve a persistent slot until they fade, even if other
   short-term events score higher on a given day. Add a small
   "watchlist" override for editor-pinned items, clearly labelled
   so it doesn't compromise scoring transparency.

---

### 6.3 Recommended build order (within Module 1)

Sequenced for the smallest path to a credible v1 of the Signal Engine,
biased toward shipping the parts that prove correctness *before* the
parts that look impressive. (Cross-module ordering is in §6.6.)

1. **Historical baseline service.** Ingest NOAA Kp + GOES X-ray + JPL
   SBDB close-approach archives into the Deep Space DB. One-time job
   plus nightly delta. *No UI yet.*
2. **Scoring engine.** Pure functions:
   `score_event(event) -> {magnitude, surprise, reach, composite}`.
   Unit-tested against historical events (e.g., the 2003 Halloween
   storms should score >99). *Still no UI.*
3. **"What Matters Now" panel.** Server-side rendered top-5 with the
   three-register cards. No animations yet. Ship this. Get feedback.
4. **Real-time refresh + animations.** Add only after the static
   version proves the scoring is correct.
5. **Perspectives CMS.** Once you've written perspectives for 5–10
   events manually, you'll know what the templates need.

This sequence avoids the most common failure mode of "intelligence"
platforms: shipping a beautiful UI on top of scores nobody trusts.

---

### 6.4 Cross-cutting clarifications

These tighten the cross-cutting requirements in Section 5.

- **5.1 Data Credibility** — also include an explicit "stale data"
  badge: when the last successful upstream fetch is older than 2×
  the configured cadence, surface it on the card.
- **5.2 Real-Time Behavior** — the existing host-level circuit
  breaker (`_si_cached_get` / `_SI_HOST_DOWN_TTL`) is the right
  model. Reuse it for SWPC and JPL endpoints; do not invent a new
  pattern per source.
- **5.3 Performance** — the 3D scenes are bounded by texture decode +
  Three.js scene setup, not data fetch. Serve panels server-side
  rendered with a JSON hydration payload; avoid client-side waterfalls.
- **5.4 Visual Experience** — animations should be reserved for
  *change* (a card moving up the list, a new entry appearing). Avoid
  ambient pulsing unless the event is truly Anomalous; otherwise
  pulsing becomes wallpaper and stops signalling.

---

### 6.5 Open questions to decide before build

1. Where does the **historical baseline** live? Same Postgres as
   `deep_space_db`, or a separate read-optimized store (e.g.,
   Parquet on S3 + DuckDB) for analytical queries?
2. Are perspectives **per-event** (written once, shown once) or
   **per-event-type** (templated, reusable)? Likely both — the spec
   should distinguish.
3. Should the platform expose a **public API** for academic /
   journalistic use, or stay reader-only? Affects rate-limit design
   and ToS.
4. Sponsored / paid Space-Track tier — out of scope for v1, but
   worth noting once feed reliability becomes mission-critical.

---

### 6.6 Cross-module sequencing (across all four modules)

The four modules in §1–§4 look parallel but they're not: each one
builds capability that the next consumes. The doc numbers them
1→2→3→4, but the right *build* order is **1 → 3 → 4 → 2**.

#### Why this order

| Position | Module | Reason |
|---|---|---|
| 1st | §1 Signal vs Noise Engine | Forces the historical baseline + unified event schema. Everything else inherits these. |
| 2nd | §3 Interstellar Watch | Lowest-effort *if* §1 is built well — an interstellar object is a special case of an Anomalous-class signal (`e > 1`). Plants a flag in a niche nobody else publishes; 3I/Atlas seed content already exists in the [3I-Atlas-Research](../../3I-Atlas-Research/) workspace. |
| 3rd | §4 Space → Earth Impact | Needs *severity duration* and *geographic scope* dimensions that accumulate naturally during Phases 1–2. Makes the platform legible to non-astronomers (executives, journalists). Defendable claims require months of historical scoring. |
| 4th | §2 What Changed? | Highest engineering effort for lowest reader leverage in v1: needs time-series storage of computed scores, not just raw events. Phases 1–3 already partially answer "what's new?" By Phase 4 you have the data history *and* know which deltas readers actually care about. |

#### Visual dependency map

```
                    Phase 1: Signal vs Noise Engine
                    ─────────────────────────────────
                     ├─ Historical baseline service ◄─────────┐
                     ├─ Unified event schema           ◄──────┤  reused by
                     ├─ Scoring engine                 ◄──────┤  Phases 2,3,4
                     └─ Three-register content pattern ◄──────┘
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
              Phase 2:        Phase 3:        Phase 4:
         Interstellar      Earth Impact     What Changed
            Watch                              (delta engine)
              │               │                  ▲
              └───────────────┴──────────────────┘
                  consumes signal events
                  produced by Phase 1
```

#### Within each phase — the same micro-discipline

For *every* phase, follow this order:

1. **Data first, no UI.** Get the source ingested, archived, and the
   scoring/derived metric correct. Unit-test against known events
   from the past.
2. **Server-rendered static page.** No animations, no live refresh.
   Prove the content is right.
3. **Three-register cards.** Layer in Popular Science and My
   Perspective content.
4. **Live refresh + animations.** Last, only when steps 1–3 are
   stable.

Anti-pattern to avoid: shiny WebGL scene before scoring is correct.
The portal already does this well — Live Orbit 3D shipped after the
data path was solid. Repeat that pattern.

#### Public-value milestones

| End of phase | Public value | Strategic position |
|---|---|---|
| **Phase 1** | Homepage gains a "What Matters Now" intelligence panel | Interpreter, not aggregator |
| **Phase 2** | Dedicated authority on interstellar objects (3I/Atlas anchored) | Owns a niche nobody else publishes |
| **Phase 3** | Executives can read the site and act on it | Bridges science and business |
| **Phase 4** | Time-series view: "what's new today" | Daily-visit-worthy without becoming repetitive |

#### Concrete next step (this week)

Phase 1.0 — **historical baseline ingest only**. No scoring yet, no
UI yet. The single piece of work everything else depends on:

1. Create `deep_space_db` tables for `kp_history`,
   `goes_xray_history`, `neo_close_approach_history`,
   `gp_decay_history`.
2. Write four ingest scripts; run once to backfill, schedule nightly
   delta jobs.
3. Build the `percentile(event_type, metric, value) -> float`
   function and unit-test it.

Schema and ingest plan: see
[deep_space_db/docs/historical-baseline-plan.md](../../deep_space_db/docs/historical-baseline-plan.md).

---

## 7. Final Thought

This system is not just about space.

It is about:

> Understanding complex systems through signals, change, anomalies, and impact.

And in doing so:

> Making the universe a little more understandable.

---