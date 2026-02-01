#!/usr/bin/env python3
"""
Simple web server to display pipeline results in a browser.
Serves the frontend and provides API endpoints for CSV data.
"""

import json
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import pandas as pd

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

PORT = 8000


@app.route('/api/summary')
def get_summary():
    """Get summary statistics"""
    scores_path = Path("data/user_scores.csv")
    if not scores_path.exists():
        return jsonify({"error": "No data available. Run pipeline first."})
    
    df = pd.read_csv(scores_path)
    
    summary = {
        "totalUsers": len(df),
        "meanScore": float(df['score'].mean()),
        "medianScore": float(df['score'].median()),
        "highIntent": int((df['score_label'] == 'high').sum()),
        "mediumIntent": int((df['score_label'] == 'medium').sum()),
        "lowIntent": int((df['score_label'] == 'low').sum())
    }
    
    return jsonify(summary)


@app.route('/api/users')
def get_users():
    """Get all users data"""
    scores_path = Path("data/user_scores.csv")
    if not scores_path.exists():
        return jsonify({"error": "No data available"})
    
    df = pd.read_csv(scores_path)
    users = df.fillna(0).to_dict('records')
    
    # Convert numeric columns properly
    for user in users:
        for key, value in user.items():
            if pd.isna(value):
                user[key] = 0
            elif isinstance(value, (int, float)):
                user[key] = float(value) if not pd.isna(value) else 0
    
    return jsonify(users)


@app.route('/api/top-users')
def get_top_users():
    """Get top users"""
    scores_path = Path("data/user_scores.csv")
    if not scores_path.exists():
        return jsonify({"error": "No data available"})
    
    df = pd.read_csv(scores_path)
    top_users = df.sort_values("score", ascending=False).head(20).fillna(0)
    
    # Select relevant columns
    cols = [
        "user_id", "username", "score", "score_label", "explanation",
        "signups", "calendar_bookings", "demo_request_clicks",
        "pricing_page_views", "location_city"
    ]
    cols = [c for c in cols if c in top_users.columns]
    
    users = top_users[cols].to_dict('records')
    
    # Convert numeric columns
    for user in users:
        for key, value in user.items():
            if pd.isna(value):
                user[key] = 0
            elif isinstance(value, (int, float)):
                user[key] = float(value) if not pd.isna(value) else 0
    
    return jsonify(users)


@app.route('/api/distribution')
def get_distribution():
    """Get score distribution data"""
    scores_path = Path("data/user_scores.csv")
    if not scores_path.exists():
        return jsonify({"error": "No data available"})
    
    df = pd.read_csv(scores_path)
    
    # Create bins
    bins = [0, 20, 40, 60, 80, 100]
    labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
    df['score_bin'] = pd.cut(df['score'], bins=bins, labels=labels, include_lowest=True)
    
    distribution = df['score_bin'].value_counts().sort_index().to_dict()
    
    result = {
        "ranges": labels,
        "counts": [int(distribution.get(label, 0)) for label in labels]
    }
    
    return jsonify(result)


@app.route('/')
def index():
    """Serve the main page"""
    # Try to serve from frontend/dist if built
    dist_index = Path("frontend/dist/index.html")
    if dist_index.exists():
        return send_file(str(dist_index))
    
    # Fallback: serve our standalone results page
    results_html = Path("results.html")
    if results_html.exists():
        return send_file(str(results_html))
    
    # Ultimate fallback: return a simple message
    return """
    <html>
        <head><title>Gesture Scoring System</title></head>
        <body>
            <h1>Gesture User Scoring System</h1>
            <p>Results will be displayed here. Make sure the pipeline has been run.</p>
        </body>
    </html>
    """


def start_server(open_browser=True):
    """Start the web server"""
    url = f'http://localhost:{PORT}'
    print(f"\n{'='*70}")
    print(f"Web server started at {url}")
    print(f"{'='*70}\n")
    
    if open_browser:
        # Wait a moment for server to start, then open browser
        def open_browser_delayed():
            time.sleep(1.5)
            webbrowser.open(url)
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    start_server()
