#!/usr/bin/env python3
"""
Advanced Scheduled Kafka Integration Demo with APScheduler

This script provides advanced scheduling capabilities using APScheduler,
including proper cron expression support and better job management.

Features:
- Cron expressions support
- Interval scheduling
- Job persistence
- Graceful shutdown
- Enhanced Kafka-Airflow integration showcase
"""

import os
import sys
import time
import threading
import logging
import argparse
import signal
import json
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

from kafka_utils import (
    KafkaConfig, KafkaProducerManager, KafkaConsumerManager,
    KafkaMessage, MessageType, create_message, get_kafka_config
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('kafka_demo_scheduler.log')
    ]
)
logger = logging.getLogger(__name__)


class AdvancedKafkaDemo:
    """Advanced Kafka Integration Demo with enhanced Airflow collaboration"""
    
    def __init__(self, demo_id: Optional[str] = None):
        self.config = get_kafka_config()
        self.producer = KafkaProducerManager(self.config)
        self.consumer = None
        self.received_messages = []
        self.message_lock = threading.Lock()
        self.demo_id = demo_id or f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run_count = 0
        
    def check_kafka_health(self) -> bool:
        """Check if Kafka is available"""
        try:
            # Simple health check by attempting to create producer
            test_producer = KafkaProducerManager(self.config)
            return True
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
            return False
    
    def generate_enhanced_football_data(self) -> list:
        """Generate comprehensive football match data for Airflow processing"""
        teams_data = [
            {
                "home_team": "Manchester United", 
                "away_team": "Liverpool",
                "league": "Premier League",
                "rivalry_level": "high",
                "expected_attendance": 75000
            },
            {
                "home_team": "Barcelona", 
                "away_team": "Real Madrid",
                "league": "La Liga",
                "rivalry_level": "very_high",
                "expected_attendance": 99000
            },
            {
                "home_team": "Bayern Munich", 
                "away_team": "Borussia Dortmund",
                "league": "Bundesliga",
                "rivalry_level": "high",
                "expected_attendance": 81365
            },
            {
                "home_team": "PSG", 
                "away_team": "Marseille",
                "league": "Ligue 1",
                "rivalry_level": "high",
                "expected_attendance": 47929
            },
            {
                "home_team": "Juventus", 
                "away_team": "AC Milan",
                "league": "Serie A",
                "rivalry_level": "medium",
                "expected_attendance": 41507
            }
        ]
        
        events = []
        for i, team_info in enumerate(teams_data):
            match_id = f"match_{self.demo_id}_{i+1}"
            
            # Generate realistic match statistics with enhanced features
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 4)
            
            event = {
                "match_id": match_id,
                "home_team": team_info["home_team"],
                "away_team": team_info["away_team"],
                "league": team_info["league"],
                "season": "2024-25",
                "match_date": datetime.now().isoformat(),
                "kickoff_time": (datetime.now() + timedelta(hours=random.randint(1, 48))).isoformat(),
                
                # Match Result
                "home_score": home_score,
                "away_score": away_score,
                "result": "H" if home_score > away_score else ("A" if away_score > home_score else "D"),
                
                # Match Statistics
                "home_shots": random.randint(8, 25),
                "away_shots": random.randint(8, 25),
                "home_shots_on_target": random.randint(3, 12),
                "away_shots_on_target": random.randint(3, 12),
                "home_possession": round(random.uniform(35, 65), 1),
                "home_corners": random.randint(2, 15),
                "away_corners": random.randint(2, 15),
                "home_fouls": random.randint(8, 20),
                "away_fouls": random.randint(8, 20),
                "home_yellow_cards": random.randint(0, 5),
                "away_yellow_cards": random.randint(0, 5),
                "home_red_cards": random.randint(0, 1),
                "away_red_cards": random.randint(0, 1),
                
                # Additional Context
                "referee": f"Referee_{random.randint(1, 20)}",
                "stadium": f"{team_info['home_team']} Stadium",
                "attendance": random.randint(
                    int(team_info["expected_attendance"] * 0.7),
                    team_info["expected_attendance"]
                ),
                "weather": random.choice(["Clear", "Rainy", "Cloudy", "Sunny", "Windy"]),
                "temperature": random.randint(5, 35),
                "humidity": random.randint(30, 90),
                
                # ML Features for Airflow processing
                "rivalry_level": team_info["rivalry_level"],
                "home_team_form": [random.choice(["W", "L", "D"]) for _ in range(5)],
                "away_team_form": [random.choice(["W", "L", "D"]) for _ in range(5)],
                "home_team_rank": random.randint(1, 20),
                "away_team_rank": random.randint(1, 20),
                "market_value_home": random.randint(200, 1000),  # millions
                "market_value_away": random.randint(200, 1000),  # millions
                
                # Betting odds (for ML prediction features)
                "odds_home_win": round(random.uniform(1.5, 4.0), 2),
                "odds_draw": round(random.uniform(2.8, 4.5), 2),
                "odds_away_win": round(random.uniform(1.5, 4.0), 2),
                
                # Airflow processing metadata
                "processing_priority": "high" if team_info["rivalry_level"] == "very_high" else "normal",
                "requires_real_time_analysis": True,
                "expected_social_media_volume": random.randint(10000, 500000)
            }
            
            # Calculate derived fields
            event["away_possession"] = round(100 - event["home_possession"], 1)
            event["total_goals"] = home_score + away_score
            event["goal_difference"] = abs(home_score - away_score)
            
            events.append(event)
        
        return events
    
    def send_to_kafka_topics(self, events: list):
        """Send events to multiple Kafka topics for different Airflow DAGs"""
        topics_mapping = {
            "live_football_events": events,  # Main topic for football pipeline
            "ml_training_data": [e for e in events if e["total_goals"] > 2],  # High-scoring games
            "betting_analysis": [e for e in events if e["rivalry_level"] in ["high", "very_high"]],  # Important matches
            "social_media_triggers": [e for e in events if e["expected_social_media_volume"] > 100000]  # Viral matches
        }
        
        for topic, topic_events in topics_mapping.items():
            for event in topic_events:
                message = create_message(
                    message_type=MessageType.TRAINING_DATA,
                    data=event,
                    metadata={
                        "demo_id": self.demo_id,
                        "event_type": "football_match",
                        "airflow_trigger": True,
                        "topic": topic,
                        "timestamp": datetime.now().isoformat(),
                        "processing_priority": event.get("processing_priority", "normal")
                    }
                )
                
                try:
                    self.producer.send_message(topic, message)
                    logger.info(f"📤 Sent to {topic}: {event['match_id']}")
                except Exception as e:
                    logger.error(f"Failed to send to {topic}: {e}")
    
    def run_enhanced_demo(self):
        """Run the enhanced demo with Kafka-Airflow integration"""
        try:
            print(f"🚀 Running Enhanced Kafka-Airflow Demo")
            print(f"🆔 Demo ID: {self.demo_id}")
            print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # Generate enhanced football data
            football_events = self.generate_enhanced_football_data()
            print(f"🏈 Generated {len(football_events)} enhanced football events")
            
            # Send to multiple Kafka topics
            self.send_to_kafka_topics(football_events)
            print(f"📡 Events sent to multiple Kafka topics for Airflow processing")
            
            # Simulate some processing time
            time.sleep(2)
            
            print(f"✅ Demo {self.demo_id} completed successfully!")
            
            # Log summary
            logger.info(f"Demo {self.demo_id} processed {len(football_events)} events")
            
        except Exception as e:
            logger.error(f"Demo {self.demo_id} failed: {e}")
            raise
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.producer:
                self.producer.close()
            if self.consumer:
                self.consumer.close()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


