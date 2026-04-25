# Live Orbit 3D — Visual Storytelling for Earth's Orbital Environment

## Summary

Build a new `/live-orbit` page that brings together — in one stunning, animated 3D visualization — the data already powering `/space-intelligence` and `/orbital-density`. A rotating Earth, live satellite positions, asteroid flyby trajectories, and a thin AI interpretation layer that turns numbers into narrative.

This is Phase 3 of the Real-Time Space Intelligence capability. It is **additive**, not a replacement: `/space-intelligence` remains the data dashboard, `/orbital-density` remains the analytical view, and `/live-orbit` becomes the **immersive experience layer** that ties them together.

**Reference:** `voyager1_project/requirements/real-time-space-intelligence.md` §6

---

## Intent (My North Star)

Three principles that should govern every decision on this page:

1. **Don't replicate — recontextualize.** NASA, ESA, and Stuff.in.Space already render satellites in 3D. We're not competing on tracking accuracy or completeness. We're competing on *perspective* — bringing data points together in a way no single agency does, with first-person interpretation no agency can offer.
2. **Be respectful of the giants.** Every visualization credits its source. The page should feel like an enthusiast standing on the shoulders of NASA, NOAA, US Space Command, and CelesTrak — not a clone competing with them.
3. **Tell a story.** A user should arrive, see something beautiful in motion, and feel pulled into a narrative — not a settings panel. Stunning visuals first; depth on demand.

---

## Architecture

| Component | Implementation |
|-----------|---------------|
| **Page route** | `GET /live-orbit` → renders `live-orbit.html` |
| **3D engine** | Three.js (r160+) via CDN with SRI hash |
| **Earth model** | Sphere + NASA Blue Marble texture (CC0) + cloud layer + atmospheric glow shader |
| **Satellite positions** | Reuse `/api/orbital-density` data; propagate TLEs client-side with `satellite.js` |
| **NEO trajectories** | Reuse `/api/space-intelligence` NEO data; render flyby arcs |
| **Live updates** | **Pragmatic approach** — client-side TLE propagation (no WebSocket required for animation); server polls every 60s via fetch |
| **AI interpretation** | Server-side cached "scene narrator" — periodic LLM summary of current state, returned as static text on page load (no per-request LLM cost) |
| **Caching / cost** | All upstream data already cached in `_si_cached_get` (15-min TTL). AI summary cached 60 min. |
| **Template** | Self-contained HTML/CSS/JS, dark mission control theme, responsive |

### Why Not Full WebSocket?

The original Phase 3 spec called for WebSockets. Re-evaluating:

- **TLE propagation is deterministic.** Given a TLE set, every satellite's position at time `t` is fully determined by orbital mechanics (SGP4). The browser can compute positions itself with `satellite.js` — no server push needed.
- **TLE updates are slow.** CelesTrak refreshes TLEs once every few hours, not per-second. A 60-second client-side fetch is more than sufficient.
- **WebSockets add operational complexity.** Gunicorn workers, sticky sessions, connection limits, reconnect logic — all for a feature the user can't perceive. We can revisit if we add genuinely event-driven data (e.g., live solar flare alerts).

**Decision:** Skip WebSockets for v1. Use 60-second `fetch` polling. Document the tradeoff. Re-evaluate when there's a specific event-stream use case.

### Why Not Per-Request LLM?

The original Phase 3 spec called for "Explain this" buttons that hit an LLM per click. Re-evaluating:

- **Cost.** Per-click LLM calls scale with traffic. Even at low traffic, this becomes a runaway risk.
- **Latency.** A user waiting 2–5 seconds for a "what changed" answer breaks the immersive feel.
- **Quality.** Most "explain this" requests on this page have a small set of recurring answers (most-crowded altitude, biggest operator, closest NEO, recent solar event).

**Decision:** Generate a small set of "scene narratives" server-side, cached for 60 minutes, refreshed by a background routine. Inject as static text. If the user wants deeper, they're one click from `/space-intelligence` or `/orbital-density`.

