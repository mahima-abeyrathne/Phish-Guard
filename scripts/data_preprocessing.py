import pandas as pd
import numpy as np
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
from urllib.parse import urlparse
import os

# --- Define NLTK Data Path (consistent with scripts/download_nltk_data.py) ---
# This path is relative to the 'scripts' directory where this file resides.
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')

# Add this path to NLTK's search path if not already present.
# This ensures NLTK looks in our local project directory for downloaded data.
if NLTK_DATA_PATH not in nltk.data.path:
    nltk.data.path.insert(0, NLTK_DATA_PATH)  # Insert at beginning for priority
    os.makedirs(NLTK_DATA_PATH, exist_ok=True) # Ensure the directory exists
    print(f"NLTK data path added to global (from data_preprocessing.py): {NLTK_DATA_PATH}")

class EmailPreprocessor:
    def __init__(self):
        # Crucial: Ensure NLTK data is available when EmailPreprocessor is initialized
        self._ensure_nltk_data()

        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            print("Warning: NLTK 'stopwords' not available during EmailPreprocessor init. Proceeding without stop words.")
            self.stop_words = set()
        self.stemmer = PorterStemmer()
        self.suspicious_keywords = [
            'urgent', 'winner', 'congratulations', 'click here', 'act now',
            'limited time', 'free', 'guarantee', 'no obligation', 'risk free',
            'call now', 'don\'t delay', 'order now', 'what are you waiting for',
            'take action', 'don\'t hesitate', 'apply now', 'get started now',
            'exclusive deal', 'as seen on', 'increase sales', 'increase traffic',
            'verify', 'account', 'password', 'ssn', 'social security number', 'bank account', 'credit card', 'login credentials', 'pin', 'security code', 'date of birth', 'dob',
            'security', 'alert', 'invoice', 'payment', 'update', 'confirm', 'suspicious', 'transaction', 'unusual', 'locked',
            'compromised', 'refund', 'claim', 'cancel', 'expire', 'restore',
            'kindly', 'dear customer', 'dear user', 'attention', 'important'
        ]
        self.common_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'aol.com', 'icloud.com']
    
    def _ensure_nltk_data(self):
        """
        Ensures NLTK 'punkt', 'stopwords', and 'vader_lexicon' are downloaded and found.
        This is called upon instantiation of EmailPreprocessor to robustly handle LookupErrors.
        """
        # Define datasets and their expected NLTK paths
        datasets_to_check = {
            'punkt': 'tokenizers/punkt',
            'stopwords': 'corpora/stopwords',
            'vader_lexicon': 'sentiment/vader_lexicon'
        }

        for name, path in datasets_to_check.items():
            try:
                # Attempt to find the data using NLTK's data path
                nltk.data.find(path)
                # print(f"NLTK '{name}' found for EmailPreprocessor initialization.")
            except LookupError:
                # If not found, attempt to download it to our custom NLTK_DATA_PATH
                print(f"NLTK '{name}' not found during EmailPreprocessor init. Attempting to download it to: {NLTK_DATA_PATH}...")
                try:
                    nltk.download(name, download_dir=NLTK_DATA_PATH, quiet=True)
                    print(f"Successfully downloaded '{name}' to {NLTK_DATA_PATH}.")
                except Exception as e:
                    print(f"ERROR: Failed to download '{name}' during EmailPreprocessor init: {e}")
                    print(f"Please ensure internet access or run 'python scripts/download_nltk_data.py' manually and check for errors.")

    def clean_text(self, text):
        """Clean and preprocess email text"""
        if pd.isna(text):
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def extract_features(self, text):
        """Extract various features from email text"""
        features = {}
        
        # Basic text features
        features['length'] = len(str(text))
        features['word_count'] = len(str(text).split())
        features['char_count'] = len(str(text))
        
        # Suspicious keywords count (using the class's list)
        text_lower = str(text).lower()
        features['suspicious_word_count'] = sum(1 for word in self.suspicious_keywords if word in text_lower)
        
        # URL and email count
        features['url_count'] = len(re.findall(r'http\S+|www\S+|https\S+', str(text)))
        features['email_count'] = len(re.findall(r'\S+@\S+', str(text)))
        
        # Exclamation marks and capital letters
        features['exclamation_count'] = str(text).count('!')
        features['capital_ratio'] = sum(1 for c in str(text) if c.isupper()) / len(str(text)) if len(str(text)) > 0 else 0
        
        return features

    def tokenize_and_stem(self, text):
        """Tokenize and stem text with robust fallback"""
        try:
            # Try to use NLTK's word_tokenize
            tokens = word_tokenize(str(text))
        except LookupError:
            # Fallback to simple split if NLTK tokenizer not found
            tokens = str(text).split()
        except Exception as e:
            # Any other error, fallback to simple split
            print(f"Warning: Error in tokenization: {e}, falling back to simple split.")
            tokens = str(text).split()
        
        # Filter stop words and stem
        tokens = [token for token in tokens if token.lower() not in self.stop_words]
        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
        return ' '.join(stemmed_tokens)

    def prepare_dataset(self, df):
        """Prepare dataset for machine learning"""
        # Clean text
        df['cleaned_subject'] = df['subject'].apply(self.clean_text)
        df['cleaned_body'] = df['body'].apply(self.clean_text)
        df['combined_text'] = df['cleaned_subject'] + ' ' + df['cleaned_body']
        
        # Extract features
        feature_dicts = df['combined_text'].apply(self.extract_features)
        feature_df = pd.DataFrame(list(feature_dicts))
        
        # Combine with original dataframe
        result_df = pd.concat([df, feature_df], axis=1)
        
        return result_df

    def generate_avoidance_advice(self, analysis_results):
        """Generates actionable advice for users to avoid phishing based on analysis."""
        advice = []

        if analysis_results.get('is_phishing'):
            advice.append("This email has been flagged as potentially malicious. Do NOT interact with it.")

            if analysis_results.get('personal_info_requests'):
                advice.append("Never share personal information (passwords, SSN, bank details) via email. Legitimate organizations will not ask for this.")
            
            if analysis_results.get('suspicious_urls_count', 0) > 0:
                advice.append("Do not click on any links in this email. Hover over links to see the actual URL before clicking, and manually type known website addresses.")
            
            if analysis_results.get('urgency_score', 0) > 5:
                advice.append("Be wary of urgent or threatening language. Phishers often create a sense of urgency to bypass critical thinking.")
            
            if analysis_results.get('spoofing_risk') == "High Risk":
                advice.append("The sender's email address or domain appears suspicious. Always verify the sender's authenticity, especially for unexpected emails.")
            
            if analysis_results.get('grammar_quality') == "70%": # Assuming 70% means moderate/poor
                advice.append("Poor grammar and spelling are common signs of phishing attempts. Legitimate communications are usually well-written.")
            
            if analysis_results.get('suspicious_keywords_list'):
                advice.append(f"Watch out for suspicious keywords like: {', '.join(analysis_results['suspicious_keywords_list'])}. These are often used in scams.")
            
            if analysis_results.get('domain_reputation') == "Untrusted":
                advice.append("The sender's domain is untrusted. Be extremely cautious with emails from unknown or unusual domains.")

            advice.append("If you suspect an email is phishing, report it to your IT department or email provider, then delete it.")
            advice.append("When in doubt, contact the organization directly using official contact information (not from the email).")
        else:
            advice.append("This email appears safe based on our analysis. However, always remain vigilant and follow general email security best practices.")
            advice.append("Always double-check the sender's email address and look for any inconsistencies.")
            advice.append("Be cautious of unexpected attachments or links, even from known senders.")

        return advice


    def get_detailed_analysis(self, subject, body, sender_email=""):
        """Extract detailed analysis points for the report"""
        full_text = str(subject) + " " + str(body)
        cleaned_text = self.clean_text(full_text)
        
        analysis = {}
        
        # --- Risk Indicators ---
        # Urgency Score (0-10)
        urgency_score = sum(1 for kw in self.suspicious_keywords if kw in full_text.lower())
        analysis['urgency_score'] = min(urgency_score, 10) # Cap at 10
        
        # Grammar Quality (mock for now, or simple check)
        # A more advanced implementation would use a grammar checking library
        analysis['grammar_quality'] = "100%" if len(cleaned_text) > 20 and len(re.findall(r'[^\w\s]', full_text)) < 5 else "70%"
        
        # Personal Info Requests
        pii_keywords = ['password', 'ssn', 'social security number', 'bank account', 'credit card', 'login credentials', 'pin', 'security code', 'date of birth', 'dob']
        analysis['personal_info_requests'] = any(kw in full_text.lower() for kw in pii_keywords)
        
        # --- Keywords ---
        # Extracted Keywords with robust tokenization
        try:
            tokens = word_tokenize(cleaned_text)
        except LookupError:
            # Fallback to simple split if NLTK tokenizer not found
            tokens = cleaned_text.split()
        except Exception as e:
            # Any other error, fallback to simple split
            tokens = cleaned_text.split()

        filtered_tokens = [word for word in tokens if word.isalpha() and word.lower() not in self.stop_words]
        
        suspicious_keywords_found = [kw for kw in self.suspicious_keywords if kw in full_text.lower()]
        analysis['suspicious_keywords_count'] = len(suspicious_keywords_found)
        analysis['extracted_keywords'] = list(set(filtered_tokens[:10])) # Top 10 unique keywords
        analysis['suspicious_keywords_list'] = list(set(suspicious_keywords_found))

        # --- URL Analysis ---
        extracted_urls = re.findall(r'http\S+|www\S+|https\S+', str(body) + str(subject))
        analysis['total_urls_found'] = len(extracted_urls)
        analysis['extracted_urls'] = extracted_urls
        
        suspicious_urls_count = 0
        for url in extracted_urls:
            parsed_url = urlparse(url)
            # Simple check for suspicious patterns
            if "badlink" in parsed_url.netloc or "verify" in parsed_url.path or "login" in parsed_url.path:
                suspicious_urls_count += 1
        analysis['suspicious_urls_count'] = suspicious_urls_count

        # --- Sender Analysis ---
        domain = ""
        if "@" in sender_email:
            domain = sender_email.split('@')[1].lower()
        
        analysis['domain_reputation'] = "Untrusted"
        if domain in self.common_domains:
            analysis['domain_reputation'] = "Trusted"
        elif domain:
            # Mock check for known good domains (e.g., major companies)
            if "google.com" in domain or "microsoft.com" in domain or "amazon.com" in domain:
                analysis['domain_reputation'] = "Trusted"
            else:
                analysis['domain_reputation'] = "Unusual/Unknown"

        # Spoofing Risk (mock for now)
        analysis['spoofing_risk'] = "Low Risk"
        if "support" in sender_email.lower() and domain not in self.common_domains:
            analysis['spoofing_risk'] = "High Risk"
        elif "admin" in sender_email.lower() and domain not in self.common_domains:
            analysis['spoofing_risk'] = "High Risk"
        elif len(sender_email.split('@')[0]) < 3: # Short sender name
            analysis['spoofing_risk'] = "Medium Risk"
            
        return analysis

