#!/usr/bin/env python3
"""
app.py — Deep Space Portal
---------------------------

Flask web application serving the Deep Space Research Platform.
Presents Voyager 1 analysis, 3I/ATLAS research, black hole cosmology,
and real-time space intelligence under a unified web portal.

Scientific analysis modules live in the sibling voyager1_project/.
This portal handles presentation, routing, and deployment concerns.

Run with:
    python app.py

Then open: http://localhost:5000
"""

import io
import base64
import datetime
import os
import sys
import tempfile
import time
from pathlib import Path

# Add sibling voyager1 science project to import path.
# Supports both local dir name (voyager1_project) and EC2 clone name (voyager1-analysis).
_PARENT = Path(__file__).resolve().parent.parent
for _name in ('voyager1_project', 'voyager1-analysis'):
    _VOYAGER1_PROJECT = _PARENT / _name
    if _VOYAGER1_PROJECT.is_dir():
        if str(_VOYAGER1_PROJECT) not in sys.path:
            sys.path.insert(0, str(_VOYAGER1_PROJECT))
        break

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests as http_requests

from flask import Flask, render_template, jsonify, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import matplotlib.dates as mdates

# Import science modules from voyager1_project
from voyager1_magneticfield_nTS_analysis import (
    fetch_ephemeris, 
    fetch_real_voyager_data, 
    fetch_real_voyager_data_alternative,
    plot_csv as original_plot_csv,
    plot_cdf as original_plot_cdf
)
from voyager1_outbound_trajectory import (
    fetch_trajectory_real,
    fetch_trajectory_synthetic,
    fetch_current_earth_position,
    MISSION_EVENTS,
    MissionEvent,
)
from voyager1_density_extraction import PlasmaFrequencyTracker
from voyager1_plasma_wave_analysis import VoyagerPWSData

try:
    import cdflib
    _CDFLIB_AVAILABLE = True
