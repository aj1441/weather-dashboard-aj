"""Weather Trivia component for the weather dashboard"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import random
import time
import os
try:
    if os.name == 'nt':
        import winsound
    else:
        winsound = None
except ImportError:
    winsound = None
import sys
import logging
from features import create_trivia_generator

class WeatherTriviaComponent:
    """Handles weather trivia game with timer and scoring"""

    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        try:
            self.logger.info("Initializing WeatherTriviaComponent...")
            
            # Initialize trivia generator
            self.logger.info("Creating trivia generator...")
            self.trivia_generator = create_trivia_generator()
            self.logger.info("Trivia generator created successfully")
            
            # Quiz state
            self.questions = []
            self.current_question = 0
            self.score = 0
            self.total_questions = 5
            self.time_remaining = 30
            self.quiz_active = False
            
            # Game statistics
            self.games_played = 0
            self.total_questions_asked = 0
            self.total_correct_answers = 0
            
            self.logger.info("WeatherTriviaComponent initialization completed")
            
        except Exception as e:
            self.logger.error(f"Error in WeatherTriviaComponent.__init__: {e}", exc_info=True)
            # Don't raise - let component continue with defaults
            self.cities = ["Denver, CO", "New York, NY", "Phoenix, AZ", "Seattle, WA"]
            self.questions = []
            self.current_question = 0
            self.score = 0
            self.total_questions = 5
            self.time_remaining = 30
            self.quiz_active = False
            self.games_played = 0
            self.total_questions_asked = 0
            self.total_correct_answers = 0

    def setup_component(self):
        """Create the trivia game interface"""
        try:
            self.logger.info("Starting trivia component setup...")
            
            # Main trivia frame
            self.trivia_frame = tb.Frame(self.parent)
            
            # Title section with grid layout
            title_frame = tb.Frame(self.trivia_frame)
            title_frame.pack(fill=X, pady=20)
            title_frame.grid_columnconfigure(1, weight=1)  # Center column expands
            
            # Left side - Statistics
            stats_frame = tb.LabelFrame(
                title_frame,
                text="📊 Stats",
                bootstyle="info",
                padding=10
            )
            stats_frame.grid(row=0, column=0, sticky="nw", padx=(0, 10))
            
            # Current game score
            self.current_result_label = tb.Label(
                stats_frame,
                text="Ready to play!",
                font=("Helvetica Neue", 10, "bold"),
                bootstyle="primary"
            )
            self.current_result_label.pack()
            
            # Overall statistics
            self.stats_label = tb.Label(
                stats_frame,
                text="Games: 0 | Questions: 0\nCorrect: 0 | Accuracy: 0%",
                font=("Helvetica Neue", 9),
                bootstyle="secondary",
                justify=LEFT
            )
            self.stats_label.pack()
            
            # Center - Title and Instructions
            center_frame = tb.Frame(title_frame)
            center_frame.grid(row=0, column=1, sticky="ew", padx=10)
            
            title_label = tb.Label(
                center_frame,
                text="⚡ Beat the Clock!",
                font=("Helvetica Neue", 28, "bold"),
                bootstyle="warning"
            )
            title_label.pack()
            
            # Instructions
            try:
                cities = self.trivia_generator.get_cities()
            except:
                cities = ["Denver, CO", "New York, NY", "Phoenix, AZ", "Seattle, WA"]
                
            cities_text = ", ".join(cities)
            instructions = f"""Race the clock to answer 5 trivia questions!
Based on 2024 weather data from: {cities_text}

