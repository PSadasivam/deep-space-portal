"""Tests for the dynamic /facts page.

Covers:
  * voyager1_position_model.voyager1_distance_au — shared synthetic model
  * _voyager1_live_stats — derived storytelling values
  * /facts route — renders, contains dynamic values, no stale strings

See docs/facts-dynamic-ticket.md for the validation-cadence rationale.
"""
import datetime
import re

import pytest

from app import (
    _voyager1_live_stats,
    _voyager1_live_stats_cached,
    app,
)
from voyager1_position_model import (
    HELIOPAUSE_AU,
    HELIOPAUSE_DATE,
    RATE_AU_PER_YR,
    VOYAGER1_LAUNCH,
    voyager1_distance_au,
)


# ---------------------------------------------------------------------------
# voyager1_distance_au — bound check (ADR validation-cadence layer 1)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("year", [2025, 2026, 2030, 2035])
def test_distance_within_sanity_envelope(year):
    """Sanity envelope: any date 2025-2035 should yield 150 <= AU <= 250.

    Catches code regressions (e.g. someone flips a sign on the rate).
    """
    d = voyager1_distance_au(datetime.date(year, 6, 15))
    assert 150.0 <= d <= 250.0, f"Distance {d} AU at {year} outside sanity envelope"


def test_distance_at_heliopause_anchor():
    """At the anchor date, distance equals the anchor value exactly."""
    assert voyager1_distance_au(HELIOPAUSE_DATE) == pytest.approx(HELIOPAUSE_AU)


def test_distance_grows_linearly_with_time():
    """Distance must grow at RATE_AU_PER_YR over a multi-year span."""
    d_start = voyager1_distance_au(datetime.date(2025, 1, 1))
    d_end = voyager1_distance_au(datetime.date(2030, 1, 1))
    delta = d_end - d_start
    expected = RATE_AU_PER_YR * 5.0
    assert delta == pytest.approx(expected, rel=1e-3)


def test_distance_before_anchor_clamps_to_anchor():
    """Dates before heliopause crossing return the anchor (no negative drift)."""
    pre = voyager1_distance_au(datetime.date(2000, 1, 1))
    assert pre == HELIOPAUSE_AU


# ---------------------------------------------------------------------------
# _voyager1_live_stats — derived values
# ---------------------------------------------------------------------------

def test_live_stats_shape_and_types():
    stats = _voyager1_live_stats(datetime.date(2026, 5, 12))
    expected_keys = {
        'distance_au', 'distance_km_billions', 'distance_miles_billions',
        'light_time_one_way_hours', 'light_time_round_trip_hours',
        'mission_age_years', 'as_of_utc',
    }
    assert set(stats.keys()) == expected_keys
    assert isinstance(stats['distance_au'], float)
    assert isinstance(stats['mission_age_years'], int)
    assert isinstance(stats['as_of_utc'], str)


def test_mission_age_matches_launch_date():
    """For a known date, mission age in whole years must match the launch."""
    today = datetime.date(2026, 9, 5)  # Exactly 49 years after launch
    stats = _voyager1_live_stats(today)
    assert stats['mission_age_years'] == 49
    # Day before the anniversary: still 48 whole years
    stats_day_before = _voyager1_live_stats(datetime.date(2026, 9, 4))
    assert stats_day_before['mission_age_years'] == 48


def test_round_trip_is_twice_one_way():
    stats = _voyager1_live_stats(datetime.date(2026, 5, 12))
    # Rounded values may differ by 0.1 due to independent rounding; verify
    # the underlying relationship rather than exact equality.
    assert abs(stats['light_time_round_trip_hours']
               - 2 * stats['light_time_one_way_hours']) <= 0.1


def test_distance_units_internally_consistent():
    """km and miles must be derived from the same AU value."""
    stats = _voyager1_live_stats(datetime.date(2026, 5, 12))
    # miles = km * 0.621371 (allow rounding slack of 0.2 billion)
    derived_miles = stats['distance_km_billions'] * 0.621371
    assert abs(derived_miles - stats['distance_miles_billions']) < 0.2


def test_launch_date_is_canonical():
    """Guard against accidental edit of the launch constant."""
    assert VOYAGER1_LAUNCH == datetime.date(1977, 9, 5)


# ---------------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------------

def test_cached_returns_same_object_for_same_day():
    a = _voyager1_live_stats_cached('2026-05-12')
    b = _voyager1_live_stats_cached('2026-05-12')
    assert a is b


# ---------------------------------------------------------------------------
# /facts route smoke + stale-string guard
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_facts_route_returns_200(client):
    resp = client.get('/facts')
    assert resp.status_code == 200
    assert b'Voyager 1' in resp.data


