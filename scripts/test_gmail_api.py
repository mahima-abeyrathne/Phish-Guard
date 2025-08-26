import os
import sys

# Add scripts directory to path to import EmailAPIClient
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Adjust path if necessary

try:
    from scripts.email_api_integration import EmailAPIClient
except ImportError:
    print("ERROR: Could not import EmailAPIClient. Make sure 'email_api_integration.py' is in the 'scripts' directory.")
    sys.exit(1)

def test_gmail_connection():
    """Tests the Gmail API connection independently."""
    print("--- Starting Gmail API Connection Test ---")
    
    client = EmailAPIClient()
    
    print("\nStep 1: Attempting to set up Gmail API...")
    if client.setup_gmail_api():
        print("✅ Gmail API setup successful.")
        
        print("\nStep 2: Attempting to fetch emails from Gmail...")
        try:
            emails = client.get_gmail_emails(max_results=2) # Fetch a couple of emails
            if emails:
                print(f"✅ Successfully fetched {len(emails)} emails from Gmail.")
                print(f"   First email subject: '{emails[0].get('subject', 'N/A')}'")
                print(f"   First email sender: '{emails[0].get('sender', 'N/A')}'")
            else:
                print("⚠️ No emails fetched from Gmail. This might be due to an empty inbox or specific Gmail settings.")
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            print("   This could indicate an issue with permissions or network connectivity after initial setup.")
    else:
        print("❌ Gmail API setup failed. Please review the output above for specific errors.")
        print("   Common issues: 'credentials.json' missing/invalid, or authorization not completed.")
    
    print("\n--- Gmail API Connection Test Complete ---")
    print("If the test failed, please review the instructions and console output carefully.")

if __name__ == "__main__":
    test_gmail_connection()
