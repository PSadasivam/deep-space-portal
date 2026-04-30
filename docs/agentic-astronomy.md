# Agentic Astronomy
### The conversational surface of a systems-thinking platform

---

## 0. The Larger Argument

Most space coverage reports **events**.

This platform reports **patterns** — clusters, deviations from baseline, and the quiet correlations that show up *between* datasets before they show up *in* any single one.

A solar flare is news.
A cluster of flares correlated with a satellite drag spike and an Atlantic radio blackout is a **system signal**.

That distinction is the entire point of this site, and it is what Agentic Astronomy must preserve.

> **We interpret events as systems, not as headlines.**

Every design decision in this document follows from that single principle. If a feature does not help the user *think in systems*, it does not belong here — no matter how impressive the underlying model is.

This is also the line that separates this work from the generic "AI assistant for X" features shipping across the industry. Those products are built around the model. This one is built around a **point of view**, with a model used as the interface.

---

## 1. Why

### 1.1 Why now

The platform already does the hard part. It ingests, scores, and explains:

- Voyager 1 magnetometer and plasma data
- 3I/ATLAS observations
- NEO close approaches
- Solar / geomagnetic activity (Kp, X-ray)
- Satellite catalogs (Space-Track OMM, ~31k active objects)

The interpretive layers — Signal vs Noise, Temporal Intelligence, Interstellar Watch, Space → Earth Impact — already produce structured, ranked output.

The remaining gap is **access**. A first-time visitor cannot ask the platform a question in their own words. They have to *know what to look at*. That is the friction we are removing.

### 1.2 Why this is not a chatbot

Chatbots are stateless answer machines. They optimize for **plausibility**.

This platform optimizes for **interpretation grounded in real data**. Every response must be traceable to a timestamped source. Plausibility without provenance is the failure mode we are explicitly designing against.

Agentic Astronomy is therefore not a new pillar. It is the **conversational surface of the four pillars that already exist** — the same engines, made addressable in natural language.

### 1.3 Why "system signals" matter more than answers

A user who walks away with one accurate fact has not been served well by this platform. A user who walks away noticing that *three things lined up* — and understanding why that is worth noticing — has.

The agent's job is to produce the second outcome.

---

## 2. What

### 2.1 What the agent is

A natural-language interface to the existing four-layer interpretive stack:

| Layer | Question it answers |
|---|---|
| Signal vs Noise | What actually matters right now? |
| Temporal Intelligence | What changed, and over what window? |
| Interstellar Watch | What does not belong? |
| Space → Earth Impact | So what — does this reach the ground? |

The agent does not generate science. It **routes**, **composes**, and **explains** the output of these engines.

### 2.2 What the agent is not — non-goals

These are explicit. They protect the credibility of everything else.

- **Not a forecaster.** The agent does not predict events the underlying data does not support. No "expect a flare in six hours."
- **Not an editorialist.** Opinion is confined to the `My Perspective` section, clearly labeled, and grounded in the same data the rest of the response cites.
- **Not omniscient.** Outside the loaded data domains, the answer is *"I don't have data on that"* — not a guess.
- **Not a memory system (v1).** Session-scoped context only. No cross-session memory until the privacy and security threat-model implications are worked through deliberately.
- **Not a parallel pipeline.** The agent reads from the same cached engine outputs the dashboard reads from. It does not open new fan-out paths to upstream APIs from inside a user request.

### 2.3 What a good response looks like

Two response modes, chosen by query type and signal severity — not by the model's mood.

**Concise mode (default).** For factual or single-metric queries.

> *"Kp is 4 right now, up from 2 six hours ago. Source: NOAA, 14:00 UTC. Worth watching but not unusual."*

Two to four sentences. One source. One line of perspective only when the data warrants it.

**Deep mode.** For high-significance events, change-detection queries, or when the user explicitly asks for depth. Six sections:

1. **Summary** — one paragraph.
2. **What Happened** — the events, with timestamps.
3. **What It Means** — the science, in plain English.
4. **Why It Matters** — the connection to systems on the ground or in orbit.
5. **My Perspective** — the systems-thinking read. Always labeled. Always distinguishable from the data.
6. **Sources** — every claim, traceable.

The default is concise. Depth is earned by the question, not imposed on it.

### 2.4 What "confidence" actually means

Confidence is **measured**, not asserted by the language model.