We can revisit per-request LLM in a Phase 4 if the static narrative proves insufficient.

---

## Page Composition (User Journey)

```
┌────────────────────────────────────────────────────────────────┐
│  Header + nav (consistent with rest of site)                   │
├────────────────────────────────────────────────────────────────┤
│  My Perspectives                                               │
│  (why this page exists; the "stand on shoulders" framing)      │
├────────────────────────────────────────────────────────────────┤
│  How to Read This Page (collapsible)                           │
│    - What you're looking at                                    │
│    - What the dots mean (LEO/MEO/GEO color coding)             │
│    - What the arcs mean (NEO flybys)                           │
│    - How the AI narrator works                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│         ╔═══════════════════════════════════════╗              │
│         ║                                       ║              │
│         ║       [ 3D EARTH + ORBITS ]           ║              │
│         ║       rotating, animated              ║              │
│         ║       drag to rotate, scroll to zoom  ║              │
│         ║                                       ║              │
│         ╚═══════════════════════════════════════╝              │
│                                                                │
│  Floating overlay (top-left): scene narrator                   │
│    "11,314 satellites in LEO right now. Starlink dominates     │
│     the 540 km band. One PHA flyby tomorrow at 0.04 AU."       │
│                                                                │
│  Bottom HUD: layer toggles                                     │
│    [ Satellites: ON ] [ NEO Arcs: ON ] [ Day/Night: AUTO ]     │
├────────────────────────────────────────────────────────────────┤
│  "What you're seeing" cards (3-up grid)                        │
│    - Satellites in view (count, breakdown)                     │
│    - Closest NEO this week                                     │
│    - Current Kp index + space weather state                    │
├────────────────────────────────────────────────────────────────┤
│  Story panel: "The View From Here" (perspective layer)         │
│    - Connect 3D scene to systems thinking                      │
│    - Don't force the message                                   │
├────────────────────────────────────────────────────────────────┤
│  Data Sources & Credits (NASA, ESA, USSC, CelesTrak, NOAA)     │
│  Journey Nav: ← Orbital Density | 3I/ATLAS →                   │
└────────────────────────────────────────────────────────────────┘
```

---

## Visual & Interaction Design

### Stunning, Not Busy

- **Slow rotation by default.** Earth rotates at ~1 full turn / 60s. Satellites animate at real orbital speed (so LEO is visibly faster than GEO). Premium feel — not a screensaver.
- **Atmospheric glow.** Soft blue rim light around Earth using a custom fragment shader. This is the single most "wow" detail and costs almost nothing.
- **Day/night terminator.** Earth texture switches between day and night maps based on real Sun position (computed from current UTC). The terminator line is a genuine, subtle "this is *now*" cue.
- **Star field.** Distant skybox of real-magnitude stars (Hipparcos catalog subset). Adds depth without distraction.
- **Color language (consistent with rest of site):**
  - LEO satellites: teal `#4ecdc4` (small, fast, dense)
  - MEO satellites: gold `#ffd700` (medium, slower)
  - GEO satellites: red `#ff6b6b` (sparse, stationary)
  - NEO trajectories: white arcs with motion (drawn over a 7-day window)
  - PHAs (potentially hazardous): pulsing red ring marker

### Interaction

- **Drag to rotate** the camera around Earth.
- **Scroll to zoom** (clamped — can't zoom into Earth surface; can't zoom past GEO).
- **Click a satellite dot:** small popover with name, operator, altitude. (Bonus — not v1 hard requirement.)
- **Layer toggles:** Satellites / NEO arcs / Atmospheric glow.
- **Reduced-motion respect:** if `prefers-reduced-motion: reduce`, freeze rotation, skip pulse animations, keep the scene navigable.

### Performance Budget

- Target 60 FPS on a 2020 mid-range laptop (Intel UHD 630 or M1 baseline).
- **Hard cap: 5,000 satellite points rendered.** Above that, downsample (e.g., show every 2nd Starlink). 12,000 points kills frame rate on integrated GPUs.
- Use `THREE.Points` with a single `BufferGeometry` and shader-based coloring — no per-satellite mesh.
- TLE propagation runs in a Web Worker so the main thread stays responsive.
- Initial scene load < 3 s on broadband; lazy-load NEO arcs and AI narrator after Earth is interactive.

