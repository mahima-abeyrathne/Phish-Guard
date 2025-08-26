import os
import json
import base64
from datetime import datetime
import sys
import joblib
import pandas as pd
import numpy as np
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import nltk

# IMPORTANT: Allow insecure transport for localhost development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Add scripts directory to path
sys.path.append('scripts')

# --- NLTK Data Path Setup (Crucial for resolving LookupError) ---
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'nltk_data')
if NLTK_DATA_PATH not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_PATH)
    os.makedirs(NLTK_DATA_PATH, exist_ok=True)
    print(f"NLTK data path added: {NLTK_DATA_PATH}")

# Verify if 'punkt' is found after setting the path
try:
    nltk.data.find('tokenizers/punkt')
    print("✅ NLTK 'punkt' tokenizer successfully located at app startup.")
except LookupError:
    print("❌ NLTK 'punkt' tokenizer NOT found at app startup. Please ensure you have run 'python scripts/download_nltk_data.py'.")

# Try to import our model training module
try:
    from model_training import PhishingDetectionModel
    MODEL_AVAILABLE = True
    print("✅ Model training module imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import model training module: {e}")
    MODEL_AVAILABLE = False
    PhishingDetectionModel = None

# Try to import email API integration module
try:
    from email_api_integration import EmailAPIClient
    EMAIL_API_MODULE_AVAILABLE = True # Renamed for clarity
    print("✅ Email API integration module imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import email API integration module: {e}")
    EMAIL_API_MODULE_AVAILABLE = False
    EmailAPIClient = None

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize detector
detector = None
if MODEL_AVAILABLE:
    detector = PhishingDetectionModel()
    
    # Try to load pre-trained model
    try:
        detector.load_model('phishing_detection_model.pkl')
        print("✅ Pre-trained model loaded successfully")
    except Exception as e:
        print(f"⚠️ No pre-trained model found: {e}")

# Initialize email API client
email_api_client = None
if EMAIL_API_MODULE_AVAILABLE:
    email_api_client = EmailAPIClient()

# Constants for Gmail API - CORRECT SCOPE
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_CREDENTIALS_FILE = 'credentials.json'

@app.route('/')
def index():
    """Main page"""
    user_email = session.get('user_email')
    return render_template('index.html', user_email=user_email)

@app.route('/support')
def support_page():
    return render_template('support.html')

@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/detect', methods=['POST'])
def detect_phishing():
    """Detect phishing in provided email content"""
    try:
        data = request.get_json()
        sender_email = data.get('senderEmail', '')
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        if not MODEL_AVAILABLE:
            return jsonify({
                'error': 'Model training module not available. Please check your installation.'
            }), 400
        
        if not detector or not detector.best_model:
            return jsonify({
                'error': 'No trained model available. Please train a model first using the "Train Model" tab.'
            }), 400
        
        # Make prediction with detailed analysis
        prediction = detector.predict(subject, body, sender_email)
        
        # Add timestamp
        prediction['timestamp'] = datetime.now().isoformat()

        # Generate avoidance advice
        if prediction['is_phishing']:
            prediction['avoidance_advice'] = detector.preprocessor.generate_avoidance_advice(prediction)
        else:
            prediction['avoidance_advice'] = detector.preprocessor.generate_avoidance_advice(prediction) # Still provide general safety tips
        
        return jsonify(prediction)
    
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/train-model', methods=['POST'])
def train_model():
    """Train the phishing detection model"""
    try:
        if not MODEL_AVAILABLE:
            return jsonify({'error': 'Model training module not available'}), 500
        
        # Initialize new detector
        global detector
        detector = PhishingDetectionModel()
        
        print("Creating sample dataset...")
        df = detector.create_sample_dataset()
        print(f"Dataset created with {len(df)} samples")
        
        print("Preparing features...")
        X, y = detector.prepare_features(df)
        print(f"Features prepared: {X.shape}")
        
        print("Training models...")
        results = detector.train_models(X, y)
        
        print("Saving model...")
        detector.save_model('phishing_detection_model.pkl')
        
        # Get best model info
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        best_accuracy = results[best_model_name]['accuracy']
        
        print(f"Training completed! Best model: {best_model_name} with accuracy: {best_accuracy:.4f}")
        
        return jsonify({
            'message': 'Model trained successfully!',
            'best_model': best_model_name,
            'accuracy': float(best_accuracy),
            'all_results': {name: float(result['accuracy']) for name, result in results.items()},
            'dataset_size': len(df),
            'feature_count': X.shape[1] if hasattr(X, 'shape') else 'unknown'
        })
    
    except Exception as e:
        print(f"Training error: {e}")
        return jsonify({'error': f'Training failed: {str(e)}'}), 500

