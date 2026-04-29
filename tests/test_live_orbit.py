"""Unit tests for Phase 3 / Live Orbit 3D backend.

Covers:
  * _solve_kepler — Newton-Raphson eccentric-anomaly solver
  * _propagate_satellite — two-body Keplerian propagation
  * _classify_orbit_simple — LEO/MEO/GEO/HEO boundaries
  * _compute_live_positions — downsampling + payload schema
  * _generate_scene_narrative — templated narrator branches
  * /api/live-orbit-data — Flask test client (mocked I/O)

The Three.js scene itself is not covered; visual / WebGL behaviour
needs a browser harness that is out of scope for this suite.
"""
import datetime
import math

import pytest

import app as portal_app
from app import (
    _classify_orbit_simple,
    _compute_live_positions,
    _generate_scene_narrative,
    _propagate_satellite,
    _solve_kepler,
    app,
)


# ---------------------------------------------------------------------------
# _solve_kepler
# ---------------------------------------------------------------------------

class TestSolveKepler:
    def test_circular_orbit_returns_mean_anomaly(self):
        # e = 0 -> E == M for all M
        for M in (0.0, 0.5, math.pi, 2.0):
            assert _solve_kepler(M, 0.0) == pytest.approx(M, abs=1e-9)

    @pytest.mark.parametrize("M,e", [
        (0.1, 0.05),    # near-circular LEO
        (1.0, 0.2),     # moderate
        (2.5, 0.5),     # elliptical
        (3.0, 0.85),    # high eccentricity (Molniya-ish)
    ])
    def test_satisfies_kepler_identity(self, M, e):
        # E - e*sin(E) must equal M
        E = _solve_kepler(M, e)
        assert E - e * math.sin(E) == pytest.approx(M, abs=1e-5)

    def test_high_eccentricity_converges(self):
        # The solver uses pi as the starting guess for e >= 0.8
        E = _solve_kepler(0.0, 0.9)
        assert math.isfinite(E)
        assert abs(E - 0.9 * math.sin(E)) < 1e-5


# ---------------------------------------------------------------------------
# _propagate_satellite
# ---------------------------------------------------------------------------

def _make_sat(**overrides):
    """Build a minimal OMM-style dict for an ISS-like orbit."""
    base = {
        'OBJECT_NAME': 'TEST-SAT',
        'EPOCH': '2026-04-25T00:00:00',
        'MEAN_MOTION': 15.5,           # ~92 min orbit (LEO)
        'ECCENTRICITY': 0.0006,
        'INCLINATION': 51.64,
        'RA_OF_ASC_NODE': 0.0,
        'ARG_OF_PERICENTER': 0.0,
        'MEAN_ANOMALY': 0.0,
    }
    base.update(overrides)
    return base


class TestPropagateSatellite:
    def test_iss_like_radius_in_leo_band(self):
        sat = _make_sat()
        now = datetime.datetime(2026, 4, 25, 0, 0, 0, tzinfo=datetime.timezone.utc)
        pos = _propagate_satellite(sat, now)
        assert pos is not None
        r = math.sqrt(sum(c * c for c in pos))
        # ISS radius ~6780 km; allow ample band for circular LEO
        assert 6500 < r < 7100

    def test_geostationary_radius(self):
        # GEO mean motion = 1.0027 rev/day -> a ~ 42164 km
        sat = _make_sat(MEAN_MOTION=1.0027, ECCENTRICITY=0.0, INCLINATION=0.0)
        now = datetime.datetime(2026, 4, 25, 0, 0, 0, tzinfo=datetime.timezone.utc)
        pos = _propagate_satellite(sat, now)
        assert pos is not None
        r = math.sqrt(sum(c * c for c in pos))
        assert r == pytest.approx(42164, abs=50)

    def test_returns_none_for_invalid_eccentricity(self):
        assert _propagate_satellite(_make_sat(ECCENTRICITY=1.5), datetime.datetime.now(datetime.timezone.utc)) is None

    def test_returns_none_for_zero_mean_motion(self):
        assert _propagate_satellite(_make_sat(MEAN_MOTION=0), datetime.datetime.now(datetime.timezone.utc)) is None

    def test_returns_none_for_missing_field(self):
        sat = _make_sat()
        sat.pop('INCLINATION')
        assert _propagate_satellite(sat, datetime.datetime.now(datetime.timezone.utc)) is None

    def test_returns_none_for_unparseable_epoch(self):
        sat = _make_sat(EPOCH='not-a-date')
        assert _propagate_satellite(sat, datetime.datetime.now(datetime.timezone.utc)) is None

    def test_position_advances_with_time(self):
        sat = _make_sat()
        t0 = datetime.datetime(2026, 4, 25, 0, 0, 0, tzinfo=datetime.timezone.utc)
        t1 = t0 + datetime.timedelta(minutes=10)
        p0 = _propagate_satellite(sat, t0)
        p1 = _propagate_satellite(sat, t1)
        # Position must change appreciably for a LEO sat over 10 min
        delta = math.sqrt(sum((a - b) ** 2 for a, b in zip(p0, p1)))
        assert delta > 1000  # km


