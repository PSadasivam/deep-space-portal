#!/usr/bin/env bash
# deploy_portal.sh — Migrate EC2 from voyager1-analysis to deep-space-portal
#
# Run on EC2 as ec2-user:
#   chmod +x deploy_portal.sh && ./deploy_portal.sh
#
# This script:
#   1. Clones the new deep-space-portal repo
#   2. Sets up a Python venv and installs dependencies
#   3. Creates the new systemd service (deep_space_portal.service)
#   4. Swaps the Nginx config
#   5. Stops the old voyager1 service
#   6. Starts the new portal service
#   7. Updates the voyager1-analysis repo (now science-only)
#
# Prerequisites:
#   - voyager1-analysis is already cloned at /home/ec2-user/voyager1-analysis
#   - Nginx and Certbot are already configured
#   - Run as ec2-user (sudo is used where needed)
#
# ref PSadasivam/deep-space-portal#1

set -euo pipefail

DEPLOY_DIR="/home/ec2-user"
PORTAL_DIR="${DEPLOY_DIR}/deep-space-portal"
VOYAGER_DIR="${DEPLOY_DIR}/voyager1-analysis"
VENV_DIR="${PORTAL_DIR}/venv"
SERVICE_NAME="deep_space_portal"
OLD_SERVICE_NAME="voyager1"

echo "=== Deep Space Portal Deployment ==="
echo "Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# -------------------------------------------------------------------
# Step 1: Clone the portal repo
# -------------------------------------------------------------------
if [ -d "${PORTAL_DIR}" ]; then
    echo "[1/7] Portal directory exists — pulling latest..."
    cd "${PORTAL_DIR}"
    git pull origin main
else
    echo "[1/7] Cloning deep-space-portal..."
    cd "${DEPLOY_DIR}"
    git clone https://github.com/PSadasivam/deep-space-portal.git
fi

# -------------------------------------------------------------------
# Step 2: Set up Python venv and install dependencies
# -------------------------------------------------------------------
echo "[2/7] Setting up Python virtual environment..."
cd "${PORTAL_DIR}"

if [ ! -d "${VENV_DIR}" ]; then
    python3.11 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install gunicorn --quiet
echo "  Dependencies installed."

# -------------------------------------------------------------------
# Step 3: Verify voyager1-analysis is present (needed for sys.path imports)
# -------------------------------------------------------------------
echo "[3/7] Verifying voyager1-analysis sibling directory..."
if [ ! -d "${VOYAGER_DIR}" ]; then
    echo "  ERROR: ${VOYAGER_DIR} not found. Portal requires it for science module imports."
    exit 1
fi
echo "  Found: ${VOYAGER_DIR}"

# -------------------------------------------------------------------
# Step 4: Create the new systemd service
# -------------------------------------------------------------------
echo "[4/7] Creating systemd service: ${SERVICE_NAME}.service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Deep Space Portal (Gunicorn)
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=${PORTAL_DIR}
ExecStart=${VENV_DIR}/bin/gunicorn \\
  --workers 2 \\
  --bind 127.0.0.1:8000 \\
  app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "  Service file created."

# -------------------------------------------------------------------
# Step 5: Swap Nginx config
# -------------------------------------------------------------------
echo "[5/7] Updating Nginx configuration..."

# Back up existing config
if [ -f /etc/nginx/conf.d/voyager1.conf ]; then
    sudo cp /etc/nginx/conf.d/voyager1.conf /etc/nginx/conf.d/voyager1.conf.bak
fi

# The nginx config proxies to 127.0.0.1:8000 — same port, so the proxy_pass
# doesn't change. We just rename/replace for clarity.
sudo cp "${PORTAL_DIR}/deep_space_portal.nginx.conf" /etc/nginx/conf.d/deep_space_portal.conf

# Test nginx config before proceeding
sudo nginx -t
echo "  Nginx config valid."

# -------------------------------------------------------------------
# Step 6: Stop old service, start new service, reload Nginx
# -------------------------------------------------------------------
echo "[6/7] Switching services..."

# Stop the old service
if sudo systemctl is-active --quiet ${OLD_SERVICE_NAME} 2>/dev/null; then
    sudo systemctl stop ${OLD_SERVICE_NAME}
    sudo systemctl disable ${OLD_SERVICE_NAME}
    echo "  Stopped and disabled: ${OLD_SERVICE_NAME}.service"
fi

# Remove old nginx config (keep backup)
if [ -f /etc/nginx/conf.d/voyager1.conf ]; then
    sudo rm /etc/nginx/conf.d/voyager1.conf
fi

# Start the new service
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}
sudo systemctl reload nginx

echo "  Started: ${SERVICE_NAME}.service"

# Verify
sleep 2
if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
    echo "  Service is running."
else
    echo "  WARNING: Service may not have started correctly."
    sudo systemctl status ${SERVICE_NAME} --no-pager
    exit 1
fi

# Quick health check
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
echo "  Health check: HTTP ${HTTP_CODE}"
if [ "${HTTP_CODE}" != "200" ]; then
    echo "  WARNING: Expected HTTP 200 but got ${HTTP_CODE}"
fi

# -------------------------------------------------------------------
# Step 7: Update voyager1-analysis repo (now science-only)
# -------------------------------------------------------------------
echo "[7/7] Updating voyager1-analysis to science-only..."
cd "${VOYAGER_DIR}"
git pull origin main
echo "  voyager1-analysis updated."

# -------------------------------------------------------------------
# Done
# -------------------------------------------------------------------
echo ""
echo "=== Deployment Complete ==="
echo "Portal running at: https://prabhusadasivam.com"
echo ""
echo "Services:"
echo "  Active:   ${SERVICE_NAME}.service"
echo "  Disabled: ${OLD_SERVICE_NAME}.service"
echo ""
echo "To verify:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  curl -I https://prabhusadasivam.com"
echo ""
echo "To rollback:"
echo "  sudo systemctl stop ${SERVICE_NAME}"
echo "  sudo systemctl start ${OLD_SERVICE_NAME}"
echo "  sudo cp /etc/nginx/conf.d/voyager1.conf.bak /etc/nginx/conf.d/voyager1.conf"
echo "  sudo rm /etc/nginx/conf.d/deep_space_portal.conf"
echo "  sudo systemctl reload nginx"