@app.route('/scan-emails', methods=['GET'])
def scan_emails():
    """Fetch and analyze emails from configured APIs for the logged-in user."""
    try:
        if not EMAIL_API_MODULE_AVAILABLE or not email_api_client:
            return jsonify({
                'error': 'Email API integration module not available. Please check your installation.'
            }), 400
        
        if not detector or not detector.best_model:
            return jsonify({
                'error': 'No trained model available. Please train a model first using the "Train Model" tab.'
            }), 400

        # Check for user credentials in session
        user_token_data = session.get('gmail_token')
        if not user_token_data:
            return jsonify({
                'error': 'No Gmail account connected. Please connect your inbox via the "Connect Inbox" tab.'
            }), 401

        # Load credentials from session data
        creds = email_api_client.load_credentials_from_dict(user_token_data)
        if not creds:
            # If refresh failed or data invalid, clear session and prompt re-auth
            session.pop('gmail_token', None)
            session.pop('user_email', None)
            return jsonify({
                'error': 'Failed to load or refresh Gmail credentials. Please reconnect your inbox.'
            }), 401

        # If credentials were refreshed, update session
        if isinstance(creds, dict): # load_credentials_from_dict returns dict if refreshed
            session['gmail_token'] = creds
            creds = email_api_client.load_credentials_from_dict(creds) # Reload as Credentials object

        print(f"Fetching emails for user: {session.get('user_email', 'Unknown')}")
        all_emails = email_api_client.get_all_emails(max_results=15, creds=creds) # Changed max_results to 15
        
        if not all_emails:
            return jsonify({
                'message': 'No emails fetched from Gmail. Check API configurations or inbox content.',
                'emails': []
            })

        analyzed_emails = []
        for email in all_emails:
            try:
                prediction = detector.predict(email.get('subject', ''), email.get('body', ''), email.get('sender', ''))
                
                # Generate avoidance advice for scanned emails
                prediction['avoidance_advice'] = detector.preprocessor.generate_avoidance_advice(prediction)

                analyzed_emails.append({
                    'id': email.get('id'),
                    'subject': email.get('subject', 'No Subject'),
                    'sender': email.get('sender', 'Unknown Sender'),
                    'date': email.get('date', 'No Date'),
                    'source': email.get('source', 'N/A'),
                    'is_phishing': prediction['is_phishing'],
                    'confidence': prediction['confidence'],
                    'phishing_probability': prediction['phishing_probability'],
                    'detailed_analysis': prediction # This now includes avoidance_advice
                })
            except Exception as e:
                print(f"Error analyzing email {email.get('id')}: {e}")
                analyzed_emails.append({
                    'id': email.get('id'),
                    'subject': email.get('subject', 'No Subject'),
                    'sender': email.get('sender', 'Unknown Sender'),
                    'date': email.get('date', 'No Date'),
                    'source': email.get('source', 'N/A'),
                    'error': f"Analysis failed: {str(e)}"
                })

        return jsonify({
            'message': f'Successfully scanned {len(analyzed_emails)} emails.',
            'emails': analyzed_emails
        })
    
    except Exception as e:
        print(f"Scan emails error: {e}")
        return jsonify({'error': f'Failed to scan emails: {str(e)}'}), 500

@app.route('/api/auth/google')
def google_auth():
    """Initiates the Google OAuth 2.0 flow."""
    if not EMAIL_API_MODULE_AVAILABLE or not email_api_client:
        return jsonify({'error': 'Email API integration not available.'}), 500

    # Determine redirect URI
    if os.environ.get('VERCEL_URL'):
        redirect_uri = f"https://{os.environ['VERCEL_URL']}/oauth2callback"
    else:
        redirect_uri = url_for('oauth2callback', _external=True)

    print(f"🔗 DEBUG: Redirect URI being used: {redirect_uri}")

    try:
        # Check if credentials.json exists
        if not os.path.exists(GMAIL_CREDENTIALS_FILE):
            return jsonify({
                'error': f"❌ {GMAIL_CREDENTIALS_FILE} not found. Please download it from Google Cloud Console."
            }), 500
        
        # Load and validate client config
        with open(GMAIL_CREDENTIALS_FILE, 'r') as f:
            client_config = json.load(f)

        # Validate client config structure
        if 'web' not in client_config and 'installed' not in client_config:
            return jsonify({
                'error': '❌ Invalid credentials.json format. Please download the correct OAuth 2.0 Client credentials.'
            }), 500

        # Generate authorization URL and state
        authorization_url, state, flow = email_api_client.get_auth_url(redirect_uri)
        
        # Store session data (only serializable parts)
        session['oauth_state'] = state
        session['oauth_client_config'] = client_config
        session['oauth_redirect_uri'] = redirect_uri
        
        print(f"🚀 Redirecting to Google OAuth: {authorization_url}")
        return redirect(authorization_url)
        
    except Exception as e:
        print(f"❌ Error initiating Google OAuth: {e}")
        return jsonify({'error': f'Failed to initiate Google OAuth: {str(e)}'}), 500