# ---------------------------------------------------------------------------
# _classify_orbit_simple
# ---------------------------------------------------------------------------

class TestClassifyOrbit:
    @pytest.mark.parametrize("alt,expected", [
        (300, 'LEO'),
        (1999, 'LEO'),
        (2000, 'MEO'),
        (20200, 'MEO'),         # GPS altitude
        (35585, 'MEO'),
        (35586, 'GEO'),
        (35786, 'GEO'),         # textbook GEO
        (35985, 'GEO'),
        (35986, 'HEO'),
        (100000, 'HEO'),
    ])
    def test_boundaries(self, alt, expected):
        assert _classify_orbit_simple(alt) == expected


# ---------------------------------------------------------------------------
# _compute_live_positions
# ---------------------------------------------------------------------------

class TestComputeLivePositions:
    def test_empty_input_returns_empty_list(self):
        assert _compute_live_positions([]) == []
        assert _compute_live_positions(None) == []

    def test_payload_schema_has_short_keys(self):
        out = _compute_live_positions([_make_sat()])
        assert len(out) == 1
        rec = out[0]
        assert set(rec.keys()) == {'n', 'x', 'y', 'z', 'c'}
        assert isinstance(rec['n'], str)
        assert isinstance(rec['c'], int) and rec['c'] in (0, 1, 2, 3)

    def test_object_name_truncated_to_40_chars(self):
        long_name = 'X' * 100
        out = _compute_live_positions([_make_sat(OBJECT_NAME=long_name)])
        assert len(out[0]['n']) == 40

    def test_leo_downsampled_to_budget(self):
        # 1000 LEO sats, budget = 100 -> exactly 100 returned
        sats = [_make_sat(OBJECT_NAME=f'LEO-{i}', MEAN_ANOMALY=i * 0.001)
                for i in range(1000)]
        out = _compute_live_positions(sats, max_points=100)
        assert len(out) == 100
        assert all(rec['c'] == 0 for rec in out)

    def test_meo_geo_heo_never_dropped(self):
        # 1000 LEO + 5 GEO + 5 HEO with very small max_points
        leo = [_make_sat(OBJECT_NAME=f'LEO-{i}', MEAN_ANOMALY=i * 0.001)
               for i in range(1000)]
        geo = [_make_sat(OBJECT_NAME=f'GEO-{i}', MEAN_MOTION=1.0027,
                         ECCENTRICITY=0.0, INCLINATION=0.0,
                         MEAN_ANOMALY=i * 0.5)
               for i in range(5)]
        heo = [_make_sat(OBJECT_NAME=f'HEO-{i}', MEAN_MOTION=2.0,
                         ECCENTRICITY=0.6,
                         MEAN_ANOMALY=i * 0.5)
               for i in range(5)]
        out = _compute_live_positions(leo + geo + heo, max_points=20)
        # All 5 GEO + 5 HEO retained; LEO trimmed to 10 to fit budget=20
        codes = [rec['c'] for rec in out]
        assert codes.count(2) == 5  # GEO
        assert codes.count(3) == 5  # HEO
        assert len(out) == 20

    def test_skips_invalid_entries(self):
        sats = [_make_sat(), {'MEAN_MOTION': 'bogus'}, _make_sat(MEAN_MOTION=0)]
        out = _compute_live_positions(sats)
        assert len(out) == 1


# ---------------------------------------------------------------------------
# _generate_scene_narrative
# ---------------------------------------------------------------------------

