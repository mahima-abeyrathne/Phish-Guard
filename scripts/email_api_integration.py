import os
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

# Gmail API setup - CORRECT scope for reading emails
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_CREDENTIALS_FILE = 'credentials.json'
GMAIL_TOKEN_FILE = 'token.json'

class EmailAPIClient:
    def __init__(self):
        self.gmail_service = None
        self.current_user_creds = None 
        
    def setup_gmail_api(self):
        """
        Setup Gmail API authentication for a single, pre-configured user.
        This method is primarily for initial setup/testing and local development.
        """
        creds = None
        
        # Load existing token
        if os.path.exists(GMAIL_TOKEN_FILE):
            print(f"Found existing token file: {GMAIL_TOKEN_FILE}")
            try:
                creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, GMAIL_SCOPES)
                print("✅ Loaded credentials from token file")
            except Exception as e:
                print(f"❌ Error loading token from {GMAIL_TOKEN_FILE}: {e}")
                creds = None
        else:
            print(f"ℹ️ No token file found at {GMAIL_TOKEN_FILE}")
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Token expired, attempting to refresh...")
                try:
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                except Exception as e:
                    print(f"❌ Error refreshing token: {e}")
                    creds = None
            else:
                print("🔐 No valid token found. Starting OAuth flow...")
                if not os.path.exists(GMAIL_CREDENTIALS_FILE):
                    print(f"❌ ERROR: {GMAIL_CREDENTIALS_FILE} not found!")
                    print("📋 Please download credentials.json from Google Cloud Console:")
                    print("   1. Go to https://console.cloud.google.com/")
                    print("   2. APIs & Services → Credentials")
                    print("   3. Download OAuth 2.0 Client ID as 'credentials.json'")
                    return False
                
                print(f"📁 Found {GMAIL_CREDENTIALS_FILE}. Starting OAuth flow...")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                    print("✅ OAuth flow completed successfully")
                except Exception as e:
                    print(f"❌ ERROR: Failed to complete OAuth flow: {e}")
                    print("🔧 This might be due to:")
                    print("   - Invalid credentials.json file")
                    print("   - Gmail API not enabled")
                    ("   - Incorrect OAuth consent screen configuration")
                    return False
            
            # Save credentials
            if creds:
                try:
                    with open(GMAIL_TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    print(f"💾 New token saved to {GMAIL_TOKEN_FILE}")
                except Exception as e:
                    print(f"❌ ERROR: Failed to save token: {e}")
                    return False
        
        if creds and creds.valid:
            try:
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                self.current_user_creds = creds
                print("✅ Gmail API service built successfully")
                
                # Test the connection
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                print(f"🎯 Connected to Gmail account: {profile.get('emailAddress')}")
                return True
            except Exception as e:
                print(f"❌ ERROR: Failed to build Gmail service: {e}")
                return False
        else:
            print("❌ ERROR: Gmail API setup failed. Credentials are not valid.")
            return False

    def get_auth_url(self, redirect_uri):
        """Generates the Google OAuth authorization URL for dynamic multi-user flow."""
        if not os.path.exists(GMAIL_CREDENTIALS_FILE):
            raise FileNotFoundError(f"credentials.json not found at {GMAIL_CREDENTIALS_FILE}")
        
        # Load client secrets from credentials.json
        with open(GMAIL_CREDENTIALS_FILE, 'r') as f:
            client_config = json.load(f)
        
        # For localhost development, we need to allow insecure transport
        # Import os module locally to avoid naming conflicts
        import os as os_module
        os_module.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        # Use the client_config to create the flow
        flow = InstalledAppFlow.from_client_config(
            client_config, GMAIL_SCOPES, redirect_uri=redirect_uri)
        
        # Generate authorization URL and state for security
        authorization_url, state = flow.authorization_url(
            access_type='offline',  # Request a refresh token
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to ensure scopes are shown
        )
        return authorization_url, state, flow

    def load_credentials_from_dict(self, token_data):
        """Loads credentials from a dictionary (e.g., from session/database)."""
        if not token_data:
            return None
        
        try:
            creds = Credentials(
                token=token_data['token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )
            
            # Check if token needs refreshing
            if creds.expired and creds.refresh_token:
                print("🔄 Token expired, attempting to refresh...")
                try:
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                    # Return updated token data to be saved back to session/database
                    return {
                        'token': creds.token,
                        'refresh_token': creds.refresh_token,
                        'token_uri': creds.token_uri,
                        'client_id': creds.client_id,
                        'client_secret': creds.client_secret,
                        'scopes': creds.scopes,
                        'expiry': creds.expiry.isoformat() if creds.expiry else None
                    }
                except Exception as e:
                    print(f"❌ Error refreshing token: {e}")
                    return None
            return creds
        except Exception as e:
            print(f"❌ Error loading credentials from dict: {e}")
            return None

    def get_gmail_emails(self, max_results=15, creds=None): # Changed default to 15
        """
        Fetch emails from Gmail using provided credentials.
        If no creds are provided, it falls back to the single-user setup.
        """
        service = None
        if creds:
            # Use provided credentials for dynamic user
            try:
                service = build('gmail', 'v1', credentials=creds)
            except Exception as e:
                print(f"❌ Error building Gmail service with provided creds: {e}")
                return []
        elif self.gmail_service:
            # Fallback to the service built by setup_gmail_api
            service = self.gmail_service
        else:
            print("❌ Gmail service not initialized and no credentials provided")
            return []
        
        try:
            print(f"📧 Fetching up to {max_results} emails from Gmail...")
            results = service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            if not messages:
                print("📭 No messages found in Gmail inbox")
                return []

            emails = []
            for message in messages:
                try:
                    msg = service.users().messages().get(
                        userId='me', id=message['id']).execute()
                    email_data = self.parse_gmail_message(msg)
                    emails.append(email_data)
                except Exception as e:
                    print(f"❌ Error processing Gmail message ID {message.get('id', 'N/A')}: {e}")
            
            print(f"✅ Successfully fetched and processed {len(emails)} emails from Gmail")
            return emails
        
        except HttpError as error:
            print(f'❌ Gmail API HTTP error: {error}')
            if error.resp.status == 403:
                print("🔐 This might be a permissions issue. Check your OAuth scopes.")
            return []
        except Exception as error:
            print(f'❌ An error occurred with Gmail API: {error}')
            return []

    def parse_gmail_message(self, message):
        """Parse Gmail message and extract relevant information"""
        headers = message['payload'].get('headers', [])
        
        # Extract headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Extract body
        body = self.extract_gmail_body(message['payload'])
        
        return {
            'id': message['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'source': 'gmail'
        }

    def extract_gmail_body(self, payload):
        """Extract body text from Gmail message payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body

    def get_all_emails(self, max_results=15, creds=None): # Changed default to 15
        """Get emails from all configured sources (currently only Gmail)"""
        all_emails = []
        
        # Get Gmail emails using provided creds or fallback to single-user setup
        gmail_emails = self.get_gmail_emails(max_results, creds)
        all_emails.extend(gmail_emails)
        
        return all_emails

# Test function
if __name__ == "__main__":
    print("🧪 Testing Gmail API Connection...")
    client = EmailAPIClient()
    
    if client.setup_gmail_api():
        print("✅ Gmail API setup successful!")
        
        # Test fetching emails
        emails = client.get_gmail_emails(max_results=3)
        if emails:
            print(f"📧 Successfully fetched {len(emails)} emails:")
            for email in emails:
                print(f"  - Subject: {email['subject'][:50]}...")
                print(f"    From: {email['sender']}")
                print(f"    Date: {email['date']}")
                print()
        else:
            print("📭 No emails fetched")
    else:
        print("❌ Gmail API setup failed!")
