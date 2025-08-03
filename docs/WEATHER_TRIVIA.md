# Weather Trivia System

## Overview

The Weather Dashboard features a comprehensive **Weather Trivia Game** that was developed as a collaborative group project. This engaging feature combines educational weather knowledge with actual weather data analysis to create an interactive learning experience. The trivia system includes both static weather knowledge questions and dynamically generated questions based on real weather data from team members' locations.

## Group Project Information

### **Team Collaboration**
This weather trivia feature represents a collaborative effort from our capstone project team:

- **GitHub Organization**: [Just-A-Fancy-Calculator](https://github.com/Just-A-Fancy-Calculator)
- **Team Repository**: [team6](https://github.com/Just-A-Fancy-Calculator/team6)
- **Project Purpose**: JTC Capstone Group Machine Learning Project

The trivia system incorporates weather data shared by all team members, creating a rich dataset for generating contextual, location-specific questions.

### **Collaborative Data Sharing**
Each team member contributed weather data from their location:
- **Team Structure**: 6 members with individual data folders
- **Data Integration**: Combined CSV data from multiple geographic locations
- **Shared Resources**: All team members can access and utilize the complete dataset
- **Version Control**: GitHub-based collaboration for seamless data sharing

## System Architecture

### **Core Components**

#### 1. **Weather Trivia Generator** (`features/weather_trivia_generator.py`)
The main trivia engine that creates questions from both static knowledge and real data.

```python
class WeatherTriviaGenerator:
    """Generates weather trivia questions from CSV data and static knowledge base"""
    
    def __init__(self, csv_file_path: str = "data/combined_data.csv"):
        # Initializes with team's combined weather data
```

**Key Features:**
- **842 lines of code** - Comprehensive trivia generation system
- **Dual Question Sources**: Static knowledge + data-driven questions
- **Smart Question Mix**: 60-70% data-based, 30-40% static knowledge
- **Difficulty Progression**: Questions adapt based on user performance

#### 2. **Question Engine** (`features/trivia/question_engine.py`)
Specialized engine for generating questions from team CSV data.

```python
class QuestionEngine:
    """Creates trivia questions from team weather data CSV files"""
    
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)  # Team's combined data
        self.cities = self.df['city'].unique().tolist()
```

**Data Processing:**
- **Multi-city Data**: Questions span all team members' locations
- **Data Cleaning**: Handles malformed data and missing values
- **Smart Sampling**: Prevents duplicate questions in game sessions
- **Dynamic Difficulty**: Adjusts question complexity based on available data

#### 3. **Trivia Interface Components**

##### **Timer Widget** (`features/trivia/timer_widget.py`)
- **Countdown Timer**: Visual countdown for each question
- **Round Management**: Tracks game progress and timing
- **User Feedback**: Clear time remaining indicators

##### **Scoreboard Header** (`features/trivia/scoreboard_header.py`)
- **Score Tracking**: Real-time score updates
- **Performance Metrics**: Accuracy and speed tracking
- **Visual Feedback**: Engaging score display animations

##### **Sound Manager** (`features/trivia/sound_manager.py`)
- **Audio Feedback**: Sound effects for correct/incorrect answers
- **Victory Sounds**: Celebration audio for achievements
- **Volume Control**: User-configurable audio settings

##### **Visual Effects** (`features/trivia/visual_effects.py`)
- **Confetti Animation**: Celebration effects for correct answers
- **Lightning Effects**: Dramatic visual feedback
- **Smooth Transitions**: Animated question transitions

##### **Stats Manager** (`features/trivia/stats_manager.py`)
- **Performance Tracking**: Long-term statistics
- **Achievement System**: Milestone tracking and rewards
- **Progress Analytics**: Detailed performance analysis

## Question Types and Categories

### **Static Knowledge Questions** (General Weather Education)
A comprehensive knowledge base covering fundamental weather concepts:

#### **Basic Weather Knowledge**
- **Precipitation Types**: Rain, snow, hail, sleet
- **Weather Phenomena**: Thunder, lightning, tornadoes, hurricanes
- **Atmospheric Science**: Pressure systems, fronts, cloud types
- **Climate Patterns**: Seasonal changes, weather cycles

**Example Questions:**
```python
{
    "question": "What causes thunder?",
    "options": ["Wind", "Lightning heating air", "Rain drops", "Cloud collision"],
    "correct": 1,
    "category": "general"
}
```

#### **Advanced Weather Science**
- **Meteorological Instruments**: Weather measurement tools
- **Climate Zones**: Global climate classifications
- **Extreme Weather**: Hurricanes, tornadoes, blizzards
- **Weather Prediction**: Forecasting methods and accuracy

### **Data-Based Questions** (Team Weather Data Analysis)
Dynamic questions generated from actual team weather data:

#### **Comparison Questions**
Questions comparing weather between team members' cities:
```python
"Which city had the highest temperature this month: Phoenix or Denver?"
"Between Austin and Seattle, which city received more rainfall last week?"
```

#### **Extreme Weather Questions**
Questions about weather extremes in the team dataset:
```python
"What was the highest temperature recorded in our team data?"
"Which team member's city experienced the most precipitation this year?"
```

#### **Seasonal Pattern Questions**
Questions analyzing seasonal trends across team locations:
```python
"Which team city shows the greatest temperature variation between seasons?"
"In which month did most team cities experience their highest rainfall?"
```

#### **Relative Comparison Questions**
Questions comparing current conditions to historical team data:
```python
"Is this month warmer or cooler than last year for Phoenix?"
"How does this winter compare to previous winters in Chicago?"
```

## Data Integration and Processing

### **Team Data Structure**
The trivia system processes combined weather data from all team members:

```python
# Combined team data structure
combined_data = {
    'city': ['Phoenix', 'Denver', 'Austin', 'Seattle', 'Chicago', 'Miami'],
    'team_member': ['aj', 'drashti', 'jumoke', 'pierre', 'stephanie', 'thomas'],
    'date': '2024-01-01 to 2025-01-01',
    'temperature_max': daily_highs,
    'temperature_min': daily_lows,
    'precipitation': daily_rainfall,
    'humidity': daily_humidity,
    'wind_speed': daily_wind,
    # ... additional weather variables
}
```

### **Data Quality and Processing**
```python
# Data cleaning and preparation
def _load_weather_data(self):
    """Load and clean team weather data"""
    
    # Load combined CSV from team repository
    df = pd.read_csv(self.csv_file_path)
    
    # Clean numeric columns
    numeric_cols = [
        'temperature_2m_max (°F)', 'temperature_2m_min (°F)',
        'rain_sum (inch)', 'snowfall_sum (inch)',
        'wind_speed_10m_max (mp/h)', 'relative_humidity_2m_mean (%)'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Extract city information
    self.cities = df['city'].unique().tolist()
    
    return df
```

### **Smart Question Generation**
```python
def get_quiz_questions(self, num_questions: int = 5) -> List[Dict]:
    """Generate optimized question mix for engaging gameplay"""
    
    # Prioritize data-based questions (60-70% of quiz)
    target_data_questions = min(int(num_questions * 0.65), len(data_questions))
    target_static_questions = num_questions - target_data_questions
    
    # Combine and shuffle for varied experience
    selected_questions = []
    selected_questions.extend(random.sample(data_questions, target_data_questions))
    selected_questions.extend(random.sample(static_questions, target_static_questions))
    
    return random.shuffle(selected_questions)
```

## Game Mechanics and Features

### **Game Flow**
1. **Game Initialization**: Load team data and prepare question pool
2. **Question Selection**: Smart mix of data-based and static questions
3. **Timer Challenge**: Countdown timer adds excitement and challenge
4. **Answer Feedback**: Immediate feedback with explanations
5. **Score Calculation**: Points based on accuracy and speed
6. **Visual Celebration**: Confetti and effects for correct answers
7. **Performance Summary**: End-game statistics and achievements

### **Scoring System**
```python
# Point calculation based on accuracy and speed
def calculate_points(self, correct: bool, time_remaining: float, question_difficulty: str):
    base_points = 100 if correct else 0
    time_bonus = int(time_remaining * 10)  # Speed bonus
    difficulty_multiplier = {
        'easy': 1.0,
        'medium': 1.5, 
        'hard': 2.0
    }
    
    return int(base_points * difficulty_multiplier[question_difficulty] + time_bonus)
```

### **Progressive Difficulty**
- **Adaptive Questioning**: Difficulty adjusts based on user performance
- **Data Complexity**: More complex data-analysis questions for advanced players
- **Knowledge Progression**: Static questions progress from basic to advanced concepts
- **Performance Tracking**: System learns user strengths and weaknesses

## User Interface and Experience

### **Main Trivia Interface**
The trivia game integrates seamlessly with the main weather dashboard:

- **Dedicated Tab**: "Weather Trivia" tab in the main interface
- **Engaging Design**: Weather-themed visual design with animations
- **Responsive Layout**: Adapts to different screen sizes
- **Accessible Controls**: Keyboard and mouse support for all interactions

### **Visual Effects System**
```python
# Confetti animation for correct answers
class ConfettiEffect:
    """Animated confetti celebration for correct answers"""
    
    def trigger_celebration(self):
        # Load and display confetti GIF
        # Play celebration sound
        # Update score with animation
        # Provide positive reinforcement
```

### **Audio Feedback**
The sound system provides rich audio feedback:

- **Correct Answer**: Uplifting success sound (`right.wav`)
- **Incorrect Answer**: Gentle error sound (`wrong.wav`)
- **Game Over**: Round completion sound (`round_over.wav`)
- **Thunder Effects**: Atmospheric thunder sounds (`thunder.wav`)

### **Performance Tracking**
```python
class StatsManager:
    """Track and analyze trivia game performance"""
    
    def track_performance(self, session_data):
        # Track accuracy over time
        # Monitor improvement trends  
        # Identify knowledge gaps
        # Suggest areas for study
```

## Technical Implementation

### **Database Integration**
The trivia system stores performance data and statistics:

```sql
-- Trivia performance tracking
CREATE TABLE trivia_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    questions_answered INTEGER,
    correct_answers INTEGER,
    accuracy_percentage REAL,
    average_response_time REAL,
    total_score INTEGER,
    question_categories TEXT  -- JSON array of categories
);

-- Individual question performance
CREATE TABLE trivia_questions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES trivia_sessions(id),
    question_type TEXT,  -- 'static' or 'data_based'
    question_category TEXT,
    was_correct BOOLEAN,
    response_time REAL,
    points_earned INTEGER
);
```

### **Performance Optimizations**
- **Question Caching**: Pre-generated question pools for faster game start
- **Data Indexing**: Optimized data structures for quick question generation
- **Memory Management**: Efficient handling of large team datasets
- **Lazy Loading**: Resources loaded only when needed

### **Error Handling and Resilience**
```python
def handle_data_errors(self):
    """Robust error handling for data-based questions"""
    try:
        # Attempt to generate data-based question
        return self._generate_data_question()
    except DataInsufficientError:
        # Fall back to static questions
        return self._get_static_question()
    except DataCorruptionError:
        # Clean data and retry
        self._clean_data()
        return self._generate_safe_question()
```

## Configuration and Customization

### **Game Settings**
```python
# Trivia game configuration
TRIVIA_CONFIG = {
    'questions_per_round': 5,
    'time_per_question': 30,  # seconds
    'data_question_ratio': 0.65,  # 65% data-based questions
    'difficulty_progression': True,
    'sound_effects_enabled': True,
    'visual_effects_enabled': True,
    'performance_tracking': True
}
```

### **Question Categories**
```python
# Available question categories
QUESTION_CATEGORIES = {
    'general': 'Basic weather knowledge',
    'science': 'Meteorological science',
    'extreme': 'Extreme weather events', 
    'climate': 'Climate and seasonal patterns',
    'data_comparison': 'Team data comparisons',
    'data_extremes': 'Team data extreme values',
    'data_trends': 'Team data trend analysis'
}
```

### **Customization Options**
- **Question Difficulty**: Adjustable difficulty levels
- **Timer Settings**: Configurable time limits
- **Sound Preferences**: Enable/disable audio feedback
- **Visual Effects**: Toggle animations and effects
- **Data Sources**: Select which team data to include

## API Usage Examples

### **Starting a Trivia Game**
```python
from features.weather_trivia_generator import WeatherTriviaGenerator

# Initialize trivia generator with team data
trivia = WeatherTriviaGenerator("data/combined_data.csv")

# Generate a 5-question quiz
questions = trivia.get_quiz_questions(num_questions=5)

# Display first question
question = questions[0]
print(f"Question: {question['question']}")
print(f"Options: {question['options']}")
print(f"Category: {question['category']}")
```

### **Tracking Performance**
```python
# Track game session performance
session_stats = {
    'questions_answered': 5,
    'correct_answers': 4,
    'accuracy': 0.8,
    'average_time': 15.2,
    'total_score': 450
}

stats_manager.record_session(session_stats)
```

### **Generating Custom Questions**
```python
# Generate specific types of questions
comparison_questions = trivia._generate_comparison_questions()
extreme_questions = trivia._generate_extreme_questions()
trend_questions = trivia._generate_relative_questions()

# Mix question types for varied experience
mixed_quiz = comparison_questions[:2] + extreme_questions[:2] + trend_questions[:1]
```

## Team Collaboration Workflow

### **Data Contribution Process**
Each team member follows this workflow for contributing data:

1. **Individual Data Collection**: Each member collects weather data from their location
2. **Repository Organization**: Data stored in individual team folders
3. **Format Standardization**: Common CSV format across all team members
4. **Version Control**: GitHub-based collaboration for data updates
5. **Integration Testing**: Validate data compatibility with trivia system
6. **Question Generation**: New data automatically incorporated into trivia questions

### **GitHub Integration**
The project leverages the team's GitHub infrastructure:

**Organization Structure:**
```
Just-A-Fancy-Calculator/
├── team6/                          # Main team repository
│   ├── aj/                        # Team member data folders
│   ├── drashti/
│   ├── jumoke/
│   ├── pierre/
│   ├── stephanie/
│   ├── thomas/
│   └── README.md                  # Collaboration guidelines
```

**Collaboration Features:**
- **Shared Data Access**: All team members can pull and use data from teammates
- **Version Control**: Track changes and updates to weather data
- **Issue Tracking**: GitHub issues for bugs and feature requests
- **Documentation**: Collaborative documentation in team repository

## Troubleshooting

### **Common Issues**

#### **Confetti Effect Not Working**
**Problem**: Celebration animation doesn't display  
**Solutions**:
1. Check that `assets/confetti.gif` exists
2. Verify visual effects are enabled in settings
3. Check system graphics capabilities
4. Review error logs for animation system issues

#### **Sound Effects Not Playing**
**Problem**: Audio feedback not working  
**Solutions**:
1. Verify sound files exist in `assets/` directory
2. Check system audio settings and volume
3. Ensure sound effects are enabled in trivia settings
4. Test with individual sound files (`right.wav`, `wrong.wav`, etc.)

#### **Questions Not Loading**
**Problem**: No questions appear or repeated questions  
**Solutions**:
1. Verify `data/combined_data.csv` exists and is readable
2. Check CSV data format and structure
3. Review data cleaning and processing logs
4. Ensure sufficient data for question generation

#### **Timer Issues**
**Problem**: Timer doesn't work or stops prematurely  
**Solutions**:
1. Check timer widget initialization
2. Verify game state management
3. Review timer thread safety
4. Test with different question types

### **Debug Mode**
Enable detailed logging for trivia system debugging:

```python
import logging
logging.getLogger('features.weather_trivia_generator').setLevel(logging.DEBUG)
logging.getLogger('features.trivia.question_engine').setLevel(logging.DEBUG)
```

## Future Enhancements

### **Planned Features**
1. **Multiplayer Mode**: Team-based trivia competitions
2. **Achievement System**: Badges and rewards for performance milestones
3. **Leaderboards**: Global and team-based scoring competitions
4. **Custom Tournaments**: Scheduled trivia events
5. **Mobile Compatibility**: Responsive design for mobile devices

### **Advanced Question Types**
1. **Image-Based Questions**: Weather satellite imagery analysis
2. **Map Questions**: Geographic weather pattern identification
3. **Prediction Challenges**: Forecast accuracy competitions
4. **Historical Analysis**: Long-term weather trend questions

### **Enhanced Analytics**
1. **Learning Analytics**: Detailed performance analysis and recommendations
2. **Knowledge Mapping**: Visual representation of weather knowledge areas
3. **Adaptive Learning**: Personalized question difficulty based on performance
4. **Team Analytics**: Collaborative performance metrics

---

## Related Documentation

- **Team Repository**: [Just-A-Fancy-Calculator/team6](https://github.com/Just-A-Fancy-Calculator/team6)
- **[USER_GUIDE.md](USER_GUIDE.md)**: User-facing instructions for trivia game
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**: Technical implementation details
- **[API_REFERENCE.md](API_REFERENCE.md)**: Complete API documentation

---

*The Weather Trivia System represents a successful collaborative effort that combines education with entertainment, leveraging real team data to create an engaging and informative gaming experience while demonstrating the power of collaborative data science projects.*