class TestNarrative:
    def test_empty_inputs_returns_fallback(self):
        result = _generate_scene_narrative({}, [], {})
        assert 'observed' in result.lower()

    def test_opening_line_includes_total_active(self):
        stats = {'total_active': 10500,
                 'orbit_distribution': {'LEO': 9000, 'GEO': 600},
                 'top_operators': []}
        out = _generate_scene_narrative(stats, [], {})
        assert '10,500' in out
        assert '9,000' in out
        assert '600' in out

    def test_dominant_operator_hook_appears_above_30pct(self):
        stats = {'total_active': 1000,
                 'orbit_distribution': {'LEO': 1000, 'GEO': 0},
                 'top_operators': [{'name': 'SpaceX', 'count': 500}]}
        out = _generate_scene_narrative(stats, [], {})
        assert 'SpaceX' in out and '50%' in out

    def test_dominant_operator_hook_suppressed_below_30pct(self):
        stats = {'total_active': 1000,
                 'orbit_distribution': {'LEO': 1000, 'GEO': 0},
                 'top_operators': [{'name': 'MinorOp', 'count': 100}]}
        out = _generate_scene_narrative(stats, [], {})
        assert 'MinorOp' not in out

    def test_hazardous_neo_close_pass_branch(self):
        neos = [{
            'name': '2026 XX', 'is_hazardous': True,
            'miss_au_raw': 0.02, 'miss_lunar': '7.8',
            'close_approach_date': '2026-04-26',
        }]
        out = _generate_scene_narrative({}, neos, {})
        assert 'hazardous' in out.lower()
        assert '7.8' in out

    def test_non_hazardous_neo_uses_closest_branch(self):
        neos = [{
            'name': 'Friendly Rock', 'is_hazardous': False,
            'miss_au_raw': 0.4, 'miss_lunar': '155',
            'close_approach_date': '2026-04-26',
        }]
        out = _generate_scene_narrative({}, neos, {})
        assert 'Friendly Rock' in out
        assert 'Closest asteroid' in out

    @pytest.mark.parametrize("kp,marker", [
        (1.0, 'quiet'),
        (3.5, 'unsettled'),
        (6.0, 'elevated'),
    ])
    def test_kp_branches(self, kp, marker):
        out = _generate_scene_narrative({}, [], {'kp_value': kp})
        assert marker in out.lower()


# ---------------------------------------------------------------------------
# /api/live-orbit-data
# ---------------------------------------------------------------------------

@pytest.fixture
def client(monkeypatch):
    # Disable rate limiter for tests
    portal_app.limiter.enabled = False
    app.config.update(TESTING=True)
    return app.test_client()


class TestLiveOrbitApi:
    def test_returns_expected_schema(self, client, monkeypatch):
        sats = [_make_sat(OBJECT_NAME='SAT-A'), _make_sat(OBJECT_NAME='SAT-B')]
        monkeypatch.setattr(portal_app, '_fetch_celestrak_active', lambda: sats)
        monkeypatch.setattr(portal_app, '_process_orbital_data', lambda s: {
            'total_active': len(s),
            'orbit_distribution': {'LEO': len(s), 'MEO': 0, 'GEO': 0, 'HEO': 0},
            'top_operators': [{'name': 'TestOp', 'count': len(s)}],
        })
        monkeypatch.setattr(portal_app, '_fetch_neo_data_safe', lambda: [])
        monkeypatch.setattr(portal_app, '_fetch_kp_index', lambda: {'kp_value': 2.0, 'label': 'Quiet'})

        resp = client.get('/api/live-orbit-data')
        assert resp.status_code == 200
        data = resp.get_json()
        for key in ('positions', 'neos', 'narrative', 'stats',
                    'refreshed', 'earth_radius_km'):
            assert key in data
        assert data['earth_radius_km'] == pytest.approx(6378.137)
        assert isinstance(data['positions'], list)
        assert data['stats']['total_active'] == 2
        assert data['stats']['rendered_count'] == len(data['positions'])

    def test_returns_503_when_upstream_fails(self, client, monkeypatch):
        def boom():
            raise RuntimeError('celestrak down')
        monkeypatch.setattr(portal_app, '_fetch_celestrak_active', boom)
        resp = client.get('/api/live-orbit-data')
        assert resp.status_code == 503
        assert 'error' in resp.get_json()

    def test_live_orbit_page_renders(self, client):
        resp = client.get('/live-orbit')
        assert resp.status_code == 200
        # Confirms the template hasn't been moved/renamed
        assert b'Loading 3D scene' in resp.data or b'live-orbit' in resp.data.lower()


# ---------------------------------------------------------------------------
# Space-Track integration
# ---------------------------------------------------------------------------

class _FakeResp:
    def __init__(self, status=200, payload=None, text=''):
        self.status_code = status
        self._payload = payload
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class _FakeSession:
    """Stand-in for requests.Session capturing posted/got URLs."""
    def __init__(self, post_resp, get_resp):
        self.post_resp = post_resp
        self.get_resp = get_resp
        self.headers = {}
        self.posted = None
        self.got = None

    def post(self, url, data=None, timeout=None):
        self.posted = (url, data)
        return self.post_resp

    def get(self, url, timeout=None):
        self.got = url
        if isinstance(self.get_resp, list):
            return self.get_resp.pop(0)
        return self.get_resp


