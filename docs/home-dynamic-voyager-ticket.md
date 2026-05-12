# Home Page — Server-render Voyager 1 Distance (Close the Third ADR-002 Gap)

## Summary

The home page (`templates/home.html`) currently runs **its own** Voyager 1 distance model in client-side JavaScript:

```js
const refAU = 163.0;                        // different anchor from app.py
const auPerYear = 3.6;
const refDate = new Date('2025-01-01...');  // different anchor date from app.py
```

This is **the third inline implementation** of the same physical model — and exactly what ADR-002 ("one model, one number, every page") was created to prevent. We already unified `app.py` and `verify_voyager_position.py` onto `voyager1_position_model.py`. The home page is the last consumer holding out.

Net effect today: server (heliopause-anchored) renders **25.5 B km** on `/facts`, JS fallback on `/` computes **25.1 B km**. The numbers will diverge further on the next re-anchor. We fix the cause, not the symptom.

**Reference:** [docs/facts-dynamic-ticket.md](./facts-dynamic-ticket.md) — ADR-002.

---

## Intent (North Star)

1. **One model, one number, every page.** This ticket completes the migration started in the Facts ticket. After it lands, *no* template or script has its own Voyager 1 constants.
2. **Eliminate flicker.** The hero number currently boots as literal `"24"` and is rewritten by JS post-load — a one-frame lie. Render the correct value at template time; no JS-rewrite, no flicker, no JS-disabled blank.
3. **Delete code, don't add it.** This ticket should *remove* JavaScript, not introduce more.
4. **Don't boil the ocean.** Two scoped substitutions on `home.html` + a small route update. Editorial and naming concerns are explicitly deferred to separate tickets.

---

## Current vs. Target

| Location | Current | Target |
|----------|---------|--------|
| `home.html` L835 — Voyager distance | `<span id="voyager-distance">24</span>&nbsp;billion kilometers` | `{{ facts.distance_km_billions }}&nbsp;billion kilometers` (no `id`) |
| `home.html` L953 — Voyager Story card | `"the 49-year journey of humanity's farthest machine"` | `"the {{ facts.mission_age_years }}-year journey of humanity's farthest machine"` |
| `home.html` ~L1090-1112 — IIFE position model | 25 lines of JS computing distance + fetch-then-fallback | **Deleted entirely** |
| `app.py` — `@app.route('/')` | `return render_template('home.html')` | `return render_template('home.html', facts=_voyager1_live_stats_cached(today_key))` |

---

## Architecture

Already in place from the Facts ticket:
- `voyager1_project/voyager1_position_model.py` — shared constants (heliopause anchor).
- `app.py:_voyager1_live_stats()` + `_voyager1_live_stats_cached()` — date-keyed memoized helper.

This ticket just **wires the home route to the same helper**. No new infrastructure.

### Why server-render and not call `/api/position` from the client?

- `/api/position` exists but generates a Matplotlib position plot; it's rate-limited to **10/minute per IP** and was never designed as a lightweight scalar feed.
- A scalar string in the rendered HTML is **smaller**, **faster**, **doesn't require JS**, and **doesn't load a matplotlib backend on the request path**.
- The original JS was already trying to be defensive (`if apiAU > 100`) — a tell that the API was the wrong source for this use.

---

## Implementation Plan

### Step 1 — Update the `/` route

```python
@app.route('/')
def index():
    """Beautiful landing page inspired by Prabhu's blog design."""
    today_key = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    return render_template('home.html', facts=_voyager1_live_stats_cached(today_key))
```

### Step 2 — Template substitutions

- Replace the `<span id="voyager-distance">24</span>` with the Jinja value. Drop the `id` attribute (no longer needed).
- Replace `"49-year journey"` in the Voyager Story card with `"{{ facts.mission_age_years }}-year journey"`.

### Step 3 — Delete the IIFE

Remove the entire `// Compute live Voyager 1 distance from Earth` block plus its closing comment. ~25 lines gone.

### Step 4 — Tests

Add to `tests/test_facts.py` (same file — they share the helper):

- `test_home_route_renders_dynamic_distance` — GET `/`, assert body contains the same `distance_km_billions` value that the helper returns for today.
- `test_home_no_inline_voyager_constants` — GET `/`, assert body does **not** contain the strings `refAU = 163` or `voyager-distance` (regression guard against re-introduction).
- `test_home_voyager_story_card_dynamic_age` — GET `/`, assert body contains `f"{mission_age_years}-year journey"`.

### Step 5 — Smoke check

Render `/` locally and confirm:
- Distance matches `/facts` exactly.
- No flicker on slow connections (test by throttling DevTools).
- Page works with JS disabled.

---

## Out of Scope (Explicitly)

- **Leadership Philosophy section editorial pass** — captured as `home-leadership-tightening-ticket.md`.
- **Canonical archetype name unification** — captured as `archetype-naming-canonical-ticket.md`.
- **Hero meta tag rewrite.** Optional polish; not blocking.
- **3I/ATLAS apostrophe normalisation, floating-emoji review, "hundreds of millions" copy.** Cosmetic; defer.
- **No changes to `/api/position`.** It serves the magnetometer/trajectory page plot; out of scope here.

---

## Acceptance Criteria

- [ ] `/` renders the same Voyager 1 distance as `/facts` (verified by an automated test reading both routes).
- [ ] `/` renders correctly with **JavaScript disabled** (no `"24"` placeholder, no missing number).
- [ ] The IIFE position-model JS is deleted from `home.html`.
- [ ] The Voyager Story card on `/` shows the dynamic mission age, not `"49-year"`.
- [ ] Three new tests in `tests/test_facts.py` pass; full suite still green.
- [ ] No new dependencies. No changes to `voyager1_position_model.py`.
- [ ] Repo memory `Voyager 1 position model (shared)` entry no longer lists `home.html` as a violator.

---

## Effort

Small. ~20 lines of code change, ~25 lines deleted, 3 tests.