# Sample dataset creation (for demonstration)
def create_sample_dataset():
    """Create a sample phishing email dataset"""
    phishing_emails = [
        # Phishing emails (label = 1)
        {'subject': 'URGENT: Your account will be suspended!', 'body': 'Dear customer, your account will be suspended unless you click here immediately and verify your information. Act now!', 'label': 1},
        {'subject': 'Congratulations! You won $1,000,000!', 'body': 'You are our lucky winner! Click here to claim your prize. Limited time offer, don\'t delay!', 'label': 1},
        {'subject': 'Security Alert: Unusual Activity', 'body': 'We detected unusual activity on your account. Click here to secure your account immediately or it will be locked.', 'label': 1},
        {'subject': 'PayPal: Verify Your Account', 'body': 'Your PayPal account has been limited. Please verify your information by clicking the link below to restore access.', 'label': 1},
        {'subject': 'Bank Alert: Suspicious Transaction', 'body': 'We noticed a suspicious transaction on your account. Please confirm your identity by providing your login details.', 'label': 1},
        {'subject': 'IRS: Tax Refund Available', 'body': 'You have a tax refund of $2,847 waiting. Click here to claim it now before it expires.', 'label': 1},
        {'subject': 'Amazon: Order Confirmation Required', 'body': 'Your order for $899.99 needs confirmation. If you didn\'t make this purchase, click here to cancel immediately.', 'label': 1},
        {'subject': 'Microsoft: Account Compromised', 'body': 'Your Microsoft account has been compromised. Click here to change your password and secure your account.', 'label': 1},
        {'subject': 'Free iPhone 15 - Limited Time!', 'body': 'Congratulations! You\'ve been selected to receive a FREE iPhone 15. Click here to claim your prize now!', 'label': 1},
        {'subject': 'Netflix: Payment Failed', 'body': 'Your Netflix payment has failed. Update your payment information immediately to avoid service interruption.', 'label': 1},
        
        # Legitimate emails (label = 0)
        {'subject': 'Meeting scheduled for tomorrow', 'body': 'Hi, I wanted to confirm our meeting scheduled for tomorrow at 2 PM. Please let me know if you need to reschedule.', 'label': 0},
        {'subject': 'Project update', 'body': 'Please find attached the latest project update. Let me know if you have any questions or need clarification.', 'label': 0},
        {'subject': 'Weekly team standup', 'body': 'Our weekly team standup is scheduled for Friday at 10 AM. We\'ll discuss project progress and upcoming tasks.', 'label': 0},
        {'subject': 'Invoice #12345', 'body': 'Please find attached invoice #12345 for services rendered last month. Payment is due within 30 days.', 'label': 0},
        {'subject': 'Conference registration confirmation', 'body': 'Thank you for registering for the Tech Conference 2024. Your registration has been confirmed.', 'label': 0},
        {'subject': 'Newsletter: Tech Updates', 'body': 'Here are the latest technology updates and industry news for this week. Enjoy reading!', 'label': 0},
        {'subject': 'Birthday party invitation', 'body': 'You\'re invited to Sarah\'s birthday party this Saturday at 7 PM. Please RSVP by Thursday.', 'label': 0},
        {'subject': 'Quarterly report ready', 'body': 'The quarterly financial report is now ready for review. Please check the shared folder for the document.', 'label': 0},
        {'subject': 'Training session reminder', 'body': 'Reminder: The mandatory training session is tomorrow at 3 PM in Conference Room A.', 'label': 0},
        {'subject': 'Welcome to the team!', 'body': 'Welcome to our team! We\'re excited to have you on board. Your first day orientation is scheduled for Monday.', 'label': 0}
    ]
    
    return pd.DataFrame(phishing_emails)