---

## "Scene Narrator" — The AI Layer (Pragmatic)

A small server-side function generates 3–5 short sentences describing the current orbital state, using existing cached data:

```
Inputs (already cached):
  - orbital_density.summary (total active, LEO/MEO/GEO counts, top operator)
  - space_intelligence.neo (closest approach, hazard count)
  - space_intelligence.weather (Kp index, recent flares)

Output (1-paragraph, ≤ 80 words):
  "Right now, 12,094 active satellites circle Earth — most in LEO,
   dominated by Starlink at 540 km. One asteroid passes inside the
   lunar orbit tomorrow. Geomagnetic conditions are quiet (Kp 2).
   The orbital environment is busy but stable. Watch the 540 km
   band — that's where the future is being written."
```

### Implementation Options (Pick One)

**Option A — Templated narrator (no LLM).** Pure Python: a function that consumes the cached structured data and assembles a paragraph from a small library of phrase templates. Free, deterministic, zero new dependencies, zero new failure modes.

**Option B — LLM-generated, cached.** Background thread (or simple `if cache_age > 60min` check inside the route) calls an LLM with the cached structured data + a system prompt encoding the perspective voice. Result cached for 60 min.
- New dependency: `openai` or equivalent.
- New secret: API key in EC2 systemd environment.
- Cost: ~$0.01–0.03/hour at GPT-4o mini pricing if always refreshed (negligible).
- New failure mode: LLM API outage. Fallback to Option A's templated text.

**Recommendation:** Ship Option A in v1 — it's faster to build, free, and gets us 80% of the value. Add Option B as a Phase 3.5 enhancement once the rest of the page is proven.

---

## Acceptance Criteria

### Page & Visuals
- [ ] `/live-orbit` route returns 200
- [ ] 3D Earth rendered with day/night texture, cloud layer, atmospheric glow
- [ ] Earth rotates at ~1 turn / 60s (configurable)
- [ ] Real Sun position drives the day/night terminator
- [ ] Star field skybox in background
- [ ] Camera supports drag-rotate and scroll-zoom; zoom is clamped
- [ ] LEO/MEO/GEO satellites rendered as colored points at correct altitudes
- [ ] NEO flyby arcs drawn for next 7 days
- [ ] Layer toggles work (satellites / NEO arcs)
- [ ] `prefers-reduced-motion: reduce` is respected (no rotation, no pulse)
- [ ] Page maintains 60 FPS at default zoom on a 2020 mid-range laptop

### Data & Performance
- [ ] Satellite positions propagated client-side via `satellite.js` SGP4
- [ ] Propagation runs in a Web Worker (main thread stays interactive)
- [ ] No more than 5,000 points rendered; gracefully downsamples Starlink if needed
- [ ] Initial Earth visible < 3s on broadband
- [ ] No per-request LLM call; AI narrator generated server-side, cached ≥ 60 min