@app.route('/oauth2callback')
def oauth2callback():
    """Handles the Google OAuth 2.0 callback."""
    state = request.args.get('state')
    code = request.args.get('code')
    error = request.args.get('error')

    print(f"🔄 OAuth callback received - State: {state}, Code: {'Present' if code else 'Missing'}, Error: {error}")

    if error:
        print(f"❌ OAuth callback error: {error}")
        return redirect(url_for('index', auth_error=error))

    if state != session.pop('oauth_state', None):
        print("❌ State mismatch during OAuth callback")
        return redirect(url_for('index', auth_error='State mismatch or session expired'))

    # Retrieve serializable parts from session
    client_config = session.pop('oauth_client_config', None)
    redirect_uri = session.pop('oauth_redirect_uri', None)

    if not client_config or not redirect_uri:
        print("❌ OAuth client config or redirect URI not found in session")
        return redirect(url_for('index', auth_error='OAuth session expired or invalid'))

    try:
        # Reconstruct the flow object
        flow = InstalledAppFlow.from_client_config(
            client_config, GMAIL_SCOPES, redirect_uri=redirect_uri)
    
        print(f"🔄 Attempting token exchange with redirect_uri: {redirect_uri}")
        print(f"🔄 Full callback URL: {request.url}")
    
        # Exchange code for token with detailed error handling
        try:
            flow.fetch_token(authorization_response=request.url)
            creds = flow.credentials
        
            # Convert credentials to dictionary for session storage
            token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes,
                'expiry': creds.expiry.isoformat() if creds.expiry else None
            }
        
            print("✅ Token exchange successful")
        
        except Exception as token_error:
            print(f"❌ Token exchange failed: {token_error}")
            print(f"❌ Token error type: {type(token_error).__name__}")
            return redirect(url_for('index', auth_error=f'Token exchange failed: {str(token_error)}'))
    
        if token_data:
            session['gmail_token'] = token_data
        
            # Get user email for display
            try:
                creds = email_api_client.load_credentials_from_dict(token_data)
                if creds:
                    service = build('gmail', 'v1', credentials=creds)
                    profile = service.users().getProfile(userId='me').execute()
                    session['user_email'] = profile.get('emailAddress')
                    print(f"✅ User {session['user_email']} connected successfully")
            except Exception as profile_error:
                print(f"⚠️ Warning: Could not get user profile: {profile_error}")
            # Still proceed with connection
        
            return redirect(url_for('index', auth_success='true'))
        else:
            print("❌ Token data is None after exchange")
            return redirect(url_for('index', auth_error='Token data is empty'))
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR during OAuth token exchange: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return redirect(url_for('index', auth_error=f'Token exchange failed: {str(e)}'))

@app.route('/logout')
def logout():
    """Logs out the user by clearing the session."""
    user_email = session.get('user_email', 'Unknown')
    session.pop('gmail_token', None)
    session.pop('user_email', None)
    print(f"👋 User {user_email} logged out")
    return redirect(url_for('index', logout_success='true'))

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    model_status = "loaded" if (detector and detector.best_model) else "not loaded"
    email_api_module_status = "available" if EMAIL_API_MODULE_AVAILABLE else "not available"
    user_connected_to_gmail = "connected" if session.get('gmail_token') else "not connected" # Check actual connection
    
    return jsonify({
        'status': 'healthy',
        'model_available': MODEL_AVAILABLE,
        'model_status': model_status,
        'model_loaded': detector.best_model is not None if detector else False,
        'email_api_module_available': email_api_module_status, # Renamed for clarity
        'user_connected_to_gmail': user_connected_to_gmail, # New status
        'gmail_scopes': GMAIL_SCOPES,
        'timestamp': datetime.now().isoformat(),
        'note': 'Gmail API integration requires proper credentials setup and scope configuration.'
    })

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('scripts', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Email Phishing Detection Tool...")
    print("🌐 Access the web interface at: http://localhost:5000")
    print("⚡ Use the 'Train Model' tab first, then 'Analyze Email' or 'Scan Emails' to test")
    print("🔓 OAUTHLIB_INSECURE_TRANSPORT enabled for localhost development")
    
    if EMAIL_API_MODULE_AVAILABLE:
        print("📧 Gmail API integration module is available")
        print("🔧 Make sure to configure your Google Cloud Console properly:")
        print("   1. Enable Gmail API")
        print("   2. Configure OAuth consent screen with gmail.readonly scope")
        print("   3. Add test users")
        print("   4. Download credentials.json")
    else:
        print("⚠️ Gmail API integration module is NOT available")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
