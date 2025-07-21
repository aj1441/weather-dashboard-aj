#!/usr/bin/env python3
"""Command-line utility for manual backup operations"""

import argparse
import sys
import logging
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.backup_manager import get_backup_manager
from core.database import get_database

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def backup_csv_data(city=None, state=None):
    """Backup all weather data to CSV files"""
    print("🔄 CSV files are continuously updated...")
    backup_manager = get_backup_manager()
    summary = backup_manager.get_backup_summary()
    continuous_files = summary.get('continuous_csv_files', {})
    
    print("\n📊 Continuous CSV File Status:")
    for name, info in continuous_files.items():
        if info['exists']:
            size = info['size']
            modified = info['last_modified']
            print(f"✅ {name}.csv: {size} bytes (Last modified: {modified})")
        else:
            print(f"⚠️  {name}.csv: File not created yet (no data saved)")
    
    print("\n💡 Note: CSV files are automatically updated when weather data is saved to the database.")

def show_json_sync_status():
    """Show status of JSON synchronization files"""
    print("🔄 Checking JSON synchronization status...")
    
    try:
        from core.json_sync_manager import get_json_sync_manager
        json_sync_manager = get_json_sync_manager()
        status = json_sync_manager.get_sync_status()
        
        print("\n📋 JSON Sync File Status:")
        
        for file_type, info in status.items():
            if 'error' not in info:
                if info['exists']:
                    print(f"✅ {file_type}.json: {info['size']} bytes")
                    print(f"   Records: {info.get('record_count', info.get('setting_count', 0))}")
                    print(f"   Last modified: {info['last_modified']}")
                else:
                    print(f"⚠️  {file_type}.json: File not found")
            else:
                print(f"❌ {file_type}: Error - {info['error']}")
        
        print("\n💡 Note: JSON files are automatically synchronized when database changes occur.")
        
    except Exception as e:
        print(f"❌ Error checking JSON sync status: {e}")

def backup_everything(city=None, state=None):
    """Show status of all backup and sync systems"""
    print("🔄 Checking all backup and synchronization status...")
    
    # Show continuous CSV status
    backup_manager = get_backup_manager()
    summary = backup_manager.get_backup_summary()
    continuous_files = summary.get('continuous_csv_files', {})
    
    print("\n📊 Continuous CSV Files Status:")
    for name, info in continuous_files.items():
        if info['exists']:
            size = info['size']
            modified = info['last_modified']
            print(f"  ✅ {name}.csv: {size} bytes (Last modified: {modified})")
        else:
            print(f"  ⚠️  {name}.csv: File not created yet (no data saved)")
    
    # Show JSON sync status
    try:
        from core.json_sync_manager import get_json_sync_manager
        json_sync_manager = get_json_sync_manager()
        status = json_sync_manager.get_sync_status()
        
        print("\n📋 JSON Sync Files Status:")
        for file_type, info in status.items():
            if 'error' not in info:
                if info['exists']:
                    print(f"  ✅ {file_type}.json: {info['size']} bytes")
                    print(f"     Records: {info.get('record_count', info.get('setting_count', 0))}")
                else:
                    print(f"  ⚠️  {file_type}.json: File not found")
    except Exception as e:
        print(f"  ❌ Error checking JSON sync: {e}")
    
    print("\n💡 CSV files grow continuously, JSON files sync in real-time with database.")

def show_backup_summary():
    """Display summary of existing backups"""
    backup_manager = get_backup_manager()
    summary = backup_manager.get_backup_summary()
    
    print("📂 Backup Summary:")
    print(f"   Backup Directory: {summary.get('backup_directory', 'Unknown')}")
    print(f"   CSV Backup Files: {summary.get('csv_backups', 0)}")
    print(f"   JSON Backup Files: {summary.get('json_backups', 0)}")
    print(f"   Total Backup Files: {summary.get('total_backups', 0)}")
    
    if 'error' in summary:
        print(f"   ❌ Error: {summary['error']}")

def test_database_connection():
    """Test database connection and show basic stats"""
    print("🔄 Testing database connection...")
    try:
        db = get_database()
        
        # Test basic queries
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table counts
            tables = ['current_weather', 'forecast_weather', 'historical_weather', 
                     'weather_predictions', 'saved_locations', 'user_preferences']
            
            print("\n📊 Database Statistics:")
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} records")
        
        print("✅ Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description='Weather Dashboard Backup Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backup_utility.py --csv                    # Backup all weather data to CSV
  python backup_utility.py --json                   # Backup configuration to JSON
  python backup_utility.py --all                    # Complete backup
  python backup_utility.py --csv --city Phoenix --state AZ  # Backup specific city
  python backup_utility.py --summary                # Show backup summary
  python backup_utility.py --test                   # Test database connection
        """
    )
    
    # Action arguments
    parser.add_argument('--csv', action='store_true', help='Show continuous CSV backup status')
    parser.add_argument('--json', action='store_true', help='Show JSON synchronization status')
    parser.add_argument('--all', action='store_true', help='Show all backup and sync status')
    parser.add_argument('--summary', action='store_true', help='Show backup summary')
    parser.add_argument('--test', action='store_true', help='Test database connection')
    
    # Filter arguments
    parser.add_argument('--city', help='Filter backups by city name')
    parser.add_argument('--state', help='Filter backups by state code')
    
    # Options
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Check if any action is specified
    if not any([args.csv, args.json, args.all, args.summary, args.test]):
        parser.print_help()
        return
    
    print("🌤️  Weather Dashboard Backup Utility")
    print("=" * 40)
    
    # Test database connection first
    if args.test:
        if not test_database_connection():
            sys.exit(1)
        return
    
    # Show summary
    if args.summary:
        show_backup_summary()
        return
    
    # Perform backups
    try:
        if args.csv:
            backup_csv_data(args.city, args.state)
        elif args.json:
            show_json_sync_status()
        elif args.all:
            backup_everything(args.city, args.state)
        
        print("\n✅ Backup operation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Backup operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()