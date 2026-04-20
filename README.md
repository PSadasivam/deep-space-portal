# Deep Space Portal

Public web portal for the Deep Space Research platform. Serves Voyager 1 analysis, 3I/ATLAS research, black hole cosmology, and real-time space intelligence at [prabhusadasivam.com](https://prabhusadasivam.com).

## Architecture

```
deep_space_portal/
├── app.py                          Flask application (12 routes, 7 API endpoints)
├── templates/                      Jinja2 HTML templates
├── Images/                         Static assets
├── deep_space_portal.nginx.conf    Nginx reverse proxy config
├── deploy_portal.sh                EC2 deployment script
├── requirements.txt                Python dependencies
└── docs/                           Documentation
```

The portal imports science modules from the sibling [voyager1-analysis](https://github.com/PSadasivam/voyager1-analysis) project via `sys.path`. Science code has no awareness of the portal.

## Quick Start

```bash
# Clone both repos into the same parent directory
git clone https://github.com/PSadasivam/deep-space-portal.git
git clone https://github.com/PSadasivam/voyager1-analysis.git

cd deep-space-portal
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000.

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [deep-space-portal](https://github.com/PSadasivam/deep-space-portal) | Web portal (this repo) |
| [voyager1-analysis](https://github.com/PSadasivam/voyager1-analysis) | Voyager 1 science modules |
| [deep-space-db](https://github.com/PSadasivam/deep-space-db) | SQLite analytics database + S3 backup |

## Documentation

- [Getting Started](docs/getting-started.md)
- [AWS Deployment](docs/aws-deployment.md)
- [Portal Separation Ticket](docs/portal-separation-ticket.md)

## License

See individual project repositories for license information.
