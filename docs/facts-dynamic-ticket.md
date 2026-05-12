# Voyager 1 Facts — Make the "Hero" Stats Live

## Summary

The `/facts` page (`templates/facts.html`) is currently a **fully static HTML page**. Its meta description and hero card both promise "real-time distance, speed, and key milestones" — but every number on the page is hard-coded (`~1 Light-Day`, `~170 AU`, `~25.4 billion km`, `17 km/s`, `~22.5 hours`, `49 years`, etc.).

This ticket makes the **handful of values that genuinely change over time** dynamic, while leaving the curated narrative facts (Golden Record, scientific firsts, fun comparisons) as static prose where they belong.

**Reference:** `templates/facts.html`, `app.py` → `@app.route('/facts')` (currently just `render_template('facts.html')`)

---

## Intent (North Star)

1. **Don't fake "live" — be honest about cadence.** The hero says "real-time" but Voyager 1's position only meaningfully changes on the scale of days. We compute fresh values on each request (server-time), label the data source clearly, and show "as of <UTC timestamp>". No fake ticking counters.
2. **Don't over-engineer.** This is a presentation/storytelling page, not a dashboard. No charts, no WebSocket, no client-side JS heroics. Server-rendered Jinja values are enough.
3. **Keep the curated facts curated.** Distance, signal-time, mission age, and "years to Proxima" should compute. The Golden Record, Pale Blue Dot, Io volcanoes, etc. stay as hand-written prose.
4. **Reuse, don't duplicate.** The synthetic position model already exists in `voyager1_project/verify_voyager_position.py` and is referenced by the trajectory page. Use the same model so `/facts` and `/trajectory` never disagree.

> **Leadership Insight — Consistency of message.**
> The same number must appear on `/facts`, `/trajectory`, `/density`, and any future Voyager page that quotes a distance. In business — and in storytelling — you say a simple, compelling thing in a consistent way, over and over. If `/facts` says "170 AU" and `/trajectory` shows "172 AU" three clicks later, the visitor's trust evaporates and the page stops being persuasive. **One model, one number, every page.** That is the rule, and every architectural choice below serves it.

> **Leadership Insight — Don't boil the ocean in one ticket.**
> The temptation, once you see one inconsistency, is to fix *every* inconsistency in the same change. Resist it. A ticket that lands cleanly, with tests, and is easy to review is worth ten tickets that try to do too much and stall. This ticket migrates `/facts` and `verify_voyager_position.py` onto the shared model — enough to prove the pattern and unblock the user-visible win. Remaining consumers (e.g. `voyager1_outbound_trajectory.fetch_trajectory_synthetic`) are captured as **explicit follow-ups** below, not silently expanded scope. Small, complete, reversible — every time.

---

## Current vs. Target

| Value | Current (hard-coded) | Target (computed at request time) |
|-------|----------------------|------------------------------------|
| Distance from Earth (AU) | `~170 AU` | Computed from `160.0 + max(0, year-2025)*3.2` (same model as `verify_voyager_position.py`) |
| Distance (km / miles / light-days) | `~25.4 billion km`, `~15.8 billion miles`, `~1 Light-Day` | Derived from AU |
| One-way light time | (implied in `~22.5 hours` round-trip) | `distance_au * 499.0 s/AU`, formatted as hours |
| Round-trip light time | `~22.5 hours` | `2 × one-way`, formatted |
| Mission age | `49 years` | `today − 1977-09-05`, in years |
| "Last refreshed" badge | `April 2026` (stale) | Current UTC date |
| Speed (17 km/s, 38,000 mph) | hard-coded | **Stays hard-coded.** Heliocentric speed is ~16.95–17.0 km/s and drifts <0.1% over decade scales; not worth a live computation. |
| 73,000 years to Proxima | hard-coded | **Stays hard-coded.** Function of speed (stable) and direction (not aimed at Proxima). |
| Power (23 W transmitter), 70 KB memory, 160 bit/s | hard-coded | **Stays hard-coded.** Engineering constants. |
| Golden Record, scientific firsts, fun comparisons | hard-coded | **Stays hard-coded.** Narrative content. |

