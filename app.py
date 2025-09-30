# from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
# from database import db, Participant
# from models import QRGenerator, SMSHandler
# from datetime import datetime
# import os

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'your-secret-key-here'

# db.init_app(app)
# qr_generator = QRGenerator()
# sms_handler = SMSHandler()

# # Create tables
# with app.app_context():
#     db.create_all()

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form['name']
#         phone = request.form['phone']
#         email = request.form.get('email', '')
        
#         # Check if participant already exists
#         existing_participant = Participant.query.filter_by(phone=phone).first()
#         if existing_participant:
#             return "Participant already registered!"
        
#         # Generate unique entrance ID and QR code
#         entrance_id = qr_generator.generate_entrance_id()
#         qr_data = f"ENTRANCE:{entrance_id}|PHONE:{phone}"
#         qr_filename = f"{entrance_id}.png"
#         qr_path = qr_generator.generate_qr_code(qr_data, qr_filename)
        
#         # Save to database
#         participant = Participant(
#             name=name,
#             phone=phone,
#             email=email,
#             entrance_id=entrance_id,
#             qr_code_path=qr_path
#         )
        
#         db.session.add(participant)
#         db.session.commit()
        
#         # Generate feedback link for SMS
#         base_url = request.host_url.rstrip('/')
#         feedback_link = sms_handler.generate_feedback_link(entrance_id, base_url)
        
#         # Send SMS (simulated)
#         sms_message = f"Hello {name}! Thank you for registering. Your entrance ID: {entrance_id}. Feedback link: {feedback_link}"
#         sms_handler.send_sms(phone, sms_message)
        
#         return redirect(url_for('invitation', entrance_id=entrance_id))
    
#     return render_template('register.html')

# @app.route('/invitation/<entrance_id>')
# def invitation(entrance_id):
#     participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
#     return render_template('invitation.html', participant=participant)

# @app.route('/entry/<entrance_id>')
# def record_entry(entrance_id):
#     participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    
#     if not participant.has_entered:
#         participant.entry_time = datetime.utcnow()
#         participant.has_entered = True
#         db.session.commit()
    
#     return jsonify({
#         'status': 'success',
#         'message': f'Entry recorded for {participant.name}',
#         'entry_time': participant.entry_time.strftime('%Y-%m-%d %H:%M:%S')
#     })

# @app.route('/feedback/<entrance_id>', methods=['GET', 'POST'])
# def feedback(entrance_id):
#     participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    
#     if request.method == 'POST':
#         feedback_msg = request.form['feedback']
        
#         participant.feedback = feedback_msg
#         participant.feedback_time = datetime.utcnow()
#         participant.has_exited = True
#         participant.exit_time = datetime.utcnow()
        
#         db.session.commit()
        
#         return render_template('feedback.html', 
#                              participant=participant, 
#                              success=True,
#                              message="Thank you for your feedback!")
    
#     return render_template('feedback.html', participant=participant)

# @app.route('/exit/<entrance_id>')
# def record_exit(entrance_id):
#     participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    
#     if not participant.has_exited:
#         participant.exit_time = datetime.utcnow()
#         participant.has_exited = True
#         db.session.commit()
    
#     return jsonify({
#         'status': 'success',
#         'message': f'Exit recorded for {participant.name}',
#         'exit_time': participant.exit_time.strftime('%Y-%m-%d %H:%M:%S')
#     })

# @app.route('/admin')
# def admin_dashboard():
#     participants = Participant.query.all()
#     stats = {
#         'total': len(participants),
#         'entered': len([p for p in participants if p.has_entered]),
#         'exited': len([p for p in participants if p.has_exited]),
#         'feedback_received': len([p for p in participants if p.feedback])
#     }
#     return render_template('admin.html', participants=participants, stats=stats)

# @app.route('/qr_code/<entrance_id>')
# def get_qr_code(entrance_id):
#     participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
#     return send_file(participant.qr_code_path, mimetype='image/png')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from datetime import datetime, timezone, timedelta
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database configuration
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Timezone configuration (Change to your local timezone)
LOCAL_TIMEZONE = timezone(timedelta(hours=5, minutes=30))  # IST - Change as needed

def get_local_time():
    """Get current time in local timezone"""
    return datetime.now(LOCAL_TIMEZONE)

def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt:
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(LOCAL_TIMEZONE)
    return None


# SQLite Models
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'entrance_id': self.entrance_id,
            'qr_code_path': self.qr_code_path,
            'registration_time': self.registration_time.isoformat() if self.registration_time else None,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'feedback': self.feedback,
            'feedback_time': self.feedback_time.isoformat() if self.feedback_time else None,
            'has_entered': self.has_entered,
            'has_exited': self.has_exited
        }

# Initialize SQLite database
with app.app_context():
    db.create_all()

# Import models after database configuration
from git.smart_attendace.models import QRGenerator, SMSHandler

qr_generator = QRGenerator()
sms_handler = SMSHandler()

