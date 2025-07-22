# trivia/question_engine.py

import pandas as pd
import random

class QuestionEngine:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.cities = self.df['name'].unique().tolist()
        self.all_questions = self._generate_unique_question_pool()
        self.used_indices = set()

    def _generate_unique_question_pool(self, n=20):
        pool = []
        seen = set()
        attempts = 0
        while len(pool) < n and attempts < 100:
            question_type = random.choice([
                'max_temp_day', 'rainy_days_month', 'snow_count',
                'common_description', 'humid_day', 'uv_index_max'
            ])
            q = None
            if question_type == 'max_temp_day':
                q = self._max_temp_day_question()
            elif question_type == 'rainy_days_month':
                q = self._rainy_days_month_question()
            elif question_type == 'snow_count':
                q = self._snow_count_question()
            elif question_type == 'common_description':
                q = self._common_description_question()
            elif question_type == 'humid_day':
                q = self._humid_day_question()
            elif question_type == 'uv_index_max':
                q = self._uv_index_max_question()
            if q:
                key = (q['question'], q['answer'])  # Simplified uniqueness key
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
        date = random.choice(self.df['datetime'].unique())
        df_on_day = self.df[self.df['datetime'] == date]
        if df_on_day.empty: return None
        correct_row = df_on_day[df_on_day['tempmax'] == df_on_day['tempmax'].max()].iloc[0]
        choices = df_on_day['name'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['name'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['name']
        random.shuffle(choices)
        question = f"Which city had the highest temperature on {date}?"
        return {'question': question, 'choices': choices, 'answer': correct_row['name']}

    def _rainy_days_month_question(self):
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        month = random.choice(range(1, 13))
        city = random.choice(self.cities)
        df_city = self.df[(self.df['name'] == city) & (self.df['datetime'].dt.month == month)]
        rainy_days = df_city[df_city['description'].str.contains('rain', case=False, na=False)].shape[0]
        offsets = [-2, 0, 2, 4]
        choices = [str(max(rainy_days + off, 0)) for off in random.sample(offsets, k=4)]
        answer = str(rainy_days)
        if answer not in choices:
            choices[random.randint(0, len(choices)-1)] = answer
        random.shuffle(choices)
        question = f"How many rainy days were there in {city} in month {month}?"
        return {'question': question, 'choices': choices, 'answer': answer}

    def _snow_count_question(self):
        city = random.choice(self.cities)
        df_city = self.df[self.df['name'] == city]
        snowy_days = df_city[df_city['description'].str.contains('snow', case=False, na=False)].shape[0]
        offsets = [-2, 0, 2, 4]
        choices = [str(max(snowy_days + off, 0)) for off in random.sample(offsets, k=4)]
        answer = str(snowy_days)
        if answer not in choices:
            choices[random.randint(0, len(choices)-1)] = answer
        random.shuffle(choices)
        question = f"How many days did it snow in {city} during 2024?"
        return {'question': question, 'choices': choices, 'answer': answer}

    def _common_description_question(self):
        city = random.choice(self.cities)
        df_city = self.df[self.df['name'] == city]
        if df_city['description'].dropna().empty: return None
        most_common = df_city['description'].value_counts().idxmax()
        options = df_city['description'].dropna().unique().tolist()
        choices = random.sample(options, min(4, len(options)))
        if most_common not in choices:
            choices[random.randint(0, len(choices)-1)] = most_common
        random.shuffle(choices)
        question = f"What was the most common weather description in {city} during 2024?"
        return {'question': question, 'choices': choices, 'answer': most_common}

    def _humid_day_question(self):
        date = random.choice(self.df['datetime'].unique())
        df_on_day = self.df[self.df['datetime'] == date]
        if df_on_day.empty: return None
        correct_row = df_on_day[df_on_day['humidity'] == df_on_day['humidity'].max()].iloc[0]
        choices = df_on_day['name'].drop_duplicates().sample(min(4, len(df_on_day))).tolist()
        if correct_row['name'] not in choices:
            choices[random.randint(0, len(choices)-1)] = correct_row['name']
        random.shuffle(choices)
        question = f"Which city had the highest humidity on {date}?"
        return {'question': question, 'choices': choices, 'answer': correct_row['name']}

    def _uv_index_max_question(self):
        city = random.choice(self.cities)
        df_city = self.df[self.df['name'] == city]
        if df_city.empty: return None
        max_day = df_city[df_city['uvindex'] == df_city['uvindex'].max()].iloc[0]
        answer = str(max_day['uvindex'])
        choices = [str(max_day['uvindex'] + i) for i in [-2, -1, 1, 2]]
        if answer not in choices:
            choices[random.randint(0, len(choices)-1)] = answer
        random.shuffle(choices)
        question = f"What was the highest UV index in {city} in 2024?"
        return {'question': question, 'choices': choices, 'answer': answer}

    def get_city_list(self):
        return self.cities