| Input | Drives confidence down when… |
|---|---|
| Source freshness | Latest sample is older than the source's expected cadence |
| Source count | Only one source corroborates the claim |
| Data completeness | The underlying observation is sparse (e.g., a NEO orbit determined from few observations) |
| Upstream health | A source is currently circuit-broken (see `_si_cached_get` host-down behavior) |

A response with one stale source from a degraded upstream is **Low** confidence regardless of how confidently the model phrases it. The label belongs to the data, not the prose.

### 2.5 What the agent *will not* answer — the rejection script

A single, consistent phrasing builds trust faster than any feature:

> *"I don't have data on that in the systems I'm connected to. Here's what I do have visibility into: \[Voyager 1, 3I/ATLAS, NEO close approaches, solar/geomagnetic activity, satellite catalog\]. Want me to look at any of those instead?"*

No improvisation. No hedged half-answer. No filling the gap with general knowledge from training data — that would violate the grounding contract.

---

## 3. How

### 3.1 The grounding contract

Every supported question type maps to an explicit, allowed set of sources. This table is the **unit-test surface** for the agent — both for correctness and for safety.

| Question type | Allowed sources | Engine consulted |
|---|---|---|
| "What changed today?" | Cached temporal-intelligence output | Temporal Intelligence |
| "Anything unusual?" | Cached signal-scoring output | Signal vs Noise |
| "Any risk to Earth?" | NEO close-approach + geomagnetic + radio blackout indices | Space → Earth Impact |
| "What is \[object\]?" | Catalog metadata only (no live trajectory inference) | Static catalog |
| "Tell me about Voyager 1" | Voyager 1 analysis modules | Voyager analysis |
| Anything outside the above | None — return rejection script | — |

A question that does not map to a row in this table is, by definition, out of scope.

### 3.2 Architecture — read from cache, never fan out from a user request

The deployment runs on a small Flask app behind two gunicorn workers with a 30-second timeout. We have already learned — the hard way — that **upstream calls inside a request are an availability risk**:

- CelesTrak began blocking the production AWS Elastic IP at the TCP layer, with no warning and no recourse. The site stopped getting satellite data despite the code being unchanged.
- We migrated the satellite catalog source to **Space-Track.org** (authenticated OMM feed, ~31k active objects, cached for two hours).
- The host-level circuit breaker in `_si_cached_get` (`_SI_HOST_DOWN_TTL=300s`) was added so a single upstream going dark cannot cascade into worker exhaustion.

The lesson is structural, not vendor-specific: **any single upstream can disappear at any time, for reasons outside our control.** The architecture must assume this, not hope against it.

Therefore:

- The agent reads from the **same cached engine outputs** the dashboard already serves.
- Cache refresh remains the responsibility of the existing background paths and `_si_cached_get`, with its negative-cache and host-level circuit breaker.
- The agent never opens a new path to NASA / NOAA / Space-Track from inside a user-facing request.
- "Parallel execution" means parallel reads against in-process cached objects, not parallel HTTP fan-out.
- When a source is degraded or has been replaced (as CelesTrak was by Space-Track), the grounding contract is updated — the agent never silently substitutes one source for another.

This is not a constraint. It is an **architectural commitment** that keeps the agent fast, cheap, and resilient when an upstream goes down.

### 3.3 The reasoning loop

For every query:

1. **Classify intent** against the grounding contract. If no match → rejection script. Stop.
2. **Resolve context** — time window, event type, severity threshold.
3. **Read from cache** — pull the relevant engine output(s).
4. **Compute confidence** from the inputs in §2.4. Do not let the model self-report.
5. **Compose** — concise by default, deep when warranted.
6. **Attribute** — every claim carries a source and a timestamp.
7. **Add perspective** only when the data shows a *pattern*, not a single point. The `My Perspective` layer is for systems observations, not for color commentary on individual events.

### 3.4 UI / UX

- **Entry point label:** `Interpret` (or `Signal`, or `The Observatory`). Not "Ask the Universe" — the platform's voice is systems-thinking and non-mystical, and the label should match.
- **Guided prompts** as the default surface for first-time users:
  - "What changed today?"
  - "Anything unusual right now?"
  - "Any risk to Earth?"
  - "Explain this event" (contextual, on a dashboard card)
- **Response rendering:**
  - Concise responses inline.
  - Deep responses expandable, section by section.
  - Linked dashboard elements highlight when referenced — the agent and the dashboard are the same surface, not two surfaces.
- **Tone:** clear, non-alarmist, authoritative without being ornate. The site already has this voice. The agent must inherit it, not invent a new one.

