
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(100))
    entrance_id = db.Column(db.String(50), unique=True, nullable=False)
    qr_code_path = db.Column(db.String(200))
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    entry_time = db.Column(db.DateTime)
    exit_time = db.Column(db.DateTime)
    feedback = db.Column(db.Text)
    feedback_time = db.Column(db.DateTime)
    has_entered = db.Column(db.Boolean, default=False)
    has_exited = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Participant {self.name}>'