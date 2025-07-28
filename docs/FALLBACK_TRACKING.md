# Fallback Tracking System

## Overview

The fallback tracking system monitors API vs fallback usage to help you understand:
- How often your APIs are failing
- Which fallback types are being used
- Response times and success rates
- Top locations and endpoints being accessed

## Features

### 📊 **Comprehensive Tracking**
- **API Success/Failure**: Tracks when live APIs work vs when fallbacks are used
- **Fallback Types**: Monitors static, random, and historical random fallback usage
- **Response Times**: Measures API response times for performance analysis
- **Location Tracking**: Records which cities/locations are being accessed
- **Error Tracking**: Captures and categorizes error messages

### 📈 **Statistics & Reports**
- **Daily Reports**: Automatic daily summaries on application startup
- **Recent Stats**: 24-hour rolling statistics
- **Historical Data**: Persistent JSON storage of all events
- **Command-line Tool**: Easy access to statistics via `utils/fallback_stats.py`

### 🧹 **Data Management**
- **Automatic Cleanup**: Removes old events (keeps last 30 days)
- **Persistent Storage**: All data saved to `data/fallback_tracking.json`
- **Performance Optimized**: Minimal impact on application performance

## Usage

### Application Startup
When you start the application, you'll see a daily report like this:
```
============================================================
📊 FALLBACK USAGE DAILY REPORT
============================================================
📅 Date: 2025-07-28
📞 Total API Calls: 15
✅ Successful API Calls: 12
📈 Success Rate: 80.0%
❌ Errors: 3

🔄 Fallback Usage:
   none: 12 (80.0%)
   static: 2 (13.3%)
   random: 1 (6.7%)

🌍 Top Locations:
   Phoenix, AZ: 5 calls
   Atlanta, GA: 3 calls
   Seattle, WA: 2 calls

🔌 Top APIs:
   api: 8 calls
   open_meteo_client: 4 calls
   openweather_history_client: 3 calls
============================================================
```

### Command Line Tool

View today's summary:
```bash
python utils/fallback_stats.py daily
```

View recent statistics (last 24 hours):
```bash
python utils/fallback_stats.py recent
```

View detailed statistics:
```bash
python utils/fallback_stats.py full
```

View custom time period (48 hours):
```bash
python utils/fallback_stats.py recent 48
```

Clean up old data:
```bash
python utils/fallback_stats.py cleanup
```

## Log Messages

The system provides clear log messages:

**✅ API Success:**
```
2025-07-28 10:30:15 - utils.fallback_tracker - INFO - ✅ API SUCCESS: api -> fetch_current_weather for Phoenix (245ms)
```

**⚠️ Fallback Used:**
```
2025-07-28 10:30:16 - utils.fallback_tracker - WARNING - ⚠️ FALLBACK USED: api -> fetch_current_weather for Atlanta (static)
2025-07-28 10:30:16 - utils.fallback_tracker - ERROR -    Error: API failed, using static fallback
```

## Data Storage

All tracking data is stored in `data/fallback_tracking.json` with this structure:
```json
{
  "events": [
    {
      "timestamp": "2025-07-28T10:30:15.123456",
      "api_name": "api",
      "endpoint": "fetch_current_weather",
      "location": "Phoenix",
      "fallback_type": "none",
      "success": true,
      "error_message": null,
      "response_time_ms": 245
    }
  ],
  "stats": {
    "total_calls": 15,
    "successful_api_calls": 12,
    "fallback_usage": {
      "static": 2,
      "random": 1,
      "historical_random": 0,
      "none": 12
    }
  },
  "last_updated": "2025-07-28T10:30:15.123456"
}
```

## Benefits

1. **Performance Monitoring**: Track API response times and success rates
2. **Reliability Assessment**: Understand how often your APIs fail
3. **User Experience**: Know when users are seeing fallback data
4. **Debugging**: Identify patterns in API failures
5. **Capacity Planning**: Understand API usage patterns

## Privacy & Security

- **No Personal Data**: Only tracks city names and API endpoints
- **Local Storage**: All data stored locally in your project
- **Optional Cleanup**: Automatic cleanup of old data
- **No External Sharing**: Data never leaves your system

## Troubleshooting

**No tracking data appears:**
- Check that `data/fallback_tracking.json` exists
- Verify the application has write permissions to the data directory

**Statistics seem incorrect:**
- Run cleanup to remove old data: `python utils/fallback_stats.py cleanup`
- Check the JSON file for data integrity

**Performance impact:**
- Tracking adds minimal overhead (< 1ms per API call)
- Data is saved every 10 events to minimize I/O
- Old events are automatically cleaned up 