class TestSpacetrack:
    def setup_method(self):
        # Reset module-level session + caches between tests
        portal_app._spacetrack_session = None
        portal_app._SI_CACHE.pop('spacetrack_active', None)
        portal_app._SI_HOST_DOWN.pop('www.space-track.org', None)
        portal_app._LAST_SAT_SOURCE = None

    def test_skips_silently_without_credentials(self, monkeypatch):
        monkeypatch.delenv('SPACETRACK_USER', raising=False)
        monkeypatch.delenv('SPACETRACK_PASS', raising=False)
        assert portal_app._fetch_spacetrack_active() is None

    def test_login_then_query_succeeds(self, monkeypatch):
        monkeypatch.setenv('SPACETRACK_USER', 'test@example.com')
        monkeypatch.setenv('SPACETRACK_PASS', 'pw')
        sats = [_make_sat(OBJECT_NAME='SAT-X')]
        sess = _FakeSession(
            post_resp=_FakeResp(200, text='{"ok":true}'),
            get_resp=_FakeResp(200, payload=sats),
        )
        monkeypatch.setattr(portal_app.http_requests, 'Session', lambda: sess)

        result = portal_app._fetch_spacetrack_active()
        assert result == sats
        assert sess.posted[0] == portal_app._SPACETRACK_LOGIN
        assert 'class/gp' in sess.got

    def test_login_failure_returns_none(self, monkeypatch):
        monkeypatch.setenv('SPACETRACK_USER', 'test@example.com')
        monkeypatch.setenv('SPACETRACK_PASS', 'pw')
        # Space-Track returns 200 but with HTML 'Login' page on bad creds
        sess = _FakeSession(
            post_resp=_FakeResp(200, text='<html>Login</html>'),
            get_resp=_FakeResp(200, payload=[]),
        )
        monkeypatch.setattr(portal_app.http_requests, 'Session', lambda: sess)
        assert portal_app._fetch_spacetrack_active() is None

    def test_session_expiry_triggers_relogin(self, monkeypatch):
        monkeypatch.setenv('SPACETRACK_USER', 'test@example.com')
        monkeypatch.setenv('SPACETRACK_PASS', 'pw')
        sats = [_make_sat(OBJECT_NAME='RETRY')]
        sessions = []

        def make_session():
            sess = _FakeSession(
                post_resp=_FakeResp(200, text='{"ok":true}'),
                # First session: 401 expired; second session: success
                get_resp=_FakeResp(401, text='') if not sessions else _FakeResp(200, payload=sats),
            )
            sessions.append(sess)
            return sess

        monkeypatch.setattr(portal_app.http_requests, 'Session', make_session)
        result = portal_app._fetch_spacetrack_active()
        assert result == sats
        assert len(sessions) == 2  # initial + re-login

    def test_connect_timeout_trips_circuit_breaker(self, monkeypatch):
        monkeypatch.setenv('SPACETRACK_USER', 'test@example.com')
        monkeypatch.setenv('SPACETRACK_PASS', 'pw')

        class _BoomSession:
            headers = {}
            def post(self, *a, **kw):
                raise portal_app.http_requests.exceptions.ConnectTimeout('boom')
            def get(self, *a, **kw):
                raise portal_app.http_requests.exceptions.ConnectTimeout('boom')

        monkeypatch.setattr(portal_app.http_requests, 'Session', _BoomSession)
        assert portal_app._fetch_spacetrack_active() is None
        assert portal_app._si_host_unreachable('www.space-track.org')

    def test_fetch_active_prefers_spacetrack(self, monkeypatch):
        sats = [_make_sat(OBJECT_NAME='ST-PRIMARY')]
        monkeypatch.setattr(portal_app, '_fetch_spacetrack_active', lambda: sats)
        # If Space-Track succeeds we must NOT hit CelesTrak
        called = {'celestrak': False}
        def _should_not_call(*a, **kw):
            called['celestrak'] = True
            return None
        monkeypatch.setattr(portal_app, '_si_cached_get', _should_not_call)
        result = portal_app._fetch_celestrak_active()
        assert result == sats
        assert portal_app._LAST_SAT_SOURCE == 'spacetrack'
        assert called['celestrak'] is False

    def test_fetch_active_falls_back_to_celestrak(self, monkeypatch):
        monkeypatch.setattr(portal_app, '_fetch_spacetrack_active', lambda: None)
        celestrak_sats = [_make_sat(OBJECT_NAME='CT-FALLBACK')]
        monkeypatch.setattr(
            portal_app, '_si_cached_get',
            lambda url, key, params=None: celestrak_sats if 'GROUP=active' in url else None,
        )
        result = portal_app._fetch_celestrak_active()
        assert result == celestrak_sats
        assert portal_app._LAST_SAT_SOURCE == 'celestrak'