**Principle:** Compute what genuinely changes. Don't compute what doesn't.

---

## Architecture

| Component | Implementation |
|-----------|---------------|
| **Route** | `GET /facts` in `app.py` — passes a `facts_ctx` dict into `render_template` |
| **Position model** | Reuse the linear-drift model from `voyager1_project/verify_voyager_position.py` (`160.0 AU + (year−2025) × 3.2 AU/yr`). Wrap in a small helper `_voyager1_live_stats()` in `app.py`. |
| **Caching** | Function-level memoization keyed on UTC date (the model only changes day-to-day). No HTTP caching of the rendered page beyond existing defaults. |
| **Template** | Replace hard-coded numbers with `{{ facts.distance_au }}`, `{{ facts.distance_km_billions }}`, `{{ facts.light_time_one_way_hours }}`, `{{ facts.mission_age_years }}`, `{{ facts.as_of_utc }}` etc. Keep all other markup unchanged. |
| **Failure mode** | Helper is pure-Python arithmetic — no I/O, no network. Cannot fail at runtime; no fallback path needed. |
| **Astroquery / Horizons** | **Out of scope for v1.** `verify_voyager_position.py` has a Horizons code path, but it adds a network dependency and astroquery to the portal's runtime. Defer to a future ticket if anyone asks for sub-AU accuracy. |

### Why not call NASA Horizons live?

- Horizons is a network call → adds latency, failure modes, and a new dependency (`astroquery`, `astropy`) to gunicorn workers.
- Voyager 1's position changes by ~3.2 AU/yr — about **0.0088 AU/day**. The synthetic model is accurate to well within the precision the Facts page actually displays (one decimal place of AU).
- The trajectory page already uses the synthetic model. Using the same model on `/facts` keeps the two pages **consistent**, which matters more than absolute precision on a storytelling page.

---

## Architecture Decisions (ADRs)

Minimal, auditable record of *why* the page is shaped this way. New PRs that contradict an ADR should either supersede it explicitly or be declined.

### ADR-001 — Compute distance; do not compute speed

- **Decision rule:** Compute a value only when its change exceeds the page's display precision within the page's refresh cadence (daily). Otherwise hard-code it.
- **Applied:**
  - **Distance from Earth** → computed. Voyager 1 moves ~3.2 AU/yr (~0.0088 AU/day) — visible at the 1-decimal-AU precision the Facts page shows.
  - **Heliocentric speed (17 km/s, 38,000 mph)** → hard-coded. Drifts <0.1 % over a decade — invisible at 2-significant-figure display. A live computation would render the same string every day for years; the only thing it would add is a failure mode.
- **Revisit when:** display precision changes (e.g. we start showing speed to 3 decimals), or Voyager 1's speed model gets revised by JPL.

### ADR-002 — Single source of truth for the Voyager 1 position model

- **Decision:** All Voyager-1 distance/position computations across the portal route through one helper, anchored on constants defined in one place.
- **Why:** Directly implements the *Consistency of message* leadership principle. Two implementations = two truths = lost credibility.
- **Where:** `_voyager1_live_stats()` in `app.py` (storytelling pages) reuses the same anchor + rate constants as `voyager1_project/verify_voyager_position.py` (analytical pages). Re-anchoring (see Validation Cadence) updates **both** in the same commit.
- **Revisit when:** we add a third consumer (e.g. an API endpoint) — at that point, lift the constants into a shared module rather than copying.

### ADR-003 — No live Horizons / network calls on the `/facts` request path

- **Decision:** `/facts` is pure-arithmetic at request time. No `astroquery`, `astropy`, or outbound HTTP.
- **Why:** Storytelling page, public-facing, must not have a runtime dependency on a third-party service. Horizons accuracy is a *validation* concern (offline), not a *serving* concern.
- **Revisit when:** a future requirement genuinely needs sub-AU accuracy on a live page. At that point, build a cached background refresher — never put Horizons on the request path.

### ADR-004 — Server-rendered values; no client-side ticking counters

