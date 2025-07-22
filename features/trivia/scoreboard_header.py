# trivia/scoreboard_header.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class TriviaScoreboardHeader(ttk.Frame):
    def __init__(self, master, stats_manager, city_list):
        super().__init__(master)
        self.stats = stats_manager
        self.city_list = city_list

        # Left Side Stats
        self.games_played_var = ttk.StringVar()
        self.questions_offered_var = ttk.StringVar()

        # Right Side Stats
        self.correct_answers_var = ttk.StringVar()
        self.percentage_var = ttk.StringVar()

        self._build_layout()
        self.update_stats()

    def _build_layout(self):
        self.pack(fill=X, padx=10, pady=5)

        left = ttk.Frame(self)
        center = ttk.Frame(self)
        right = ttk.Frame(self)

        left.pack(side=LEFT, fill=Y, expand=YES)
        center.pack(side=LEFT, fill=BOTH, expand=YES)
        right.pack(side=RIGHT, fill=Y, expand=YES)

        ttk.Label(left, textvariable=self.games_played_var, font=("Helvetica", 12)).pack(anchor=W)
        ttk.Label(left, textvariable=self.questions_offered_var, font=("Helvetica", 12)).pack(anchor=W)

        ttk.Label(center, text="Team 6 Weather Trivia", font=("Helvetica", 16, "bold")).pack()
        ttk.Label(center, text=f"Each round will consist of trivia questions comprised of weather data for the year 2024 from the following cities:", wraplength=500, font=("Helvetica", 10)).pack()
        ttk.Label(center, text=", ".join(self.city_list), font=("Helvetica", 10, "italic"), wraplength=500).pack()
        ttk.Label(center, text="You will have 20 seconds to answer 5 questions", font=("Helvetica", 10)).pack()

        ttk.Label(right, textvariable=self.correct_answers_var, font=("Helvetica", 12)).pack(anchor=E)
        ttk.Label(right, textvariable=self.percentage_var, font=("Helvetica", 12)).pack(anchor=E)

    def update_stats(self):
        stats = self.stats.get_stats_summary()
        self.games_played_var.set(f"Games Played: {stats['games_played']}")
        self.questions_offered_var.set(f"Total Questions Offered: {stats['total_questions']}")
        self.correct_answers_var.set(f"Correct Answers: {stats['correct_answers']}")
        self.percentage_var.set(f"Score Percentage: {stats['score_percentage']}%")
