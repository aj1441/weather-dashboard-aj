#!/usr/bin/env python3
"""
Test script for the hybrid weather data implementation.
This will test the new hybrid data coordinator and verify predictions work.
"""

import logging
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hybrid_data_coordinator import HybridWeatherDataCoordinator
from core.weather_predictor import WeatherPredictor
from core.database import WeatherDatabase

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hybrid_coordinator():
    """Test the hybrid data coordinator"""
    print("=" * 60)
    print("🧪 TESTING HYBRID DATA COORDINATOR")
    print("=" * 60)
    
    try:
        # Test city (replace with your actual saved city)
        city = "Seattle"
        state = "WA"
        latitude = 47.6062
        longitude = -122.3321
        
        # Initialize coordinator
        coordinator = HybridWeatherDataCoordinator()
        
        # Test data coverage analysis
        print(f"\n📊 Analyzing existing data coverage for {city}, {state}...")
        coverage = coordinator._analyze_existing_data_coverage(city, state)
        print(f"   Bulk records: {coverage.get('bulk_records', 0)}")
        print(f"   Recent records: {coverage.get('recent_records', 0)}")
        print(f"   Total records: {coverage.get('total_records', 0)}")
        
        # Test combined data retrieval
        print(f"\n🔄 Getting combined historical data...")
        combined_data = coordinator._get_combined_historical_data(city, state)
        if combined_data:
            print(f"   ✅ Successfully retrieved {len(combined_data)} combined records")
            
            # Show date range
            if combined_data:
                dates = [r['date'] for r in combined_data]
                print(f"   📅 Date range: {min(dates)} to {max(dates)}")
        else:
            print("   ❌ No combined data found")
        
        # Test sufficiency check
        print(f"\n✅ Checking data sufficiency...")
        sufficient = coordinator.has_sufficient_data_for_predictions(city, state)
        print(f"   Sufficient for predictions: {'✅ YES' if sufficient else '❌ NO'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing hybrid coordinator: {e}")
        return False

def test_enhanced_predictor():
    """Test the enhanced weather predictor with hybrid data"""
    print("\n" + "=" * 60)
    print("🔮 TESTING ENHANCED WEATHER PREDICTOR")
    print("=" * 60)
    
    try:
        # Test city
        city = "Seattle"
        state = "WA"
        
        # Initialize predictor
        predictor = WeatherPredictor()
        
        # Test data sufficiency check (now uses hybrid approach)
        print(f"\n📊 Checking data sufficiency for {city}, {state}...")
        sufficient = predictor.has_sufficient_data(city, state)
        print(f"   Sufficient data: {'✅ YES' if sufficient else '❌ NO'}")
        
        if sufficient:
            print(f"\n🤖 Generating predictions using hybrid data...")
            success, predictions = predictor.predict_weather(city, state)
            
            if success:
                print(f"   ✅ Predictions generated successfully!")
                print(f"   🎯 Confidence: {predictions.get('confidence', 0):.1%}")
                
                forecast = predictions.get('forecast', [])
                if forecast:
                    print(f"   📅 Forecast days: {len(forecast)}")
                    for day in forecast[:2]:  # Show first 2 days
                        date = day.get('date', 'Unknown')
                        temp_max = day.get('temperature_max', 0)
                        temp_min = day.get('temperature_min', 0)
                        conditions = day.get('conditions', 'Unknown')
                        print(f"      {date}: {temp_max:.0f}°/{temp_min:.0f}°F - {conditions}")
                
                # Show data points used
                data_points = predictions.get('data_points_used', 0)
                print(f"   📊 Data points used: {data_points}")
                
            else:
                print(f"   ❌ Prediction failed: {predictions.get('error', 'Unknown error')}")
        else:
            print("   ⚠️ Insufficient data for predictions. Try fetching hybrid data first.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced predictor: {e}")
        return False

def test_database_structure():
    """Test database structure for hybrid approach"""
    print("\n" + "=" * 60)
    print("🗄️ TESTING DATABASE STRUCTURE")
    print("=" * 60)
    
    try:
        db = WeatherDatabase()
        
        # Test both historical tables exist
        print("\n📋 Checking database tables...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check historical_weather table
            cursor.execute("SELECT COUNT(*) FROM historical_weather")
            bulk_count = cursor.fetchone()[0]
            print(f"   historical_weather table: {bulk_count} records")
            
            # Check recent_historical_weather table  
            cursor.execute("SELECT COUNT(*) FROM recent_historical_weather")
            recent_count = cursor.fetchone()[0]
            print(f"   recent_historical_weather table: {recent_count} records")
            
            print(f"   📊 Total historical records: {bulk_count + recent_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database structure: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 STARTING HYBRID WEATHER DATA TESTS")
    print("=" * 60)
    
    tests = [
        ("Database Structure", test_database_structure),
        ("Hybrid Coordinator", test_hybrid_coordinator),  
        ("Enhanced Predictor", test_enhanced_predictor),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your hybrid implementation is ready!")
        print("\nNext steps:")
        print("1. Add some cities to your saved cities")
        print("2. Click '📊 Hybrid Data' to fetch combined historical data")
        print("3. Click '🔮 Predicted Weather' to see improved predictions!")
    else:
        print(f"\n⚠️ Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main()