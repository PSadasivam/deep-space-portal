# Satellite & Orbital Density Intelligence

## Summary

Build a new `/orbital-density` page delivering real-time satellite and orbital density intelligence using CelesTrak public data. The page visualizes orbital congestion (LEO/MEO/GEO distribution), operator breakdown, altitude density histograms, and a Starlink constellation case study — all with interactive Chart.js charts and the site's established perspective/storytelling layer.

This is Phase 2 of the Real-Time Space Intelligence capability, building on the existing `/space-intelligence` page (Phase 1: NEO Watch + Space Weather).

**Reference:** `voyager1_project/requirements/real-time-space-intelligence.md` §5

---

## Architecture

| Component | Implementation |
|-----------|---------------|
| **Page route** | `GET /orbital-density` → renders `orbital-density.html` |
| **API route** | `GET /api/orbital-density` → JSON (rate-limited 10/min) |
| **Data source** | CelesTrak GP API (`celestrak.org/NORAD/elements/gp.php`) — no auth required |
| **Caching** | Same `_si_cached_get` pattern (in-memory dict, 15-min TTL, stale fallback) |
| **Charting** | Chart.js 4.x via CDN with SRI integrity hash |
| **Template** | Self-contained HTML/CSS/JS, dark mission control theme |

---

## Acceptance Criteria

- [ ] `/orbital-density` route returns 200 with live satellite data
- [ ] Donut chart shows active satellite distribution by orbit class (LEO/MEO/GEO/HEO/Other)
- [ ] Bar chart shows top 10 operators by active satellite count
- [ ] Altitude histogram (100 km bins) highlights congested bands
- [ ] Starlink constellation section with count and orbital shell breakdown
- [ ] "How to Read This Page" collapsible guide explains TLEs, orbit classes, and altitude bands
- [ ] "My Perspective" sections appear where data naturally invites them (congestion, Kessler)
- [ ] Severity color bands on altitude histogram (green=sparse, yellow=moderate, red=congested)
- [ ] Data sources credited inline and in footer (CelesTrak, US Space Command)
- [ ] API responses cached (15-min TTL); page degrades gracefully on API failure
- [ ] Chart.js loaded via CDN with SRI integrity hash
- [ ] All API data escaped before DOM insertion (extend `esc()` pattern)
- [ ] Meta tags, Open Graph, and JSON-LD schema present
- [ ] Journey navigation connects: Space Intelligence ← Orbital Density → 3I/ATLAS
- [ ] Page added to navbar on all templates, `/ai-index`, and site structure
- [ ] Responsive layout works on mobile (charts resize, cards stack)

---

## Security Hardening

### Threat Surface

| Threat | Vector | Mitigation |
|--------|--------|------------|
| **SSRF via CelesTrak URL** | Attacker manipulates upstream URL construction | Hardcoded base URLs only — no user input in URL construction |
| **XSS from upstream API data** | Satellite names or operator fields contain script | `esc()` helper escapes all API data before DOM insertion; `textContent` preferred over `innerHTML` |
| **CDN resource tampering** | Compromised Chart.js CDN | SRI integrity hash + `crossorigin="anonymous"` on `<script>` tag |
| **API abuse / DoS** | Expensive CelesTrak fetch triggered repeatedly | `flask-limiter` 10/min on `/api/orbital-density`; in-memory cache prevents upstream flood |
| **Data injection via JSON response** | Malformed JSON from CelesTrak | Server-side validation: only expected fields extracted; unknown fields discarded |
| **Information disclosure** | Error messages leak internal paths | Generic error response on failure; details logged server-side only |
| **Cache poisoning** | Stale/bad data persists in cache | 15-min TTL auto-expires; stale cache only used as fallback when fresh fetch fails |

### Controls Applied

- [ ] Rate limiting: `@limiter.limit('10/minute')` on API endpoint
- [ ] Input validation: No user-supplied parameters influence CelesTrak URLs
- [ ] Output escaping: `esc()` on all dynamic content inserted into DOM
- [ ] SRI hashes: Chart.js CDN loaded with `integrity` and `crossorigin` attributes
- [ ] Error handling: Generic "data unavailable" on API failure; no stack traces to client
- [ ] HTTPS only: CelesTrak fetched over HTTPS; site served over HTTPS
- [ ] No secrets: CelesTrak requires no API key; no new credentials introduced

### Threat Model Update

Update `docs/security-threat-model.md` §13 to reflect:
- New API endpoint `/api/orbital-density` added to asset inventory
- New external dependency: CelesTrak GP API (HTTPS, no auth)
- Chart.js CDN added as external resource (with SRI)
- New template `orbital-density.html` in template inventory

---

## Tasks

