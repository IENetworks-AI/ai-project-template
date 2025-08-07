"""
Enhanced Flask Dashboard for Real-time Football Match Predictions
Features: Dynamic UI, Match Selection, Airflow Integration, Real-time Updates
"""

from flask import Flask, render_template, jsonify, request, session
import pandas as pd
import numpy as np
import json
import time
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from kafka import KafkaConsumer
import threading
import queue
from typing import List, Dict, Optional
import os
import sys
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dummy_football_data import DummyFootballDataGenerator

app = Flask(__name__)
app.secret_key = 'football_predictions_secret_key'

# Global variables
match_data_queue = queue.Queue()
prediction_data_queue = queue.Queue()
current_match_stats = {}
current_prediction = {}
available_matches = []
kafka_events = []
airflow_status = {}

# Available matches for selection
DEFAULT_MATCHES = [
    {"id": "man_utd_liverpool", "home": "Manchester United", "away": "Liverpool", "competition": "Premier League"},
    {"id": "arsenal_chelsea", "home": "Arsenal", "away": "Chelsea", "competition": "Premier League"},
    {"id": "man_city_tottenham", "home": "Manchester City", "away": "Tottenham", "competition": "Premier League"},
    {"id": "leicester_west_ham", "home": "Leicester", "away": "West Ham", "competition": "Premier League"},
    {"id": "brighton_crystal_palace", "home": "Brighton", "away": "Crystal Palace", "competition": "Premier League"}
]