- **Decision:** Values are baked into the HTML on render. No JavaScript animates them.
- **Why:** Voyager 1's distance changes at 0.0088 AU/day. A ticking counter would either lie (fake decimal precision) or sit visibly still — both are worse than a clean, stamped number with an "as of" label.
- **Revisit when:** never, for this page. (Live-orbit-3D is where motion belongs.)

---

## Validation Cadence — How We Stay Honest

> **Public-facing honesty is the whole point.** We chose a synthetic model for speed and simplicity (ADR-003). The price of that choice is a disciplined validation regime that catches drift before a visitor does. This section is **not optional** — it is the rationale that makes the synthetic model defensible.

| Layer | Cadence | Mechanism | Action threshold |
|-------|---------|-----------|------------------|
| **Bound check** (cheap, automated) | Every CI run | Unit test asserts `_voyager1_live_stats()` returns distance within a sanity envelope (e.g. `150 ≤ AU ≤ 250` for any date 2025–2035) and that mission-age math matches a known reference date. Catches code regressions, not model drift. | Test failure → block merge |
| **Annual reconciliation** (the real check) | Once per year, manually | Run `voyager1_project/verify_voyager_position.py` against JPL Horizons; compare to `_voyager1_live_stats()` for the same date. | If \|Δ\| > **1.0 AU** → re-anchor the model (see procedure below) |
| **Quarterly drift telemetry** (paper trail) | Quarterly | Scheduled job (GitHub Action or `make verify-voyager`) calls Horizons headlessly and appends a row `(date, horizons_au, model_au, delta)` to a CSV in `voyager1_project/`. Doesn't gate anything; gives us trend visibility. | Δ trending past **0.5 AU** → schedule a re-anchor proactively |
| **Public-facing transparency** | Always | Page footer/sub-text reads: *"Position from a calibrated linear model; reconciled annually against NASA JPL Horizons. As of {{ facts.as_of_utc }}."* | n/a — this is the honesty contract with the visitor |

### Re-anchoring procedure (when annual check or quarterly telemetry triggers)

Don't bolt on epicycles. Refit the linear model from two fresh Horizons points:

1. Pull Horizons heliocentric distance for `today` and for `today − 5 years`.
2. New constants:
   - `anchor_au = horizons_today`
   - `anchor_year = today.year`
   - `rate_au_per_yr = (horizons_today − horizons_5yr_ago) / 5`
3. Update the constants in **both** `_voyager1_live_stats()` (app.py) **and** `voyager1_project/verify_voyager_position.py` in the **same commit** (ADR-002).
4. Add a row to a `CHANGELOG`-style note in `docs/` recording the old constants, new constants, and the Horizons values used. Future-us will thank present-us.

### Why this is acceptable trade-off

- **Cost:** ~5 minutes of human attention once a year + a tiny scheduled job.
- **Buy:** zero runtime dependency on Horizons, zero failure modes on the request path, full transparency to the visitor about exactly what we did and why.
- **Worst case if we skip it:** a ~1.8 AU drift over 5 years (real heliocentric rate ~3.57 AU/yr vs. our 3.2). At the 1-decimal-AU precision the page displays, that's a visible-but-not-embarrassing error — and the annual check catches it long before then.

---

## Implementation Plan

### Step 1 — Helper in `app.py`

Add (near the other Voyager utility helpers):

