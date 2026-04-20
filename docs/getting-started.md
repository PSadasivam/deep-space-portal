# Getting Started

This guide walks you through setting up and running the Deep Space Portal locally.

## Prerequisites

- **Python 3.8+** (tested with 3.13)
- **Git** for cloning repositories
- **VS Code** (recommended) — a multi-root workspace file is included

## 1. Clone the Repositories

The portal imports science modules from the sibling `voyager1-analysis` project. Both repositories must be cloned into the same parent directory.

```bash
mkdir Deep-Space-Research && cd Deep-Space-Research

git clone https://github.com/PSadasivam/deep-space-portal.git
git clone https://github.com/PSadasivam/voyager1-analysis.git
```

Your directory layout should look like:

```
Deep-Space-Research/
├── deep-space-portal/      ← this project
└── voyager1-analysis/      ← science modules (sibling)
```

## 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**

```powershell
cd deep-space-portal
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
cd deep-space-portal
python -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

| Package      | Purpose                                       |
|--------------|-----------------------------------------------|
| flask        | Web framework                                 |
| gunicorn     | Production WSGI server                        |
| Pillow       | Image processing (favicon generation)         |
| requests     | HTTP client for NASA APIs                     |
| astropy      | Astronomical calculations and coordinates     |
| astroquery   | NASA JPL HORIZONS ephemeris queries           |
| pandas       | Data manipulation and analysis                |
| numpy        | Numerical computing                           |
| matplotlib   | Plotting and visualization                    |
| cdflib       | NASA CDF file format support                  |
| scipy        | Scientific computing and signal processing    |

## 4. Run the Development Server

```bash
python app.py
```

Open http://localhost:5000 in your browser.

### Available Pages

| Route | Page |
|-------|------|
| `/` | Home |
| `/dashboard` | Mission Dashboard |
| `/trajectory` | Voyager 1 Trajectory |
| `/plasma` | Plasma Wave Analysis |
| `/density` | Electron Density |
| `/facts` | Mission Facts |
| `/atlas` | 3I/ATLAS Research |
| `/blackhole` | Black Hole Cosmology |
| `/mars` | Mars |
| `/space-intelligence` | Real-Time Space Intelligence |
| `/architecture` | Platform Architecture |
| `/ai-index.html` | AI/Search Sitemap |

## 5. Open in VS Code

For a multi-root workspace that includes all Deep Space Research projects:

```
File → Open Workspace from File → Prabhus-Deep-Space-Labs.code-workspace
```

## Production Deployment

See [aws-deployment.md](aws-deployment.md) for EC2 deployment with Nginx, Gunicorn, and HTTPS.