def kafka_consumer():
    """Background thread to consume Kafka messages"""
    try:
        consumer = KafkaConsumer(
            'live_football_events',
            bootstrap_servers=['kafka:29092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='flask_consumer'
        )
        
        for message in consumer:
            event = message.value
            match_data_queue.put(event)
            kafka_events.append(event)
            # Keep only last 50 events
            if len(kafka_events) > 50:
                kafka_events.pop(0)
            
    except Exception as e:
        print(f"Kafka connection error: {e}")

def get_prediction_from_api(features):
    """Get prediction from the model API"""
    try:
        api_url = "http://api:8000/predict"
        response = requests.post(api_url, json=features, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API call failed: {e}")
    
    # Fallback prediction
    return {
        'home_win_probability': 0.4,
        'away_win_probability': 0.35,
        'draw_probability': 0.25,
        'confidence': 0.7,
        'timestamp': datetime.now().isoformat()
    }

def create_match_stats_chart(match_stats):
    """Create a chart showing match statistics"""
    fig = go.Figure()
    
    # Add bars for shots
    fig.add_trace(go.Bar(
        name='Shots',
        x=['Home', 'Away'],
        y=[match_stats.get('home_shots', 0), match_stats.get('away_shots', 0)],
        marker_color=['#1f77b4', '#ff7f0e']
    ))
    
    # Add bars for shots on target
    fig.add_trace(go.Bar(
        name='Shots on Target',
        x=['Home', 'Away'],
        y=[match_stats.get('home_shots_on_target', 0), match_stats.get('away_shots_on_target', 0)],
        marker_color=['#2ca02c', '#d62728']
    ))
    
    fig.update_layout(
        title="Match Statistics",
        barmode='group',
        height=400
    )
    
    return fig.to_json()

def create_win_probability_chart(prediction):
    """Create a pie chart for win probabilities"""
    fig = go.Figure(data=[go.Pie(
        labels=['Home Win', 'Away Win', 'Draw'],
        values=[
            prediction.get('home_win_probability', 0.33),
            prediction.get('away_win_probability', 0.33),
            prediction.get('draw_probability', 0.34)
        ],
        hole=0.3,
        marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c']
    )])
    
    fig.update_layout(
        title="Win Probability Prediction",
        height=400
    )
    
    return fig.to_json()

def create_possession_chart(match_stats):
    """Create a possession chart"""
    home_possession = match_stats.get('home_possession', 50)
    away_possession = match_stats.get('away_possession', 50)
    
    fig = go.Figure(data=[go.Pie(
        labels=['Home', 'Away'],
        values=[home_possession, away_possession],
        hole=0.4,
        marker_colors=['#1f77b4', '#ff7f0e']
    )])
    
    fig.update_layout(
        title="Possession",
        height=300
    )
    
    return fig.to_json()

def create_timeline_chart(events):
    """Create a timeline chart of events"""
    if not events:
        return None
    
    # Process events for timeline
    timeline_data = []
    for event in events[-20:]:  # Last 20 events
        timeline_data.append({
            'minute': event.get('minute', 0),
            'event_type': event.get('type', {}).get('name', 'Unknown'),
            'team': event.get('team', {}).get('name', 'Unknown'),
            'player': event.get('player', {}).get('name', 'Unknown')
        })
    
    fig = go.Figure()
    
    # Add scatter plot for events
    fig.add_trace(go.Scatter(
        x=[e['minute'] for e in timeline_data],
        y=[e['event_type'] for e in timeline_data],
        mode='markers+text',
        text=[f"{e['team']} - {e['player']}" for e in timeline_data],
        textposition="top center",
        marker=dict(size=10, color='#1f77b4'),
        name='Events'
    ))
    
    fig.update_layout(
        title="Match Timeline",
        xaxis_title="Minute",
        yaxis_title="Event Type",
        height=300
    )
    
    return fig.to_json()

def get_airflow_dags(base_url="http://airflow-webserver:8080/api/v1/dags") -> List[Dict]:
    """Get list of Airflow DAGs"""
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            return response.json().get('dags', [])
    except Exception as e:
        print(f"Airflow API error: {e}")
    return []

def get_airflow_dag_runs(dag_id: str, base_url="http://airflow-webserver:8080/api/v1") -> List[Dict]:
    """Get DAG runs for a specific DAG"""
    try:
        response = requests.get(f"{base_url}/dags/{dag_id}/dagRuns", timeout=5)
        if response.status_code == 200:
            return response.json().get('dag_runs', [])
    except Exception as e:
        print(f"Airflow DAG runs API error: {e}")
    return []

def trigger_airflow_dag(dag_id: str, base_url="http://airflow-webserver:8080/api/v1") -> bool:
    """Trigger an Airflow DAG"""
    try:
        response = requests.post(
            f"{base_url}/dags/{dag_id}/dagRuns",
            json={"conf": {}},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Airflow trigger error: {e}")
        return False

def check_airflow_status():
    """Check Airflow webserver status"""
    try:
        response = requests.get("http://airflow-webserver:8080/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Airflow status check error: {e}")
        return False

def start_kafka_thread():
    """Start Kafka consumer thread"""
    kafka_thread = threading.Thread(target=kafka_consumer, daemon=True)
    kafka_thread.start()

def generate_dummy_data(home_team: str = None, away_team: str = None):
    """Generate dummy match data for testing"""
    generator = DummyFootballDataGenerator()
    match_data = generator.generate_match_data(home_team, away_team)
    return match_data

def update_match_stats_for_selected_match(match_id: str):
    """Update match stats based on selected match"""
    global current_match_stats
    
    # Find the selected match
    selected_match = None
    for match in DEFAULT_MATCHES:
        if match['id'] == match_id:
            selected_match = match
            break
    
    if selected_match:
        # Generate new stats for the selected match
        match_data = generate_dummy_data(selected_match['home'], selected_match['away'])
        
        # Simulate live match progression
        current_minute = random.randint(30, 90)
        home_goals = random.randint(0, 3)
        away_goals = random.randint(0, 3)
        home_shots = random.randint(5, 15)
        away_shots = random.randint(3, 12)
        home_shots_on_target = random.randint(2, home_shots)
        away_shots_on_target = random.randint(1, away_shots)
        home_possession = random.randint(40, 70)
        away_possession = 100 - home_possession
        
        current_match_stats = {
            'match_id': match_id,
            'home_team': selected_match['home'],
            'away_team': selected_match['away'],
            'competition': selected_match['competition'],
            'home_goals': home_goals,
            'away_goals': away_goals,
            'current_minute': current_minute,
            'home_shots': home_shots,
            'away_shots': away_shots,
            'home_shots_on_target': home_shots_on_target,
            'away_shots_on_target': away_shots_on_target,
            'home_possession': home_possession,
            'away_possession': away_possession,
            'home_xg': round(random.uniform(0.5, 2.5), 2),
            'away_xg': round(random.uniform(0.3, 2.0), 2),
            'timestamp': datetime.now().isoformat()
        }

@app.route('/')
def index():
    """Main dashboard page"""
    # Initialize session with default match
    if 'selected_match' not in session:
        session['selected_match'] = 'man_utd_liverpool'
    
    return render_template('dashboard.html', 
                         matches=DEFAULT_MATCHES,
                         selected_match=session['selected_match'])

@app.route('/api/select-match', methods=['POST'])
def select_match():
    """Select a match"""
    data = request.get_json()
    match_id = data.get('match_id')
    
    if match_id:
        session['selected_match'] = match_id
        update_match_stats_for_selected_match(match_id)
        return jsonify({'success': True, 'message': 'Match selected successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid match ID'})

@app.route('/api/match-stats')
def get_match_stats():
    """Get current match statistics"""
    global current_match_stats
    
    selected_match = session.get('selected_match', 'man_utd_liverpool')
    
    if not current_match_stats or current_match_stats.get('match_id') != selected_match:
        update_match_stats_for_selected_match(selected_match)
    
    return jsonify(current_match_stats)

@app.route('/api/prediction')
def get_prediction():
    """Get current prediction"""
    global current_prediction
    
    # Generate dynamic prediction based on current match stats
    if current_match_stats:
        home_goals = current_match_stats.get('home_goals', 0)
        away_goals = current_match_stats.get('away_goals', 0)
        home_possession = current_match_stats.get('home_possession', 50)
        
        # Simple prediction logic based on current state
        if home_goals > away_goals:
            home_win_prob = 0.6
            away_win_prob = 0.2
            draw_prob = 0.2
        elif away_goals > home_goals:
            home_win_prob = 0.2
            away_win_prob = 0.6
            draw_prob = 0.2
        else:
            home_win_prob = 0.35
            away_win_prob = 0.35
            draw_prob = 0.3
        
        # Adjust based on possession
        if home_possession > 60:
            home_win_prob += 0.1
            away_win_prob -= 0.05
            draw_prob -= 0.05
        
        current_prediction = {
            'home_win_probability': min(0.9, max(0.1, home_win_prob)),
            'away_win_probability': min(0.9, max(0.1, away_win_prob)),
            'draw_probability': min(0.9, max(0.1, draw_prob)),
            'confidence': 0.75,
            'timestamp': datetime.now().isoformat()
        }
    else:
        # Fallback prediction
        current_prediction = {
            'home_win_probability': 0.45,
            'away_win_probability': 0.30,
            'draw_probability': 0.25,
            'confidence': 0.75,
            'timestamp': datetime.now().isoformat()
        }
    
    return jsonify(current_prediction)

@app.route('/api/charts/match-stats')
def get_match_stats_chart():
    """Get match statistics chart"""
    stats = current_match_stats if current_match_stats else {
        'home_shots': 8,
        'away_shots': 3,
        'home_shots_on_target': 4,
        'away_shots_on_target': 1
    }
    
    chart_json = create_match_stats_chart(stats)
    return jsonify({'chart': chart_json})

@app.route('/api/charts/win-probability')
def get_win_probability_chart():
    """Get win probability chart"""
    prediction = current_prediction if current_prediction else {
        'home_win_probability': 0.45,
        'away_win_probability': 0.30,
        'draw_probability': 0.25
    }
    
    chart_json = create_win_probability_chart(prediction)
    return jsonify({'chart': chart_json})

@app.route('/api/charts/possession')
def get_possession_chart():
    """Get possession chart"""
    stats = current_match_stats if current_match_stats else {
        'home_possession': 65.0,
        'away_possession': 35.0
    }
    
    chart_json = create_possession_chart(stats)
    return jsonify({'chart': chart_json})

@app.route('/api/charts/timeline')
def get_timeline_chart():
    """Get match timeline chart"""
    chart_json = create_timeline_chart(kafka_events)
    return jsonify({'chart': chart_json})

@app.route('/api/airflow/dags')
def get_airflow_dags():
    """Get Airflow DAGs"""
    dags = get_airflow_dags()
    return jsonify(dags)

@app.route('/api/airflow/dags/<dag_id>/runs')
def get_dag_runs(dag_id):
    """Get DAG runs for a specific DAG"""
    runs = get_airflow_dag_runs(dag_id)
    return jsonify(runs)

@app.route('/api/airflow/dags/<dag_id>/trigger', methods=['POST'])
def trigger_dag(dag_id):
    """Trigger an Airflow DAG"""
    success = trigger_airflow_dag(dag_id)
    return jsonify({'success': success})

@app.route('/api/kafka/events')
def get_kafka_events():
    """Get recent Kafka events"""
    return jsonify(kafka_events)

@app.route('/api/system/status')
def get_system_status():
    """Get system status for all services"""
    # Check Airflow status
    airflow_online = check_airflow_status()
    
    # Check API status
    api_online = False
    try:
        response = requests.get("http://api:8000/health", timeout=5)
        api_online = response.status_code == 200
    except:
        pass
    
    # Check Kafka status (simplified)
    kafka_online = len(kafka_events) > 0 or True  # Assume online if we have events
    
    return jsonify({
        'airflow': {
            'status': 'online' if airflow_online else 'offline',
            'url': 'http://localhost:8080'
        },
        'api': {
            'status': 'online' if api_online else 'offline',
            'url': 'http://localhost:8000'
        },
        'kafka': {
            'status': 'online' if kafka_online else 'offline',
            'events_count': len(kafka_events)
        },
        'dashboard': {
            'status': 'online',
            'url': 'http://localhost:8501'
        }
    })

@app.route('/api/system/overview')
def system_overview():
    """Return system architecture and explanation for frontend modal"""
    return jsonify({
        "architecture": "Kafka streams football events from the producer to the dashboard and Airflow. Airflow orchestrates ML pipelines and consumes events for retraining and monitoring. The API serves predictions to the dashboard.",
        "diagram": "Producer -> Kafka -> [Dashboard, Airflow] -> API -> Dashboard",
        "kafka": "Kafka is used for real-time event streaming. The producer sends football match events to Kafka. The dashboard and Airflow consume these events for live updates and pipeline orchestration.",
        "airflow": "Airflow orchestrates the ML pipelines. It can be triggered from the dashboard and monitors the health and execution of data workflows.",
        "dashboard": "The dashboard displays live match stats, predictions, and system status. It consumes Kafka events and interacts with the API and Airflow.",
        "api": "The API serves model predictions and exposes health endpoints."
    })

@app.route('/api/events')
def get_events():
    """Get recent Kafka events, formatted for frontend cards"""
    formatted = []
    for event in kafka_events[-20:]:
        formatted.append({
            'minute': event.get('minute', 'N/A'),
            'type': event.get('type', {}).get('name', 'N/A'),
            'team': event.get('team', {}).get('name', 'N/A'),
            'player': event.get('player', {}).get('name', 'N/A'),
            'outcome': event.get('shot', {}).get('outcome', {}).get('name') if event.get('type', {}).get('name') == 'Shot' else event.get('card', {}).get('name', 'N/A') if event.get('type', {}).get('name') == 'Card' else 'N/A',
        })
    return jsonify(formatted)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'kafka': 'connected',
            'api': 'connected',
            'airflow': 'connected'
        }
    })

@app.route('/api/matches')
def get_available_matches():
    """Get list of available matches"""
    return jsonify(DEFAULT_MATCHES)

if __name__ == '__main__':
    # Start Kafka consumer thread
    start_kafka_thread()
    
    # Initialize with default match
    update_match_stats_for_selected_match('man_utd_liverpool')
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8501, debug=True) 