### Content & Site Integration
- [ ] "How to Read This Page" collapsible section
- [ ] "My Perspectives" section above How to Read (consistent with `/orbital-density`)
- [ ] "What You're Seeing" 3-card summary (satellites / NEO / space weather)
- [ ] "The View From Here" perspective panel (light touch — don't force)
- [ ] Data sources credited inline and in footer (NASA, ESA, USSC, CelesTrak, NOAA)
- [ ] Journey navigation: ← `/orbital-density` | `/atlas` →
- [ ] Added to navbar dropdown ("Space Intelligence" group, third item)
- [ ] Added to `/ai-index`
- [ ] Added to home page CTA dropdown
- [ ] Meta tags, Open Graph, JSON-LD present
- [ ] Responsive layout (mobile: smaller scene, simplified HUD)

### Security
- [ ] Three.js, satellite.js loaded via CDN with SRI integrity hashes
- [ ] All dynamic API data escaped before DOM insertion
- [ ] No user-controlled input feeds upstream URLs
- [ ] Rate limiting on `/api/live-orbit-narrative` (10/min)
- [ ] CSP allows only required CDN origins (jsdelivr, unpkg)
- [ ] Texture assets served from same origin or CC0 NASA URLs (no untrusted CDNs)

---

## Security Hardening

| Threat | Vector | Mitigation |
|--------|--------|------------|
| **Supply chain (3D libs)** | Compromised Three.js / satellite.js CDN | SRI integrity hash + `crossorigin="anonymous"` |
| **XSS via narrator text** | If Option B (LLM) is used and prompt-injected | Strip HTML on server side; treat narrator as plain text only; never `innerHTML` |
| **Texture exfiltration / replacement** | Untrusted texture URL | Self-host textures or use NASA CC0 URLs only; verify content-type |
| **DoS via expensive narrator** | Repeated calls to LLM endpoint | Rate limit `@limiter.limit('10/minute')`; cache 60 min server-side |
| **CPU DoS via TLE flood** | Browser propagating 100k+ TLEs | Hard cap 5,000 points; downsample server-side before sending |
| **Information disclosure (LLM)** | LLM error messages leak prompt or key | Generic 503 on failure; never echo upstream error to client |

### Threat Model Update
Update `docs/security-threat-model.md` §13 to add:
- New page route `/live-orbit`
- New API endpoint `/api/live-orbit-narrative` (if implemented)
- New external dependencies: Three.js, satellite.js (both via CDN with SRI)
- (If Option B) New external dependency: LLM API; new secret: `LLM_API_KEY` env var

---

## My Perspectives — Draft Voice

Two paragraphs to seed the page's perspective layer. To be polished during build, not before.

> **Why this page exists.** NASA, ESA, US Space Command, CelesTrak — these are the giants. They have decades of instruments, deep-space networks, and authority I will never have. What I can do is bring their data into one frame, render it the way an engineer sees a system at runtime, and pair it with one perspective they can't offer: mine. This page isn't trying to compete. It's trying to make the orbital environment feel real to someone who's never thought about it.

> **The view from here.** When I watch this scene rotate, I see the same thing I see on a healthy production system at 3 AM: small things moving in coordinated patterns, on top of infrastructure that just works, until it doesn't. Most of these satellites will never make news. Most of our incidents never make news either. The art is keeping it that way — through observation, discipline, and the quiet decision to act before you have to.

---

## Data Sources

| Source | Provider | URL | Auth | Notes |
|--------|----------|-----|------|-------|
| Earth Day texture | NASA Visible Earth | https://visibleearth.nasa.gov/ | None | CC0; self-host one resized copy |
| Earth Night texture | NASA Visible Earth (Black Marble) | https://earthobservatory.nasa.gov/features/NightLights | None | CC0; self-host |
| Cloud texture | NASA Visible Earth | https://visibleearth.nasa.gov/ | None | CC0; self-host |
| Star catalog | Hipparcos via public mirrors | — | None | Pre-bake top 10k stars as JSON, ship with app |
| Satellite TLEs | (already integrated) | CelesTrak GP API | None | Reuse `/api/orbital-density` |
| NEO trajectories | (already integrated) | NASA NeoWs | API key | Reuse `/api/space-intelligence` |
| Space weather | (already integrated) | NOAA SWPC + NASA DONKI | None / key | Reuse `/api/space-intelligence` |
| Three.js | jsdelivr | `cdn.jsdelivr.net/npm/three@0.160.0/` | None | SRI required |
| satellite.js | jsdelivr | `cdn.jsdelivr.net/npm/satellite.js@5.0.0/` | None | SRI required |

**Citation on page (footer):**
> 3D Earth textures: NASA Visible Earth (CC0). Satellite catalog: CelesTrak / US Space Command 18th Space Defense Squadron. Near-Earth Objects: NASA CNEOS / JPL. Space weather: NOAA SWPC and NASA DONKI. Stars: Hipparcos catalog (ESA). Visualization libraries: Three.js, satellite.js. This page is an enthusiast's interpretation; primary authority remains with the cited agencies.

---

## SEO

### Meta Tags
```html
<title>Live Orbit 3D — Real-Time Earth, Satellites & Asteroid Flybys | Prabhu's Deep Space Labs</title>
<meta name="description" content="Live 3D visualization of Earth, every active satellite, and incoming asteroids. Built on NASA, NOAA, and US Space Command public data — with one engineer's perspective on how to see the system.">
<meta name="keywords" content="live satellite map 3D, real-time earth orbit, asteroid flyby visualization, satellites in orbit now, three.js earth, Prabhu Sadasivam">
```

### Target Queries
| Query | How This Page Ranks |
|-------|---------------------|
| "live satellite map 3d" | Interactive 3D Earth + ~5,000 active satellites |
| "real-time earth orbit visualization" | Animated, time-accurate, drag-to-rotate |
| "asteroid flybys this week" | NEO arcs over Earth + closest-approach summary |
| "what's in orbit right now" | Live count, breakdown, dominant operators |
| "Prabhu Sadasivam space" | Author authority + perspective layer |

---

## Phased Build Plan (Suggested Sprints)

To keep momentum and risk small, build in slices that each deliver something visible:

### Slice 1 — Static Beautiful Earth (2–3 sessions)
- New route `/live-orbit`, new template, navbar integration, journey nav stubs
- Three.js scene with rotating textured Earth, cloud layer, atmospheric glow shader, star field
- "How to Read" + "My Perspectives" + footer credits
- **Outcome:** Page exists, looks stunning, no dynamic data yet. Already a win.

### Slice 2 — Satellites Layer (2–3 sessions)
- Web Worker propagating TLEs from `/api/orbital-density`
- 5,000-point shader-based rendering with LEO/MEO/GEO color coding
- Layer toggle for satellites
- **Outcome:** Live, animated satellite cloud over Earth.

### Slice 3 — NEO Arcs + "What You're Seeing" Cards (1–2 sessions)
- Pull NEO data from `/api/space-intelligence`, render approach arcs
- 3-card summary panel below the scene
- **Outcome:** All three data streams visible in one frame.

### Slice 4 — Scene Narrator (1 session)
- Server-side templated narrator (Option A)
- Floating overlay on the scene
- **Outcome:** Page now *speaks* — turns numbers into narrative.

### Slice 5 — Polish & Perf (1 session)
- Reduced-motion handling
- Mobile layout pass
- Performance profiling, downsampling tuning
- SRI hashes verified, security review
- **Outcome:** Production-ready.

### Slice 6 (Optional) — LLM Narrator (Phase 3.5)
- Replace templated narrator with cached LLM output
- Add `LLM_API_KEY` to EC2 environment
- Update threat model
- **Outcome:** Narrator gets a richer voice.

---

## Not In Scope (Deferred)

- WebSocket live push (re-evaluate when there's a true event-stream use case)
- Per-click "explain this" LLM (cost + latency + complexity not justified yet)
- Click-to-inspect satellite popovers (nice-to-have for Phase 4)
- Time scrubber ("show orbits 2 hours ago") — interesting, deferred
- VR / WebXR — fun, deferred
- Full debris cloud rendering (requires Space-Track auth; cataloged ~30k debris adds complexity)

---

## Definition of Done

- All Acceptance Criteria checked
- Threat model updated, security review notes recorded
- Local smoke test passes on Chrome, Firefox, Safari
- 60 FPS sustained at default zoom on baseline hardware
- Deployed to EC2 and verified at `https://prabhusadasivam.com/live-orbit`
- Journey navigation works in both directions
- All credits visible and accurate

---

## One Last Note

The temptation here will be to over-build. To make every satellite clickable, every orbit selectable, every metric configurable. Resist it. The page wins by being one beautiful, calm, true picture of the system — not a control panel. If a feature doesn't make the scene more *legible* or more *moving*, it doesn't belong in v1.
