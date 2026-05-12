# Canonical Archetype Name — Adopt "Scientist-Leader Archetype" Everywhere

## Summary

The portal's signature concept — the new kind of leader who fluidly combines physics, systems thinking, signal interpretation, and narrative communication — is currently named **three different ways** in different surfaces:

| Where | Phrase |
|-------|--------|
| `home.html` Leadership emphasis block | **"scientist-leader archetype"** |
| Repo memory (Portal Identity) | "new archetype of leader" |
| Repo memory (Density review quote) | "new archetype of technology leader" |

This violates ADR-002 in spirit: *one model, one number, every page* applies to **concepts**, not just numbers. A signature idea with three names dilutes the brand of all three.

This ticket adopts **"scientist-leader archetype"** as the canonical term and aligns every reference.

---

## Intent (North Star)

1. **One concept, one name, every surface.** The signature of the portal deserves the same discipline we apply to numbers.
2. **"Scientist-leader archetype" is the right choice.** Two words, evocative, already polished on the live page. The other two phrasings are descriptions of it, not names for it.
3. **This is a naming pass, not a content pass.** Don't expand the concept. Don't re-define it. Just align the label.

---

## Why "scientist-leader archetype"

- **Already on the live page** ([home.html#L900](../templates/home.html#L900)), in the emphasis block — the most prominent placement on the home page.
- **Two words.** Easier to say, easier to remember, easier to search.
- **Evocative without being a buzzword.** *Scientist* carries the physics + rigor + curiosity load; *leader* carries the responsibility + execution + voice load. *Archetype* signals "a kind of person," not "a methodology" or "a framework" (both of which would feel corporate).
- **Generalisable.** Works on Voyager pages, Density, 3I/ATLAS, Black Hole, and future writing. Doesn't tie the concept to any single domain.

---

## Surfaces to Update

### 1. Repo memory — `/memories/repo/deep-space-portal.md`

- *"Portal Identity"* section: change *"a new archetype of leader"* → *"the scientist-leader archetype"*.
- *"Implications for future tickets/edits"* (Density review section): change *"new archetype of technology leader"* → *"scientist-leader archetype"*, and quote Copilot's original phrasing once as a footnote (preserve the source for provenance, but treat the canonical name as the primary).

### 2. `home.html` — confirm and reinforce

- Leadership emphasis block ([L900](../templates/home.html#L900)) already says *"the scientist-leader archetype is becoming increasingly necessary."* **No change needed; this becomes the canonical anchor.**
- Consider linking the term on first appearance to a future glossary or about page (deferred — not in this ticket).

### 3. `.pdsl-thesis` line in `home.html` — leave unchanged

The mission statement *"Leaders who can interpret signals — from spacecraft, markets, or systems — will define the next era"* is the **operational definition** of the archetype, not a label for it. Keep both: the label says *who*, the thesis says *what they do*.

### 4. Future-writing rule (add to repo memory)

Add one line to the *"Portal Identity"* memory section:

> **Canonical name:** *"the scientist-leader archetype"*. Use exactly this phrasing in any new page copy, footer, or ticket. Variations ("new archetype of leader", "scientist-leader", "technology-leader archetype") are aliases for searchability, not labels.

---

## Implementation Plan

### Step 1 — Update repo memory

Two str_replace operations on `/memories/repo/deep-space-portal.md`. Pure naming alignment; no content changes.

### Step 2 — Audit other templates

Quick `grep_search` for the three variant phrases across `templates/` and `docs/`. If any other surface uses an alias, align it (most likely there are none today — but cheap to verify).

### Step 3 — No tests needed

This is a documentation/memory naming pass. The signature-phrase test added in the leadership-tightening ticket already includes `"scientist-leader"` as a must-preserve token.

---

## Out of Scope (Explicitly)

- **Defining the archetype in prose.** That work lives on `/voyager-story` and the leadership-philosophy section. Not opening that here.
- **A glossary or about page.** Maybe later. Don't boil the ocean.
- **Renaming anything in code** (class names, route names). The archetype is a narrative concept, not a code symbol. No file renames.

---

## Acceptance Criteria

- [ ] Repo memory uses **"scientist-leader archetype"** as the primary label in both the Portal Identity and Density-review sections.
- [ ] The two alias phrases ("new archetype of leader", "new archetype of technology leader") survive only as parenthetical/quoted sources, never as the operative label.
- [ ] A short "Canonical name" rule is written into repo memory so future tickets adopt the label automatically.
- [ ] `home.html` is unchanged (the existing usage is already canonical).
- [ ] No other surface in `templates/` or `docs/` uses an alias as a primary label (verified by grep).

---

## Effort

Trivial. ~5 minutes of writing, ~2 minutes of grep.