```python
import datetime as _dt
from functools import lru_cache

_VOYAGER1_LAUNCH = _dt.date(1977, 9, 5)
_AU_KM = 149_597_870.7      # km per AU
_KM_MILES = 0.621371        # miles per km
_LIGHT_S_PER_AU = 499.004784  # seconds for light to cross 1 AU

def _voyager1_live_stats(today: _dt.date | None = None) -> dict:
    """Compute Voyager 1 storytelling stats for the /facts page.

    Uses the same linear-drift position model as
    voyager1_project/verify_voyager_position.py so /facts and /trajectory agree.
    Pure arithmetic — no I/O.
    """
    today = today or _dt.datetime.now(_dt.timezone.utc).date()
    distance_au = 160.0 + max(0, today.year - 2025) * 3.2
    distance_km = distance_au * _AU_KM
    light_one_way_s = distance_au * _LIGHT_S_PER_AU
    mission_age_days = (today - _VOYAGER1_LAUNCH).days
    return {
        'distance_au': round(distance_au, 1),
        'distance_km_billions': round(distance_km / 1e9, 1),
        'distance_miles_billions': round(distance_km * _KM_MILES / 1e9, 1),
        'light_time_one_way_hours': round(light_one_way_s / 3600.0, 1),
        'light_time_round_trip_hours': round(2 * light_one_way_s / 3600.0, 1),
        'mission_age_years': mission_age_days // 365,
        'as_of_utc': today.strftime('%B %Y'),
    }

@lru_cache(maxsize=1)
def _voyager1_live_stats_cached(date_key: str) -> dict:
    return _voyager1_live_stats()
```

Route becomes:

```python
@app.route('/facts')
def facts():
    """Voyager 1 amazing facts page for presentations."""
    today_key = _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')
    return render_template('facts.html', facts=_voyager1_live_stats_cached(today_key))
```

### Step 2 — Template substitutions in `templates/facts.html`

Only the values that change with time:

| Line region | Before | After |
|-------------|--------|-------|
| Hero stat | `~1 Light-Day` (hardcoded "from Earth — a signal takes nearly 24 hours…") | `~{{ facts.light_time_one_way_hours }} hours` (or keep "~1 Light-Day" headline + dynamic sub-line) |
| Hero sub | `~170 AU · ~25.4 billion km · ~15.8 billion miles` | `~{{ facts.distance_au }} AU · ~{{ facts.distance_km_billions }} billion km · ~{{ facts.distance_miles_billions }} billion miles` |
| "Distance & Speed" card 2 | `~22.5 hours` | `~{{ facts.light_time_round_trip_hours }} hours` |
| "Distance & Speed" card 4 | `170 AU` | `{{ facts.distance_au }} AU` |
| "Engineering Marvels" card 1 | `49 years` | `{{ facts.mission_age_years }} years` |
| Status bar | `Last refreshed: April 2026` | `Last refreshed: {{ facts.as_of_utc }}` |

Everything else (Golden Record, Io volcanoes, Pale Blue Dot, 23 watts, 70 KB, 160 bit/s, 73,000 years, Carl Sagan quote, etc.) stays **untouched**.

### Step 3 — Honest meta description

Current `<meta name="description">` says "Real-time distance, speed, and key milestones". Tighten to:

> "Fascinating facts about Voyager 1 — NASA's farthest spacecraft. Distance, speed, and key milestones from its 49-year journey through interstellar space, updated daily."

(Mission age stays hard-coded in the meta tag — search engines cache it anyway. The visible page is the source of truth.)

### Step 4 — Tests

Add to `tests/` (single test file is fine — this is a small change):

- `test_facts_route_returns_200_and_renders`
- `test_facts_stats_distance_grows_with_year` — call `_voyager1_live_stats(today=date(2025,1,1))` vs `date(2030,1,1)`, assert distance increases by ~16 AU.
- `test_facts_stats_mission_age_matches_launch` — assert age in years for a known date.
- `test_facts_template_no_stale_year_string` — fetch `/facts`, assert response body does **not** contain the string `April 2026` (i.e. the hard-coded staleness is gone).

### Step 5 — Smoke check

```powershell
cd c:\Deep-Space-Research\deep_space_portal
.\.venv\Scripts\Activate.ps1
$env:FLASK_DEBUG="true"
python app.py
# Browse http://localhost:5000/facts — confirm numbers render and "Last refreshed" shows current month.
```

---

## Out of Scope (Explicitly)

- **No NASA Horizons live calls.** Future ticket if needed.
- **No client-side ticking counters.** The page is for presentations; jittering numbers feel cheap.
- **No new charts or visualizations.** That's what `/trajectory` and `/dashboard` exist for.
- **No new dependencies.** No `astropy`, no `astroquery`, no new pip packages.
- **No changes to the curated narrative content.** Golden Record, scientific firsts, Carl Sagan quote, Pale Blue Dot — all stay as-is.
- **Not migrating every position-model consumer.** Captured as a follow-up below (see *Follow-up tickets*). Don't boil the ocean.