def test_facts_route_renders_dynamic_distance(client):
    """Page body must contain the computed AU value, not a hard-coded one."""
    resp = client.get('/facts')
    today = datetime.datetime.now(datetime.timezone.utc).date()
    expected_au = round(voyager1_distance_au(today), 1)
    assert f'{expected_au} AU'.encode() in resp.data


def test_facts_route_has_no_stale_refresh_string(client):
    """The hard-coded 'April 2026' staleness must be gone."""
    resp = client.get('/facts')
    assert b'April 2026' not in resp.data
    assert b'Last refreshed' not in resp.data  # replaced with "As of"


def test_facts_route_carries_honesty_footer(client):
    """Per acceptance criteria: footer must disclose the synthetic model."""
    resp = client.get('/facts')
    assert b'calibrated linear model' in resp.data
    assert b'JPL Horizons' in resp.data


# ---------------------------------------------------------------------------
# / (home) — same shared model, no inline JS constants (ADR-002)
# ---------------------------------------------------------------------------

def test_home_route_renders_dynamic_distance(client):
    """Home page must render the same distance as /facts (one model, one number)."""
    today = datetime.datetime.now(datetime.timezone.utc).date()
    expected_km_billions = _voyager1_live_stats(today)['distance_km_billions']
    resp = client.get('/')
    # Render uses &nbsp; between value and 'billion' — match the bare number.
    assert f'{expected_km_billions}'.encode() in resp.data
    assert b'billion kilometers' in resp.data


def test_home_no_inline_voyager_constants(client):
    """Regression guard: the old JS position model must not return."""
    resp = client.get('/')
    assert b'refAU = 163' not in resp.data
    assert b'voyager-distance' not in resp.data
    assert b'auPerYear' not in resp.data


def test_home_voyager_story_card_dynamic_age(client):
    """Voyager Story card must reflect dynamic mission age, not '49-year'."""
    today = datetime.datetime.now(datetime.timezone.utc).date()
    expected_years = _voyager1_live_stats(today)['mission_age_years']
    resp = client.get('/')
    assert f'{expected_years}-year journey'.encode() in resp.data


# ---------------------------------------------------------------------------
# Home — Leadership Philosophy voice integrity (issue #15)
# Editorial pass tightened the section from 13 paragraphs + 3 bullets to 5
# paragraphs. These tests guard the signature phrases Anthropic Claude
# specifically singled out as the strong beats — losing any of them silently
# would re-introduce exactly the dilution the edit was meant to remove.
# ---------------------------------------------------------------------------

def test_home_preserves_signature_phrases(client):
    """Voice regression guard for the leadership section."""
    resp = client.get('/')
    body = resp.data
    must_preserve = [
        b'engineered for a future no one could fully predict',
        b'the how becomes reactive',
        b'compounding investments',
        b'That is who I am',
        b'scientist-leader',
    ]
    for phrase in must_preserve:
        assert phrase in body, f'Signature phrase lost from home leadership section: {phrase!r}'


def test_home_leadership_section_is_tightened(client):
    """The editorial pass removed the old bullet list and the bridge paragraphs.
    If they reappear, the section is drifting back toward 13 paragraphs."""
    resp = client.get('/')
    body = resp.data
    must_be_absent = [
        # Bullet list shape — folded into prose.
        b'It is how one-platform visions are shaped.',
        b'It is how complex portfolios are simplified.',
        # Pure-bridge / setup sentences that were absorbed into stronger paragraphs.
        b'What fascinates me is not just the distance, but the design philosophy behind it.',
        b'That mindset has fundamentally shaped who I am as a technology leader.',
        # The old typo'd setup line ("insights:" plural).
        b'Voyager offers a simple but enduring leadership insights',
    ]
    for phrase in must_be_absent:
        assert phrase not in body, f'Old diluted phrasing returned to home leadership section: {phrase!r}'


# ---------------------------------------------------------------------------
# Home — Card sections removed, replaced with "Where to Next" block (issue #18)
# ---------------------------------------------------------------------------

def test_home_card_sections_removed(client):
    """The three sitemap-style card grids are gone (Voyager / 3I-ATLAS / Black Hole)."""
    body = client.get('/').data
    must_be_absent = [
        b'Voyager 1: Deep Space Analysis',
        b'3I/ATLAS: Interstellar Comet Research',
        b'Black Hole Cosmology: Scientific Paper',
    ]
    for phrase in must_be_absent:
        assert phrase not in body, f'Card section heading returned to home: {phrase!r}'


def test_home_where_to_next_block_present(client):
    """The replacement narrative pointer block must be live with curated entry points."""
    body = client.get('/').data
    assert b'Where To Go Next' in body
    for path in (b'/voyager-story', b'/space-intelligence', b'/atlas', b'/blackhole'):
        assert path in body, f'Curated entry point missing from Where-to-Next block: {path!r}'