### 1. Backend — CelesTrak Data Helpers
- [ ] Add `_fetch_celestrak_active()` — fetch active satellite catalog from CelesTrak GP API
- [ ] Parse GP JSON: extract `OBJECT_NAME`, `NORAD_CAT_ID`, `MEAN_MOTION`, `ECCENTRICITY`, `INCLINATION`, `PERIOD`, semi-major axis (derived)
- [ ] Classify orbits: LEO (<2000 km), MEO (2000–35586 km), GEO (35586–35986 km), HEO (eccentricity >0.25), Other
- [ ] Aggregate: count by orbit class, by operator (from `OBJECT_NAME` prefix heuristic), by altitude bin (100 km)
- [ ] Detect Starlink subset from `OBJECT_NAME LIKE 'STARLINK%'`
- [ ] Cache with `_si_cached_get` pattern (key: `celestrak_active`, TTL: 900s)

### 2. Backend — API Endpoint
- [ ] Add `/orbital-density` page route
- [ ] Add `/api/orbital-density` JSON endpoint with `@limiter.limit('10/minute')`
- [ ] Return JSON: `orbit_distribution`, `top_operators`, `altitude_histogram`, `starlink_stats`, `total_active`, `refreshed`
- [ ] Graceful degradation: return `{"error": "Data temporarily unavailable"}` on CelesTrak failure

### 3. Frontend — Template
- [ ] Create `templates/orbital-density.html` with dark mission control theme
- [ ] Header + status bar (consistent with space-intelligence.html)
- [ ] "How to Read This Page" collapsible section
- [ ] Opening "My Perspective" (orbital congestion as resource contention)
- [ ] Orbit distribution donut chart (Chart.js)
- [ ] Top operators bar chart (Chart.js)
- [ ] Altitude histogram with congestion color bands (Chart.js)
- [ ] Starlink constellation case study panel
- [ ] Kessler Syndrome perspective (after congestion visualizations)
- [ ] Data sources & credits
- [ ] Journey navigation: ← Space Intelligence | 3I/ATLAS →
- [ ] SEO meta tags, Open Graph, JSON-LD

### 4. Site Integration
- [ ] Add "Orbital Density" to nav bar on all 12 templates
- [ ] Update space-intelligence.html journey nav: "Continue →" points to `/orbital-density`
- [ ] Update atlas.html journey nav (if present): "← Previous" points to `/orbital-density`
- [ ] Add section in `/ai-index`
- [ ] Add to site structure list in ai-index.html

### 5. Security & Threat Model
- [ ] Add SRI hash on Chart.js CDN `<script>` tag
- [ ] Verify `esc()` pattern on all dynamic DOM content
- [ ] Update `docs/security-threat-model.md` §13 with new endpoint, dependency, template
- [ ] Verify rate limiting works locally

### 6. Validation
- [ ] Local smoke test: `/orbital-density` loads with live CelesTrak data
- [ ] API returns valid JSON: `/api/orbital-density`
- [ ] Charts render correctly on desktop and mobile
- [ ] Graceful degradation: disable network → "Data temporarily unavailable"
- [ ] Journey navigation links work both directions
- [ ] All navbar links include new page

---

## Data Sources

| Source | URL | Auth | Update Frequency |
|--------|-----|------|------------------|
| CelesTrak GP API | `https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json` | None | Daily (catalog refreshed by US Space Command) |
| CelesTrak Satcat (future) | `https://celestrak.org/satcat/records.php` | None | Daily |

**Citation on page:**
> Satellite catalog data: CelesTrak (Dr. T.S. Kelso), sourced from US Space Command 18th Space Defense Squadron.
> Orbital elements: NORAD Two-Line Element sets via CelesTrak General Perturbations (GP) API.

---

## SEO

### Meta Tags
```html
<title>Orbital Density Intelligence — Satellite Congestion & LEO Analysis | Prabhu's Deep Space Labs</title>
<meta name="description" content="Live satellite orbital density analysis. LEO congestion heatmaps, Starlink tracking, operator distribution — with expert perspective on orbital sustainability.">
```

### Target Queries
| Query | How This Page Ranks |
|-------|---------------------|
| "how many satellites in orbit" | Live count + orbit class breakdown |
| "LEO congestion" | Altitude histogram with congestion bands |
| "Starlink satellite count" | Dedicated Starlink section with live count |
| "Kessler syndrome" | Perspective section with engineering analogy |
| "orbital debris" | Density visualization + congestion context |

---

## Journey Navigation (Updated Site Flow)

```
Facts → Trajectory → Plasma Waves → Density → Magnetometer → Space Intelligence → Orbital Density → 3I/ATLAS → Black Hole
```

---

## Not In Scope (Deferred to Phase 3)

- 3D globe visualization (Three.js)
- WebSocket real-time updates
- AI interpretation layer
- Space-Track.org or ESA DISCOS integration (requires registration)
- Debris-specific tracking (requires Space-Track auth)