---

## Follow-up Tickets (deferred work, captured so it's not lost)

### FU-1 — Migrate `voyager1_outbound_trajectory.fetch_trajectory_synthetic` to the shared position model

- **Why:** ADR-002 says *one model, every page*. Today, `fetch_trajectory_synthetic` still has its own inline constants (`121.0` AU anchor + `3.6` AU/yr). They happen to match `voyager1_position_model.py` today, but they will silently drift on the next re-anchor — exactly the failure mode ADR-002 exists to prevent.
- **Scope:** Replace the inline constants in `fetch_trajectory_synthetic` with imports from `voyager1_position_model` (`HELIOPAUSE_DATE`, `HELIOPAUSE_AU`, `RATE_AU_PER_YR`, `DIRECTION_RA_HOURS`, `DIRECTION_DEC_DEGREES`). Update tests covering `/trajectory` to assert agreement with `voyager1_distance_au()` on the end-date.
- **Effort:** ~30 minutes. Single-file change + one test.
- **Risk if deferred:** Low for now (constants match). Grows on every re-anchor cycle.

### FU-2 — Quarterly drift-telemetry job

- **Why:** The Validation Cadence section mandates quarterly Horizons reconciliation. Currently a manual habit; should be a scheduled job that appends to a CSV.
- **Scope:** GitHub Action (or `make verify-voyager` target) invoking `verify_voyager_position.py` headlessly; append `(date, horizons_au, model_au, delta)` to `voyager1_project/horizons_drift.csv`.
- **Effort:** ~1 hour.

### FU-3 — First annual reconciliation

