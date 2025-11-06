"""
Database Models for Roommate Matching System
Defines Student and Match entities
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    """Student model - stores student profile and preferences"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    
    # Lifestyle preferences (stored as integers for easy calculation)
    sleep_time = db.Column(db.Integer, nullable=False)  # 0: Early (before 10pm), 1: Medium (10pm-12am), 2: Late (after 12am)
    study_time = db.Column(db.Integer, nullable=False)  # 0: Morning, 1: Afternoon, 2: Evening, 3: Night
    cleanliness = db.Column(db.Integer, nullable=False)  # 1-5 scale
    noise_tolerance = db.Column(db.Integer, nullable=False)  # 1-5 scale
    personality = db.Column(db.Integer, nullable=False)  # 0: Introvert, 1: Ambivert, 2: Extrovert
    
    # Hobbies stored as comma-separated string
    hobbies = db.Column(db.String(500), nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to matches
    matches = db.relationship('Match', foreign_keys='Match.student1_id', backref='student1', lazy=True)
    
    def get_hobbies_list(self):
        """Convert comma-separated hobbies to list"""
        if self.hobbies:
            return [h.strip().lower() for h in self.hobbies.split(',')]
        return []
    
    def to_vector(self):
        """Convert student data to numeric vector for similarity calculation"""
        return {
            'id': self.id,
            'name': self.name,
            'sleep_time': self.sleep_time,
            'study_time': self.study_time,
            'cleanliness': self.cleanliness,
            'noise_tolerance': self.noise_tolerance,
            'personality': self.personality,
            'hobbies': self.get_hobbies_list()
        }
    
    def __repr__(self):
        return f'<Student {self.name}>'


class Match(db.Model):
    """Match model - stores roommate pair assignments"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    student1_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student2_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Compatibility score (0-100)
    compatibility_score = db.Column(db.Float, nullable=False)
    
    # Match reasons (JSON-like string)
    reasons = db.Column(db.Text, nullable=True)
    
    # Timestamp
    matched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Get second student reference
    student2 = db.relationship('Student', foreign_keys=[student2_id], backref='matched_with')
    
    def __repr__(self):
        return f'<Match {self.student1_id}-{self.student2_id}: {self.compatibility_score}%>'
