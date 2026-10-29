"""Tests for the /andromeda Deep Research page."""

import re
from pathlib import Path

import pytest

from app import app

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_andromeda_page_renders_reproduced_numbers(client):
    resp = client.get("/andromeda")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    for expected in ("52.3%", "90.1%", "Gaia Data Release 4", "/images/andromeda_futures.png",
                     "/images/andromeda_futures_large.png", "not a figure taken from either paper",
                     "HOW TO READ THIS EQUATION"):
        assert expected in html


@pytest.mark.parametrize("name", ["andromeda_futures.png", "andromeda_futures_large.png"])
def test_andromeda_figure_is_served(client, name):
    resp = client.get(f"/images/{name}")
    assert resp.status_code == 200
    assert resp.mimetype == "image/png"


def test_andromeda_in_sitemap(client):
    assert "https://prabhusadasivam.com/andromeda" in client.get("/sitemap.xml").get_data(as_text=True)


@pytest.mark.parametrize("template", sorted(p.name for p in TEMPLATES.glob("*.html")
                                            if 'href="/mars">Mars (1993)' in p.read_text(encoding="utf-8")
                                            or 'href="/mars" class="active">Mars (1993)' in p.read_text(encoding="utf-8")))
def test_every_deep_research_menu_lists_andromeda(template):
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    mars_links = len(re.findall(r'href="/mars"[^>]*>Mars \(1993\)', text))
    assert len(re.findall(r'href="/andromeda"', text)) >= mars_links