You have 30 seconds to answer as many questions as possible."""
            
            instructions_label = tb.Label(
                center_frame,
                text=instructions,
                font=("Helvetica Neue", 11),
                justify=CENTER,
                wraplength=500,
                bootstyle="secondary"
            )
            instructions_label.pack(pady=10)
            
            # Right side - Timer
            timer_frame = tb.LabelFrame(
                title_frame,
                text="⏰ Timer",
                bootstyle="info",
                padding=10
            )
            timer_frame.grid(row=0, column=2, sticky="ne", padx=(10, 0))
            
            # Timer display
            self.timer_label = tb.Label(
                timer_frame,
                text="Timer: :30",
                font=("Helvetica Neue", 16, "bold"),
                bootstyle="info"
            )
            self.timer_label.pack()
            
            # Game controls frame
            controls_frame = tb.Frame(self.trivia_frame)
            controls_frame.pack(fill=X, pady=20)
            
            # Start Quiz button
            self.start_btn = tb.Button(
                controls_frame,
                text="🚀 Start Quiz",
                command=self.start_quiz,
                bootstyle="success",
                style="Outline.TButton"
            )
            self.start_btn.pack(side=LEFT, padx=10)
            
            # Reset button
            self.reset_btn = tb.Button(
                controls_frame,
                text="🔄 Reset Stats",
                command=self.reset_stats,
                bootstyle="danger",
                style="Outline.TButton"
            )
            self.reset_btn.pack(side=LEFT, padx=10)
            
            # Question area
            self.question_frame = tb.LabelFrame(
                self.trivia_frame,
                text="Question",
                bootstyle="primary",
                padding=20
            )
            self.question_frame.pack(fill=BOTH, expand=True, pady=20)
            
            # Question text
            self.question_label = tb.Label(
                self.question_frame,
                text="Click 'Start Quiz' to begin!",
                font=("Helvetica Neue", 14),
                wraplength=700,
                justify=CENTER
            )
            self.question_label.pack(pady=20)
            
            # Answer buttons frame
            self.answers_frame = tb.Frame(self.question_frame)
            self.answers_frame.pack(fill=X, pady=10)
            
            # Create answer buttons
            self.answer_buttons = []
            for i in range(4):
                btn = tb.Button(
                    self.answers_frame,
                    text="",
                    command=lambda idx=i: self.answer_selected(idx),
                    bootstyle="outline-primary",
                    state=DISABLED
                )
                btn.pack(fill=X, pady=5)
                self.answer_buttons.append(btn)
            
            self.logger.info("Trivia component setup completed successfully")
            return self.trivia_frame
            
        except Exception as e:
            self.logger.error(f"Error in setup_component: {e}", exc_info=True)
            # Create a minimal fallback frame
            self.trivia_frame = tb.Frame(self.parent)
            error_label = tb.Label(
                self.trivia_frame, 
                text="Error loading trivia component - using fallback", 
                font=("Helvetica", 14)
            )
            error_label.pack(pady=50)
            return self.trivia_frame
    
    def start_quiz(self):
        """Start a new trivia quiz"""
        if self.quiz_active:
            return
            
        try:
            self.quiz_active = True
            self.current_question = 0
            self.score = 0
            self.time_remaining = 30
            
            # Get questions from trivia generator
            try:
                self.questions = self.trivia_generator.get_quiz_questions(self.total_questions)
                self.logger.info(f"Generated {len(self.questions)} trivia questions")
            except Exception as e:
                self.logger.error(f"Error generating questions: {e}")
                # Fallback to a simple question if generator fails
                self.questions = [{
                    "question": "What does a barometer measure?",
                    "options": ["Temperature", "Humidity", "Wind Speed", "Air Pressure"],
                    "correct": 3
                }]
            
            # Update UI
            self.start_btn.config(state=DISABLED)
            self.current_result_label.config(text="Quiz in progress...")
            
            # Enable answer buttons
            for btn in self.answer_buttons:
                btn.config(state=NORMAL)
            
            # Start timer
            self.start_timer()
            
            # Show first question
            self.show_question()
            
        except Exception as e:
            self.logger.error(f"Error starting quiz: {e}", exc_info=True)
            self.current_result_label.config(text="Error starting quiz")
    
    def start_timer(self):
        """Start the 30-second countdown timer"""
        self.update_timer_display()  # Initial display
        self.schedule_timer_update()
    
    def schedule_timer_update(self):
        """Schedule the next timer update using tkinter's after method"""
        if self.quiz_active and self.time_remaining > 0:
            # Schedule next update in 1000ms (1 second)
            self.parent.after(1000, self.timer_tick)
    
    def timer_tick(self):
        """Handle each timer tick"""
        if not self.quiz_active:
            return
            
        self.time_remaining -= 1
        self.update_timer_display()
        
        if self.time_remaining <= 0:
            self.timer_expired()
        else:
            self.schedule_timer_update()
    
    def update_timer_display(self):
        """Update timer display on main thread"""
        try:
            self.timer_label.config(text=f"Timer: :{self.time_remaining:02d}")
            
            # Change color as time runs low
            if self.time_remaining <= 10:
                self.timer_label.config(bootstyle="danger")
            elif self.time_remaining <= 20:
                self.timer_label.config(bootstyle="warning")
            else:
                self.timer_label.config(bootstyle="info")
        except Exception as e:
            self.logger.error(f"Error updating timer display: {e}")
    
    def timer_expired(self):
        """Handle timer expiration on main thread"""
        try:
            self.timer_label.config(text="Timer: :00", bootstyle="danger")
            self.play_sound("timeout")
            self.end_quiz()
        except Exception as e:
            self.logger.error(f"Error in timer expiration: {e}")
    
    def show_question(self):
        """Display the current question"""
        try:
            if self.current_question >= len(self.questions):
                self.end_quiz()
                return
            
            question_data = self.questions[self.current_question]
            self.question_label.config(
                text=f"Question {self.current_question + 1}/{self.total_questions}: {question_data['question']}"
            )
            
            # Update answer buttons
            for i, btn in enumerate(self.answer_buttons):
                if i < len(question_data['options']):
                    btn.config(text=question_data['options'][i], state=NORMAL)
                else:
                    btn.config(text="", state=DISABLED)
                    
        except Exception as e:
            self.logger.error(f"Error showing question: {e}")
    
    def answer_selected(self, selected_idx):
        """Handle answer selection"""
        if not self.quiz_active:
            return
        
        try:
            question_data = self.questions[self.current_question]
            correct_idx = question_data['correct']
            
            if selected_idx == correct_idx:
                self.score += 1
                self.play_sound("correct")
            else:
                self.play_sound("incorrect")
            
            self.current_question += 1
            
            if self.current_question >= self.total_questions:
                self.end_quiz()
            else:
                self.show_question()
                
        except Exception as e:
            self.logger.error(f"Error in answer selection: {e}")
    
    def end_quiz(self):
        """End the current quiz and show results"""
        try:
            self.quiz_active = False
            
            # Update statistics
            self.games_played += 1
            questions_answered = min(self.current_question, self.total_questions)
            self.total_questions_asked += questions_answered
            self.total_correct_answers += self.score
            
            # Calculate percentage
            percentage = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
            
            # Show results
            self.current_result_label.config(
                text=f"Quiz Complete! Score: {self.score}/{questions_answered} ({percentage:.0f}%)"
            )
            
            # Update overall stats
            overall_accuracy = (self.total_correct_answers / self.total_questions_asked * 100) if self.total_questions_asked > 0 else 0
            self.stats_label.config(
                text=f"Games: {self.games_played} | Questions: {self.total_questions_asked}\nCorrect: {self.total_correct_answers} | Accuracy: {overall_accuracy:.1f}%"
            )
            
            # Show celebration or encouragement
            if percentage >= 75:
                self.show_celebration()
            else:
                self.show_encouragement()
            
            # Reset UI
            self.start_btn.config(state=NORMAL)
            self.timer_label.config(text="Timer: :30", bootstyle="info")
            self.question_label.config(text="Click 'Start Quiz' to play again!")
            
            # Disable answer buttons
            for btn in self.answer_buttons:
                btn.config(state=DISABLED, text="")
                
        except Exception as e:
            self.logger.error(f"Error ending quiz: {e}")
    
    def show_celebration(self):
        """Show celebration for 75%+ score"""
        try:
            self.current_result_label.config(
                text=f"🎉 EXCELLENT! Score: {self.score}/{self.total_questions} 🎉",
                bootstyle="success"
            )
            print("🎊 Confetti celebration! 🎊")
        except Exception as e:
            self.logger.error(f"Error showing celebration: {e}")
    
    def show_encouragement(self):
        """Show encouragement for <75% score"""
        try:
            self.current_result_label.config(
                text=f"⚡ Better Luck Next Time! Score: {self.score}/{self.total_questions} ⚡",
                bootstyle="warning"
            )
            print("⚡ Lightning strike! Better luck next time! ⚡")
        except Exception as e:
            self.logger.error(f"Error showing encouragement: {e}")
    
    def play_sound(self, sound_type):
        """Play sound effects"""
        try:
            if os.name == 'nt' and winsound:  # Windows
                if sound_type == "correct":
                    winsound.Beep(800, 200)  # High beep
                elif sound_type == "incorrect":
                    winsound.Beep(400, 400)  # Low beep
                elif sound_type == "timeout":
                    winsound.Beep(200, 800)  # Buzzer
            else:  # Mac/Linux
                if sound_type == "correct":
                    os.system("afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || echo '\\a'")
                elif sound_type == "incorrect":
                    os.system("afplay /System/Library/Sounds/Sosumi.aiff 2>/dev/null || echo '\\a'")
                elif sound_type == "timeout":
                    os.system("afplay /System/Library/Sounds/Funk.aiff 2>/dev/null || echo '\\a'")
        except Exception as e:
            self.logger.error(f"Sound error: {e}")
            # Fallback to system beep
            print("\\a")
    
    def reset_stats(self):
        """Reset all game statistics"""
        try:
            self.games_played = 0
            self.total_questions_asked = 0
            self.total_correct_answers = 0
            
            self.current_result_label.config(text="Statistics reset!")
            self.stats_label.config(text="Games: 0 | Questions: 0\nCorrect: 0 | Accuracy: 0%")
        except Exception as e:
            self.logger.error(f"Error resetting stats: {e}")
    
    def restyle(self):
        """Safe restyle method"""
        try:
            # Safe restyle - only if not in middle of quiz to avoid conflicts
            if not hasattr(self, 'quiz_active') or not self.quiz_active:
                self.logger.debug("WeatherTriviaComponent restyle completed")
        except Exception as e:
            self.logger.error(f"Error in trivia component restyle: {e}")