if __name__ == "__main__":
    # Create sample dataset
    df = create_sample_dataset()

    # Initialize preprocessor
    preprocessor = EmailPreprocessor()

    # Prepare dataset
    processed_df = preprocessor.prepare_dataset(df)

    print("Sample processed dataset:")
    print(processed_df.head())

    # Test detailed analysis
    test_subject = "URGENT: Your account is locked! Verify your password now."
    test_body = "Click this link to reset your password immediately: http://badlink.com/login?user=admin. Also visit www.malicious.net"
    test_sender = "support@bad-domain.xyz"

    detailed_analysis = preprocessor.get_detailed_analysis(test_subject, test_body, test_sender)
    print("\nDetailed Analysis for test email:")
    for key, value in detailed_analysis.items():
        print(f"- {key}: {value}")
    
    # Test avoidance advice
    advice = preprocessor.generate_avoidance_advice(detailed_analysis)
    print("\nAvoidance Advice:")
    for item in advice:
        print(f"- {item}")

    safe_email_analysis = preprocessor.get_detailed_analysis("Meeting Reminder", "Don't forget about our meeting tomorrow at 2 PM.", "john.doe@company.com")
    safe_advice = preprocessor.generate_avoidance_advice(safe_email_analysis)
    print("\nAvoidance Advice for safe email:")
    for item in safe_advice:
        print(f"- {item}")