except ImportError:
    _CDFLIB_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32).hex())

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri='memory://'
)

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images from the Images directory."""
    from flask import send_from_directory, abort
    if '..' in filename or filename.startswith('/'):
        abort(403)
    return send_from_directory(Path(__file__).resolve().parent / 'Images', filename)

@app.route('/favicon.ico')
def favicon():
    """Serve a circular-cropped profile image as favicon."""
    from flask import send_file
    from PIL import Image, ImageDraw
    img_path = Path(__file__).parent / 'Images' / 'al-0135.JPG'
    img = Image.open(img_path).convert('RGBA')
    size = min(img.size)
    left = (img.width - size) // 2
    top = 0
    img = img.crop((left, top, left + size, top + size))
    img = img.resize((64, 64), Image.LANCZOS)
    mask = Image.new('L', (64, 64), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 63, 63), fill=255)
    output = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    buf = io.BytesIO()
    output.save(buf, format='ICO', sizes=[(64, 64)])
    buf.seek(0)
    return send_file(buf, mimetype='image/x-icon')

def plot_to_base64(fig):
    """Convert matplotlib figure to base64 string for web display."""
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=150)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return plot_url

def create_position_plot():
    """Create 3D position plot and return as base64 string."""
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        v_pos, e_pos = fetch_ephemeris(now)
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot celestial bodies
        ax.scatter(0, 0, 0, label='Sun', s=100, c='yellow', edgecolors='orange')
        ax.scatter(e_pos[0], e_pos[1], e_pos[2], label='Earth', s=80, c='blue', edgecolors='darkblue')
        ax.scatter(v_pos[0], v_pos[1], v_pos[2], label='Voyager 1', s=80, c='red', edgecolors='darkred')
        
        # Add reference line from Sun to Voyager 1
        ax.plot([0, v_pos[0]], [0, v_pos[1]], [0, v_pos[2]], 
                linestyle='--', color='gray', alpha=0.5, linewidth=2)
        
        ax.set_xlabel('X (AU)')
        ax.set_ylabel('Y (AU)')
        ax.set_zlabel('Z (AU)')
        ax.set_title(f'Voyager 1 Position - {now.strftime("%Y-%m-%d %H:%M UTC")}', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Calculate distance
        distance = np.linalg.norm(v_pos)
        
        # Add distance annotation
        ax.text2D(0.02, 0.98, f'Distance from Sun: {distance:.1f} AU', 
                 transform=ax.transAxes, fontsize=12, 
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
        
        plot_url = plot_to_base64(fig)
        
        # Calculate galactic coordinates for display
        try:
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            coord = SkyCoord(x=v_pos[0] * u.au, y=v_pos[1] * u.au, z=v_pos[2] * u.au,
                           representation_type='cartesian')
            gal = coord.galactic
            galactic_info = {
                'longitude': f"{gal.l.deg:.2f}°",
                'latitude': f"{gal.b.deg:.2f}°"
            }
        except:
            galactic_info = {'longitude': 'N/A', 'latitude': 'N/A'}
        
        return {
            'plot': plot_url,
            'distance': f"{distance:.1f}",
            'position': {
                'x': f"{v_pos[0]:.2f}",
                'y': f"{v_pos[1]:.2f}", 
                'z': f"{v_pos[2]:.2f}"
            },
            'galactic': galactic_info,
            'timestamp': now.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
    except Exception as e:
        return {'error': f"Failed to create position plot: {str(e)}"}

def create_magnetometer_plot(days_back=7):
    """Create magnetometer data plot and return as base64 string."""
    try:
        print(f"Fetching magnetometer data for last {days_back} days...")
        
        # Try to fetch real data first
        try:
            data_path = fetch_real_voyager_data(days_back)
            data_source = "NASA SPDF Archives"
            
            if str(data_path).endswith('.cdf') and _CDFLIB_AVAILABLE:
                # Process CDF file
                cdf = cdflib.CDF(str(data_path))
                info = cdf.cdf_info()
                rvars = info['rVariables']
                
                # Find time and magnetic field variables
                time_candidates = ['Epoch', 'epoch', 'TIME', 'time']
                value_candidates = ['B', 'B_mag', 'B_nT', 'value', 'mag']
                
                time_var = next((v for v in time_candidates if v in rvars), None)
                value_var = next((v for v in value_candidates if v in rvars), None)
                
                if time_var and value_var:
                    time_data = cdf.varget(time_var)
                    value_data = cdf.varget(value_var)
                    
                    try:
                        times = cdflib.cdfepoch.to_datetime(time_data)
                    except:
                        times = [datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=float(t)) 
                                for t in time_data]
                    
                    df = pd.DataFrame({'time': times, 'B_field': value_data})
                else:
                    raise ValueError("Could not find suitable variables in CDF file")
            else:
                # Assume CSV format
                df = pd.read_csv(data_path, parse_dates=['time'])
                
        except Exception as e:
            print(f"Real data fetch failed: {e}")
            print("Using realistic synthetic data...")
            data_path = fetch_real_voyager_data_alternative()
            data_source = "Realistic Synthetic Data"
            df = pd.read_csv(data_path, parse_dates=['time'])
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot magnetic field data
        ax.plot(df['time'], df.iloc[:, 1], 'b-', linewidth=1, alpha=0.8)
        
        ax.set_xlabel('Time (UTC)', fontsize=12)
        ax.set_ylabel('Magnetic Field Strength (nT)', fontsize=12)
        ax.set_title(f'Voyager 1 Magnetometer Data\nSource: {data_source}', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        plt.xticks(rotation=0)
        
        # Add statistics
        field_data = df.iloc[:, 1].dropna()
        stats_text = f'Mean: {field_data.mean():.3f} nT\n'
        stats_text += f'Std: {field_data.std():.3f} nT\n'
        stats_text += f'Range: {field_data.min():.3f} - {field_data.max():.3f} nT'
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8))
        
        # Add reference lines for typical ISM values
        ax.axhspan(0.3, 0.5, alpha=0.1, color='orange', label='Typical ISM Range')
        ax.legend()
        
        plt.tight_layout()
        plot_url = plot_to_base64(fig)
        
        return {
            'plot': plot_url,
            'data_source': data_source,
            'data_points': len(df),
            'time_range': f"{df['time'].min().strftime('%Y-%m-%d %H:%M')} to {df['time'].max().strftime('%Y-%m-%d %H:%M')}",
            'statistics': {
                'mean': f"{field_data.mean():.3f}",
                'std': f"{field_data.std():.3f}",
                'min': f"{field_data.min():.3f}",
                'max': f"{field_data.max():.3f}"
            }
        }
        
    except Exception as e:
        return {'error': f"Failed to create magnetometer plot: {str(e)}"}

def create_trajectory_plot():
    """Create trajectory visualization and return as base64 string with metadata."""
    try:
        import copy
        start_date = MISSION_EVENTS[0].date  # Launch date
        end_date = datetime.datetime.now(datetime.timezone.utc)

        # Build event list including current position
        events = list(MISSION_EVENTS)
        current_event = MissionEvent("Current", end_date, "#9467bd", marker='X', size=120)
        events.append(current_event)

        # Try real data first, fall back to synthetic
        try:
            trajectory, dates = fetch_trajectory_real(start_date, end_date, 30)
            data_source = "NASA JPL HORIZONS"
        except Exception:
            trajectory, dates = fetch_trajectory_synthetic(start_date, end_date, 30)
            data_source = "Synthetic Model"

        # --- Build figure ---
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')

        # Trajectory path
        ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
                'w-', linewidth=2, alpha=0.8, label='Trajectory')

        # Mission event markers
        event_colors = {
            "Launch": ("#1f77b4", "lightsteelblue", "navy"),
            "Jupiter Flyby": ("#ff7f0e", "moccasin", "darkorange"),
            "Saturn Flyby": ("#2ca02c", "lightgreen", "darkgreen"),
            "Pale Blue Dot": ("#17becf", "lightcyan", "darkcyan"),
            "Termination Shock": ("#e377c2", "mistyrose", "mediumvioletred"),
            "Heliopause": ("#d62728", "lightcoral", "darkred"),
            "Current": ("#9467bd", "plum", "purple"),
        }
        for event in events:
            time_diffs = [abs((d - event.date).total_seconds()) for d in dates]
            closest_idx = int(np.argmin(time_diffs))
            pos = trajectory[closest_idx]
            c, face, edge = event_colors.get(event.name, (event.color, "white", "gray"))
            ax.scatter(pos[0], pos[1], pos[2],
                       c=c, marker=event.marker, s=event.size,
                       label=event.name, edgecolors='black', linewidth=1, zorder=5)

            # Annotation offset
            dist_from_origin = np.linalg.norm(pos)
            if dist_from_origin < 15:
                offset_base = 10.0
                if event.name == "Launch":
                    offset = np.array([offset_base, offset_base, offset_base])
                elif event.name == "Jupiter Flyby":
                    offset = np.array([offset_base, -offset_base, 0])
                elif event.name == "Saturn Flyby":
                    offset = np.array([-offset_base, offset_base, 0])
                else:
                    offset = np.array([offset_base, 0, offset_base])
            else:
                offset = pos * 0.25
            text_pos = pos + offset
            ax.text(text_pos[0], text_pos[1], text_pos[2],
                    f'{event.name}\n{event.date.strftime("%Y-%m-%d")}',
                    fontsize=9, ha='center', va='center', color='white', weight='bold',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=face, alpha=0.85, edgecolor=edge))
            ax.plot([pos[0], text_pos[0]], [pos[1], text_pos[1]], [pos[2], text_pos[2]],
                    color=edge, linewidth=1.2, alpha=0.6, linestyle='--')

        # Sun
        ax.scatter(0, 0, 0, c='yellow', s=200, marker='*',
                   label='Sun', edgecolors='orange', linewidth=2, zorder=5)

        # Sun-to-Voyager dashed line
        current_pos = trajectory[-1]
        ax.plot([0, current_pos[0]], [0, current_pos[1]], [0, current_pos[2]],
                linestyle='--', color='gray', alpha=0.4, linewidth=1.5)

        # Earth
        earth_pos = fetch_current_earth_position()
        if earth_pos is not None:
            ax.scatter(earth_pos[0], earth_pos[1], earth_pos[2],
                       c='deepskyblue', s=80, marker='o', label='Earth',
                       edgecolors='darkblue', linewidth=1, zorder=5)

        # Style for dark background
        fig.patch.set_facecolor('#0c0c0c')
        ax.set_facecolor('#0c0c0c')
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor('#333')
        ax.yaxis.pane.set_edgecolor('#333')
        ax.zaxis.pane.set_edgecolor('#333')
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.label.set_color('white')
            axis.set_tick_params(colors='white')
        ax.set_xlabel('X (AU)', fontsize=11, color='white')
        ax.set_ylabel('Y (AU)', fontsize=11, color='white')
        ax.set_zlabel('Z (AU)', fontsize=11, color='white')
        ax.set_title('Voyager 1 Complete Outbound Trajectory\n(Heliocentric Coordinates)',
                     fontsize=14, fontweight='bold', color='white')
        ax.grid(True, alpha=0.15, color='white')

        # Equal aspect ratio
        max_range = np.max(np.ptp(trajectory, axis=0))
        mid_point = np.mean(trajectory, axis=0)
        ax.set_xlim(mid_point[0] - max_range / 2, mid_point[0] + max_range / 2)
        ax.set_ylim(mid_point[1] - max_range / 2, mid_point[1] + max_range / 2)
        ax.set_zlim(mid_point[2] - max_range / 2, mid_point[2] + max_range / 2)

        leg = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left',
                        facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
        plt.tight_layout()

        plot_url = plot_to_base64(fig)

        total_distance = float(np.linalg.norm(current_pos))
        heliopause_date = datetime.datetime(2012, 8, 25, tzinfo=datetime.timezone.utc)
        years_since_hp = (end_date - heliopause_date).days / 365.25

        # Galactic coords
        try:
            from astropy import units as u
            from astropy.coordinates import SkyCoord
            coord = SkyCoord(x=current_pos[0] * u.au, y=current_pos[1] * u.au,
                             z=current_pos[2] * u.au, representation_type='cartesian')
            gal = coord.galactic
            galactic_info = {'longitude': f"{gal.l.deg:.2f}", 'latitude': f"{gal.b.deg:.2f}"}
        except Exception:
            galactic_info = {'longitude': 'N/A', 'latitude': 'N/A'}

        return {
            'plot': plot_url,
            'data_source': data_source,
            'distance_au': f"{total_distance:.1f}",
            'trajectory_points': len(trajectory),
            'years_since_heliopause': f"{years_since_hp:.1f}",
            'galactic': galactic_info,
            'events': [
                {'name': e.name, 'date': e.date.strftime('%Y-%m-%d'),
                 'distance': f"{np.linalg.norm(trajectory[int(np.argmin([abs((d - e.date).total_seconds()) for d in dates]))]):.1f}"}
                for e in events
            ],
            'timestamp': end_date.strftime('%Y-%m-%d %H:%M:%S UTC'),
        }
    except Exception as e:
        return {'error': f"Failed to create trajectory plot: {str(e)}"}


@app.route('/')
def index():
    """Beautiful landing page inspired by Prabhu's blog design."""
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    """Main analysis dashboard with Voyager 1 data visualization."""
    return render_template('dashboard.html')

@app.route('/trajectory')
def trajectory():
    """Trajectory visualization page."""
    return render_template('trajectory.html')

@app.route('/api/trajectory')
@limiter.limit('10/minute')
def api_trajectory():
    """API endpoint for trajectory data."""
    return jsonify(create_trajectory_plot())

@app.route('/plasma-waves')
def plasma_waves():
    """Plasma wave analysis page (placeholder for now)."""
    return jsonify({'message': 'Plasma wave analysis coming soon!', 
                   'redirect': '/dashboard'})

@app.route('/facts')
def facts():
    """Voyager 1 amazing facts page for presentations."""
    return render_template('facts.html')

@app.route('/density')
def density():
    """Density extraction page."""
    return render_template('density.html')

@app.route('/plasma')
def plasma():
    """Plasma wave analysis page."""
    return render_template('plasma.html')

