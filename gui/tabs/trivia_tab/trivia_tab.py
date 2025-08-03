# trivia/trivia_tab.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import StringVar
from features.trivia.question_engine import QuestionEngine
from features.trivia.stats_manager import StatsManager
from features.trivia.scoreboard_header import TriviaScoreboardHeader
from features.trivia.timer_widget import TimerWidget
from features.trivia.sound_manager import SoundManager
from features.trivia.visual_effects import ConfettiGif, LightningEffect, LightningGif

class TriviaTab(tb.Frame):
    def __init__(self, master, csv_path):
        super().__init__(master)
        self.engine = QuestionEngine(csv_path)
        self.stats = StatsManager()
        
        # Initialize sound manager with error handling
        try:
            self.sound_mgr = SoundManager()
        except Exception as e:
            print(f"Warning: Sound initialization failed: {e}")
            self.sound_mgr = None
        self.questions = []
        self.current_index = 0
        
        # Game structure: 4 rounds of 5 questions each
        self.total_rounds = 4
        self.questions_per_round = 5
        self.current_round = 0
        self.current_round_correct = 0
        self.game_in_progress = False
        self.round_in_progress = False

        self.question_var = StringVar()
        self.question_var.set("Press 'Start Round' to begin.")
        self.answer_vars = []
        self.answer_buttons = []

        for i in range(4):
            var = StringVar()
            var.set("")  # Initialize with empty string
            # Use default parameter to properly capture the loop variable
            btn = tb.Button(self, textvariable=var, command=self._make_answer_handler(i))
            self.answer_vars.append(var)
            self.answer_buttons.append(btn)

        self.header = TriviaScoreboardHeader(self, self.stats, self.engine.get_city_list())
        self.header.pack(fill=X, pady=5)

        self.timer = TimerWidget(self, duration=20, callback=self.handle_timeout)
        self.timer.pack(pady=5)

        self.question_label = tb.Label(self, textvariable=self.question_var, wraplength=600, font=("Helvetica", 14))
        self.question_label.pack(pady=10)

        for btn in self.answer_buttons:
            btn.configure(width=40)  # Set fixed width in characters
            btn.pack(padx=100, pady=3)  # Remove fill=X, increase padx for centering

        control_frame = tb.Frame(self)
        control_frame.pack(pady=10)
        self.start_button = tb.Button(control_frame, text="Start Round", command=self.start_round)
        self.start_button.pack(side=LEFT, padx=10)
        tb.Button(control_frame, text="Quit", command=self.quit_game).pack(side=LEFT, padx=10)

    def _make_answer_handler(self, idx):
        """Create a proper closure for answer button handlers"""
        return lambda: self.check_answer(idx)

    def start_round(self):
        if not self.game_in_progress:
            # Starting a new game
            self.current_round = 1
            self.game_in_progress = True
            self.stats.increment_games_played()
        else:
            # Starting next round in current game
            self.current_round += 1
            
        # Disable start button during round
        self.round_in_progress = True
        self.start_button.config(state="disabled")
            
        self.questions = self.engine.get_question_round()
        self.current_index = 0
        self.current_round_correct = 0
        self.show_question()
        self.timer.reset()
        self.timer.start()
        self.header.update_stats()

    def show_question(self):
        if self.current_index >= len(self.questions):
            # Round complete - show round stats only
            round_percent = (self.current_round_correct / self.questions_per_round) * 100
            self.question_var.set(f"Round {self.current_round} complete! You scored {self.current_round_correct} out of {self.questions_per_round} ({round_percent:.1f}%).")
            
            # Round is complete - re-enable start button
            self.round_in_progress = False
            self.start_button.config(state="normal")
            
            if self.current_round >= self.total_rounds:
                # Game complete - show final effects
                self.end_game()
            else:
                # More rounds to play - timer already stopped in check_answer()
                self.question_var.set(f"Round {self.current_round} complete! You scored {self.current_round_correct} out of {self.questions_per_round} ({round_percent:.1f}%). Click 'Start Round' for Round {self.current_round + 1}.")
            return

        q = self.questions[self.current_index]
        self.question_var.set(q['question'])
        for i, choice in enumerate(q['choices']):
            self.answer_vars[i].set(choice)
        self.header.update_stats()

    def check_answer(self, idx):
        # Check if we're still within the questions list
        if self.current_index >= len(self.questions):
            return  # Round is already complete, ignore the click
        
        selected = self.answer_vars[idx].get()
        correct = self.questions[self.current_index]['answer']
        
        # Track stats
        self.stats.increment_total_questions()
        if selected == correct:
            self.stats.increment_correct_answers()
            self.current_round_correct += 1
            if self.sound_mgr:
                self.sound_mgr.play("right")
        else:
            if self.sound_mgr:
                self.sound_mgr.play("wrong")
            
        self.current_index += 1
        
        # Check if round complete (all 5 questions answered)
        if self.current_index >= len(self.questions):
            self.timer.stop()  # Stop timer when round complete
            if self.sound_mgr:
                self.sound_mgr.play("round_over")  # Play round over sound
            
        self.show_question()

    def handle_timeout(self):
        # Timer ran out before all questions answered
        if self.sound_mgr:
            self.sound_mgr.play("round_over")
        
        # Count remaining questions as attempted but wrong
        remaining_questions = len(self.questions) - self.current_index
        for _ in range(remaining_questions):
            self.stats.increment_total_questions()
            
        # Show round completion
        round_percent = (self.current_round_correct / self.questions_per_round) * 100
        self.question_var.set(f"Time's up! Round {self.current_round} complete! You scored {self.current_round_correct} out of {self.questions_per_round} ({round_percent:.1f}%).")
        
        # Round is complete - re-enable start button
        self.round_in_progress = False
        self.start_button.config(state="normal")
        
        if self.current_round >= self.total_rounds:
            # Game complete
            self.end_game()
        else:
            # More rounds to play
            self.question_var.set(f"Time's up! Round {self.current_round} complete! You scored {self.current_round_correct} out of {self.questions_per_round} ({round_percent:.1f}%). Click 'Start Round' for Round {self.current_round + 1}.")
            
        self.header.update_stats()
    
    def end_game(self):
        """Handle end of complete game (5 rounds)"""
        self.game_in_progress = False
        final_percent = self.stats.get_score_percentage()
        
        self.question_var.set(f"Game Complete! Final Score: {self.stats.correct_answers} out of {self.stats.total_questions_asked} ({final_percent}%). Click 'Start Round' for a new game.")
        
        # Show celebration or encouragement based on final percentage
        if final_percent >= 75:
            ConfettiGif(master=self)
        else:
            if self.sound_mgr:
                self.sound_mgr.play("thunder")
            LightningGif(master=self)

    def quit_game(self):
        self.stats.reset()
        self.timer.stop()
        self.engine.reset()
        self.current_round = 0
        self.current_round_correct = 0
        self.game_in_progress = False
        self.round_in_progress = False
        self.start_button.config(state="normal")  # Re-enable start button
        self.question_var.set("Press 'Start Round' to begin.")
        for var in self.answer_vars:
            var.set("")
        self.header.update_stats()