# Event Agenda Data
EVENT_AGENDA = {
    "title": "Tech Innovation Summit 2024",
    "date": "December 15, 2024",
    "venue": "Grand Convention Center",
    "schedule": [
        {"time": "09:00 - 09:30", "session": "Registration & Welcome Coffee", "speaker": ""},
        {"time": "09:30 - 10:15", "session": "Opening Keynote: Future of AI", "speaker": "Dr. Sarah Chen"},
        {"time": "10:15 - 11:00", "session": "Blockchain Revolution", "speaker": "Mike Rodriguez"},
        {"time": "11:00 - 11:30", "session": "Networking Break", "speaker": ""},
        {"time": "11:30 - 12:15", "session": "Cloud Computing Trends", "speaker": "Priya Patel"},
        {"time": "12:15 - 13:30", "session": "Lunch & Exhibition", "speaker": ""},
        {"time": "13:30 - 14:15", "session": "Cybersecurity in 2024", "speaker": "James Wilson"},
        {"time": "14:15 - 15:00", "session": "IoT Innovations", "speaker": "Lisa Zhang"},
        {"time": "15:00 - 15:30", "session": "Afternoon Break", "speaker": ""},
        {"time": "15:30 - 16:30", "session": "Panel Discussion: Tech Ethics", "speaker": "Multiple Speakers"},
        {"time": "16:30 - 17:00", "session": "Closing Remarks & Networking", "speaker": "Organizing Committee"}
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        
        # Check if participant already exists
        existing_participant = Participant.query.filter_by(phone=phone).first()
        if existing_participant:
            return "Participant already registered!"
        
        # Generate unique entrance ID and QR code
        entrance_id = qr_generator.generate_entrance_id()
        
        # QR data now points to agenda page
        qr_data = f"{request.host_url}agenda/{entrance_id}"
        qr_filename = f"{entrance_id}.png"
        qr_path = qr_generator.generate_qr_code(qr_data, qr_filename)
        
        # Save to database
        participant = Participant(
            name=name,
            phone=phone,
            email=email,
            entrance_id=entrance_id,
            qr_code_path=qr_path
        )
        
        db.session.add(participant)
        db.session.commit()
        
        # Generate feedback link for SMS (sent immediately after registration)
        base_url = request.host_url.rstrip('/')
        feedback_link = sms_handler.generate_feedback_link(entrance_id, base_url)
        
        # Send SMS with feedback link
        sms_message = f"Hello {name}! Welcome to {EVENT_AGENDA['title']}. Your entrance ID: {entrance_id}. Save this link for feedback after event: {feedback_link}"
        sms_handler.send_sms(phone, sms_message)
        
        return redirect(url_for('invitation', entrance_id=entrance_id))
    
    return render_template('register.html')

@app.route('/invitation/<entrance_id>')
def invitation(entrance_id):
    participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    return render_template('invitation.html', participant=participant, agenda=EVENT_AGENDA)

@app.route('/agenda/<entrance_id>')
def show_agenda(entrance_id):
    participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    
    # Record entry when agenda is accessed via QR code
    if not participant.has_entered:
        participant.entry_time = datetime.utcnow()
        participant.has_entered = True
        db.session.commit()
    
    return render_template('agenda.html', participant=participant, agenda=EVENT_AGENDA)

@app.route('/record_exit', methods=['POST'])
def record_exit():
    entrance_id = request.json.get('entrance_id')
    participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    
    if not participant.has_exited:
        participant.exit_time = datetime.utcnow()
        participant.has_exited = True
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Exit recorded for {participant.name}',
            'exit_time': participant.exit_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'status': 'info',
        'message': 'Exit already recorded'
    })

@app.route('/feedback/<entrance_id>', methods=['GET', 'POST'])
def feedback(entrance_id):
    participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    
    # Check if participant has exited before allowing feedback
    if not participant.has_exited:
        return render_template('feedback.html', 
                             participant=participant, 
                             error=True,
                             message="Please record your exit first before providing feedback.")
    
    if request.method == 'POST':
        feedback_msg = request.form['feedback']
        
        participant.feedback = feedback_msg
        participant.feedback_time = datetime.utcnow()
        db.session.commit()
        
        return render_template('feedback.html', 
                             participant=participant, 
                             success=True,
                             message="Thank you for your feedback!")
    
    return render_template('feedback.html', participant=participant, error=False)

@app.route('/admin')
def admin_dashboard():
    participants = Participant.query.all()
    stats = {
        'total': len(participants),
        'entered': len([p for p in participants if p.has_entered]),
        'exited': len([p for p in participants if p.has_exited]),
        'feedback_received': len([p for p in participants if p.feedback])
    }
    return render_template('admin.html', participants=participants, stats=stats, agenda=EVENT_AGENDA)

@app.route('/qr_code/<entrance_id>')
def get_qr_code(entrance_id):
    participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    return send_file(participant.qr_code_path, mimetype='image/png')

# Real-time updates endpoint
@app.route('/updates/<entrance_id>')
def get_updates(entrance_id):
    participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    return jsonify({
        'has_entered': participant.has_entered,
        'has_exited': participant.has_exited,
        'entry_time': participant.entry_time.strftime('%Y-%m-%d %H:%M:%S') if participant.entry_time else None,
        'exit_time': participant.exit_time.strftime('%Y-%m-%d %H:%M:%S') if participant.exit_time else None,
        'feedback_provided': bool(participant.feedback)
    })

# API endpoints
@app.route('/api/participants')
def api_participants():
    participants = Participant.query.all()
    return jsonify([p.to_dict() for p in participants])

@app.route('/api/participant/<entrance_id>')
def api_participant(entrance_id):
    participant = Participant.query.filter_by(entrance_id=entrance_id).first_or_404()
    return jsonify(participant.to_dict())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)