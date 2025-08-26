import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    packages = [
        "scikit-learn",
        "nltk",
        "pandas",
        "numpy",
        "transformers",
        "torch",
        "Flask",
        "Flask-CORS",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "msal",
        "matplotlib",
        "seaborn",
        "wordcloud",
        "python-dotenv",
        "joblib"
    ]
    
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("All packages installed successfully!")

def setup_directories():
    """Create necessary directories"""
    directories = [
        "scripts",
        "templates",
        "static",
        "data",
        "models",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def create_env_file():
    """Create environment file template"""
    env_content = """# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Microsoft Graph API Configuration
MICROSOFT_CLIENT_ID=your_client_id_here
MICROSOFT_CLIENT_SECRET=your_client_secret_here
MICROSOFT_TENANT_ID=your_tenant_id_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Created .env file template")

def download_nltk_data():
    """Download required NLTK data"""
    import nltk
    
    datasets = ['punkt', 'stopwords', 'vader_lexicon', 'wordnet']
    
    for dataset in datasets:
        try:
            nltk.download(dataset)
            print(f"Downloaded NLTK dataset: {dataset}")
        except Exception as e:
            print(f"Error downloading {dataset}: {e}")

if __name__ == "__main__":
    print("Setting up Email Phishing Detection Tool environment...")
    
    # Install packages
    install_requirements()
    
    # Setup directories
    setup_directories()
    
    # Create environment file
    create_env_file()
    
    # Download NLTK data
    download_nltk_data()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Configure your Gmail API credentials in credentials.json")
    print("2. Update .env file with your Microsoft Graph API credentials")
    print("3. Run the application with: python app.py")
