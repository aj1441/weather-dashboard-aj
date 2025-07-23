"""
Weather Trivia Question Generator

This module generates trivia questions based on actual weather data from the CSV files.
It analyzes the data to create contextual, relevant questions while maintaining 
a pool of static weather knowledge questions.
"""

import random
import os
import logging
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime


class WeatherTriviaGenerator:
    """Generates weather trivia questions from CSV data and static knowledge base"""
    
    def __init__(self, csv_file_path: str = "data/combined_data.csv"):
        """
        Initialize the trivia generator
        
        Args:
            csv_file_path: Path to the combined weather data CSV file
        """
        try:
            self.csv_file_path = csv_file_path
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"Initializing WeatherTriviaGenerator with {csv_file_path}")
            
            self.weather_data = None
            self.cities = []
            
            # Load and analyze data
            self.logger.info("Loading weather data...")
            self._load_weather_data()
            self.logger.info("Analyzing weather data...")
            self._analyze_data()
            self.logger.info("WeatherTriviaGenerator initialization completed")
            
        except Exception as e:
            self.logger.error(f"Error initializing WeatherTriviaGenerator: {e}", exc_info=True)
            raise
    
    def _load_weather_data(self) -> None:
        """Load weather data from CSV file"""
        try:
            if os.path.exists(self.csv_file_path):
                with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    self.weather_data = list(reader)
                
                # Get unique cities
                cities_set = set()
                for row in self.weather_data:
                    if 'name' in row and row['name']:
                        cities_set.add(row['name'])
                
                self.cities = sorted(list(cities_set))
                self.logger.info(f"Loaded weather data for {len(self.cities)} cities")
            else:
                self.logger.warning(f"CSV file not found: {self.csv_file_path}")
                self.cities = ["Denver, CO", "New York, NY", "Phoenix, AZ", "Seattle, WA"]
                self.weather_data = []
        except Exception as e:
            self.logger.error(f"Error loading weather data: {e}")
            self.cities = ["Denver, CO", "New York, NY", "Phoenix, AZ", "Seattle, WA"]
            self.weather_data = []
    
    def _analyze_data(self) -> None:
        """Analyze weather data to extract interesting facts for questions"""
        if not self.weather_data:
            return
        
        try:
            # Calculate interesting statistics
            self.data_insights = {}
            
            for city in self.cities:
                city_rows = [row for row in self.weather_data if row.get('name') == city]
                
                if city_rows:
                    # Convert string values to numbers
                    temps_max = [float(row.get('tempmax', 0)) for row in city_rows if row.get('tempmax', '').replace('.','').replace('-','').isdigit()]
                    temps_min = [float(row.get('tempmin', 0)) for row in city_rows if row.get('tempmin', '').replace('.','').replace('-','').isdigit()]
                    temps_avg = [float(row.get('temp', 0)) for row in city_rows if row.get('temp', '').replace('.','').replace('-','').isdigit()]
                    humidity_vals = [float(row.get('humidity', 0)) for row in city_rows if row.get('humidity', '').replace('.','').isdigit()]
                    wind_vals = [float(row.get('windspeed', 0)) for row in city_rows if row.get('windspeed', '').replace('.','').isdigit()]
                    precip_vals = [float(row.get('precip', 0)) for row in city_rows if row.get('precip', '').replace('.','').isdigit()]
                    conditions = [row.get('conditions', 'Clear') for row in city_rows if row.get('conditions')]
                    
                    # Find most common condition
                    common_condition = 'Clear'
                    if conditions:
                        condition_counts = {}
                        for cond in conditions:
                            condition_counts[cond] = condition_counts.get(cond, 0) + 1
                        common_condition = max(condition_counts, key=condition_counts.get)
                    
                    self.data_insights[city] = {
                        'max_temp': max(temps_max) if temps_max else 70,
                        'min_temp': min(temps_min) if temps_min else 30,
                        'avg_temp': sum(temps_avg) / len(temps_avg) if temps_avg else 50,
                        'max_humidity': max(humidity_vals) if humidity_vals else 80,
                        'min_humidity': min(humidity_vals) if humidity_vals else 30,
                        'avg_humidity': sum(humidity_vals) / len(humidity_vals) if humidity_vals else 55,
                        'max_wind': max(wind_vals) if wind_vals else 15,
                        'total_precip': sum(precip_vals) if precip_vals else 0,
                        'common_condition': common_condition
                    }
            
            self.logger.info("Weather data analysis completed")
            
        except Exception as e:
            self.logger.error(f"Error analyzing weather data: {e}")
            self.data_insights = {}
    
    def get_static_questions(self) -> List[Dict[str, Any]]:
        """Get the pool of static weather knowledge questions"""
        return [
            # Basic Weather Knowledge
            {
                "question": "What is the most common type of precipitation?",
                "options": ["Rain", "Snow", "Hail", "Sleet"],
                "correct": 0,
                "category": "general"
            },
            {
                "question": "What causes thunder?",
                "options": ["Wind", "Lightning heating air", "Rain drops", "Cloud collision"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "What weather phenomenon is also called a 'twister'?",
                "options": ["Hurricane", "Tornado", "Cyclone", "Typhoon"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "What is the eye of a hurricane?",
                "options": ["The strongest part", "The calmest part", "The wettest part", "The windiest part"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "What is the difference between sleet and freezing rain?",
                "options": ["No difference", "Sleet freezes before hitting ground", "Freezing rain is warmer", "Sleet is larger"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "Which weather condition can create a 'whiteout'?",
                "options": ["Heavy rain", "Dense fog", "Blizzard", "High winds"],
                "correct": 2,
                "category": "general"
            },
            {
                "question": "What creates the colors in a rainbow?",
                "options": ["Ice crystals", "Water droplets", "Dust particles", "Temperature changes"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "What does 'precipitation' mean in weather terms?",
                "options": ["Wind speed", "Air pressure", "Water falling from clouds", "Cloud formation"],
                "correct": 2,
                "category": "general"
            },
            {
                "question": "What weather pattern causes droughts in the Pacific Northwest?",
                "options": ["El Niño", "La Niña", "Arctic Oscillation", "Polar Vortex"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "In what season do most hurricanes occur in the Atlantic?",
                "options": ["Spring", "Summer", "Fall", "Winter"],
                "correct": 2,
                "category": "general"
            },
            
            # Cloud Types and Formation
            {
                "question": "Which cloud type is associated with thunderstorms?",
                "options": ["Cirrus", "Stratus", "Cumulonimbus", "Nimbostratus"],
                "correct": 2,
                "category": "general"
            },
            {
                "question": "What are the highest clouds in the atmosphere called?",
                "options": ["Cumulus", "Stratus", "Cirrus", "Nimbus"],
                "correct": 2,
                "category": "general"
            },
            {
                "question": "Which clouds typically produce steady, light rain?",
                "options": ["Cumulus", "Nimbostratus", "Cirrus", "Altocumulus"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "What do mammatus clouds indicate?",
                "options": ["Good weather", "Severe storms", "Light rain", "Snow"],
                "correct": 1,
                "category": "general"
            },
            {
                "question": "At what altitude do cirrus clouds typically form?",
                "options": ["0-6,000 feet", "6,000-20,000 feet", "20,000-40,000 feet", "Above 40,000 feet"],
                "correct": 2,
                "category": "general"
            },
            
            # Weather Instruments and Measurements
            {
                "question": "What does a barometer measure?",
                "options": ["Temperature", "Humidity", "Wind Speed", "Air Pressure"],
                "correct": 3,
                "category": "instruments"
            },
            {
                "question": "Which instrument measures wind speed?",
                "options": ["Thermometer", "Barometer", "Anemometer", "Hygrometer"],
                "correct": 2,
                "category": "instruments"
            },
            {
                "question": "What does a hygrometer measure?",
                "options": ["Wind direction", "Humidity", "Precipitation", "Cloud height"],
                "correct": 1,
                "category": "instruments"
            },
            {
                "question": "What instrument measures rainfall amounts?",
                "options": ["Rain gauge", "Pluviometer", "Both A and B", "Barometer"],
                "correct": 2,
                "category": "instruments"
            },
            {
                "question": "What is a weather vane used for?",
                "options": ["Measuring temperature", "Showing wind direction", "Measuring humidity", "Predicting storms"],
                "correct": 1,
                "category": "instruments"
            },
            
            # Weather Scales and Classifications
            {
                "question": "Which scale is used to measure tornado intensity?",
                "options": ["Richter Scale", "Enhanced Fujita Scale", "Beaufort Scale", "Saffir-Simpson Scale"],
                "correct": 1,
                "category": "scales"
            },
            {
                "question": "What scale is used to rate hurricane intensity?",
                "options": ["Fujita Scale", "Beaufort Scale", "Saffir-Simpson Scale", "Richter Scale"],
                "correct": 2,
                "category": "scales"
            },
            {
                "question": "The Beaufort Scale measures what weather element?",
                "options": ["Temperature", "Wind speed", "Humidity", "Air pressure"],
                "correct": 1,
                "category": "scales"
            },
            {
                "question": "On the Enhanced Fujita Scale, what is the strongest tornado rating?",
                "options": ["EF4", "EF5", "EF6", "EF10"],
                "correct": 1,
                "category": "scales"
            },
            
            # Extreme Weather Records
            {
                "question": "What is the hottest temperature ever recorded on Earth?",
                "options": ["134°F", "142°F", "128°F", "136°F"],
                "correct": 0,
                "category": "records"
            },
            {
                "question": "What is the coldest temperature ever recorded on Earth?",
                "options": ["-128.6°F", "-144.9°F", "-134.1°F", "-156.2°F"],
                "correct": 0,
                "category": "records"
            },
            {
                "question": "What is the highest wind speed ever recorded?",
                "options": ["231 mph", "301 mph", "189 mph", "267 mph"],
                "correct": 1,
                "category": "records"
            },
            {
                "question": "What is the largest hailstone ever recorded?",
                "options": ["6 inches", "8 inches", "10 inches", "12 inches"],
                "correct": 1,
                "category": "records"
            },
            {
                "question": "Which hurricane holds the record for lowest pressure?",
                "options": ["Hurricane Gilbert", "Hurricane Camille", "Hurricane Wilma", "Hurricane Mitch"],
                "correct": 2,
                "category": "records"
            },
            
            # Geography and Climate
            {
                "question": "Which state experiences the most tornadoes annually?",
                "options": ["Oklahoma", "Kansas", "Texas", "Nebraska"],
                "correct": 2,
                "category": "geography"
            },
            {
                "question": "What is the wettest place on Earth?",
                "options": ["Amazon Rainforest", "Mount Waialeale, Hawaii", "Seattle, Washington", "Mawsynram, India"],
                "correct": 3,
                "category": "geography"
            },
            {
                "question": "Which city is known as the 'Lightning Capital of the World'?",
                "options": ["Tampa, Florida", "Phoenix, Arizona", "New Orleans, Louisiana", "Miami, Florida"],
                "correct": 0,
                "category": "geography"
            },
            {
                "question": "What is the driest place on Earth?",
                "options": ["Sahara Desert", "Atacama Desert", "Death Valley", "Antarctic Desert"],
                "correct": 1,
                "category": "geography"
            },
            {
                "question": "Which ocean experiences the most hurricanes?",
                "options": ["Atlantic", "Pacific", "Indian", "Arctic"],
                "correct": 1,
                "category": "geography"
            },
            
            # Weather Safety and Preparedness
            {
                "question": "What weather event typically brings the most property damage?",
                "options": ["Tornadoes", "Hurricanes", "Hailstorms", "Lightning"],
                "correct": 1,
                "category": "safety"
            },
            {
                "question": "Which weather condition makes roads most dangerous?",
                "options": ["Heavy rain", "Snow", "Black ice", "High winds"],
                "correct": 2,
                "category": "safety"
            },
            {
                "question": "What outdoor activity is most affected by lightning?",
                "options": ["Swimming", "Golf", "Hiking", "Cycling"],
                "correct": 1,
                "category": "safety"
            },
            {
                "question": "During a tornado warning, where should you go?",
                "options": ["Basement center", "Top floor", "Near windows", "Outside"],
                "correct": 0,
                "category": "safety"
            },
            {
                "question": "What weather condition cancels the most flights?",
                "options": ["Rain", "Snow", "Fog", "Wind"],
                "correct": 2,
                "category": "safety"
            },
            
            # Weather Phenomena
            {
                "question": "What weather phenomenon can lift a house?",
                "options": ["Hurricane", "Tornado", "Straight-line winds", "Microburst"],
                "correct": 1,
                "category": "phenomena"
            },
            {
                "question": "Which season has the most lightning strikes?",
                "options": ["Spring", "Summer", "Fall", "Winter"],
                "correct": 1,
                "category": "phenomena"
            },
            {
                "question": "What causes a heat mirage?",
                "options": ["Hot air rising", "Light refraction", "Desert sand", "Optical illusion"],
                "correct": 1,
                "category": "phenomena"
            },
            {
                "question": "What is a derecho?",
                "options": ["A type of tornado", "Widespread windstorm", "Hail event", "Lightning phenomenon"],
                "correct": 1,
                "category": "phenomena"
            },
            {
                "question": "What causes the Northern Lights?",
                "options": ["Solar wind particles", "Ice crystals", "Moon reflection", "Atmospheric pressure"],
                "correct": 0,
                "category": "phenomena"
            },
            
            # Pop Culture and Weather
            {
                "question": "What movie features a storm chaser team called 'Dorothy'?",
                "options": ["Twister", "Into the Storm", "The Perfect Storm", "Hurricane"],
                "correct": 0,
                "category": "pop_culture"
            },
            {
                "question": "What weather phenomenon inspired the song 'Purple Rain'?",
                "options": ["Actual purple rain", "Sunset during rain", "Prince's imagination", "Chemical precipitation"],
                "correct": 2,
                "category": "pop_culture"
            },
            {
                "question": "Which superhero controls weather in Marvel Comics?",
                "options": ["Thor", "Storm", "Iceman", "Human Torch"],
                "correct": 1,
                "category": "pop_culture"
            },
            {
                "question": "In the movie 'The Day After Tomorrow', what weather event occurs?",
                "options": ["Mega hurricane", "Super tornado", "Sudden ice age", "Global drought"],
                "correct": 2,
                "category": "pop_culture"
            },
            {
                "question": "What weather app was one of the first popular iPhone apps?",
                "options": ["Weather Channel", "AccuWeather", "Weather Underground", "Built-in Weather"],
                "correct": 3,
                "category": "pop_culture"
            },
            
            # Weather Prediction and Folklore
            {
                "question": "What does 'Red sky at night' traditionally predict?",
                "options": ["Rain tomorrow", "Sailor's delight", "Strong winds", "Temperature drop"],
                "correct": 1,
                "category": "folklore"
            },
            {
                "question": "According to folklore, what does a ring around the moon mean?",
                "options": ["Clear skies", "Rain within 24 hours", "Temperature change", "Strong winds"],
                "correct": 1,
                "category": "folklore"
            },
            {
                "question": "What animal is said to predict the length of winter?",
                "options": ["Groundhog", "Squirrel", "Bear", "Rabbit"],
                "correct": 0,
                "category": "folklore"
            },
            {
                "question": "Who is the most famous TV weatherman?",
                "options": ["Al Roker", "Jim Cantore", "Both A and B", "Neither"],
                "correct": 2,
                "category": "pop_culture"
            },
            
            # Weather Technology and Modern Forecasting
            {
                "question": "What does Doppler radar detect?",
                "options": ["Temperature", "Wind patterns", "Humidity", "Air pressure"],
                "correct": 1,
                "category": "technology"
            },
            {
                "question": "How far in advance can weather be accurately predicted?",
                "options": ["2-3 days", "5-7 days", "10-14 days", "1 month"],
                "correct": 1,
                "category": "technology"
            },
            {
                "question": "What do weather satellites primarily measure?",
                "options": ["Ground temperature", "Cloud patterns", "Wind speed", "Humidity"],
                "correct": 1,
                "category": "technology"
            },
            {
                "question": "What is the most accurate weather prediction method?",
                "options": ["Computer models", "Almanacs", "Animal behavior", "Cloud watching"],
                "correct": 0,
                "category": "technology"
            },
            
            # Seasonal Weather Patterns
            {
                "question": "What causes seasons on Earth?",
                "options": ["Distance from sun", "Earth's tilt", "Solar activity", "Moon phases"],
                "correct": 1,
                "category": "seasons"
            },
            {
                "question": "During which season do most thunderstorms occur?",
                "options": ["Spring", "Summer", "Fall", "Winter"],
                "correct": 1,
                "category": "seasons"
            },
            {
                "question": "What weather pattern brings heavy rains to California?",
                "options": ["El Niño", "La Niña", "Monsoon", "Trade winds"],
                "correct": 0,
                "category": "seasons"
            },
            {
                "question": "When is peak hurricane season in the Atlantic?",
                "options": ["June-July", "July-August", "August-September", "September-October"],
                "correct": 2,
                "category": "seasons"
            }
        ]
    
    def generate_data_based_questions(self) -> List[Dict[str, Any]]:
        """Generate questions based on actual CSV data"""
        questions = []
        
        if not self.data_insights:
            return questions
        
        try:
            # Basic comparison questions
            questions.extend(self._generate_comparison_questions())
            
            # Extreme weather questions  
            questions.extend(self._generate_extreme_questions())
            
            # Temperature range questions
            questions.extend(self._generate_range_questions())
            
            # Seasonal and condition questions
            questions.extend(self._generate_condition_questions())
            
            # Relative comparison questions
            questions.extend(self._generate_relative_questions())
            
            self.logger.info(f"Generated {len(questions)} data-based questions")
            
        except Exception as e:
            self.logger.error(f"Error generating data-based questions: {e}")
        
        return questions
    
    def _generate_comparison_questions(self) -> List[Dict[str, Any]]:
        """Generate basic comparison questions"""
        questions = []
        
        # Temperature questions
        cities_by_max_temp = sorted(self.data_insights.items(), 
                                  key=lambda x: x[1]['max_temp'], reverse=True)
        cities_by_min_temp = sorted(self.data_insights.items(), 
                                  key=lambda x: x[1]['min_temp'])
        
        if len(cities_by_max_temp) >= 4:
            hottest_city = cities_by_max_temp[0][0]
            other_cities = [city[0] for city in cities_by_max_temp[1:4]]
            questions.append({
                "question": "Based on 2024 data, which city recorded the highest maximum temperature?",
                "options": [hottest_city] + other_cities,
                "correct": 0,
                "category": "data_based"
            })
            
            coldest_city = cities_by_min_temp[0][0]
            other_cities = [city[0] for city in cities_by_min_temp[-3:]]
            questions.append({
                "question": "Which city experienced the lowest minimum temperature in 2024?",
                "options": [coldest_city] + other_cities,
                "correct": 0,
                "category": "data_based"
            })
        
        # Humidity questions
        cities_by_humidity = sorted(self.data_insights.items(), 
                                  key=lambda x: x[1]['avg_humidity'], reverse=True)
        cities_by_min_humidity = sorted(self.data_insights.items(), 
                                      key=lambda x: x[1]['min_humidity'])
        
        if len(cities_by_humidity) >= 4:
            most_humid = cities_by_humidity[0][0]
            other_cities = [city[0] for city in cities_by_humidity[1:4]]
            questions.append({
                "question": "Which city had the highest average humidity in 2024?",
                "options": [most_humid] + other_cities,
                "correct": 0,
                "category": "data_based"
            })
            
            driest_city = cities_by_min_humidity[0][0]
            other_cities = [city[0] for city in cities_by_min_humidity[-3:]]
            questions.append({
                "question": "Which city had the lowest humidity levels in 2024?",
                "options": [driest_city] + other_cities,
                "correct": 0,
                "category": "data_based"
            })
        
        # Wind and precipitation
        cities_by_wind = sorted(self.data_insights.items(), 
                              key=lambda x: x[1]['max_wind'], reverse=True)
        cities_by_precip = sorted(self.data_insights.items(), 
                                key=lambda x: x[1]['total_precip'], reverse=True)
        
        if len(cities_by_wind) >= 4:
            windiest_city = cities_by_wind[0][0]
            other_cities = [city[0] for city in cities_by_wind[1:4]]
            questions.append({
                "question": "Which city experienced the highest wind speeds in 2024?",
                "options": [windiest_city] + other_cities,
                "correct": 0,
                "category": "data_based"
            })
        
        if len(cities_by_precip) >= 4:
            wettest_city = cities_by_precip[0][0]
            other_cities = [city[0] for city in cities_by_precip[1:4]]
            questions.append({
                "question": "Which city received the most total precipitation in 2024?",
                "options": [wettest_city] + other_cities,
                "correct": 0,
                "category": "data_based"
            })
            
            driest_precip = cities_by_precip[-1][0]
            other_cities = [city[0] for city in cities_by_precip[-4:-1]]
            questions.append({
                "question": "Which city received the least precipitation in 2024?",
                "options": [driest_precip] + other_cities,
                "correct": 0,
                "category": "data_based"
            })
        
        return questions
    
    def _generate_extreme_questions(self) -> List[Dict[str, Any]]:
        """Generate questions about extreme values"""
        questions = []
        
        for city, data in self.data_insights.items():
            # Specific temperature facts
            max_temp = data['max_temp']
            min_temp = data['min_temp']
            
            # Create plausible but wrong temperatures
            wrong_max_temps = [
                max_temp + random.randint(5, 15),
                max_temp - random.randint(3, 8),
                max_temp + random.randint(18, 25)
            ]
            
            options = [f"{max_temp:.0f}°F"] + [f"{temp:.0f}°F" for temp in wrong_max_temps]
            random.shuffle(options)
            correct_idx = options.index(f"{max_temp:.0f}°F")
            
            questions.append({
                "question": f"What was the highest temperature recorded in {city} during 2024?",
                "options": options,
                "correct": correct_idx,
                "category": "data_based"
            })
            
            # Humidity extremes
            max_humidity = data['max_humidity']
            wrong_humidity = [
                max_humidity + random.randint(5, 15),
                max_humidity - random.randint(5, 15),
                max_humidity + random.randint(20, 30)
            ]
            wrong_humidity = [max(0, min(100, h)) for h in wrong_humidity]  # Keep within 0-100%
            
            options = [f"{max_humidity:.0f}%"] + [f"{h:.0f}%" for h in wrong_humidity]
            random.shuffle(options)
            correct_idx = options.index(f"{max_humidity:.0f}%")
            
            questions.append({
                "question": f"What was the highest humidity level recorded in {city} during 2024?",
                "options": options,
                "correct": correct_idx,
                "category": "data_based"
            })
        
        return questions[:8]  # Limit to avoid too many
    
    def _generate_range_questions(self) -> List[Dict[str, Any]]:
        """Generate questions about temperature ranges"""
        questions = []
        
        for city, data in list(self.data_insights.items())[:3]:  # Limit to 3 cities
            temp_range = data['max_temp'] - data['min_temp']
            
            # Create plausible wrong answers
            wrong_ranges = [
                temp_range + random.randint(10, 20),
                temp_range - random.randint(5, 15),
                temp_range + random.randint(25, 35)
            ]
            
            options = [f"{temp_range:.0f}°F"] + [f"{wr:.0f}°F" for wr in wrong_ranges]
            random.shuffle(options)
            correct_idx = options.index(f"{temp_range:.0f}°F")
            
            questions.append({
                "question": f"What was the temperature range (max - min) for {city} in 2024?",
                "options": options,
                "correct": correct_idx,
                "category": "data_based"
            })
        
        return questions
    
    def _generate_condition_questions(self) -> List[Dict[str, Any]]:
        """Generate questions about weather conditions"""
        questions = []
        
        # Most common conditions per city
        for city, data in self.data_insights.items():
            common_condition = data['common_condition']
            
            # Create alternative conditions
            other_conditions = ['Clear', 'Cloudy', 'Partially cloudy', 'Rain', 'Snow', 'Overcast']
            other_conditions = [c for c in other_conditions if c != common_condition]
            
            if len(other_conditions) >= 3:
                options = [common_condition] + random.sample(other_conditions, 3)
                random.shuffle(options)
                correct_idx = options.index(common_condition)
                
                questions.append({
                    "question": f"What was the most common weather condition in {city} during 2024?",
                    "options": options,
                    "correct": correct_idx,
                    "category": "data_based"
                })
        
        return questions[:4]  # Limit to avoid repetition
    
    def _generate_relative_questions(self) -> List[Dict[str, Any]]:
        """Generate questions comparing cities relatively"""
        questions = []
        
        cities_list = list(self.data_insights.items())
        
        if len(cities_list) >= 3:
            # Compare average temperatures between two cities
            city1, data1 = cities_list[0]
            city2, data2 = cities_list[1]
            city3, data3 = cities_list[2]
            
            avg1, avg2, avg3 = data1['avg_temp'], data2['avg_temp'], data3['avg_temp']
            
            # Find which city had higher average
            if avg1 > avg2:
                higher_city, lower_city = city1, city2
            else:
                higher_city, lower_city = city2, city1
            
            questions.append({
                "question": f"Which city had a higher average temperature in 2024?",
                "options": [higher_city, lower_city, city3, "They were equal"],
                "correct": 0,
                "category": "data_based"
            })
            
            # Wind comparison
            if data1['max_wind'] > data2['max_wind']:
                windier_city, calmer_city = city1, city2
            else:
                windier_city, calmer_city = city2, city1
                
            questions.append({
                "question": f"Between {city1} and {city2}, which city experienced stronger winds in 2024?",
                "options": [windier_city, calmer_city, "Both had identical winds", "Neither had wind data"],
                "correct": 0,
                "category": "data_based"
            })
        
        return questions
    
    def get_quiz_questions(self, num_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Get a mix of static and data-based questions for a quiz
        Prioritizes CSV-based questions when available
        
        Args:
            num_questions: Number of questions to return
            
        Returns:
            List of question dictionaries
        """
        static_questions = self.get_static_questions()
        data_questions = self.generate_data_based_questions()
        
        selected_questions = []
        
        # Prioritize data-based questions (aim for 60-70% if available)
        target_data_questions = min(int(num_questions * 0.65), len(data_questions))
        target_static_questions = num_questions - target_data_questions
        
        # Select data-based questions first
        if data_questions and target_data_questions > 0:
            selected_data = random.sample(data_questions, target_data_questions)
            selected_questions.extend(selected_data)
        
        # Fill remaining with static questions
        remaining_needed = num_questions - len(selected_questions)
        if static_questions and remaining_needed > 0:
            selected_static = random.sample(static_questions, min(remaining_needed, len(static_questions)))
            selected_questions.extend(selected_static)
        
        # If we still need more questions, use any remaining
        if len(selected_questions) < num_questions:
            all_remaining = [q for q in (static_questions + data_questions) if q not in selected_questions]
            still_needed = num_questions - len(selected_questions)
            if all_remaining:
                additional = random.sample(all_remaining, min(still_needed, len(all_remaining)))
                selected_questions.extend(additional)
        
        # Shuffle the final list
        random.shuffle(selected_questions)
        
        # Shuffle answer options for static questions only
        for question in selected_questions:
            if question.get('category') != 'data_based':
                # Store correct answer before shuffling
                correct_answer = question['options'][question['correct']]
                
                # Shuffle options
                random.shuffle(question['options'])
                
                # Update correct index
                question['correct'] = question['options'].index(correct_answer)
        
        return selected_questions
    
    def get_cities(self) -> List[str]:
        """Get the list of cities from the data"""
        return self.cities.copy()
    
    def refresh_data(self) -> None:
        """Reload and reanalyze the CSV data"""
        self._load_weather_data()
        self._analyze_data()
        self.logger.info("Weather data refreshed")


# Convenience function for easy import
def create_trivia_generator(csv_file_path: str = "data/combined_data.csv") -> WeatherTriviaGenerator:
    """
    Factory function to create a trivia generator instance
    
    Args:
        csv_file_path: Path to the weather data CSV file
        
    Returns:
        WeatherTriviaGenerator instance
    """
    return WeatherTriviaGenerator(csv_file_path)