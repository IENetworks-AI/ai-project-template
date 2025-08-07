"""
Dummy Football Data Generator
Generates realistic football match events for testing and development
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummyFootballDataGenerator:
    """
    Generates realistic football match events for testing
    """
    
    def __init__(self):
        self.teams = [
            "Manchester United", "Liverpool", "Arsenal", "Chelsea", 
            "Manchester City", "Tottenham", "Leicester", "West Ham",
            "Aston Villa", "Newcastle", "Brighton", "Crystal Palace",
            "Wolves", "Southampton", "Burnley", "Fulham",
            "Brentford", "Nottingham Forest", "Leeds", "Bournemouth"
        ]
        
        self.players = {
            "Manchester United": ["Marcus Rashford", "Bruno Fernandes", "Anthony Martial", "Jadon Sancho", "Scott McTominay"],
            "Liverpool": ["Mohamed Salah", "Sadio Mane", "Roberto Firmino", "Diogo Jota", "Harvey Elliott"],
            "Arsenal": ["Bukayo Saka", "Gabriel Martinelli", "Emile Smith Rowe", "Martin Odegaard", "Thomas Partey"],
            "Chelsea": ["Mason Mount", "Kai Havertz", "Timo Werner", "Christian Pulisic", "N'Golo Kante"],
            "Manchester City": ["Erling Haaland", "Kevin De Bruyne", "Phil Foden", "Jack Grealish", "Bernardo Silva"]
        }
        
        self.event_types = [
            {"name": "Shot", "probability": 0.25},
            {"name": "Pass", "probability": 0.35},
            {"name": "Duel", "probability": 0.20},
            {"name": "Foul", "probability": 0.10},
            {"name": "Card", "probability": 0.05},
            {"name": "Substitution", "probability": 0.03},
            {"name": "Goal", "probability": 0.02}
        ]
        
        self.shot_outcomes = [
            {"name": "Goal", "probability": 0.15},
            {"name": "Saved", "probability": 0.25},
            {"name": "Off Target", "probability": 0.40},
            {"name": "Blocked", "probability": 0.20}
        ]
        
        self.pass_outcomes = [
            {"name": "Complete", "probability": 0.75},
            {"name": "Incomplete", "probability": 0.20},
            {"name": "Out", "probability": 0.05}
        ]
        
        self.card_types = [
            {"name": "Yellow Card", "probability": 0.70},
            {"name": "Red Card", "probability": 0.30}
        ]
    
    def generate_match_data(self, home_team: str = None, away_team: str = None) -> Dict[str, Any]:
        """
        Generate complete match data with events
        """
        if home_team is None:
            home_team = random.choice(self.teams)
        if away_team is None:
            away_team = random.choice([t for t in self.teams if t != home_team])
        
        match_data = {
            'match_id': random.randint(10000, 99999),
            'home_team': home_team,
            'away_team': away_team,
            'competition': 'Premier League',
            'season': '2023/24',
            'match_date': datetime.now().strftime('%Y-%m-%d'),
            'kick_off': '15:00:00',
            'events': []
        }
        
        # Generate events for 90 minutes + injury time
        total_minutes = 95
        events_per_minute = random.uniform(0.5, 2.0)
        total_events = int(total_minutes * events_per_minute)
        
        for i in range(total_events):
            minute = random.randint(1, total_minutes)
            second = random.randint(0, 59)
            
            event = self.generate_event(minute, second, home_team, away_team)
            if event:
                match_data['events'].append(event)
        
        # Sort events by time
        match_data['events'].sort(key=lambda x: (x['minute'], x.get('second', 0)))
        
        logger.info(f"Generated {len(match_data['events'])} events for {home_team} vs {away_team}")
        return match_data
    
    def generate_event(self, minute: int, second: int, home_team: str, away_team: str) -> Optional[Dict[str, Any]]:
        """
        Generate a single football event
        """
        # Choose event type based on probability
        event_type = self._choose_by_probability(self.event_types)
        team = random.choice([home_team, away_team])
        
        event = {
            'id': random.randint(1, 999999),
            'minute': minute,
            'second': second,
            'type': {'name': event_type['name']},
            'team': {'name': team},
            'timestamp': datetime.now().isoformat()
        }
        
        # Add player
        if team in self.players:
            event['player'] = {'name': random.choice(self.players[team])}
        
        # Add event-specific data
        if event_type['name'] == 'Shot':
            event.update(self._generate_shot_data())
        elif event_type['name'] == 'Pass':
            event.update(self._generate_pass_data())
        elif event_type['name'] == 'Goal':
            event.update(self._generate_goal_data())
        elif event_type['name'] == 'Card':
            event.update(self._generate_card_data())
        elif event_type['name'] == 'Substitution':
            event.update(self._generate_substitution_data(team))
        
        return event
    
    def _generate_shot_data(self) -> Dict[str, Any]:
        """Generate shot-specific data"""
        outcome = self._choose_by_probability(self.shot_outcomes)
        return {
            'shot': {
                'outcome': outcome,
                'technique': {'name': random.choice(['Normal', 'Volley', 'Half Volley', 'Lob'])},
                'body_part': {'name': random.choice(['Right Foot', 'Left Foot', 'Head'])},
                'xG': round(random.uniform(0.01, 0.95), 3)
            }
        }
    
    def _generate_pass_data(self) -> Dict[str, Any]:
        """Generate pass-specific data"""
        outcome = self._choose_by_probability(self.pass_outcomes)
        return {
            'pass': {
                'outcome': outcome,
                'technique': {'name': random.choice(['Normal', 'Cross', 'Through Ball', 'Long Ball'])},
                'body_part': {'name': random.choice(['Right Foot', 'Left Foot', 'Head'])},
                'length': random.randint(5, 80)
            }
        }
    
    def _generate_goal_data(self) -> Dict[str, Any]:
        """Generate goal-specific data"""
        return {
            'shot': {
                'outcome': {'name': 'Goal'},
                'technique': {'name': random.choice(['Normal', 'Volley', 'Half Volley', 'Lob'])},
                'body_part': {'name': random.choice(['Right Foot', 'Left Foot', 'Head'])},
                'xG': round(random.uniform(0.1, 0.9), 3)
            }
        }
    
    def _generate_card_data(self) -> Dict[str, Any]:
        """Generate card-specific data"""
        card_type = self._choose_by_probability(self.card_types)
        return {
            'card': {
                'name': card_type['name'],
                'colour': 'Yellow' if 'Yellow' in card_type['name'] else 'Red'
            }
        }
    
    def _generate_substitution_data(self, team: str) -> Dict[str, Any]:
        """Generate substitution-specific data"""
        if team in self.players:
            player_out = random.choice(self.players[team])
            player_in = f"Sub_{random.randint(1, 20)}"
            return {
                'substitution': {
                    'outcome': {'name': 'Substitution'},
                    'replacement': {'name': player_in}
                },
                'player': {'name': player_out}
            }
        return {}
    
    def _choose_by_probability(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Choose an option based on probability weights"""
        total_prob = sum(opt['probability'] for opt in options)
        rand_val = random.uniform(0, total_prob)
        
        cumulative_prob = 0
        for option in options:
            cumulative_prob += option['probability']
            if rand_val <= cumulative_prob:
                return option
        
        return options[0]  # Fallback
    
    def generate_live_event(self, match_data: Dict[str, Any], current_minute: int) -> Dict[str, Any]:
        """
        Generate a single live event for streaming
        """
        if not match_data['events']:
            return None
        
        # Find events around the current minute
        relevant_events = [
            event for event in match_data['events']
            if abs(event['minute'] - current_minute) <= 2
        ]
        
        if relevant_events:
            event = random.choice(relevant_events).copy()
            event['timestamp'] = datetime.now().isoformat()
            return event
        
        # Generate a new event if no relevant events found
        return self.generate_event(
            current_minute, 
            random.randint(0, 59), 
            match_data['home_team'], 
            match_data['away_team']
        )
    
    def generate_match_stats(self, match_data: Dict[str, Any], current_minute: int) -> Dict[str, Any]:
        """
        Generate current match statistics
        """
        home_team = match_data['home_team']
        away_team = match_data['away_team']
        
        # Count events by team
        home_events = [e for e in match_data['events'] if e['team']['name'] == home_team and e['minute'] <= current_minute]
        away_events = [e for e in match_data['events'] if e['team']['name'] == away_team and e['minute'] <= current_minute]
        
        # Count goals
        home_goals = len([e for e in home_events if e['type']['name'] == 'Goal'])
        away_goals = len([e for e in away_events if e['type']['name'] == 'Goal'])
        
        # Count shots
        home_shots = len([e for e in home_events if e['type']['name'] == 'Shot'])
        away_shots = len([e for e in away_events if e['type']['name'] == 'Shot'])
        
        # Count shots on target
        home_shots_on_target = len([e for e in home_events if e['type']['name'] == 'Shot' and e.get('shot', {}).get('outcome', {}).get('name') in ['Goal', 'Saved']])
        away_shots_on_target = len([e for e in away_events if e['type']['name'] == 'Shot' and e.get('shot', {}).get('outcome', {}).get('name') in ['Goal', 'Saved']])
        
        # Calculate possession (simplified)
        total_events = len(home_events) + len(away_events)
        if total_events > 0:
            home_possession = round((len(home_events) / total_events) * 100, 1)
            away_possession = round(100 - home_possession, 1)
        else:
            home_possession = 50.0
            away_possession = 50.0
        
        # Calculate xG
        home_xg = sum(e.get('shot', {}).get('xG', 0) for e in home_events if e['type']['name'] == 'Shot')
        away_xg = sum(e.get('shot', {}).get('xG', 0) for e in away_events if e['type']['name'] == 'Shot')
        
        return {
            'home_goals': home_goals,
            'away_goals': away_goals,
            'current_minute': current_minute,
            'home_shots': home_shots,
            'away_shots': away_shots,
            'home_shots_on_target': home_shots_on_target,
            'away_shots_on_target': away_shots_on_target,
            'home_possession': home_possession,
            'away_possession': away_possession,
            'home_xg': round(home_xg, 2),
            'away_xg': round(away_xg, 2),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Test the dummy data generator"""
    generator = DummyFootballDataGenerator()
    
    # Generate sample match data
    match_data = generator.generate_match_data("Manchester United", "Liverpool")
    
    print(f"Generated match: {match_data['home_team']} vs {match_data['away_team']}")
    print(f"Total events: {len(match_data['events'])}")
    
    # Generate live event
    live_event = generator.generate_live_event(match_data, 45)
    if live_event:
        print(f"Live event: {live_event['type']['name']} by {live_event['team']['name']}")
    
    # Generate match stats
    stats = generator.generate_match_stats(match_data, 45)
    print(f"Match stats at 45': {stats}")

if __name__ == "__main__":
    main() 