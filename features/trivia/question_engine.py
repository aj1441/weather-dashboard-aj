# trivia/question_engine.py

import pandas as pd
import random

class QuestionEngine:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df['city'] = self.df['city'].str.title()
        self.df['time'] = pd.to_datetime(self.df['time'])
        
        # Clean numeric columns - convert malformed string data to numeric
        numeric_cols = [
            'temperature_2m_max (°F)', 'temperature_2m_min (°F)', 'weather_code (wmo code)',
            'temperature_2m_mean (°F)', 'rain_sum (inch)', 'snowfall_sum (inch)',
            'wind_speed_10m_max (mp/h)', 'sunshine_duration (s)', 'surface_pressure_mean (hPa)',
            'relative_humidity_2m_mean (%)', 'cloud_cover_mean (%)'
        ]
        
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        self.cities = self.df['city'].unique().tolist()
        self.all_questions = self._generate_unique_question_pool()
        self.used_indices = set()

    def _generate_unique_question_pool(self, n=20):
        pool = []
        seen = set()
        attempts = 0
        while len(pool) < n and attempts < 100:
            question_type = random.choice([
                'max_temp_day', 'min_temp_day', 'rainy_days_month', 'snow_count',
                'humid_day', 'sunshine_leader', 'cloudiest_city', 'lowest_pressure_day',
                'wind_speed_day', 'early_sunrise_city', 'average_temp_leader'
            ])
            q = getattr(self, f"_{question_type}_question")()
            if q:
                key = (q['question'], q['answer'])
                if key not in seen:
                    pool.append(q)
                    seen.add(key)
            attempts += 1
        return pool

    def get_question_round(self):
        available = [i for i in range(len(self.all_questions)) if i not in self.used_indices]
        round_indices = random.sample(available, min(5, len(available)))
        self.used_indices.update(round_indices)
        return [self.all_questions[i] for i in round_indices]

    def reset(self):
        self.used_indices.clear()

    def _max_temp_day_question(self):
        date = random.choice(self.df['time'].unique())
        df_on_day = self.df[self.df['time'] == date]
        col = 'temperature_2m_max (°F)'
        if df_on_day.empty: return None
        correct_row = df_on_day[df_on_day[col] == df_on_day[col].max()].iloc[0]
        choices = df_on_day['city'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['city'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['city']
        random.shuffle(choices)
        return {
            'question': f"Which city had the highest max temperature on {date.date()}?",
            'choices': choices,
            'answer': correct_row['city']
        }

    def _min_temp_day_question(self):
        date = random.choice(self.df['time'].unique())
        df_on_day = self.df[self.df['time'] == date]
        col = 'temperature_2m_min (°F)'
        if df_on_day.empty: return None
        correct_row = df_on_day[df_on_day[col] == df_on_day[col].min()].iloc[0]
        choices = df_on_day['city'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['city'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['city']
        random.shuffle(choices)
        return {
            'question': f"Which city had the lowest minimum temperature on {date.date()}?",
            'choices': choices,
            'answer': correct_row['city']
        }

    def _rainy_days_month_question(self):
        month = random.choice(range(1, 13))
        city = random.choice(self.cities)
        df_city = self.df[(self.df['city'] == city) & (self.df['time'].dt.month == month)]
        rainy_days = df_city[df_city['rain_sum (inch)'] > 0].shape[0]
        offsets = [-2, 0, 2, 4]
        choices = [str(max(rainy_days + off, 0)) for off in random.sample(offsets, k=4)]
        answer = str(rainy_days)
        if answer not in choices:
            choices[random.randint(0, len(choices)-1)] = answer
        random.shuffle(choices)
        return {
            'question': f"How many rainy days were there in {city} in month {month}?",
            'choices': choices,
            'answer': answer
        }

    def _snow_count_question(self):
        city = random.choice(self.cities)
        df_city = self.df[self.df['city'] == city]
        snowy_days = df_city[df_city['snowfall_sum (inch)'] > 0].shape[0]
        offsets = [-2, 0, 2, 4]
        choices = [str(max(snowy_days + off, 0)) for off in random.sample(offsets, k=4)]
        answer = str(snowy_days)
        if answer not in choices:
            choices[random.randint(0, len(choices)-1)] = answer
        random.shuffle(choices)
        return {
            'question': f"How many days did it snow in {city} during 2024?",
            'choices': choices,
            'answer': answer
        }

    def _humid_day_question(self):
        date = random.choice(self.df['time'].unique())
        df_on_day = self.df[self.df['time'] == date]
        col = 'relative_humidity_2m_mean (%)'
        if df_on_day.empty: return None
        correct_row = df_on_day[df_on_day[col] == df_on_day[col].max()].iloc[0]
        choices = df_on_day['city'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['city'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['city']
        random.shuffle(choices)
        return {
            'question': f"Which city had the highest humidity on {date.date()}?",
            'choices': choices,
            'answer': correct_row['city']
        }

    def _sunshine_leader_question(self):
        city = random.choice(self.cities)
        df_city = self.df[self.df['city'] == city]
        if df_city.empty: return None
        total_sun = int(df_city['sunshine_duration (s)'].sum())
        others = [random.choice(self.cities) for _ in range(3)]
        choices = [city] + others
        random.shuffle(choices)
        return {
            'question': "Which city had the most sunshine in total during 2024?",
            'choices': choices,
            'answer': city
        }

    def _cloudiest_city_question(self):
        date = random.choice(self.df['time'].unique())
        df_on_day = self.df[self.df['time'] == date]
        col = 'cloud_cover_mean (%)'
        if df_on_day.empty or col not in df_on_day.columns: return None
        correct_row = df_on_day[df_on_day[col] == df_on_day[col].max()].iloc[0]
        choices = df_on_day['city'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['city'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['city']
        random.shuffle(choices)
        return {
            'question': f"Which city had the most cloud cover on {date.date()}?",
            'choices': choices,
            'answer': correct_row['city']
        }

    def _lowest_pressure_day_question(self):
        date = random.choice(self.df['time'].unique())
        df_on_day = self.df[self.df['time'] == date]
        col = 'surface_pressure_mean (hPa)'
        if df_on_day.empty or col not in df_on_day.columns: return None
        correct_row = df_on_day[df_on_day[col] == df_on_day[col].min()].iloc[0]
        choices = df_on_day['city'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['city'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['city']
        random.shuffle(choices)
        return {
            'question': f"Which city had the lowest surface pressure on {date.date()}?",
            'choices': choices,
            'answer': correct_row['city']
        }

    def _wind_speed_day_question(self):
        date = random.choice(self.df['time'].unique())
        col = 'wind_speed_10m_max (mp/h)'
        df_on_day = self.df[self.df['time'] == date]
        if df_on_day.empty or col not in df_on_day.columns: return None
        correct_row = df_on_day[df_on_day[col] == df_on_day[col].max()].iloc[0]
        choices = df_on_day['city'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['city'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['city']
        random.shuffle(choices)
        return {
            'question': f"Which city had the highest wind speed on {date.date()}?",
            'choices': choices,
            'answer': correct_row['city']
        }

    def _early_sunrise_city_question(self):
        date = random.choice(self.df['time'].unique())
        df_on_day = self.df[self.df['time'] == date].copy()
        if df_on_day.empty or 'sunrise (iso8601)' not in df_on_day.columns: return None
        df_on_day['sunrise_time'] = pd.to_datetime(df_on_day['sunrise (iso8601)'], errors='coerce')
        df_on_day = df_on_day.dropna(subset=['sunrise_time'])
        if df_on_day.empty: return None
        correct_row = df_on_day[df_on_day['sunrise_time'] == df_on_day['sunrise_time'].min()].iloc[0]
        choices = df_on_day['city'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['city'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['city']
        random.shuffle(choices)
        return {
            'question': f"Which city had the earliest sunrise on {date.date()}?",
            'choices': choices,
            'answer': correct_row['city']
        }

    def _average_temp_leader_question(self):
        city = random.choice(self.cities)
        df_city = self.df[self.df['city'] == city]
        col = 'temperature_2m_mean (°F)'
        if df_city.empty or col not in df_city.columns: return None
        avg_temp = df_city[col].mean()
        others = [c for c in self.cities if c != city]
        choices = random.sample(others, 3) + [city]
        random.shuffle(choices)
        return {
            'question': "Which city had the highest average temperature in 2024?",
            'choices': choices,
            'answer': city
        }

    def get_city_list(self):
        return self.cities