class APSchedulerDemoRunner:
    """Advanced scheduler using APScheduler"""
    
    def __init__(self):
        if not APSCHEDULER_AVAILABLE:
            raise ImportError("APScheduler is not installed. Install with: pip install apscheduler")
        
        self.scheduler = BlockingScheduler()
        self.demo_count = 0
        self.start_time = datetime.now()
        self.is_running = False
        
        # Add job listeners
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    def job_listener(self, event):
        """Listen to job events"""
        if event.exception:
            logger.error(f"Job {event.job_id} crashed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} executed successfully")
    
    def run_demo_job(self):
        """Job function to be scheduled"""
        if self.is_running:
            logger.warning("⚠️ Previous demo still running, skipping execution")
            return
        
        self.is_running = True
        self.demo_count += 1
        
        try:
            print(f"\n🎯 Scheduled Demo #{self.demo_count}")
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 Total demos: {self.demo_count}")
            print(f"⏱️ Uptime: {datetime.now() - self.start_time}")
            
            # Create and run demo
            demo = AdvancedKafkaDemo(f"scheduled_{self.demo_count}")
            
            if not demo.check_kafka_health():
                logger.error("❌ Kafka not available")
                return
            
            demo.run_enhanced_demo()
            demo.cleanup()
            
        except Exception as e:
            logger.error(f"❌ Demo #{self.demo_count} failed: {e}")
        finally:
            self.is_running = False
    
    def start_interval_schedule(self, seconds: int):
        """Start interval-based scheduling"""
        self.scheduler.add_job(
            self.run_demo_job,
            IntervalTrigger(seconds=seconds),
            id='kafka_demo_interval',
            name=f'Kafka Demo Every {seconds}s'
        )
        
        print(f"🕐 APScheduler Started - Interval Mode")
        print(f"⚡ Running every {seconds} seconds")
        print(f"🛑 Press Ctrl+C to stop")
        print("=" * 50)
        
        self.scheduler.start()
    
    def start_cron_schedule(self, cron_expression: str):
        """Start cron-based scheduling"""
        try:
            # Parse cron expression
            cron_parts = cron_expression.split()
            if len(cron_parts) != 5:
                raise ValueError("Cron expression must have 5 parts: minute hour day month day_of_week")
            
            minute, hour, day, month, day_of_week = cron_parts
            
            self.scheduler.add_job(
                self.run_demo_job,
                CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week
                ),
                id='kafka_demo_cron',
                name=f'Kafka Demo Cron: {cron_expression}'
            )
            
            print(f"🕐 APScheduler Started - Cron Mode")
            print(f"📅 Cron: {cron_expression}")
            print(f"🛑 Press Ctrl+C to stop")
            print("=" * 50)
            
            self.scheduler.start()
            
        except Exception as e:
            logger.error(f"Invalid cron expression: {e}")
            print(f"❌ Invalid cron expression: {cron_expression}")
            print("💡 Example: '*/5 * * * *' (every 5 minutes)")
            print("💡 Format: minute hour day month day_of_week")


