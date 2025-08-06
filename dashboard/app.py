"""
Streamlit Dashboard for Real-time Football Match Predictions
Displays live match statistics and win probability predictions
"""

import streamlit as st
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
# Add Airflow API imports
from typing import List, Dict

# Configure page
st.set_page_config(
    page_title="Football Match Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables
match_data_queue = queue.Queue()
prediction_data_queue = queue.Queue()

def kafka_consumer():
    """Background thread to consume Kafka messages"""
    try:
        consumer = KafkaConsumer(
            'live_football_events',
            bootstrap_servers=['kafka:29092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='streamlit_consumer'
        )
        
        for message in consumer:
            event = message.value
            match_data_queue.put(event)
            
    except Exception as e:
        st.error(f"Kafka connection error: {e}")

def get_prediction_from_api(features):
    """Get prediction from the model API"""
    try:
        api_url = "http://api:8000/predict"
        response = requests.post(api_url, json=features, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"API call failed: {e}")
    
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
    
    return fig

def create_win_probability_chart(prediction):
    """Create a pie chart for win probabilities"""
    labels = ['Home Win', 'Away Win', 'Draw']
    values = [
        prediction.get('home_win_probability', 0.33),
        prediction.get('away_win_probability', 0.33),
        prediction.get('draw_probability', 0.34)
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c']
    )])
    
    fig.update_layout(
        title="Win Probability Prediction",
        height=400
    )
    
    return fig