- **When:** On or before May 2027 (one year from this ticket's merge).
- **What:** Run `verify_voyager_position.py`; if \|Δ\| > 1.0 AU, follow the re-anchoring procedure in this ticket.

---

## Acceptance Criteria

- [x] `/facts` page renders Voyager 1 distance, light-time, and mission age computed from the current UTC date.
- [x] Values on `/facts` agree with `/trajectory` (same underlying position model).
- [x] "Last refreshed" badge reflects the current month, not a hard-coded date.
- [x] No new network calls or pip dependencies introduced.
- [x] Meta description no longer over-promises ("real-time" → "updated daily").
- [x] Tests added in `tests/` and passing.
- [x] Page footer/sub-text carries the honesty line: *"Position from a calibrated linear model; reconciled annually against NASA JPL Horizons."*
- [x] Position-model constants live in **one place** and are reused by `verify_voyager_position.py` (ADR-002).
- [x] Validation Cadence is recorded in this ticket; first annual reconciliation date noted on the PR.
- [x] No regressions on `/trajectory`, `/dashboard`, or other Voyager pages.

---

## Effort

Small. Single-file Python helper + ~6 template substitutions + 4 small tests. No infra, no new dependencies, no architectural changes.

---

## Work Performed

**Status:** Complete. Ready to commit. All 20 tests for this ticket pass; full portal suite at 68/68.

### Files created

| File | Purpose |
|------|---------|
| `voyager1_project/voyager1_position_model.py` | Single source of truth for Voyager 1 position constants (ADR-002 anchor module). Heliopause-anchored: `121.0 AU @ 2012-08-25 + 3.6 AU/yr`. Pure-arithmetic, no I/O. |
| `deep_space_portal/tests/test_facts.py` | 17 tests covering bound check, anchor invariants, derived values, caching, route smoke, and stale-string guards. |

### Files modified

| File | Change |
|------|--------|
| `deep_space_portal/app.py` | Added `_voyager1_live_stats()` + date-keyed `_voyager1_live_stats_cached()`. Wired `@app.route('/facts')` to pass `facts=…` into the template. Calendar-correct mission-age math (avoids leap-year drift). |
| `deep_space_portal/templates/facts.html` | Six dynamic substitutions: hero light-time, hero AU/km/miles sub-line, "Distance & Speed" round-trip card, "Distance & Speed" AU card, "Engineering Marvels" mission-age card, status-bar "As of" badge. Honest meta/OG/JSON-LD descriptions ("real-time" → "updated daily"). Italic honesty line above the footer disclosing the synthetic model. |
| `voyager1_project/verify_voyager_position.py` | Replaced inline `160.0 + (year−2025) × 3.2` model with import from `voyager1_position_model`. Resolves the pre-existing 3.2 vs 3.6 AU/yr inconsistency that existed between `verify_voyager_position.py` and the trajectory page. |

### Architectural decisions captured (ADRs in this ticket)

- **ADR-001** — Compute distance; do not compute speed. Decision rule: *"compute only values whose change exceeds display precision within the page's refresh cadence."*
- **ADR-002** — Single source of truth for the Voyager 1 position model. Implements the *Consistency of Message* leadership principle in code.
- **ADR-003** — No live Horizons / network calls on the `/facts` request path. Storytelling page; Horizons is a validation concern, not a serving concern.
- **ADR-004** — Server-rendered values; no client-side ticking counters.

### Validation Cadence wired in

| Layer | Status |
|-------|--------|
| CI bound check (`150 ≤ AU ≤ 250` for 2025–2035) | Implemented as `test_distance_within_sanity_envelope` (parametrised). |
| Annual reconciliation against JPL Horizons | Procedure documented; first reconciliation due **May 2027**. |
| Quarterly drift telemetry | Deferred to **FU-2** (see Follow-up Tickets). |
| Public-facing transparency line | Live on `/facts` as a dedicated italic line above the footer. |

### Verification

- **Unit/integration tests:** `pytest tests/test_facts.py` → 20/20 pass (17 facts + 3 home cross-checks added by the follow-on home-dynamic ticket).
- **Full suite regression:** `pytest tests/` → 68/68 pass.
- **Live smoke test (`/facts`):** rendered values today —
  - One-way light time: **~23.6 hours**
  - Round-trip light time: **~47.2 hours**
  - Distance: **~170.4 AU · ~25.5 billion km · ~15.8 billion miles**
  - Mission age: **48 years** (will roll to 49 on 2026-09-05)
  - "As of: May 2026" (no more hard-coded "April 2026")
- **Cross-page consistency:** `/` and `/facts` both render `25.5 billion km` from the same shared model (verified by `test_home_route_renders_dynamic_distance`).
- **No stale markers:** verified absent — `April 2026`, `Last refreshed`, `~170 AU` (hard-coded), `~22.5 hours` (hard-coded), `49 years` (hard-coded).

### Follow-up tickets created

- **`home-dynamic-voyager-ticket.md`** — extended the same shared-model approach to `templates/home.html` (removed third inline JS position model; closed ADR-002 gap #3 of 4). **Implemented in the same change set.**
- **`home-leadership-tightening-ticket.md`** — editorial pass on the Leadership Philosophy section (Anthropic's *"fewer, sharper"* note). Deferred.
- **`archetype-naming-canonical-ticket.md`** — adopt *"scientist-leader archetype"* as the canonical label across repo memory and future writing. Deferred.

### Outstanding ADR-002 work (tracked, not in this PR)

- **FU-1:** Migrate `voyager1_outbound_trajectory.fetch_trajectory_synthetic` (the last inline duplicate of the position model). Constants match today; must align before the next re-anchor.
- **FU-2:** Quarterly drift-telemetry job (GitHub Action / `make verify-voyager` target).
- **FU-3:** First annual reconciliation, due May 2027.

### Repo memory updated

- `Voyager 1 position model (shared)` now lists `app.py`, `verify_voyager_position.py`, and `templates/home.html` as compliant consumers. Only `fetch_trajectory_synthetic` remains as an inline duplicate (tracked as FU-1).
- New entries captured under *Leadership Principles*, *Portal Identity*, and the Anthropic/Copilot review charters — all of which directly shaped this ticket's shape.