@app.route('/atlas')
def atlas():
    """3I/ATLAS interstellar comet research page."""
    return render_template('atlas.html')

@app.route('/blackhole')
def blackhole():
    """Universe inside a black hole — scientific paper page."""
    return render_template('blackhole.html')

@app.route('/mars')
def mars():
    """Mission to Mars (1993) — early research paper page."""
    return render_template('mars.html')

@app.route('/ai-index')
def ai_index():
    """AI-friendly structured knowledge index for LLM and search crawlers."""
    return render_template('ai-index.html')

@app.route('/architecture')
def architecture():
    """Software architecture document for the Deep Space Research Platform."""
    return render_template('architecture.html')

@app.route('/sitemap.xml')
def sitemap():
    """XML sitemap for search engine crawlers."""
    today = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    pages = [
        {'loc': 'https://prabhusadasivam.com/', 'priority': '1.0', 'changefreq': 'weekly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/facts', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/trajectory', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/plasma', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/density', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/dashboard', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/space-intelligence', 'priority': '0.9', 'changefreq': 'hourly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/atlas', 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/blackhole', 'priority': '0.9', 'changefreq': 'monthly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/mars', 'priority': '0.7', 'changefreq': 'yearly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/ai-index', 'priority': '0.6', 'changefreq': 'weekly', 'lastmod': today},
        {'loc': 'https://prabhusadasivam.com/architecture', 'priority': '0.7', 'changefreq': 'monthly', 'lastmod': today},
    ]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{page["loc"]}</loc>\n'
        xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += '  </url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Robots.txt for search engine crawlers."""
    txt = """User-agent: *
Allow: /
Disallow: /api/

Sitemap: https://prabhusadasivam.com/sitemap.xml
"""
    return Response(txt, mimetype='text/plain')

@app.route('/api/plasma')
@limiter.limit('10/minute')
def api_plasma():
    """API endpoint for plasma wave analysis data."""
    duration = request.args.get('hours', default=24, type=int)
    duration = max(6, min(duration, 72))
    freq_min = request.args.get('freq_min', default=10, type=int)
    freq_max = request.args.get('freq_max', default=10000, type=int)
    return jsonify(create_plasma_plots(duration, (freq_min, freq_max)))

