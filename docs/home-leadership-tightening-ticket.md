# Home Page — Leadership Section Editorial Pass ("Fewer, Sharper")

## Summary

The "From Deep Space to Enterprise Platforms" section on `templates/home.html` currently consists of **13 paragraphs (most one sentence each)**, a 3-item bullet list, an emphasis block of 4 paragraphs, and a final color-accented strong tag. The cumulative shape risks the exact dilution Anthropic Claude specifically flagged in its Voyager Story review:

> *"The piece is rich. The leadership lessons could be fewer — a tighter selection of four or five would let the strongest ones land harder. Nine callouts slightly dulls the impact of each."*

This is an **editorial pass**, not a code change. It touches voice, rhythm, and information density. Scoped separately because it deserves a separate review lens (read-aloud test, voice integrity, no JS/CSS/Python diff to evaluate).

**Reference:** Repo memory entry *"Anthropic Claude's review of the Voyager Story page"* — the *Fewer, sharper* rule.

---

## Intent (North Star)

1. **Apply Anthropic's edit note directly.** Four to five strong paragraphs, not thirteen sentence-paragraphs. The strongest beats deserve room to breathe.
2. **Preserve every distinctive line.** This is consolidation, not amputation. The unique phrasings *"engineered for a future no one could fully predict,"* *"if we are not clear on the why and the what, the how becomes reactive,"* *"compounding investments,"* and the closing *"That is who I am"* must survive.
3. **Don't sanitize the voice.** First-person, lived-experience tone is part of the portal's signature (per the identity charter). Do not flatten into generic third-person leadership prose.
4. **Earn the emphasis block.** The italic / bold emphasis closer works precisely *because* the prose preceding it is rigorous. Don't soften the closer; tighten the runway.

---

## Current Shape

| Paragraph | Beat | Strength |
|-----------|------|----------|
| 1 | "I was a child when Voyager 1 launched…" | **Strong** — personal entry point |
| 2 | "What fascinates me is not just the distance, but the design philosophy behind it" | Bridge; could merge into 3 |
| 3 | "Engineered for a future no one could fully predict…" | **Strong** — the anchor metaphor |
| 4 | "That mindset has fundamentally shaped who I am as a technology leader" | Transition; could fold into 5 |
| 5 | "I start with understanding — not with immediate execution" | Insight |
| 6 | "I take a step back to assess the landscape… if we are not clear on the why and the what, the how becomes reactive" | **Strong** — distinctive line |
| 7 | "This approach has consistently enabled… hundreds of millions in incremental revenue" | Outcome paragraph; reads resume-bullet mid-narrative |
| Bullets (3) | "one-platform visions / simplified portfolios / long-term direction" | Could become inline prose |
| 8 | "Engineer in me is relentless…" | Transition |
| 9 | "Voyager reinforces a second principle…" | Setup for 10 |
| 10 | "Architectural integrity… compounding investments" | **Strong** — thesis line |
| 11 | "Voyager offers a simple but enduring leadership insight" | Pure setup; can be deleted |
| Emphasis block (4) | "Great engineering / Leadership is the same / scientist-leader / That is who I am" | **Strong** — leave intact |

That's **13 paragraphs + 3 bullets + 4-paragraph emphasis = 20 narrative units** before the closing "That is who I am." Anthropic's note: aim for **4–5 strong paragraphs** before the emphasis block.

---

## Target Shape (proposed, not prescriptive)

Reduce the 13 paragraphs + bullets to roughly **5 paragraphs**, preserving every distinctive line:

1. **Opening — personal entry point.** Merge current ¶1 + ¶2 + ¶3. Voyager launched when I was a child; today it has traveled `{{ facts.distance_km_billions }} billion km`; *what fascinates me is the design philosophy* — engineered for a future no one could fully predict.
2. **The leadership translation.** Merge current ¶4 + ¶5 + ¶6. That mindset shaped how I lead: start with understanding, not execution; **if we are not clear on the why and the what, the how becomes reactive.**
3. **Outcome paragraph.** Tighten current ¶7 + the 3 bullets into one prose paragraph. Trade the bullet-list shape for fluent prose. (*"This is how one-platform visions are shaped, how complex portfolios are simplified, how technology aligns to long-term direction rather than short-term noise — hundreds of millions in incremental revenue over a five-year horizon."*)
4. **First-principles + the second Voyager principle.** Merge current ¶8 + ¶9 + ¶10. The engineer in me is relentless about a path forward; Voyager reinforces a second principle — *the systems we design today will outlive immediate roadmaps. Architectural integrity is a compounding investment.*
5. **Setup line to the emphasis block.** Either delete current ¶11 entirely (the emphasis block can stand on its own) or compress to one line: *"And one final insight."*

Then the **emphasis block stays exactly as is**. It already lands; the runway just gets shorter.

---

## Implementation Plan

### Step 1 — Read aloud

Before any edit, read the current section aloud and time it. Then read the proposed shape aloud. The proposed version should feel **shorter to read but heavier per sentence**.

### Step 2 — Single template edit

One `multi_replace_string_in_file` operation on `home.html` covering the paragraph block between `<div class="leadership-text">` and `</div>` preceding the emphasis block. **CSS untouched. JS untouched.**

### Step 3 — Verify the preserved lines

A grep-based test, added to `tests/test_facts.py` or a new `test_home_voice.py`:

```python
def test_home_preserves_signature_phrases():
    resp = client.get('/')
    body = resp.data
    must_preserve = [
        b"engineered for a future no one could fully predict",
        b"the how becomes reactive",
        b"compounding investments",
        b"That is who I am",
        b"scientist-leader",
    ]
    for phrase in must_preserve:
        assert phrase in body, f"Signature phrase lost: {phrase!r}"
```

This is **the regression guard for voice** — the same way `test_facts_route_has_no_stale_refresh_string` guards numeric staleness.

### Step 4 — Smoke check

Render `/` and confirm the section visually reads as a tighter, more deliberate sequence. The "ah" moments should hit harder, not softer.

---

## Out of Scope

- **Hero subtitle, blog-subtitle, or the `.pdsl-thesis` line.** All three are already at the right density. Don't touch.
- **Projects / 3I/ATLAS / Black Hole cards.** Different section, different ticket if anything.
- **The emphasis block itself.** Stays verbatim.
- **CSS, layout, fonts.** This is a prose ticket only.

---

## Acceptance Criteria

- [ ] Leadership-philosophy prose reduces from **13 paragraphs + 3 bullets** to roughly **5 paragraphs**, before the emphasis block.
- [ ] Every signature phrase listed above is preserved exactly (verified by automated test).
- [ ] Read-aloud time for the section is shorter; per-sentence weight is heavier (subjective; reviewer sign-off).
- [ ] No layout, CSS, or JS changes.
- [ ] No regressions to other home-page sections.

---

## Effort

Small (editorial). Single-file change. Risk is in the *voice review*, not the diff size.

## Dependencies

- Should land **after** `home-dynamic-voyager-ticket.md`, so the dynamic `{{ facts.distance_km_billions }}` is available to fold into the opening paragraph naturally.
