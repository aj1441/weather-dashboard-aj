"""Fallback tracking system for monitoring API vs fallback usage"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

@dataclass
class FallbackEvent:
    """Represents a single fallback event"""
    timestamp: str
    api_name: str
    endpoint: str
    location: str
    fallback_type: str  # 'static', 'random', 'historical_random', 'none'
    success: bool
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None

class FallbackTracker:
    """Tracks and analyzes fallback usage patterns"""
    
    def __init__(self, log_file: str = "data/fallback_tracking.json"):
        self.log_file = log_file
        self.events: List[FallbackEvent] = []
        self.stats = {
            'total_calls': 0,
            'successful_api_calls': 0,
            'fallback_usage': {
                'static': 0,
                'random': 0,
                'historical_random': 0,
                'none': 0
            },
            'api_endpoints': defaultdict(int),
            'locations': defaultdict(int),
            'errors': defaultdict(int)
        }
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing tracking data from file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.events = [FallbackEvent(**event) for event in data.get('events', [])]
                    self.stats = data.get('stats', self.stats)
                logger.info(f"Loaded {len(self.events)} existing fallback events")
        except Exception as e:
            logger.warning(f"Could not load existing fallback data: {e}")
    
    def _save_data(self):
        """Save tracking data to file"""
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            data = {
                'events': [asdict(event) for event in self.events],
                'stats': self.stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save fallback tracking data: {e}")
    
    def track_api_call(self, api_name: str, endpoint: str, location: str, 
                      fallback_type: str, success: bool, 
                      error_message: Optional[str] = None,
                      response_time_ms: Optional[int] = None):
        """Track an API call and its fallback status"""
        event = FallbackEvent(
            timestamp=datetime.now().isoformat(),
            api_name=api_name,
            endpoint=endpoint,
            location=location,
            fallback_type=fallback_type,
            success=success,
            error_message=error_message,
            response_time_ms=response_time_ms
        )
        
        self.events.append(event)
        
        # Update statistics
        self.stats['total_calls'] += 1
        if success and fallback_type == 'none':
            self.stats['successful_api_calls'] += 1
        else:
            self.stats['fallback_usage'][fallback_type] += 1
        
        self.stats['api_endpoints'][endpoint] += 1
        self.stats['locations'][location] += 1
        
        if error_message:
            self.stats['errors'][error_message] += 1
        
        # Log the event
        if fallback_type == 'none':
            logger.info(f"✅ API SUCCESS: {api_name} -> {endpoint} for {location} ({response_time_ms}ms)")
        else:
            logger.warning(f"⚠️ FALLBACK USED: {api_name} -> {endpoint} for {location} ({fallback_type})")
            if error_message:
                logger.error(f"   Error: {error_message}")
        
        # Save data periodically (every 10 events)
        if len(self.events) % 10 == 0:
            self._save_data()
    
    def get_recent_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self.events 
            if datetime.fromisoformat(event.timestamp) > cutoff
        ]
        
        if not recent_events:
            return {'message': f'No events in the last {hours} hours'}
        
        stats = {
            'period_hours': hours,
            'total_calls': len(recent_events),
            'successful_api_calls': len([e for e in recent_events if e.success and e.fallback_type == 'none']),
            'fallback_usage': Counter([e.fallback_type for e in recent_events]),
            'top_locations': Counter([e.location for e in recent_events]).most_common(5),
            'top_endpoints': Counter([e.endpoint for e in recent_events]).most_common(5),
            'top_errors': Counter([e.error_message for e in recent_events if e.error_message]).most_common(3),
            'avg_response_time': sum([e.response_time_ms or 0 for e in recent_events]) / len(recent_events) if recent_events else 0
        }
        
        # Calculate success rate
        stats['success_rate'] = (stats['successful_api_calls'] / stats['total_calls']) * 100
        
        return stats
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Get today's summary"""
        today = datetime.now().date()
        today_events = [
            event for event in self.events 
            if datetime.fromisoformat(event.timestamp).date() == today
        ]
        
        if not today_events:
            return {'message': 'No events today'}
        
        summary = {
            'date': today.isoformat(),
            'total_calls': len(today_events),
            'successful_api_calls': len([e for e in today_events if e.success and e.fallback_type == 'none']),
            'fallback_breakdown': Counter([e.fallback_type for e in today_events]),
            'api_breakdown': Counter([e.api_name for e in today_events]),
            'location_breakdown': Counter([e.location for e in today_events]),
            'error_count': len([e for e in today_events if e.error_message])
        }
        
        summary['success_rate'] = (summary['successful_api_calls'] / summary['total_calls']) * 100
        
        return summary
    
    def print_daily_report(self):
        """Print a formatted daily report"""
        summary = self.get_daily_summary()
        
        if 'message' in summary:
            logger.info(f"📊 Daily Report: {summary['message']}")
            return
        
        logger.info("=" * 60)
        logger.info("📊 FALLBACK USAGE DAILY REPORT")
        logger.info("=" * 60)
        logger.info(f"📅 Date: {summary['date']}")
        logger.info(f"📞 Total API Calls: {summary['total_calls']}")
        logger.info(f"✅ Successful API Calls: {summary['successful_api_calls']}")
        logger.info(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"❌ Errors: {summary['error_count']}")
        
        logger.info("\n🔄 Fallback Usage:")
        for fallback_type, count in summary['fallback_breakdown'].items():
            percentage = (count / summary['total_calls']) * 100
            logger.info(f"   {fallback_type}: {count} ({percentage:.1f}%)")
        
        logger.info("\n🌍 Top Locations:")
        for location, count in summary['location_breakdown'].most_common(5):
            logger.info(f"   {location}: {count} calls")
        
        logger.info("\n🔌 Top APIs:")
        for api, count in summary['api_breakdown'].most_common(5):
            logger.info(f"   {api}: {count} calls")
        
        logger.info("=" * 60)
    
    def cleanup_old_events(self, days_to_keep: int = 30):
        """Remove events older than specified days"""
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        original_count = len(self.events)
        self.events = [
            event for event in self.events 
            if datetime.fromisoformat(event.timestamp) > cutoff
        ]
        removed_count = original_count - len(self.events)
        if removed_count > 0:
            logger.info(f"🧹 Cleaned up {removed_count} old fallback events (keeping last {days_to_keep} days)")
            self._save_data()

# Global tracker instance
fallback_tracker = FallbackTracker()

def track_fallback_usage(api_name: str, endpoint: str, location: str, 
                        fallback_type: str, success: bool, 
                        error_message: Optional[str] = None,
                        response_time_ms: Optional[int] = None):
    """Convenience function to track fallback usage"""
    fallback_tracker.track_api_call(
        api_name=api_name,
        endpoint=endpoint,
        location=location,
        fallback_type=fallback_type,
        success=success,
        error_message=error_message,
        response_time_ms=response_time_ms
    ) 