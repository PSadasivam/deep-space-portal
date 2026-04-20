# Architectural Refactor: Build Web Portal Project; Voyager 1 Project for Science-only 

## Summary

Extract the web UI, deployment infrastructure, and presentation layer from `voyager1_project` into a new standalone project `deep_space_portal`. This enforces separation of concerns: Voyager 1 handles pure scientific analysis; the portal handles presentation and serving for all research projects.

---

## Motivation

The `voyager1_project` currently mixes two distinct responsibilities:

1. **Scientific analysis** — trajectory computation, plasma wave processing, magnetometer data, electron density extraction  
2. **Web presentation** — Flask app, 12 HTML templates, nginx config, AWS deployment, favicon generation, sitemap, SEO

This coupling creates several problems:

- Flask/Gunicorn/Pillow dependencies are pulled into an environment that should only need scipy/astropy
- The web app serves pages for **other projects** (3I/ATLAS, black hole, Mars) — it's a platform portal, not a Voyager-specific UI
- Adding a new research page requires touching the science project's repository
- Science modules cannot be imported cleanly into notebooks or CLI without web dependencies

---

## Scope of Change

### New Project: `deep_space_portal/`

| Item | Source | Destination |
|------|--------|-------------|
| `voyager1_web_app.py` | `voyager1_project/` | `deep_space_portal/app.py` |
| `templates/` (12 files) | `voyager1_project/templates/` | `deep_space_portal/templates/` |
| `voyager1.nginx.conf` | `voyager1_project/` | `deep_space_portal/deep_space_portal.nginx.conf` |
| `Images/` | `voyager1_project/Images/` | `deep_space_portal/Images/` |
| `docs/aws-deployment.md` | `voyager1_project/docs/` | `deep_space_portal/docs/` |
| `docs/aws-deployment-ticket.md` | `voyager1_project/docs/` | `deep_space_portal/docs/` |
| `docs/storytelling-perspective-ticket.md` | `voyager1_project/docs/` | `deep_space_portal/docs/` |
| `requirements.txt` (web deps) | New | `deep_space_portal/requirements.txt` |

### Modified: `voyager1_project/`

| Change | Detail |
|--------|--------|
| Removed `voyager1_web_app.py` | Web app moved to portal |
| Removed `templates/` | All 12 HTML templates moved to portal |
| Removed `voyager1.nginx.conf` | Nginx config moved to portal |
| Removed deployment docs | AWS docs moved to portal |
| Updated `requirements.txt` | Removed `flask`, `gunicorn`, `Pillow` — science-only deps remain |

### Modified: `deep_space_db/docs/software-architecture.md`

- Platform overview updated from 4 projects to 5
- Architecture diagram shows portal as presentation layer above science modules
- Integration section documents `sys.path` import mechanism
- Repository map includes `deep-space-portal`
- Key configuration files reference portal locations
- Process lifecycle references `deep_space_portal.service`

### Modified: `deep_space_portal/templates/architecture.html`

- Same updates as software-architecture.md (HTML version)
- Footer links include portal repository
- Repository map table includes portal entry

### Modified: `Prabhus-Deep-Space-Labs.code-workspace`

- Added `../deep_space_portal` as a workspace folder

### No Change Required

- `templates/ai-index.html` — references URL routes only, no project structure
- Sitemap (generated dynamically in `app.py`) — routes unchanged
- All science modules in `voyager1_project/` — untouched

---

## Architecture After

```
C:\Deep-Space-Research\
├── deep_space_portal/          ← NEW: Web presentation layer
│   ├── app.py                  (Flask app, imports science modules)
│   ├── templates/              (12 HTML templates)
│   ├── Images/                 (static assets)
│   ├── deep_space_portal.nginx.conf
│   ├── requirements.txt        (flask, gunicorn, pillow + science)
│   └── docs/                   (deployment & feature docs)
│
├── voyager1_project/           ← SLIMMED: Pure science
│   ├── voyager1_outbound_trajectory.py
│   ├── voyager1_plasma_wave_analysis.py
│   ├── voyager1_density_extraction.py
│   ├── voyager1_magneticfield_nTS_analysis.py
│   ├── verify_voyager_position.py
│   ├── requirements.txt        (astropy, scipy, numpy — no flask)
│   └── tests/
│
├── 3I-Atlas-Research/          (unchanged)
├── universe-inside-blackhole/  (unchanged)
└── deep_space_db/              (docs updated)
```

---

## Integration Mechanism

The portal imports Voyager 1 science modules via `sys.path`:

```python
_VOYAGER1_PROJECT = Path(__file__).resolve().parent.parent / 'voyager1_project'
if str(_VOYAGER1_PROJECT) not in sys.path:
    sys.path.insert(0, str(_VOYAGER1_PROJECT))
```

This avoids packaging overhead while maintaining clean separation. The science modules have no awareness of the portal.

---

## Acceptance Criteria

- [ ] `python app.py` starts successfully from `deep_space_portal/`
- [ ] All 12 pages render correctly at their existing URL routes
- [ ] All 7 API endpoints return valid JSON responses
- [ ] Sitemap and robots.txt serve correctly
- [ ] Science modules in `voyager1_project/` can be imported independently (no Flask dependency)
- [ ] `pip install -r requirements.txt` in `voyager1_project/` does NOT install Flask/Gunicorn
- [ ] Architecture docs (MD + HTML) reflect 5-project structure
- [ ] Workspace file includes all 5 project folders
- [ ] EC2 deployment is updated to pull from portal repository

---

## Deployment Impact

- **EC2 `git pull` target** changes from `voyager1-analysis` to `deep-space-portal`
- **systemd service** WorkingDirectory changes to portal path
- **Gunicorn** invocation changes: `gunicorn app:app` (from `gunicorn voyager1_web_app:app`)
- **Nginx** config filename may change (or be symlinked)
- **Voyager 1 project** must be cloned as sibling directory on EC2 for imports

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Import path breaks on EC2 | Verify sibling directory layout matches local; add startup check |
| Old `voyager1_web_app.py` still deployed | Remove from EC2 after portal deploy confirmed |
| Git history lost for moved files | Files are copied (not `git mv` across repos); history preserved in original repo |
| Feature flags still reference old project | `requirements/` folder remains in voyager1_project for science feature tickets |

---

## Follow-Up Tasks

- [x] Initialize `deep_space_portal` as its own Git repository
- [x] Create GitHub repo `PSadasivam/deep-space-portal`
- [x] Update EC2 deployment script for new project layout (`deploy_portal.sh`)
- [x] Update systemd service file (`deep_space_portal.service` in deploy script)
- [ ] Consider `pip install -e ../voyager1_project` for more robust imports
- [x] Add `getting-started.md` to portal docs
- [x] Add portal-specific README.md
