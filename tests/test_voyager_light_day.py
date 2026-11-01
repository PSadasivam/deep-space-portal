"""Tests for the Voyager 1 one light-day milestone: countdown banner, explainer page, story revision."""

import datetime as dt
import re
from pathlib import Path

import pytest

import app as portal_app
from app import app

BANNER_PAGES = ["/", "/facts", "/voyager-story", "/voyager-light-day"]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("path", BANNER_PAGES)
def test_banner_counts_down_before_the_milestone(client, monkeypatch, path):
    monkeypatch.setattr(portal_app, "ONE_LIGHT_DAY_UTC", dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=3, hours=5))
    html = client.get(path).get_data(as_text=True)
    assert 'id="lightDayBanner"' in html
    assert "Countdown to a milestone" in html
    assert '<span class="ld-num" id="ldD">3</span>' in html
    assert 'href="/voyager-light-day"' in html


@pytest.mark.parametrize("path", BANNER_PAGES)
def test_banner_switches_after_the_milestone(client, monkeypatch, path):
    monkeypatch.setattr(portal_app, "ONE_LIGHT_DAY_UTC", dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1))
    html = client.get(path).get_data(as_text=True)
    assert "Milestone reached" in html
    assert 'id="ldBefore" hidden' in html


def test_banner_targets_nasa_time(client):
    assert 'data-target="2026-11-18T10:16:07Z"' in client.get("/facts").get_data(as_text=True)


def test_light_day_page_states_checked_findings(client):
    resp = client.get("/voyager-light-day")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    for expected in ("25,902,068,356 km", "10:16:07 UTC", "4 February 2027", "24 April 2027",
                     "1.4 minutes", "02:18 UTC on 19 November", "/images/voyager1_light_day.png"):
        assert expected in html


@pytest.mark.parametrize("name", ["voyager1_light_day.png", "voyager1_light_day_large.png"])
def test_light_day_figure_is_served(client, name):
    resp = client.get(f"/images/{name}")
    assert resp.status_code == 200 and resp.mimetype == "image/png"


def test_light_day_page_in_sitemap(client):
    assert "https://prabhusadasivam.com/voyager-light-day</loc>" in client.get("/sitemap.xml").get_data(as_text=True)


def test_story_revision_three_and_history(client):
    html = client.get("/voyager-story").get_data(as_text=True)
    for expected in ('id="revisions"', "Revision 3 &mdash; 1 November 2026", "Revision 2 &mdash; 11 May 2026",
                     "Revision 1 &mdash; 11 May 2026", "Big Bang", "October 18 and 19", "1.7 light-years",
                     "A faint ring system", 'href="/voyager-light-day"'):
        assert expected in html
    assert "Four faint rings" not in html
    assert "a 48-year mission" not in html


def test_light_time_uses_earth_distance_on_milestone_day():
    stats = portal_app._voyager1_live_stats(dt.date(2026, 11, 18))
    assert stats["light_time_one_way_hours"] == 24.0


TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


@pytest.mark.parametrize("template", sorted(p.name for p in TEMPLATES.glob("*.html")
                                            if '>The Voyager Story</a>' in p.read_text(encoding="utf-8")))
def test_every_voyager_menu_lists_light_day(template):
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    menus = len(re.findall(r'<a href="/voyager-story"(?: class="active")?>The Voyager Story</a>\s*\n\s*<a href="/voyager-light-day"', text))
    story_links = len(re.findall(r'\n\s*<a href="/voyager-story"(?: class="active")?>The Voyager Story</a>\s*\n\s*(?:<a|</div>)', text))
    assert menus == story_links
