import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaProducer
from statsbombpy import sb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballEventProducer:
    """
    Kafka producer for streaming football match events in real-time
    """
    
    def __init__(self, kafka_broker: str = "localhost:9092", topic: str = "live_football_events"):
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.producer = None
        self.match_data = None
        self.current_minute = 0
        
    def connect(self):
        """Connect to Kafka broker"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.kafka_broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info(f"Connected to Kafka broker at {self.kafka_broker}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def load_match_data(self, competition_id: int = 39, season_id: int = 4, match_id: int = None):
        """
        Load match data from StatsBomb Open Data
        Args:
            competition_id: Premier League = 39
            season_id: 2021/22 = 4
            match_id: Specific match ID (optional)
        """
        try:
            # Get matches for the specified competition and season
            matches = sb.matches(competition_id=competition_id, season_id=season_id)
            
            if match_id is None:
                # Select the first match if no specific match_id provided
                match_id = matches.iloc[0]['match_id']
                logger.info(f"Selected match_id: {match_id}")
            
            # Get events for the selected match
            events = sb.events(match_id=match_id)
            
            # Get match info
            match_info = matches[matches['match_id'] == match_id].iloc[0]
            
            self.match_data = {
                'match_id': match_id,
                'home_team': match_info['home_team_name'],
                'away_team': match_info['away_team_name'],
                'competition': match_info['competition_name'],
                'season': match_info['season_name'],
                'events': events.to_dict('records')
            }
            
            logger.info(f"Loaded {len(self.match_data['events'])} events for {self.match_data['home_team']} vs {self.match_data['away_team']}")
            
        except Exception as e:
            logger.error(f"Failed to load match data: {e}")
            # Fallback to sample data if StatsBomb fails
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample match data for testing"""
        logger.info("Creating sample match data")
        self.match_data = {
            'match_id': 12345,
            'home_team': 'Manchester United',
            'away_team': 'Liverpool',
            'competition': 'Premier League',
            'season': '2023/24',
            'events': [
                {
                    'id': 1,
                    'minute': 5,
                    'second': 30,
                    'type': {'name': 'Shot'},
                    'team': {'name': 'Manchester United'},
                    'player': {'name': 'Marcus Rashford'},
                    'shot': {'outcome': {'name': 'Goal'}},
                    'location': [50, 30]
                },
                {
                    'id': 2,
                    'minute': 12,
                    'second': 15,
                    'type': {'name': 'Pass'},
                    'team': {'name': 'Liverpool'},
                    'player': {'name': 'Mohamed Salah'},
                    'pass': {'outcome': {'name': 'Complete'}},
                    'location': [45, 25]
                },
                {
                    'id': 3,
                    'minute': 18,
                    'second': 45,
                    'type': {'name': 'Shot'},
                    'team': {'name': 'Liverpool'},
                    'player': {'name': 'Darwin Nunez'},
                    'shot': {'outcome': {'name': 'Saved'}},
                    'location': [55, 40]
                }
            ]
        }
    
    def _enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich event with additional metadata"""
        enriched_event = event.copy()
        enriched_event.update({
            'timestamp': datetime.now().isoformat(),
            'producer_id': 'football_event_producer',
            'event_id': f"{self.match_data['match_id']}_{event.get('id', 0)}"
        })
        return enriched_event
    
    def stream_events(self, delay_seconds: float = 1.0, max_events: int = None):
        """
        Stream events to Kafka topic with specified delay
        Args:
            delay_seconds: Delay between events in seconds
            max_events: Maximum number of events to stream (for testing)
        """
        if not self.producer:
            self.connect()
        
        if not self.match_data:
            logger.error("No match data loaded. Call load_match_data() first.")
            return
        
        events = self.match_data['events']
        if max_events:
            events = events[:max_events]
        
        logger.info(f"Starting to stream {len(events)} events with {delay_seconds}s delay")
        
        for i, event in enumerate(events):
            try:
                # Enrich event with metadata
                enriched_event = self._enrich_event(event)
                
                # Send to Kafka
                future = self.producer.send(
                    topic=self.topic,
                    key=str(event.get('id', i)),
                    value=enriched_event
                )
                
                # Wait for send to complete
                record_metadata = future.get(timeout=10)
                
                logger.info(f"Sent event {i+1}/{len(events)}: {event.get('type', {}).get('name', 'Unknown')} at minute {event.get('minute', 0)}")
                
                # Wait before next event
                time.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"Failed to send event {i+1}: {e}")
                continue
        
        logger.info("Finished streaming events")
    
    def close(self):
        """Close Kafka producer connection"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer connection closed")

def main():
    """Main function to run the producer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Football Event Kafka Producer')
    parser.add_argument('--kafka-broker', default='localhost:9092', help='Kafka broker address')
    parser.add_argument('--topic', default='live_football_events', help='Kafka topic name')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between events in seconds')
    parser.add_argument('--max-events', type=int, help='Maximum number of events to stream')
    parser.add_argument('--match-id', type=int, help='Specific match ID to load')
    
    args = parser.parse_args()
    
    # Create producer
    producer = FootballEventProducer(
        kafka_broker=args.kafka_broker,
        topic=args.topic
    )
    
    try:
        # Load match data
        producer.load_match_data(match_id=args.match_id)
        
        # Stream events
        producer.stream_events(
            delay_seconds=args.delay,
            max_events=args.max_events
        )
        
    except KeyboardInterrupt:
        logger.info("Producer stopped by user")
    except Exception as e:
        logger.error(f"Producer error: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main() 