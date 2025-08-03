#!/usr/bin/env python3
"""Command-line tool to view fallback statistics"""

import sys
import json
import os
from datetime import datetime, timedelta

# Add the project root to Python path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fallback.fallback_tracker import fallback_tracker

def print_help():
    """Print help information"""
    print("""
Fallback Statistics Tool

Usage: python utils/fallback_stats.py [command] [options]

Commands:
  daily          - Show today's fallback usage summary
  recent [hours] - Show recent statistics (default: 24 hours)
  full           - Show full statistics
  cleanup        - Clean up old events (keeps last 30 days)
  help           - Show this help message

Examples:
  python utils/fallback_stats.py daily
  python utils/fallback_stats.py recent 48
  python utils/fallback_stats.py full
""")

def print_detailed_stats():
    """Print detailed statistics"""
    stats = fallback_tracker.get_recent_stats(24)
    
    if 'message' in stats:
        print(f"📊 {stats['message']}")
        return
    
    print("=" * 60)
    print("📊 DETAILED FALLBACK STATISTICS (Last 24 Hours)")
    print("=" * 60)
    print(f"📞 Total API Calls: {stats['total_calls']}")
    print(f"✅ Successful API Calls: {stats['successful_api_calls']}")
    print(f"📈 Success Rate: {stats['success_rate']:.1f}%")
    print(f"⏱️  Average Response Time: {stats['avg_response_time']:.0f}ms")
    
    print("\n🔄 Fallback Usage Breakdown:")
    for fallback_type, count in stats['fallback_usage'].items():
        percentage = (count / stats['total_calls']) * 100 if stats['total_calls'] > 0 else 0
        print(f"   {fallback_type}: {count} ({percentage:.1f}%)")
    
    print("\n🌍 Top Locations:")
    for location, count in stats['top_locations']:
        print(f"   {location}: {count} calls")
    
    print("\n🔌 Top Endpoints:")
    for endpoint, count in stats['top_endpoints']:
        print(f"   {endpoint}: {count} calls")
    
    if stats['top_errors']:
        print("\n❌ Top Errors:")
        for error, count in stats['top_errors']:
            print(f"   {error}: {count} times")
    
    print("=" * 60)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        print_help()
    elif command == 'daily':
        fallback_tracker.print_daily_report()
    elif command == 'recent':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        stats = fallback_tracker.get_recent_stats(hours)
        print(f"📊 Recent Statistics (Last {hours} hours):")
        print(json.dumps(stats, indent=2))
    elif command == 'full':
        print_detailed_stats()
    elif command == 'cleanup':
        fallback_tracker.cleanup_old_events()
        print("🧹 Cleanup completed")
    else:
        print(f"❌ Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    main() 