"""
Configuration settings for the Roommate Matching System
"""
import os

class Config:
    """Application configuration"""
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - using SQLite for simplicity
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///roommate_matcher.db'
    
    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Similarity calculation weights (must sum to 1.0)
    WEIGHTS = {
        'sleep_time': 0.25,
        'study_time': 0.20,
        'cleanliness': 0.20,
        'noise_tolerance': 0.15,
        'personality': 0.10,
        'hobbies': 0.10
    }
    
    # Hobby overlap bonus multiplier
    HOBBY_OVERLAP_BONUS = 1.2
    
    # A* Search Algorithm Parameters
    ASTAR_MAX_NODES = 10000  # Maximum nodes to explore (prevent infinite loops)
    ASTAR_ENABLED = True  # Enable A* search algorithm