def create_plasma_plots(duration_hours=24, freq_range=(10, 10000)):
    """Generate plasma wave analysis plots and return as base64 with metadata."""
    try:
        pws_data = VoyagerPWSData()
        pws_data.load_synthetic_data(duration_hours, freq_range)

        time_nums = mdates.date2num(pws_data.time)

        # --- Figure 1: Spectrogram ---
        fig1, ax1 = plt.subplots(figsize=(14, 7))
        fig1.patch.set_facecolor('#0c0c0c')
        ax1.set_facecolor('#0c0c0c')

        T, F = np.meshgrid(time_nums, pws_data.frequencies)
        im = ax1.pcolormesh(T, F, pws_data.wave_intensity.T,
                            norm=plt.matplotlib.colors.LogNorm(vmin=0.01, vmax=100),
                            cmap='viridis', shading='auto')
        ax1.set_yscale('log')
        ax1.set_ylabel('Frequency (Hz)', color='white', fontsize=12)
        ax1.set_xlabel('Time (UTC)', color='white', fontsize=12)
        ax1.set_title('Voyager 1 Plasma Wave Spectrogram\n'
                      f'{pws_data.time[0].strftime("%Y-%m-%d %H:%M")} — '
                      f'{pws_data.time[-1].strftime("%Y-%m-%d %H:%M")} UTC',
                      color='white', fontsize=14, fontweight='bold')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, duration_hours // 8)))
        ax1.tick_params(colors='white')
        plt.setp(ax1.get_xticklabels(), rotation=45, color='white')
        ax1.grid(True, alpha=0.2, color='white')
        cbar = plt.colorbar(im, ax=ax1)
        cbar.set_label('Wave Intensity (V²/m²/Hz)', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')
        for spine in ax1.spines.values():
            spine.set_color('#444')
        fig1.tight_layout()
        spectrogram_plot = plot_to_base64(fig1)

        # --- Figure 2: Frequency spectrum at mid-point ---
        mid_idx = len(pws_data.time) // 2
        spectrum = pws_data.wave_intensity[mid_idx, :]

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        fig2.patch.set_facecolor('#0c0c0c')
        ax2.set_facecolor('#0c0c0c')
        ax2.loglog(pws_data.frequencies, spectrum, '#4ecdc4', linewidth=2)
        ax2.axvspan(10, 100, alpha=0.15, color='red', label='Low-freq turbulence')
        ax2.axvspan(1000, 5000, alpha=0.15, color='orange', label='Plasma frequency range')
        if freq_range[1] >= 10000:
            ax2.axvspan(10000, min(50000, freq_range[1]), alpha=0.15, color='green', label='Upper hybrid range')
        ax2.set_xlabel('Frequency (Hz)', color='white', fontsize=12)
        ax2.set_ylabel('Wave Intensity (V²/m²/Hz)', color='white', fontsize=12)
        ax2.set_title(f'PWS Frequency Spectrum — {pws_data.time[mid_idx].strftime("%Y-%m-%d %H:%M")} UTC',
                      color='white', fontsize=14, fontweight='bold')
        ax2.legend(facecolor='#1a1a2e', edgecolor='#444', labelcolor='white', fontsize=10)
        ax2.grid(True, alpha=0.2, color='white')
        ax2.tick_params(colors='white')
        for spine in ax2.spines.values():
            spine.set_color('#444')
        fig2.tight_layout()
        spectrum_plot = plot_to_base64(fig2)

        # --- Figure 3: Time series (integrated intensity + electric field) ---
        integrated = np.mean(pws_data.wave_intensity, axis=1)

        fig3, (ax3a, ax3b) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
        fig3.patch.set_facecolor('#0c0c0c')
        for ax in [ax3a, ax3b]:
            ax.set_facecolor('#0c0c0c')

        ax3a.plot(pws_data.time, integrated, '#4ecdc4', linewidth=1.2)
        ax3a.set_ylabel('Integrated Intensity', color='white', fontsize=11)
        ax3a.set_title('Voyager 1 PWS Time Series — All Frequencies',
                       color='white', fontsize=13, fontweight='bold')
        ax3a.grid(True, alpha=0.2, color='white')
        ax3a.tick_params(colors='white')

        if pws_data.electric_field is not None:
            ax3b.plot(pws_data.time, pws_data.electric_field, '#ff6b6b', linewidth=1.2)
        ax3b.set_ylabel('Electric Field (mV/m)', color='white', fontsize=11)
        ax3b.set_xlabel('Time (UTC)', color='white', fontsize=11)
        ax3b.grid(True, alpha=0.2, color='white')
        ax3b.tick_params(colors='white')

        for ax in [ax3a, ax3b]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, duration_hours // 8)))
            for spine in ax.spines.values():
                spine.set_color('#444')
        plt.setp(ax3b.get_xticklabels(), rotation=45, color='white')
        fig3.tight_layout()
        timeseries_plot = plot_to_base64(fig3)

        # --- Compute statistics ---
        mean_intensity = float(np.mean(integrated))
        max_intensity = float(np.max(integrated))
        min_intensity = float(np.min(integrated))
        std_intensity = float(np.std(integrated))

        # Plasma density estimate
        low_mask = (pws_data.frequencies >= 1000) & (pws_data.frequencies <= 5000)
        plasma_freqs = []
        for i in range(len(pws_data.time)):
            spec = pws_data.wave_intensity[i, low_mask]
            peak_idx = np.argmax(spec)
            plasma_freqs.append(pws_data.frequencies[low_mask][peak_idx])
        plasma_freqs = np.array(plasma_freqs)
        mean_plasma_freq = float(np.mean(plasma_freqs))

        e = 1.602e-19
        m_e = 9.109e-31
        eps0 = 8.854e-12
        densities = (2 * np.pi * plasma_freqs)**2 * eps0 * m_e / e**2 / 1e6
        mean_density = float(np.mean(densities))

        return {
            'spectrogram_plot': spectrogram_plot,
            'spectrum_plot': spectrum_plot,
            'timeseries_plot': timeseries_plot,
            'duration_hours': duration_hours,
            'freq_range': list(freq_range),
            'data_points': len(pws_data.time),
            'freq_channels': len(pws_data.frequencies),
            'statistics': {
                'mean_intensity': f"{mean_intensity:.3f}",
                'max_intensity': f"{max_intensity:.3f}",
                'min_intensity': f"{min_intensity:.3f}",
                'std_intensity': f"{std_intensity:.3f}",
                'mean_plasma_freq': f"{mean_plasma_freq:.0f}",
                'mean_density': f"{mean_density:.4f}",
            },
            'time_range': f"{pws_data.time[0].strftime('%Y-%m-%d %H:%M')} to {pws_data.time[-1].strftime('%Y-%m-%d %H:%M')}",
            'timestamp': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        }
    except Exception as e:
        return {'error': f'Failed to create plasma wave plots: {str(e)}'}


@app.route('/api/density')
@limiter.limit('10/minute')
def api_density():
    """API endpoint for density extraction data."""
    duration = request.args.get('hours', default=48, type=int)
    duration = max(6, min(duration, 72))
    return jsonify(create_density_plots(duration))

def create_density_plots(duration_hours=48):
    """Run density extraction and return process + NASA-style plots with metadata."""
    try:
        # Load synthetic PWS data
        pws_data = VoyagerPWSData()
        pws_data.load_synthetic_data(duration_hours)

        # Extract plasma frequency ridge
        tracker = PlasmaFrequencyTracker()
        plasma_frequencies = tracker.detect_plasma_frequency_ridge(
            pws_data.wave_intensity, pws_data.frequencies, (500, 8000))
        densities = tracker.frequency_to_density(plasma_frequencies)
        stats = tracker.analyze_density_statistics(densities, pws_data.time)

        time_nums = mdates.date2num(pws_data.time)

        # --- Figure 1: 3-panel process plot ---
        fig1 = plt.figure(figsize=(14, 11))
        fig1.patch.set_facecolor('#0c0c0c')

        # Panel 1 – spectrogram + ridge
        ax1 = fig1.add_subplot(3, 1, 1)
        T, F = np.meshgrid(time_nums, pws_data.frequencies)
        ax1.pcolormesh(T, F, pws_data.wave_intensity.T,
                       norm=plt.matplotlib.colors.LogNorm(vmin=0.01, vmax=100),
                       cmap='viridis', shading='auto')
        ax1.plot(time_nums, plasma_frequencies, 'r-', linewidth=2,
                 label='Detected Plasma Frequency')
        ax1.set_yscale('log')
        ax1.set_ylabel('Frequency (Hz)', color='white')
        ax1.set_title('PWS Spectrogram with Plasma Frequency Ridge',
                      color='white', fontsize=13, fontweight='bold')
        ax1.legend(facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
        ax1.grid(True, alpha=0.2, color='white')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax1.set_facecolor('#0c0c0c')
        ax1.tick_params(colors='white')
        ax1.yaxis.label.set_color('white')
        plt.setp(ax1.get_xticklabels(), rotation=45, color='white')

        # Panel 2 – plasma frequency
        ax2 = fig1.add_subplot(3, 1, 2)
        ax2.plot(pws_data.time, plasma_frequencies, '#4ecdc4', linewidth=1.5)
        ax2.axhspan(1000, 3000, alpha=0.15, color='orange', label='Typical ISM range')
        ax2.set_ylabel('Plasma Frequency (Hz)', color='white')
        ax2.set_title('Extracted Plasma Frequency', color='white', fontsize=13, fontweight='bold')
        ax2.legend(facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
        ax2.grid(True, alpha=0.2, color='white')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax2.set_facecolor('#0c0c0c')
        ax2.tick_params(colors='white')
        plt.setp(ax2.get_xticklabels(), rotation=45, color='white')

        # Panel 3 – electron density
        ax3 = fig1.add_subplot(3, 1, 3)
        ax3.semilogy(pws_data.time, densities, '#ffd700', linewidth=1.5)
        ax3.axhspan(0.01, 0.1, alpha=0.12, color='red', label='Heliosheath')
        ax3.axhspan(0.1, 1.0, alpha=0.12, color='deepskyblue', label='Local ISM')
        ax3.set_ylabel('Electron Density (cm⁻³)', color='white')
        ax3.set_xlabel('Time (UTC)', color='white')
        ax3.set_title('Derived Electron Density', color='white', fontsize=13, fontweight='bold')
        ax3.legend(facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
        ax3.grid(True, alpha=0.2, color='white')
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax3.set_facecolor('#0c0c0c')
        ax3.tick_params(colors='white')
        plt.setp(ax3.get_xticklabels(), rotation=45, color='white')

        fig1.tight_layout()
        process_plot = plot_to_base64(fig1)

        # --- Figure 2: NASA-style density plot ---
        fig2, ax = plt.subplots(figsize=(12, 6))
        fig2.patch.set_facecolor('#0c0c0c')
        ax.set_facecolor('#0c0c0c')

        ax.semilogy(pws_data.time, densities, '#4ecdc4', linewidth=1.2, alpha=0.8,
                    label='Raw measurements')

        # Running average
        window = min(len(densities) // 10, 20)
        if window >= 3:
            running_avg = pd.Series(densities).rolling(window=window, center=True).mean()
            ax.semilogy(pws_data.time, running_avg, '#ff6b6b', linewidth=2.5,
                        label=f'{window}-pt running average')

        ax.axhspan(0.005, 0.05, alpha=0.12, color='orange', label='Heliosheath')
        ax.axhspan(0.05, 0.5, alpha=0.12, color='deepskyblue', label='Local ISM')
        ax.axhspan(0.5, 2.0, alpha=0.12, color='lightgreen', label='Dense ISM')

        ax.set_ylabel('Electron Density (cm⁻³)', fontsize=12, color='white')
        ax.set_xlabel('Time (UTC)', fontsize=12, color='white')
        ax.set_title('Voyager 1 Electron Density — Plasma Wave Analysis\n'
                     f'Mean: {stats["mean_density"]:.4f} ± {stats["std_density"]:.4f} cm⁻³',
                     fontsize=14, fontweight='bold', color='white')
        ax.grid(True, alpha=0.2, color='white')
        ax.legend(fontsize=10, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#444')

        valid = densities[densities > 0]
        if len(valid) > 0:
            ax.set_ylim(max(0.001, valid.min() * 0.5), min(10.0, valid.max() * 2.0))

        fig2.tight_layout()
        nasa_plot = plot_to_base64(fig2)

        return {
            'process_plot': process_plot,
            'nasa_plot': nasa_plot,
            'duration_hours': duration_hours,
            'data_points': int(stats['n_points']),
            'statistics': {
                'mean': f"{stats['mean_density']:.4f}",
                'std': f"{stats['std_density']:.4f}",
                'min': f"{stats['min_density']:.4f}",
                'max': f"{stats['max_density']:.4f}",
                'median': f"{stats['median_density']:.4f}",
            },
            'time_range': f"{pws_data.time[0].strftime('%Y-%m-%d %H:%M')} to {pws_data.time[-1].strftime('%Y-%m-%d %H:%M')}",
            'reference': {
                'heliosheath': '0.01 – 0.1 cm⁻³',
                'local_ism': '0.1 – 1 cm⁻³',
                'solar_wind_1au': '5 – 10 cm⁻³',
            },
            'timestamp': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        }
    except Exception as e:
        return {'error': f'Failed to create density plots: {str(e)}'}


@app.route('/api/position')
@limiter.limit('10/minute')
def api_position():
    """API endpoint for position data."""
    return jsonify(create_position_plot())

@app.route('/api/magnetometer')
@limiter.limit('10/minute')
def api_magnetometer():
    """API endpoint for magnetometer data."""
    days_back = request.args.get('days', default=7, type=int)
    days_back = max(1, min(days_back, 30))  # Limit between 1-30 days
    return jsonify(create_magnetometer_plot(days_back))

# ---------------------------------------------------------------------------
# Space Intelligence: caching + data helpers
# ---------------------------------------------------------------------------
_SI_CACHE = {}
_SI_CACHE_TTL = 900  # 15 minutes
_SI_NEG_TTL = 300    # 5 minutes — short cooldown for 403/empty results to avoid hammering

NASA_API_KEY = os.environ.get('NASA_API_KEY', 'DEMO_KEY')


def _si_cached_get(url, key, params=None):
    """GET *url* with 15-min in-memory cache. Returns parsed JSON or None."""
    now = time.time()
    if key in _SI_CACHE and now - _SI_CACHE[key]['ts'] < _SI_CACHE_TTL:
        return _SI_CACHE[key]['data']
    try:
        headers = {
            'User-Agent': 'DeepSpacePortal/1.0 (research; +https://prabhusadasivam.com)',
            'Accept': 'application/json',
        }
        r = http_requests.get(url, params=params, headers=headers, timeout=15)
        # CelesTrak returns 403 when data hasn't changed since last download.
        # Treat this as a cache-hit rather than an error.
        if r.status_code == 403 and 'has not updated' in r.text:
            if key in _SI_CACHE:
                _SI_CACHE[key]['ts'] = now  # extend TTL
                return _SI_CACHE[key]['data']
            # No cache yet — store a short-TTL negative entry so we don't
            # retry the primary on every request while CelesTrak is in its
            # 2-hour cooldown window.
            _SI_CACHE[key] = {'data': None, 'ts': now - (_SI_CACHE_TTL - _SI_NEG_TTL)}
            return None
        r.raise_for_status()
        data = r.json()
        _SI_CACHE[key] = {'data': data, 'ts': now}
        return data
    except Exception as exc:
        print(f"[space-intelligence] fetch {key} failed: {exc}")
        # Return stale cache if available
        if key in _SI_CACHE:
            return _SI_CACHE[key]['data']
        # Negative cache for transient failures (e.g. CelesTrak iridium
        # group occasionally returns non-JSON).
        _SI_CACHE[key] = {'data': None, 'ts': now - (_SI_CACHE_TTL - _SI_NEG_TTL)}
        return None


def _fetch_neo_data():
    """Return list of close-approach objects for the next 7 days."""
    today = datetime.date.today()
    end = today + datetime.timedelta(days=7)
    params = {
        'start_date': today.isoformat(),
        'end_date': end.isoformat(),
        'api_key': NASA_API_KEY,
    }
    raw = _si_cached_get(
        'https://api.nasa.gov/neo/rest/v1/feed', 'neo_feed', params)
    if not raw:
        return []
    neos = []
    for day_list in raw.get('near_earth_objects', {}).values():
        for obj in day_list:
            ca = obj.get('close_approach_data', [{}])[0]
            miss_km = float(ca.get('miss_distance', {}).get('kilometers', 0))
            miss_au = float(ca.get('miss_distance', {}).get('astronomical', 0))
            miss_lunar = float(ca.get('miss_distance', {}).get('lunar', 0))
            diam = obj.get('estimated_diameter', {}).get('meters', {})
            neos.append({
                'name': obj.get('name', 'Unknown'),
                'id': obj.get('id', ''),
                'is_hazardous': obj.get('is_potentially_hazardous_asteroid', False),
                'close_approach_date': ca.get('close_approach_date_full', ca.get('close_approach_date', '')),
                'velocity_kph': f"{float(ca.get('relative_velocity', {}).get('kilometers_per_hour', 0)):,.0f}",
                'miss_km': f"{miss_km:,.0f}",
                'miss_au': f"{miss_au:.4f}",
                'miss_lunar': f"{miss_lunar:.2f}",
                'diameter_min': f"{diam.get('estimated_diameter_min', 0):.1f}",
                'diameter_max': f"{diam.get('estimated_diameter_max', 0):.1f}",
                'miss_au_raw': miss_au,
            })
    neos.sort(key=lambda x: x['miss_au_raw'])
    return neos


def _fetch_solar_flares():
    """Recent solar flares from DONKI (last 7 days)."""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=7)
    params = {
        'startDate': start.isoformat(),
        'endDate': today.isoformat(),
        'api_key': NASA_API_KEY,
    }
    raw = _si_cached_get(
        'https://api.nasa.gov/DONKI/FLR', 'donki_flr', params)
    if not raw:
        return []
    flares = []
    for f in raw:
        flares.append({
            'flrID': f.get('flrID', ''),
            'beginTime': f.get('beginTime', ''),
            'peakTime': f.get('peakTime', ''),
            'endTime': f.get('endTime', ''),
            'classType': f.get('classType', 'Unknown'),
            'sourceLocation': f.get('sourceLocation', ''),
        })
    # Most recent first
    flares.sort(key=lambda x: x['peakTime'], reverse=True)
    return flares


def _fetch_cme():
    """Recent CMEs from DONKI (last 7 days)."""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=7)
    params = {
        'startDate': start.isoformat(),
        'endDate': today.isoformat(),
        'api_key': NASA_API_KEY,
    }
    raw = _si_cached_get(
        'https://api.nasa.gov/DONKI/CME', 'donki_cme', params)
    if not raw:
        return []
    cmes = []
    for c in raw:
        analysis = c.get('cmeAnalyses') or []
        speed = ''
        half_angle = ''
        if analysis:
            a = analysis[0]
            speed = f"{a.get('speed', '')}"
            half_angle = f"{a.get('halfAngle', '')}"
        cmes.append({
            'activityID': c.get('activityID', ''),
            'startTime': c.get('startTime', ''),
            'sourceLocation': c.get('sourceLocation', ''),
            'speed': speed,
            'halfAngle': half_angle,
            'note': (c.get('note') or '')[:120],
        })
    cmes.sort(key=lambda x: x['startTime'], reverse=True)
    return cmes


def _fetch_geomagnetic():
    """Recent geomagnetic storms from DONKI (last 30 days)."""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=30)
    params = {
        'startDate': start.isoformat(),
        'endDate': today.isoformat(),
        'api_key': NASA_API_KEY,
    }
    raw = _si_cached_get(
        'https://api.nasa.gov/DONKI/GST', 'donki_gst', params)
    if not raw:
        return []
    storms = []
    for g in raw:
        kp_vals = g.get('allKpIndex') or []
        max_kp = max((k.get('kpIndex', 0) for k in kp_vals), default=0)
        storms.append({
            'gstID': g.get('gstID', ''),
            'startTime': g.get('startTime', ''),
            'kpMax': max_kp,
            'gScale': _kp_to_g(max_kp),
        })
    storms.sort(key=lambda x: x['startTime'], reverse=True)
    return storms


def _fetch_kp_index():
    """Current Kp index from NOAA SWPC."""
    raw = _si_cached_get(
        'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json',
        'swpc_kp')
    if not raw or len(raw) < 2:
        return None
    # First row is header; last row is latest
    # Rows may be lists or dicts depending on API version
    latest = raw[-1]
    try:
        if isinstance(latest, dict):
            kp = float(latest.get('Kp', latest.get('kp', latest.get('kp_index', 0))))
            ts = latest.get('time_tag', latest.get('model_prediction_time', ''))
        else:
            kp = float(latest[1])
            ts = latest[0] if latest else ''
    except (IndexError, ValueError, KeyError, TypeError):
        kp = 0
        ts = ''
    return {
        'timestamp': ts,
        'kp': kp,
        'gScale': _kp_to_g(kp),
    }


def _fetch_kp_forecast():
    """Kp forecast from NOAA SWPC."""
    raw = _si_cached_get(
        'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json',
        'swpc_kp_forecast')
    if not raw or len(raw) < 1:
        return []
    # Filter to predicted/future rows if possible; use last 8 entries
    rows = raw
    if isinstance(rows[0], dict) and 'observed' in rows[0]:
        predicted = [r for r in rows if r.get('observed') == 'predicted']
        rows = predicted if predicted else rows
    forecast = []
    for row in rows[-8:]:  # last 8 forecast periods
        try:
            if isinstance(row, dict):
                t = row.get('time_tag', row.get('model_prediction_time', ''))
                kp_val = float(row.get('Kp', row.get('kp', row.get('kp_index', 0))))
            else:
                t = row[0]
                kp_val = float(row[1])
            forecast.append({
                'time': t,
                'kp': kp_val,
                'gScale': _kp_to_g(kp_val),
            })
        except (IndexError, ValueError):
            continue
    return forecast


def _kp_to_g(kp):
    """Convert Kp index to NOAA G-scale label."""
    if kp >= 9:
        return 'G5 — Extreme'
    if kp >= 8:
        return 'G4 — Severe'
    if kp >= 7:
        return 'G3 — Strong'
    if kp >= 6:
        return 'G2 — Moderate'
    if kp >= 5:
        return 'G1 — Minor'
    return 'Quiet'


def _severity_color(kp):
    """Return severity label for template color-coding."""
    if kp >= 7:
        return 'red'
    if kp >= 5:
        return 'orange'
    if kp >= 4:
        return 'yellow'
    return 'green'


def _flare_severity(class_type):
    """Severity color from flare class."""
    if not class_type:
        return 'green'
    c = class_type[0].upper()
    if c == 'X':
        return 'red'
    if c == 'M':
        return 'orange'
    if c == 'C':
        return 'yellow'
    return 'green'


def _build_highlights(neos, flares, kp_info, storms):
    """Pick top 2-3 events for the "What to Watch" panel."""
    highlights = []
    # Closest NEO
    if neos:
        closest = neos[0]
        severity = 'red' if closest['is_hazardous'] else ('orange' if closest['miss_au_raw'] < 0.05 else 'teal')
        highlights.append({
            'title': f"Close Approach: {closest['name']}",
            'detail': f"{closest['miss_lunar']} lunar distances — {closest['close_approach_date']}",
            'severity': severity,
            'section': 'neo',
        })
    # Strongest recent flare
    if flares:
        top = flares[0]
        highlights.append({
            'title': f"Solar Flare: {top['classType']}",
            'detail': f"Peak {top['peakTime']} — {top['sourceLocation'] or 'location N/A'}",
            'severity': _flare_severity(top['classType']),
            'section': 'weather',
        })
    # Kp / storm
    if kp_info and kp_info['kp'] >= 4:
        highlights.append({
            'title': f"Kp Index: {kp_info['kp']:.0f} ({kp_info['gScale']})",
            'detail': f"Measured {kp_info['timestamp']}",
            'severity': _severity_color(kp_info['kp']),
            'section': 'weather',
        })
    elif storms:
        s = storms[0]
        highlights.append({
            'title': f"Recent Storm: {s['gScale']}",
            'detail': f"Started {s['startTime']} — peak Kp {s['kpMax']}",
            'severity': _severity_color(s['kpMax']),
            'section': 'weather',
        })
    return highlights[:3]


@app.route('/space-intelligence')
def space_intelligence():
    """Real-Time Space Intelligence page — shell loads instantly, data via API."""
    return render_template('space-intelligence.html')


@app.route('/api/space-intelligence')
@limiter.limit('10/minute')
def api_space_intelligence():
    """JSON API: fetch all space-intelligence data for client-side rendering."""
    neos = _fetch_neo_data()
    flares = _fetch_solar_flares()
    cmes = _fetch_cme()
    storms = _fetch_geomagnetic()
    kp_info = _fetch_kp_index()
    kp_forecast = _fetch_kp_forecast()
    highlights = _build_highlights(neos, flares, kp_info, storms)
    refreshed = datetime.datetime.now(datetime.timezone.utc).strftime('%B %d, %Y %H:%M UTC')

    return jsonify(
        neos=neos,
        flares=[{'classType': f.get('classType', ''), 'peakTime': f.get('peakTime', ''), 'sourceLocation': f.get('sourceLocation', '')} for f in (flares or [])],
        cmes=[{'startTime': c.get('startTime', ''), 'speed': c.get('cmeAnalyses', [{}])[0].get('speed') if c.get('cmeAnalyses') else c.get('speed'), 'halfAngle': c.get('cmeAnalyses', [{}])[0].get('halfAngle') if c.get('cmeAnalyses') else c.get('halfAngle')} for c in (cmes or [])],
        storms=[{'startTime': s.get('startTime', ''), 'kpMax': s.get('allKpIndex', [{}])[-1].get('kpIndex') if s.get('allKpIndex') else s.get('kpMax', ''), 'gScale': _kp_to_g(s.get('allKpIndex', [{}])[-1].get('kpIndex', 0) if s.get('allKpIndex') else s.get('kpMax', 0))} for s in (storms or [])],
        kp_info=kp_info,
        kp_forecast=kp_forecast,
        highlights=highlights,
        refreshed=refreshed,
    )


# ---------------------------------------------------------------------------
# Orbital Density Intelligence: CelesTrak data helpers
# ---------------------------------------------------------------------------

import math as _math

_EARTH_RADIUS_KM = 6371.0  # Mean Earth radius
_GEO_ALTITUDE_KM = 35786.0  # Geostationary altitude


def _mean_motion_to_altitude(mean_motion, eccentricity=0.0):
    """Convert mean motion (rev/day) to approximate altitude (km) above Earth."""
    if not mean_motion or mean_motion <= 0:
        return None
    mu = 398600.4418  # Earth gravitational parameter km^3/s^2
    period_sec = 86400.0 / mean_motion
    semi_major = (mu * (period_sec / (2 * _math.pi)) ** 2) ** (1.0 / 3.0)
    altitude = semi_major * (1.0 - eccentricity) - _EARTH_RADIUS_KM  # perigee altitude
    return round(altitude, 1) if altitude > 0 else None


def _classify_orbit(altitude_km, eccentricity):
    """Classify orbit regime from perigee altitude and eccentricity."""
    if eccentricity and eccentricity > 0.25:
        return 'HEO'
    if altitude_km is None:
        return 'Other'
    if altitude_km < 2000:
        return 'LEO'
    if altitude_km < 35586:
        return 'MEO'
    if altitude_km <= 35986:
        return 'GEO'
    return 'Other'


def _extract_operator(name):
    """Heuristic operator extraction from OBJECT_NAME."""
    if not name:
        return 'Unknown'
    upper = name.upper().strip()
    if upper.startswith('STARLINK'):
        return 'SpaceX Starlink'
    if upper.startswith('ONEWEB'):
        return 'OneWeb'
    if upper.startswith('IRIDIUM'):
        return 'Iridium'
    if upper.startswith('COSMOS') or upper.startswith('KOSMOS'):
        return 'Russia (Cosmos)'
    if upper.startswith('GPS'):
        return 'US GPS'
    if upper.startswith('GLOBALSTAR'):
        return 'Globalstar'
    if upper.startswith('ORBCOMM'):
        return 'ORBCOMM'
    if upper.startswith('BEIDOU') or upper.startswith('CZ-'):
        return 'China (BeiDou/CZ)'
    if upper.startswith('GALILEO'):
        return 'EU Galileo'
    if upper.startswith('INTELSAT'):
        return 'Intelsat'
    if upper.startswith('SES'):
        return 'SES'
    if upper.startswith('TELESAT'):
        return 'Telesat'
    if upper.startswith('YAOGAN') or upper.startswith('SHIYAN') or upper.startswith('SHIJIAN'):
        return 'China (Military/Civil)'
    if upper.startswith('GOES') or upper.startswith('NOAA'):
        return 'NOAA'
    if upper.startswith('LANDSAT') or upper.startswith('TERRA') or upper.startswith('AQUA'):
        return 'NASA'
    if upper.startswith('NAVSTAR'):
        return 'US GPS'
    return 'Other'


def _fetch_celestrak_active():
    """Fetch active satellite catalog from CelesTrak GP API.

    CelesTrak throttles GROUP=active to once per 2-hour update cycle (403
    with 'has not updated' message).  On a cold start with no in-memory
    cache the primary URL will fail.  As a fallback, we merge several
    smaller group queries that are not subject to the same restriction.
    """
    raw = _si_cached_get(
        'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json',
        'celestrak_active')
    if raw and isinstance(raw, list):
        return raw

    # Fallback: fetch smaller groups and merge (no dedup needed for charts)
    # Use NAME=STARLINK instead of GROUP=starlink because the GROUP
    # endpoint has a per-IP 2-hour cooldown that blocks cold starts.
    # NOTE: 'iridium' is intentionally omitted — CelesTrak has been
    # returning non-JSON for that group, which floods logs with
    # 'Expecting value: line 1 column 1 (char 0)' on every request.
    _FALLBACK_GROUPS = [
        'oneweb', 'stations', 'weather', 'geo',
        'resource', 'science', 'gnss', 'globalstar',
        'amateur', 'military',
    ]
    merged = []
    # Starlink via NAME query (not subject to GROUP rate limit)
    starlink_part = _si_cached_get(
        'https://celestrak.org/NORAD/elements/gp.php?NAME=STARLINK&FORMAT=json',
        'celestrak_starlink_name')
    if starlink_part and isinstance(starlink_part, list):
        merged.extend(starlink_part)
    for grp in _FALLBACK_GROUPS:
        part = _si_cached_get(
            f'https://celestrak.org/NORAD/elements/gp.php?GROUP={grp}&FORMAT=json',
            f'celestrak_{grp}')
        if part and isinstance(part, list):
            merged.extend(part)
    if merged:
        print(f"[orbital-density] fallback: merged {len(merged)} sats from {len(_FALLBACK_GROUPS)} groups")
        return merged
    return None


def _process_orbital_data(satellites):
    """Process raw CelesTrak satellite list into aggregated stats."""
    orbit_counts = {'LEO': 0, 'MEO': 0, 'GEO': 0, 'HEO': 0, 'Other': 0}
    operator_counts = {}
    altitude_bins = {}  # bin_start -> count
    starlink_count = 0
    starlink_altitudes = {}
    total = 0

    for sat in satellites:
        name = sat.get('OBJECT_NAME', '')
        mm = sat.get('MEAN_MOTION')
        ecc = sat.get('ECCENTRICITY', 0.0)
        try:
            mm = float(mm)
            ecc = float(ecc)
        except (TypeError, ValueError):
            continue

        altitude = _mean_motion_to_altitude(mm, ecc)
        orbit_class = _classify_orbit(altitude, ecc)
        orbit_counts[orbit_class] = orbit_counts.get(orbit_class, 0) + 1
        total += 1

        # Operator
        op = _extract_operator(name)
        operator_counts[op] = operator_counts.get(op, 0) + 1

        # Altitude histogram (100 km bins, up to 2000 km for LEO detail)
        if altitude is not None and 0 < altitude <= 2000:
            bin_start = int(altitude // 100) * 100
            altitude_bins[bin_start] = altitude_bins.get(bin_start, 0) + 1

        # Starlink
        if name.upper().startswith('STARLINK'):
            starlink_count += 1
            if altitude is not None:
                shell = int(altitude // 10) * 10  # 10 km bins for shells
                starlink_altitudes[shell] = starlink_altitudes.get(shell, 0) + 1

    # Sort operators by count, top 10
    top_operators = sorted(operator_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Sort altitude bins
    sorted_alt = sorted(altitude_bins.items(), key=lambda x: x[0])

    # Starlink shell breakdown (top 5 altitude bands)
    starlink_shells = sorted(starlink_altitudes.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'total_active': total,
        'orbit_distribution': orbit_counts,
        'top_operators': [{'name': op, 'count': cnt} for op, cnt in top_operators],
        'altitude_histogram': {
            'labels': [f"{b}-{b+100}" for b, _ in sorted_alt],
            'values': [c for _, c in sorted_alt],
        },
        'starlink': {
            'count': starlink_count,
            'shells': [{'altitude_km': alt, 'count': cnt} for alt, cnt in starlink_shells],
        },
    }


@app.route('/orbital-density')
def orbital_density():
    """Orbital Density Intelligence page — shell loads instantly, data via API."""
    return render_template('orbital-density.html')


@app.route('/api/orbital-density')
@limiter.limit('10/minute')
def api_orbital_density():
    """JSON API: fetch orbital density data for client-side rendering."""
    try:
        satellites = _fetch_celestrak_active()
        if not satellites:
            return jsonify(error='Satellite data temporarily unavailable'), 503

        data = _process_orbital_data(satellites)
        data['refreshed'] = datetime.datetime.now(
            datetime.timezone.utc).strftime('%B %d, %Y %H:%M UTC')

        # Cross-reference Kp for geomagnetic drag context
        kp_info = _fetch_kp_index()
        if kp_info:
            data['kp_info'] = kp_info

        return jsonify(**data)
    except Exception:
        return jsonify(error='Failed to process orbital data'), 500


# ----------------------------------------------------------------------
# Live Orbit 3D — server-side Keplerian propagation + scene narrator
# ----------------------------------------------------------------------

# Earth gravitational parameter (km^3/s^2) and equatorial radius (km)
_EARTH_MU = 398600.4418
_EARTH_R = 6378.137


def _solve_kepler(M, e, tol=1e-6, max_iter=20):
    """Solve Kepler's equation M = E - e*sin(E) via Newton-Raphson.

    M and E in radians.  e is eccentricity (0 <= e < 1).  Returns
    eccentric anomaly E.  Converges quickly for typical Earth orbits.
    """
    # Good starting guess
    E = M if e < 0.8 else _math.pi
    for _ in range(max_iter):
        f = E - e * _math.sin(E) - M
        fp = 1.0 - e * _math.cos(E)
        dE = -f / fp
        E += dE
        if abs(dE) < tol:
            break
    return E


def _propagate_satellite(sat, now_utc):
    """Compute current ECI position (km) for a satellite from its OMM elements.

    Uses two-body Keplerian propagation — accurate to a few km for
    short propagation intervals (typical TLE epoch is hours to days
    old).  Good enough for visualization; not for collision avoidance.

    Returns (x, y, z) in km, or None if elements are invalid.
    """
    try:
        # Required orbital elements
        n_rev_day = float(sat['MEAN_MOTION'])         # revs/day
        e = float(sat['ECCENTRICITY'])
        i = _math.radians(float(sat['INCLINATION']))
        raan = _math.radians(float(sat['RA_OF_ASC_NODE']))
        argp = _math.radians(float(sat['ARG_OF_PERICENTER']))
        M0 = _math.radians(float(sat['MEAN_ANOMALY']))
        epoch_str = sat['EPOCH']
    except (KeyError, TypeError, ValueError):
        return None

    if not (0.0 <= e < 1.0) or n_rev_day <= 0:
        return None

    # Mean motion in rad/s; semi-major axis from n
    n = n_rev_day * 2.0 * _math.pi / 86400.0
    a = (_EARTH_MU / (n * n)) ** (1.0 / 3.0)

    # Time since epoch (seconds)
    try:
        # CelesTrak gives ISO-8601 without timezone; treat as UTC
        epoch = datetime.datetime.fromisoformat(epoch_str)
        if epoch.tzinfo is None:
            epoch = epoch.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return None
    dt = (now_utc - epoch).total_seconds()

    # Mean anomaly at current time
    M = (M0 + n * dt) % (2.0 * _math.pi)

    # Eccentric anomaly
    E = _solve_kepler(M, e)

    # True anomaly and radius
    cos_nu = (_math.cos(E) - e) / (1.0 - e * _math.cos(E))
    sin_nu = (_math.sqrt(1.0 - e * e) * _math.sin(E)) / (1.0 - e * _math.cos(E))
    r = a * (1.0 - e * _math.cos(E))

    # Position in perifocal frame
    x_p = r * cos_nu
    y_p = r * sin_nu

    # Rotate perifocal -> ECI (3-1-3 rotation: argp, i, raan)
    cos_argp, sin_argp = _math.cos(argp), _math.sin(argp)
    cos_i, sin_i = _math.cos(i), _math.sin(i)
    cos_raan, sin_raan = _math.cos(raan), _math.sin(raan)

    # Combined rotation matrix elements (standard formulation)
    x = (cos_raan * cos_argp - sin_raan * sin_argp * cos_i) * x_p + \
        (-cos_raan * sin_argp - sin_raan * cos_argp * cos_i) * y_p
    y = (sin_raan * cos_argp + cos_raan * sin_argp * cos_i) * x_p + \
        (-sin_raan * sin_argp + cos_raan * cos_argp * cos_i) * y_p
    z = (sin_argp * sin_i) * x_p + (cos_argp * sin_i) * y_p

    return (x, y, z)


def _classify_orbit_simple(altitude_km):
    """Classify orbit class for live-orbit rendering (matches density page legend)."""
    if altitude_km < 2000:
        return 'LEO'
    if altitude_km < 35586:
        return 'MEO'
    if altitude_km < 35986:
        return 'GEO'
    return 'HEO'


def _compute_live_positions(satellites, max_points=5000):
    """Compute current ECI positions for satellites with intelligent downsampling.

    Returns list of {n, x, y, z, c} dicts (short keys to keep payload small).
    'c' is orbit class: 0=LEO, 1=MEO, 2=GEO, 3=HEO.
    """
    if not satellites:
        return []

    now = datetime.datetime.now(datetime.timezone.utc)

    # First pass: classify everything
    classified = {'LEO': [], 'MEO': [], 'GEO': [], 'HEO': []}
    for sat in satellites:
        try:
            n_rev_day = float(sat.get('MEAN_MOTION', 0))
            e = float(sat.get('ECCENTRICITY', 0))
        except (TypeError, ValueError):
            continue
        if n_rev_day <= 0:
            continue
        n = n_rev_day * 2.0 * _math.pi / 86400.0
        a = (_EARTH_MU / (n * n)) ** (1.0 / 3.0)
        alt = a * (1.0 - e) - _EARTH_R  # perigee altitude
        if e > 0.25:
            cls = 'HEO'
        else:
            cls = _classify_orbit_simple(alt)
        classified[cls].append(sat)

    # Downsample LEO (mostly Starlink) to fit budget; keep all MEO/GEO/HEO
    keep_meo = classified['MEO']
    keep_geo = classified['GEO']
    keep_heo = classified['HEO']
    leo_budget = max(0, max_points - len(keep_meo) - len(keep_geo) - len(keep_heo))
    leo_all = classified['LEO']
    if len(leo_all) > leo_budget and leo_budget > 0:
        step = len(leo_all) / leo_budget
        keep_leo = [leo_all[int(i * step)] for i in range(leo_budget)]
    else:
        keep_leo = leo_all

    class_code = {'LEO': 0, 'MEO': 1, 'GEO': 2, 'HEO': 3}
    out = []
    for cls, group in (('LEO', keep_leo), ('MEO', keep_meo),
                       ('GEO', keep_geo), ('HEO', keep_heo)):
        code = class_code[cls]
        for sat in group:
            pos = _propagate_satellite(sat, now)
            if pos is None:
                continue
            x, y, z = pos
            out.append({
                'n': sat.get('OBJECT_NAME', '')[:40],
                'x': round(x, 1),
                'y': round(y, 1),
                'z': round(z, 1),
                'c': code,
            })
    return out


def _generate_scene_narrative(stats, neos, kp_info):
    """Templated scene narrator — Option A (no LLM, deterministic).

    Builds a 2-3 sentence narrative from cached structured data.  Pure
    Python; no external calls; identical input -> identical output.
    """
    parts = []

    total = stats.get('total_active', 0)
    leo = stats.get('orbit_distribution', {}).get('LEO', 0)
    geo = stats.get('orbit_distribution', {}).get('GEO', 0)
    if total:
        parts.append(
            f"What you're seeing is real. {total:,} active satellites are "
            f"circling Earth right now — {leo:,} hugging Low Earth Orbit, "
            f"{geo:,} fixed in the distant geostationary ring 35,786 km out."
        )

    # Top operator hook
    top_ops = stats.get('top_operators', [])
    if top_ops:
        leader = top_ops[0]
        share = (leader['count'] / total * 100) if total else 0
        if share >= 30:
            parts.append(
                f"{leader['name']} alone accounts for "
                f"{share:.0f}% of active satellites — concentrated in the 540 km band."
            )

    # NEO hook — pick the closest hazardous, otherwise the closest of any
    if neos:
        haz = [n for n in neos if n.get('is_hazardous')]
        nearest = haz[0] if haz else neos[0]
        au = nearest.get('miss_au_raw', 999)
        lunar = nearest.get('miss_lunar', '?')
        date = nearest.get('close_approach_date', 'this week')
        if nearest.get('is_hazardous') and au < 0.05:
            parts.append(
                f"One potentially hazardous asteroid passes inside {lunar} "
                f"lunar distances on {date} — close, but cataloged."
            )
        else:
            parts.append(
                f"Closest asteroid this week: {nearest.get('name', '?')} "
                f"at {lunar} lunar distances."
            )

    # Space weather hook
    if kp_info:
        kp = kp_info.get('kp_value')
        if kp is not None:
            if kp >= 5:
                parts.append(
                    f"Geomagnetic conditions are elevated (Kp {kp:.0f}) — "
                    f"satellite drag and HF radio are seeing it."
                )
            elif kp >= 3:
                parts.append(
                    f"Geomagnetic activity is unsettled (Kp {kp:.0f}); "
                    f"baseline drag remains nominal."
                )
            else:
                parts.append(
                    f"Geomagnetic conditions are quiet (Kp {kp:.0f}). "
                    f"The orbital environment is busy but stable."
                )

    if not parts:
        return ("The orbital environment is being observed. Live data will "
                "appear as soon as the upstream sources respond.")

    return ' '.join(parts)


def _fetch_neo_data_safe():
    """Fetch NEO data, returning [] on any failure (used by /live-orbit)."""
    try:
        return _fetch_neo_data()
    except Exception:
        return []


@app.route('/live-orbit')
def live_orbit():
    """Live Orbit 3D page — shell loads instantly, scene populated via API."""
    return render_template('live-orbit.html')


@app.route('/api/live-orbit-data')
@limiter.limit('10/minute')
def api_live_orbit_data():
    """Combined JSON endpoint for the 3D scene.

    Bundles satellite positions + NEO list + summary stats + narrator
    into one response so the client makes a single fetch per refresh.
    """
    try:
        satellites = _fetch_celestrak_active()
        positions = _compute_live_positions(satellites or [], max_points=5000)
        stats = _process_orbital_data(satellites or [])
        neos = _fetch_neo_data_safe()[:10]
        kp_info = _fetch_kp_index() or {}

        narrative = _generate_scene_narrative(stats, neos, kp_info)

        # Trim NEO payload to fields the client needs
        neos_lite = [{
            'name': n['name'],
            'miss_au': n['miss_au_raw'],
            'miss_lunar': n['miss_lunar'],
            'velocity_kph': n['velocity_kph'],
            'date': n['close_approach_date'],
            'hazardous': n['is_hazardous'],
        } for n in neos]

        return jsonify({
            'positions': positions,
            'neos': neos_lite,
            'narrative': narrative,
            'stats': {
                'total_active': stats.get('total_active', 0),
                'orbit_distribution': stats.get('orbit_distribution', {}),
                'top_operator': (stats.get('top_operators') or [{}])[0],
                'kp': kp_info.get('kp_value'),
                'kp_label': kp_info.get('label'),
                'rendered_count': len(positions),
            },
            'refreshed': datetime.datetime.now(
                datetime.timezone.utc).strftime('%B %d, %Y %H:%M UTC'),
            'earth_radius_km': _EARTH_R,
        })
    except Exception as exc:
        print(f"[live-orbit] data fetch failed: {exc}")
        return jsonify(error='Live orbit data temporarily unavailable'), 503


@app.route('/api/status')
@limiter.limit('10/minute')
def api_status():
    """API endpoint for system status."""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'cdflib_available': _CDFLIB_AVAILABLE,
        'data_sources': [
            'NASA JPL HORIZONS (Position)',
            'NASA SPDF Archives (Magnetometer)',
            'Realistic Synthetic Fallback',
            'CelesTrak GP API (Orbital Density)',
        ]
    })

if __name__ == '__main__':
    print("Starting Voyager 1 Web Analysis Dashboard...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true', port=5000)
