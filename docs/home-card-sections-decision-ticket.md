# Home Page — Remove Card Sections, Replace With "Where to Next" Block

## Summary

After the Leadership emphasis block, the home page currently carries **three full card grids** — *Voyager 1: Deep Space Analysis* (6 cards), *3I/ATLAS: Interstellar Comet Research* (3 cards), *Black Hole Cosmology: Scientific Paper* (3 cards) — totalling **12 cards across three sections**.

Every link in those cards already exists in the hero CTA dropdowns (Voyager 1 / Space Intelligence / Deep Research). The sections are a sitemap dressed up as content — and they are **asymmetric**: Space Intelligence and Mars get no card grid, even though Space Intelligence is a top-level CTA in the hero. The "missing" Space Intelligence section was the prompt for this audit.

This ticket removes the three card sections entirely and replaces them with a single short *"Where to next"* prose block — 3–4 lines pointing the reader at the strongest entry points. The hero dropdown handles complete navigation.

**Reference:** `templates/home.html` lines ~872–1010 (the three `<section class="content-section">` blocks).

---

## Intent (North Star)

1. **Don't duplicate navigation.** The hero CTA already exposes every page these cards link to. Repeating the same links lower on the page is sitemap, not story.
2. **Don't ship asymmetry.** Three of the five top-level areas have card grids; two don't. That visibly downgrades Space Intelligence and Mars without intent. Removing all three card sections fixes the asymmetry by deletion rather than expansion (don't boil the ocean — *Leadership Principle*).
3. **Honour the page's narrative arc.** Hero → About PDSL → Leadership Philosophy → emphasis block → *"That is who I am"* — and then 12 text cards that read like a navigation menu. The right next beat after the emphasis block is either a clean curated pointer or the footer, not a sitemap.
4. **Apply Anthropic's *fewer, sharper* rule beyond prose.** Same edit note that reshaped the Leadership section in #15 applies here: *fewer cards land harder than many.*

---

## Why Option A (delete) over Option B (one unified grid) or Option C (expand symmetrically)

| Option | Verdict | Reason |
|--------|---------|--------|
| **A. Delete all three card sections, add a short "Where to next" block** | **Chosen** | Hero dropdowns already cover navigation. Page becomes hero → about → leadership → next-step → footer. Story-driven, fast scroll, matches *"stunning visuals first; depth on demand."* |
| B. Collapse to one unified ~6-card grid (2 Voyager + 2 Space Intelligence + 2 Deep Research) | Rejected | Halves the redundancy but doesn't eliminate it. Still a sitemap, just shorter. |
| C. Add Space Intelligence + Mars card grids for symmetry | Rejected | Worst outcome — turns the home page into a pure sitemap. Five card grids after the leadership emphasis block; the page stops being a story. |

---

## Current vs. Target

| Region | Current | Target |
|--------|---------|--------|
| After Leadership emphasis block | Three `<section class="content-section">` grids: Voyager 1 (6 cards), 3I/ATLAS (3 cards), Black Hole (3 cards) — ~140 lines of HTML | One short prose block with 3–4 curated pointers (~15 lines of HTML) |
| Hero CTA dropdowns | Voyager 1 / Space Intelligence / Deep Research — each with its sub-pages | **Unchanged** — they remain the canonical navigation |
| Section anchors `#projects` `#atlas` `#blackhole` | Targets of in-page jumps (if any nav uses them) | Verify zero internal references before deletion |

---

## Implementation Plan

### Step 1 — Confirm no in-page anchors are linked elsewhere

`grep_search` for `#projects`, `#atlas`, `#blackhole` across `templates/`. If anything outside `home.html` jumps to these anchors, retain the IDs (re-attach them to the new "Where to next" block or to the footer) and document.

### Step 2 — Replace three sections with a single "Where to next" block

Single `replace_string_in_file` covering lines ~872 through ~1010 of `home.html` (the three `<section>` blocks). New block sits in roughly the same position — between the Leadership section and whatever follows (footer / scripts).

Proposed copy (subject to voice review):

```html
<section class="content-section" id="explore">
    <div class="container" style="text-align: center; max-width: 820px;">
        <h2 class="section-title">Where to Next <a href="#top" class="scroll-top-rocket" title="Back to top">&#x25B3;</a></h2>
        <p style="font-size: 1.15rem; line-height: 1.8; color: rgba(255,255,255,0.85);">
            If you have a few minutes, start with <a href="/voyager-story" class="project-link" style="display:inline;">The Voyager Story</a> &mdash; the {{ facts.mission_age_years }}-year journey, told with the engineering and the leadership lessons intact.
        </p>
        <p style="font-size: 1.15rem; line-height: 1.8; color: rgba(255,255,255,0.85);">
            For real-time situational awareness of near-Earth space, open <a href="/space-intelligence" class="project-link" style="display:inline;">Space Intelligence</a>. For an interstellar visitor we are still learning to read, see <a href="/atlas" class="project-link" style="display:inline;">3I/ATLAS</a>. For the cosmological hypothesis, the <a href="/blackhole" class="project-link" style="display:inline;">Black Hole paper</a> is one click away.
        </p>
        <p style="font-size: 1rem; color: rgba(255,255,255,0.6); margin-top: 30px;">
            Everything else &mdash; Voyager analytics (facts, trajectory, plasma, density, magnetometer), Space Intelligence sub-pages, and the Mars 1993 mission &mdash; is in the menus at the top.
        </p>
    </div>
</section>
```

### Step 3 — Voice-regression test guard

Add to `tests/test_facts.py` (extends the pattern from #15):

```python
def test_home_card_sections_removed(client):
    """Issue #17: the three sitemap-style card grids are gone."""
    body = client.get('/').data
    must_be_absent = [
        b'Voyager 1: Deep Space Analysis',
        b'3I/ATLAS: Interstellar Comet Research',
        b'Black Hole Cosmology: Scientific Paper',
    ]
    for phrase in must_be_absent:
        assert phrase not in body, f'Card section heading returned to home: {phrase!r}'

def test_home_where_to_next_block_present(client):
    """The replacement narrative pointer block must be live."""
    body = client.get('/').data
    assert b'Where to Next' in body
    # Curated entry points still discoverable via prose.
    for path in (b'/voyager-story', b'/space-intelligence', b'/atlas', b'/blackhole'):
        assert path in body
```

### Step 4 — Local smoke (this ticket explicitly requests local Flask before push)

```powershell
cd c:\Deep-Space-Research\deep_space_portal
.\.venv\Scripts\Activate.ps1
$env:FLASK_DEBUG = "true"
python app.py
# Browse http://localhost:5000/  — read top-to-bottom, confirm flow lands.
```

### Step 5 — Commit, push, deploy

Standard sequence: commit with `Closes PSadasivam/deep-space-portal#17`, push, EC2 pull + systemd restart, verify `/` returns 200.

---

## Out of Scope

- **Hero CTA dropdowns.** Stay exactly as they are — they are the canonical navigation and already complete.
- **About PDSL section, Leadership section, footer.** Untouched.
- **`/atlas`, `/blackhole`, individual Voyager pages.** Their dedicated routes are unaffected. Only the *redundant card teasers on the home page* are removed.
- **Adding a Space Intelligence card grid.** The original prompt — *"should we add Space Intelligence cards?"* — is answered "no" by deletion, not by expansion.

---

## Acceptance Criteria

- [ ] Three `<section>` card grids (`#projects` / `#atlas` / `#blackhole`) removed from `templates/home.html`.
- [ ] Replacement *"Where to Next"* prose block present, with curated links to `/voyager-story`, `/space-intelligence`, `/atlas`, `/blackhole`.
- [ ] No in-page `#projects` / `#atlas` / `#blackhole` references elsewhere in `templates/` are broken (or, if they exist, the new block carries the appropriate ID).
- [ ] Hero CTA dropdowns unchanged (regression-checked by grep).
- [ ] Voice-regression tests added: `test_home_card_sections_removed`, `test_home_where_to_next_block_present`.
- [ ] Full portal suite green (target: 72/72 = 70 + 2 new).
- [ ] Local Flask smoke completed before push (per requester).
- [ ] Deployed; `/` returns 200; reads top-to-bottom as story, not sitemap.

---

## Effort

Small. One template region replaced, two tests added. No CSS, JS, or backend change.

## Dependencies

- None. Independent of FU-2 (drift telemetry) and FU-3 (annual reconciliation).