def create_possession_chart(match_stats):
    """Create a gauge chart for possession"""
    home_possession = match_stats.get('home_possession', 50)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=home_possession,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Home Team Possession (%)"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, 33], 'color': "lightgray"},
                {'range': [33, 66], 'color': "gray"},
                {'range': [66, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

# Add Airflow API helper functions

def get_airflow_dags(base_url="http://airflow-webserver:8080/api/v1/dags") -> List[Dict]:
    try:
        resp = requests.get(base_url, auth=("airflow", "airflow"), timeout=5)
        if resp.status_code == 200:
            return resp.json().get("dags", [])
    except Exception as e:
        st.warning(f"Airflow API error: {e}")
    return []

def get_airflow_dag_runs(dag_id: str, base_url="http://airflow-webserver:8080/api/v1") -> List[Dict]:
    try:
        resp = requests.get(f"{base_url}/dags/{dag_id}/dagRuns", auth=("airflow", "airflow"), timeout=5)
        if resp.status_code == 200:
            return resp.json().get("dag_runs", [])
    except Exception as e:
        st.warning(f"Airflow API error: {e}")
    return []

def trigger_airflow_dag(dag_id: str, base_url="http://airflow-webserver:8080/api/v1") -> bool:
    try:
        resp = requests.post(f"{base_url}/dags/{dag_id}/dagRuns", json={}, auth=("airflow", "airflow"), timeout=5)
        return resp.status_code == 200 or resp.status_code == 201
    except Exception as e:
        st.warning(f"Airflow API error: {e}")
    return False

# Start Kafka consumer in background thread (only once)
def start_kafka_thread():
    if 'kafka_thread_started' not in st.session_state:
        thread = threading.Thread(target=kafka_consumer, daemon=True)
        thread.start()
        st.session_state.kafka_thread_started = True

def main():
    """Main dashboard function"""
    start_kafka_thread()
    st.title("⚽ Real-time Football Match Predictions")
    st.markdown("Live match statistics and win probability predictions")

    # Tabs for navigation
    tab1, tab2, tab3 = st.tabs(["Live Events (Kafka)", "Data Pipeline (Airflow)", "Analytics"])

    with tab1:
        st.header("Live Football Events (Kafka)")
        events = []
        # Drain the queue for new events
        while not match_data_queue.empty():
            event = match_data_queue.get()
            events.append(event)
            # Optionally update match stats here if event structure matches
        if events:
            for event in reversed(events[-10:]):
                st.info(json.dumps(event))
        else:
            st.write("No live events yet.")
        st.caption("Showing the 10 most recent events from Kafka topic 'live_football_events'.")

    with tab2:
        st.header("Data Pipeline (Airflow)")
        dags = get_airflow_dags()
        if dags:
            dag_names = [dag['dag_id'] for dag in dags]
            selected_dag = st.selectbox("Select DAG", dag_names)
            if st.button("Trigger DAG Run"):
                if trigger_airflow_dag(selected_dag):
                    st.success(f"Triggered DAG: {selected_dag}")
                else:
                    st.error("Failed to trigger DAG run.")
            st.subheader("DAG Run History")
            dag_runs = get_airflow_dag_runs(selected_dag)
            if dag_runs:
                for run in dag_runs[:5]:
                    st.write(f"Run ID: {run['dag_run_id']} | State: {run['state']} | Start: {run['start_date']}")
            else:
                st.write("No runs found.")
        else:
            st.write("No DAGs found or Airflow API not reachable.")

    with tab3:
        # Sidebar
        st.sidebar.header("Match Information")
        
        # Initialize session state
        if 'match_stats' not in st.session_state:
            st.session_state.match_stats = {
                'home_team': 'Manchester United',
                'away_team': 'Liverpool',
                'current_minute': 0,
                'home_goals': 0,
                'away_goals': 0,
                'home_shots': 0,
                'away_shots': 0,
                'home_shots_on_target': 0,
                'away_shots_on_target': 0,
                'home_possession': 50,
                'away_possession': 50,
                'home_xg': 0.0,
                'away_xg': 0.0
            }
        
        if 'current_prediction' not in st.session_state:
            st.session_state.current_prediction = {
                'home_win_probability': 0.33,
                'away_win_probability': 0.33,
                'draw_probability': 0.34,
                'confidence': 0.5,
                'timestamp': datetime.now().isoformat()
            }
        
        # Sidebar controls
        st.sidebar.subheader("Match Details")
        home_team = st.sidebar.text_input("Home Team", st.session_state.match_stats['home_team'])
        away_team = st.sidebar.text_input("Away Team", st.session_state.match_stats['away_team'])
        
        st.sidebar.subheader("Manual Override")
        if st.sidebar.button("Update Prediction"):
            # Get prediction from API
            features = {
                'home_goals': st.session_state.match_stats['home_goals'],
                'away_goals': st.session_state.match_stats['away_goals'],
                'current_minute': st.session_state.match_stats['current_minute'],
                'home_shots': st.session_state.match_stats['home_shots'],
                'away_shots': st.session_state.match_stats['away_shots'],
                'home_shots_on_target': st.session_state.match_stats['home_shots_on_target'],
                'away_shots_on_target': st.session_state.match_stats['away_shots_on_target'],
                'home_possession': st.session_state.match_stats['home_possession'],
                'away_possession': st.session_state.match_stats['away_possession'],
                'home_xg': st.session_state.match_stats['home_xg'],
                'away_xg': st.session_state.match_stats['away_xg']
            }
            
            prediction = get_prediction_from_api(features)
            st.session_state.current_prediction = prediction
            st.sidebar.success("Prediction updated!")
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Live Match Statistics")
            
            # Score display
            score_col1, score_col2, score_col3 = st.columns(3)
            with score_col1:
                st.metric(
                    label=home_team,
                    value=st.session_state.match_stats['home_goals'],
                    delta=f"{st.session_state.match_stats['home_shots']} shots"
                )
            with score_col2:
                st.metric(
                    label="Minute",
                    value=st.session_state.match_stats['current_minute'],
                    delta=""
                )
            with score_col3:
                st.metric(
                    label=away_team,
                    value=st.session_state.match_stats['away_goals'],
                    delta=f"{st.session_state.match_stats['away_shots']} shots"
                )
            
            # Statistics
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.write("**Shots on Target:**")
                st.write(f"{home_team}: {st.session_state.match_stats['home_shots_on_target']}")
                st.write(f"{away_team}: {st.session_state.match_stats['away_shots_on_target']}")
                
                st.write("**Expected Goals (xG):**")
                st.write(f"{home_team}: {st.session_state.match_stats['home_xg']:.2f}")
                st.write(f"{away_team}: {st.session_state.match_stats['away_xg']:.2f}")
            
            with stats_col2:
                st.write("**Possession:**")
                st.write(f"{home_team}: {st.session_state.match_stats['home_possession']:.1f}%")
                st.write(f"{away_team}: {st.session_state.match_stats['away_possession']:.1f}%")
                
                st.write("**Confidence:**")
                confidence = st.session_state.current_prediction.get('confidence', 0.5)
                st.progress(confidence)
                st.write(f"{confidence:.1%}")
        
        with col2:
            st.subheader("Win Probability")
            
            # Display prediction
            home_prob = st.session_state.current_prediction.get('home_win_probability', 0.33)
            away_prob = st.session_state.current_prediction.get('away_win_probability', 0.33)
            draw_prob = st.session_state.current_prediction.get('draw_probability', 0.34)
            
            st.metric("Home Win", f"{home_prob:.1%}")
            st.metric("Away Win", f"{away_prob:.1%}")
            st.metric("Draw", f"{draw_prob:.1%}")
            
            # Prediction timestamp
            timestamp = st.session_state.current_prediction.get('timestamp', '')
            if timestamp:
                st.caption(f"Last updated: {timestamp}")
        
        # Charts
        st.subheader("Match Analytics")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Match statistics chart
            stats_chart = create_match_stats_chart(st.session_state.match_stats)
            st.plotly_chart(stats_chart, use_container_width=True)
        
        with chart_col2:
            # Win probability chart
            prob_chart = create_win_probability_chart(st.session_state.current_prediction)
            st.plotly_chart(prob_chart, use_container_width=True)
        
        # Possession gauge
        st.subheader("Possession")
        possession_chart = create_possession_chart(st.session_state.match_stats)
        st.plotly_chart(possession_chart, use_container_width=True)
        
        # Event log
        st.subheader("Recent Events (Simulated)")
        
        # Simulate event processing
        if st.button("Simulate New Event"):
            # Simulate a random event
            import random
            event_types = ['Shot', 'Pass', 'Goal', 'Save']
            teams = [st.session_state.match_stats['home_team'], st.session_state.match_stats['away_team']]
            
            event = {
                'type': random.choice(event_types),
                'team': random.choice(teams),
                'minute': min(90, st.session_state.match_stats['current_minute'] + random.randint(1, 5))
            }
            
            # Update match stats based on event
            if event['type'] == 'Shot':
                if event['team'] == st.session_state.match_stats['home_team']:
                    st.session_state.match_stats['home_shots'] += 1
                    st.session_state.match_stats['home_shots_on_target'] += 1
                else:
                    st.session_state.match_stats['away_shots'] += 1
                    st.session_state.match_stats['away_shots_on_target'] += 1
            elif event['type'] == 'Goal':
                if event['team'] == st.session_state.match_stats['home_team']:
                    st.session_state.match_stats['home_goals'] += 1
                else:
                    st.session_state.match_stats['away_goals'] += 1
            
            st.session_state.match_stats['current_minute'] = event['minute']
            
            # Update prediction
            features = {
                'home_goals': st.session_state.match_stats['home_goals'],
                'away_goals': st.session_state.match_stats['away_goals'],
                'current_minute': st.session_state.match_stats['current_minute'],
                'home_shots': st.session_state.match_stats['home_shots'],
                'away_shots': st.session_state.match_stats['away_shots'],
                'home_shots_on_target': st.session_state.match_stats['home_shots_on_target'],
                'away_shots_on_target': st.session_state.match_stats['away_shots_on_target'],
                'home_possession': st.session_state.match_stats['home_possession'],
                'away_possession': st.session_state.match_stats['away_possession'],
                'home_xg': st.session_state.match_stats['home_xg'],
                'away_xg': st.session_state.match_stats['away_xg']
            }
            
            prediction = get_prediction_from_api(features)
            st.session_state.current_prediction = prediction
            
            st.success(f"Event: {event['type']} by {event['team']} at minute {event['minute']}")
        
        # Auto-refresh
        if st.checkbox("Auto-refresh (every 5 seconds)"):
            time.sleep(5)
            st.experimental_rerun()

if __name__ == "__main__":
    main() 