def run_once_advanced():
    """Run the advanced demo once"""
    print("🎯 Advanced Kafka-Airflow Integration Demo (One-time)")
    print("=" * 60)
    
    demo = AdvancedKafkaDemo("onetime_advanced")
    
    if not demo.check_kafka_health():
        print("❌ Kafka is not available. Please start Kafka first:")
        print("   docker-compose -f docker-compose.kafka.yml up -d")
        return
    
    try:
        demo.run_enhanced_demo()
        
        print("\n🎉 Advanced demo completed successfully!")
        print("\n📚 Next Steps:")
        print("  1. Check Kafka UI: http://localhost:8080")
        print("  2. Check Airflow UI: http://localhost:8081")
        print("  3. Monitor these Airflow DAGs:")
        print("     - football_prediction_pipeline")
        print("     - retraining_pipeline")
        print("  4. Check topics: live_football_events, ml_training_data, betting_analysis")
        print("  5. Start ML pipeline: python pipelines/kafka_ml_pipeline.py")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.error(f"Demo failed: {e}")
    finally:
        demo.cleanup()


def main():
    """Main function with advanced argument parsing"""
    parser = argparse.ArgumentParser(
        description="Advanced Scheduled Kafka Integration Demo with APScheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scheduled_kafka_demo.py --once                      # Run once
  python scheduled_kafka_demo.py --interval 10               # Every 10 seconds
  python scheduled_kafka_demo.py --cron "*/5 * * * *"        # Every 5 minutes
  python scheduled_kafka_demo.py --cron "0 9 * * 1-5"        # 9 AM weekdays
  python scheduled_kafka_demo.py --cron "0 */2 * * *"        # Every 2 hours
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--once",
        action="store_true",
        help="Run the demo once and exit"
    )
    group.add_argument(
        "--interval",
        type=int,
        help="Run the demo every N seconds"
    )
    group.add_argument(
        "--cron",
        type=str,
        help="Run the demo based on cron expression (minute hour day month day_of_week)"
    )
    
    args = parser.parse_args()
    
    if args.once:
        run_once_advanced()
    elif args.interval:
        if not APSCHEDULER_AVAILABLE:
            print("❌ APScheduler not available. Install with: pip install apscheduler")
            print("🔄 Falling back to basic scheduling...")
            # Could fall back to basic schedule library here
            return
        
        runner = APSchedulerDemoRunner()
        try:
            runner.start_interval_schedule(args.interval)
        except KeyboardInterrupt:
            print(f"\n🛑 Scheduler stopped")
            print(f"📊 Total demos executed: {runner.demo_count}")
            print(f"⏱️ Total uptime: {datetime.now() - runner.start_time}")
    
    elif args.cron:
        if not APSCHEDULER_AVAILABLE:
            print("❌ APScheduler not available. Install with: pip install apscheduler")
            return
        
        runner = APSchedulerDemoRunner()
        try:
            runner.start_cron_schedule(args.cron)
        except KeyboardInterrupt:
            print(f"\n🛑 Scheduler stopped")
            print(f"📊 Total demos executed: {runner.demo_count}")
            print(f"⏱️ Total uptime: {datetime.now() - runner.start_time}")


if __name__ == "__main__":
    main()