### 3.5 Safety and degradation

- **No hallucinated data.** Enforced by the grounding contract, not by hope.
- **Transparent failure.** When a source is degraded, the agent says so, names the source, and offers the last known value with its timestamp. It does not silently fall back.
- **Bounded blast radius.** Out-of-domain queries are rejected with the standard script. The agent does not reach for general knowledge to fill gaps.

### 3.6 Success — measured the right way

Vanity metrics will lie about this feature. The metrics that matter:

- **Grounded-response rate.** Fraction of responses where every claim resolves to a cited source. Target: 100%.
- **Rejection rate on out-of-domain queries.** Should be high and *stable*. A drop means the agent has started improvising.
- **Concise/Deep ratio.** Most queries should resolve in concise mode. If deep mode dominates, the response template is too heavy.
- **Time-to-insight.** Can a first-time user understand what is significant about today in under ten seconds?
- **Repeat usage on signal days.** When something real happens in space, do users come back to the agent to make sense of it?

Engagement is a downstream effect. Trust is the upstream cause.

---

## 4. A pragmatic, phased approach

The temptation with agentic features is to ship the whole stack at once. We will not. Each phase below is independently shippable, independently valuable, and independently verifiable.

### Phase 1 — Grounded Q&A on cached state (the floor)

**Scope.** Concise mode only. Five question types, each mapped to a row in the grounding contract. Read from existing cached engine outputs. Rejection script for everything else.

**Ships.** A working `Interpret` entry point on the homepage, with guided prompts. No deep mode, no perspective layer, no proactive surfacing.

**Why first.** This is the smallest version that is *honest*. It proves the architecture (read-from-cache, no upstream fan-out) and the grounding contract before any narrative layer is added on top.

**Done when.** Every response carries a source and a timestamp. Out-of-domain queries return the rejection script verbatim. p95 latency under 2 seconds. Zero upstream calls inside a request path.

### Phase 2 — Deep mode and the `My Perspective` layer

**Scope.** The six-section response template, triggered by significance thresholds or explicit user request. Data-driven confidence labels. The systems-thinking perspective layer, applied only when the underlying engines actually surface a *pattern* (cluster, correlation, deviation).

**Ships.** The voice of the platform, made conversational.

**Why second.** Perspective without grounding is editorializing. We earn the right to add perspective only after Phase 1 has proven the grounding holds.

**Done when.** Confidence is computed from source freshness / count / completeness, not asserted by the model. `My Perspective` never appears on single-event responses where no pattern is present.

### Phase 3 — Proactive surfacing

**Scope.** The agent volunteers — on the homepage, without being asked — the top one to three system signals of the day, drawn from Signal vs Noise and Temporal Intelligence.

**Ships.** The platform starts to feel like it is *paying attention* on the user's behalf.

**Why third.** Proactive surfacing is only valuable once the grounding contract and the perspective layer are both trustworthy. Surfacing the wrong thing loudly is worse than surfacing nothing at all.

**Done when.** The proactive panel updates from the same cached signal-scoring output, refuses to surface anything when no event clears the significance threshold, and never invents urgency on a quiet day.

### Phase 4 — Multi-engine correlation (the original argument, fully realized)

**Scope.** The agent identifies and explains *cross-engine* patterns — a solar event correlated with a satellite drag signature correlated with a ground-impact indicator. This is the "clusters, not headlines" promise made operational.

**Ships.** The clearest expression of what makes this platform different from every other space dashboard.

**Why last.** Cross-engine correlation is the most powerful and the most dangerous feature. False correlations are worse than no correlations. It can only ship on top of three earlier phases that have already established the grounding discipline.

**Done when.** Every correlation claim is supported by data from each engine cited, timestamps line up within a defensible window, and the `My Perspective` layer can articulate *why* the pattern matters in systems terms — not just that it exists.

### Out of scope (deliberately, for now)

- Cross-session memory.
- Voice interaction.
- Predictive alerts beyond what the underlying data supports.
- Personalization.

These are not bad ideas. They are simply ideas that should not ship before Phases 1–4 have built the trust required to make them safe.

---

## 5. The closing thought

The universe does not need another interface that talks fluently about it.

It needs one that **interprets it as a system** — patiently, with provenance, and with restraint about what it does and does not know.

If we get that right, the agent stops feeling like a feature and starts feeling like the platform's point of view, made addressable.

That is the bar.
