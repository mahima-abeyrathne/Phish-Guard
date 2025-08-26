from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import json
import os

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gmail_token_json = db.Column(db.Text, nullable=True) # Store serialized token

    # Relationship to scan results
    scan_results = db.relationship('EmailScanResult', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_gmail_token(self, token_data):
        self.gmail_token_json = json.dumps(token_data)

    def get_gmail_token(self):
        return json.loads(self.gmail_token_json) if self.gmail_token_json else None

class EmailScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    sender = db.Column(db.String(255), nullable=False)
    body_snippet = db.Column(db.Text, nullable=True) # Store a snippet of the body
    is_phishing = db.Column(db.Boolean, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    phishing_probability = db.Column(db.Float, nullable=False)
    detailed_analysis_json = db.Column(db.Text, nullable=True) # Store serialized detailed analysis
    timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<EmailScanResult {self.subject} - {self.timestamp}>'

    def set_detailed_analysis(self, analysis_data):
        self.detailed_analysis_json = json.dumps(analysis_data)

    def get_detailed_analysis(self):
        return json.loads(self.detailed_analysis_json) if self.detailed_analysis_json else None

def init_db(app):
    """Initializes the database with the Flask app."""
    with app.app_context():
        db.create_all()
        print("Database tables created or already exist.")

def check_db_connection(app):
    """Checks if the database connection is successful."""
    with app.app_context():
        try:
            # Attempt a simple query to check connection
            db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful.")
            return True
        except OperationalError as e:
            print(f"❌ Database connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ An unexpected error occurred during database connection check: {e}")
            return False

if __name__ == '__main__':
    # This block is for testing the models and database setup independently
    from flask import Flask
    
    test_app = Flask(__name__)
    # Use an in-memory SQLite database for quick testing
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(test_app)
    
    with test_app.app_context():
        db.create_all()
        print("Test database tables created.")

        # Example usage:
        new_user = User(email='test@example.com')
        db.session.add(new_user)
        db.session.commit()
        print(f"Added user: {new_user}")

        new_user.set_gmail_token({'access_token': 'abc', 'refresh_token': 'xyz'})
        db.session.commit()
        print(f"User token: {new_user.get_gmail_token()}")

        scan_result = EmailScanResult(
            user_id=new_user.id,
            subject="Test Phishing Email",
            sender="bad@phish.com",
            body_snippet="Click here to verify...",
            is_phishing=True,
            confidence=0.95,
            phishing_probability=0.98,
            timestamp=datetime.now()
        )
        scan_result.set_detailed_analysis({'urgency_score': 8, 'suspicious_urls_count': 1})
        db.session.add(scan_result)
        db.session.commit()
        print(f"Added scan result: {scan_result}")
        print(f"Scan result detailed analysis: {scan_result.get_detailed_analysis()}")

        # Querying
        user_from_db = User.query.filter_by(email='test@example.com').first()
        print(f"Retrieved user: {user_from_db}")
        print(f"User's scan results: {user_from_db.scan_results}")
