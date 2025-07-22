# trivia/trivia_tab.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar
from features.trivia.question_engine import QuestionEngine
from features.trivia.stats_manager import StatsManager
from features.trivia.scoreboard_header import TriviaScoreboardHeader
from features.trivia.timer_widget import TimerWidget
from features.trivia.sound_manager import SoundManager
from features.trivia.visual_effects import ConfettiGif, LightningEffect

class TriviaTab(ttk.Frame):
    def __init__(self, master, csv_path):
        super().__init__(master)
        self.engine = QuestionEngine(csv_path)
        self.stats = StatsManager()
        self.sound_mgr = SoundManager()
        self.questions = []
        self.current_index = 0

        self.question_var = StringVar()
        self.answer_vars = []
        self.answer_buttons = []

        for i in range(4):
            var = StringVar()
            btn = ttk.Button(self, textvariable=var, command=lambda idx=i: self.check_answer(idx))
            self.answer_vars.append(var)
            self.answer_buttons.append(btn)

        self.header = TriviaScoreboardHeader(self, self.stats, self.engine.get_city_list())
        self.header.pack(fill=X, pady=5)

        self.timer = TimerWidget(self, duration=20, callback=self.handle_timeout)
        self.timer.pack(pady=5)

        self.question_label = ttk.Label(self, textvariable=self.question_var, wraplength=600, font=("Helvetica", 14))
        self.question_label.pack(pady=10)

        for btn in self.answer_buttons:
            btn.pack(fill=X, padx=50, pady=5)

        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10)
        ttk.Button(control_frame, text="Start Round", command=self.start_round).pack(side=LEFT, padx=10)
        ttk.Button(control_frame, text="Quit", command=self.quit_game).pack(side=LEFT, padx=10)

    def start_round(self):
        self.questions = self.engine.get_question_round()
        self.current_index = 0
        self.stats.increment_games_played()
        self.show_question()
        self.timer.reset()
        self.timer.start()
        self.header.update_stats()

    def show_question(self):
        if self.current_index >= len(self.questions):
            percent = self.stats.get_score_percentage()
            self.question_var.set(f"Round complete! You scored {self.stats.correct_answers} out of {self.stats.total_questions_asked} ({percent}%).")
            self.sound_mgr.play("round_over")
            if percent >= 75:
                ConfettiGif(master=self)
            else:
                self.sound_mgr.play("thunder")
                LightningEffect(master=self)
            return

        q = self.questions[self.current_index]
        self.question_var.set(q['question'])
        for i, choice in enumerate(q['choices']):
            self.answer_vars[i].set(choice)
        self.header.update_stats()

    def check_answer(self, idx):
        selected = self.answer_vars[idx].get()
        correct = self.questions[self.current_index]['answer']
        self.stats.increment_total_questions()
        if selected == correct:
            self.stats.increment_correct_answers()
            self.sound_mgr.play("right")
        else:
            self.sound_mgr.play("wrong")
        self.current_index += 1
        self.show_question()

    def handle_timeout(self):
        self.stats.increment_total_questions()
        self.current_index += 1
        self.show_question()

    def quit_game(self):
        self.stats.reset()
        self.timer.stop()
        self.engine.reset()
        self.question_var.set("Press 'Start Round' to begin.")
        for var in self.answer_vars:
            var.set("")
        self.header.update_stats()
