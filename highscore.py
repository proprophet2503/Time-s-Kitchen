"""
High score management for Time's Kitchen game
"""

import json
import os
from datetime import datetime
from settings import HIGHSCORE_FILE


class HighScoreManager:
    """Manages saving and loading high scores"""
    
    def __init__(self):
        self.scores = []
        self.load_scores()
        
    def load_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    self.scores = json.load(f)
            else:
                self.scores = []
        except (json.JSONDecodeError, IOError):
            self.scores = []
    
    def save_scores(self):
        """Save high scores to file"""
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except IOError as e:
            print(f"Could not save high scores: {e}")
    
    def add_score(self, score, num_players):
        """Add a new score and return if it's a high score"""
        new_entry = {
            'score': score,
            'players': num_players,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.scores.append(new_entry)
        
        # Sort by score descending
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only top 20
        self.scores = self.scores[:20]
        
        self.save_scores()
        
        # Check if this score is in top 10
        is_high_score = any(s['score'] == score and s['date'] == new_entry['date'] 
                          for s in self.scores[:10])
        
        return is_high_score
    
    def get_high_scores(self, limit=10):
        """Get top high scores"""
        return self.scores[:limit]
    
    def get_best_score(self):
        """Get the best score"""
        if self.scores:
            return self.scores[0]['score']
        return 0
