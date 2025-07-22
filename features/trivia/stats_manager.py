# trivia/stats_manager.py

class StatsManager:
    def __init__(self):
        self.games_played = 0
        self.total_questions_asked = 0
        self.correct_answers = 0

    def reset(self):
        self.games_played = 0
        self.total_questions_asked = 0
        self.correct_answers = 0

    def increment_games_played(self):
        self.games_played += 1

    def increment_total_questions(self):
        self.total_questions_asked += 1

    def increment_correct_answers(self):
        self.correct_answers += 1

    def get_score_percentage(self):
        if self.total_questions_asked == 0:
            return 0
        return round((self.correct_answers / self.total_questions_asked) * 100, 2)

    def get_stats_summary(self):
        return {
            'games_played': self.games_played,
            'total_questions': self.total_questions_asked,
            'correct_answers': self.correct_answers,
            'score_percentage': self.get_score_percentage()
        }