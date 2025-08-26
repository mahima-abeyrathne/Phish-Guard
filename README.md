# PhishGuard - Email Phishing Detection Tool

![PhishGuard AI](https://img.shields.io/badge/PhishGuard-AI%20Powered-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

An intelligent email phishing detection tool powered by Natural Language Processing (NLP) and Machine Learning (ML). This project was developed as a bachelor's degree final project, demonstrating the application of AI techniques to cybersecurity challenges.

## 🚀 Features

- **AI-Powered Detection**: Uses machine learning models trained on phishing and legitimate email datasets
- **Real-time Analysis**: Instant analysis of email content with confidence scoring
- **Gmail Integration**: Direct inbox scanning via Google Gmail API with OAuth 2.0 authentication
- **Detailed Reports**: Comprehensive analysis including risk indicators, suspicious keywords, URL analysis, and sender reputation
- **User Management**: Secure user authentication and persistent scan history
- **Interactive Dashboard**: Modern web interface with responsive design
- **Avoidance Advice**: Actionable recommendations to help users avoid phishing attacks

## 🛠️ Technologies Used

### Backend
- **Python 3.8+** - Core programming language
- **Flask** - Web framework for API and routing
- **SQLAlchemy** - Database ORM for user and scan data management
- **Flask-SQLAlchemy** - Flask integration for database operations

### Machine Learning & NLP
- **Scikit-learn** - ML algorithms and model training
- **NLTK** - Natural language processing and text analysis
- **Pandas & NumPy** - Data manipulation and numerical operations
- **TF-IDF Vectorization** - Text feature extraction

### Email Integration
- **Google Gmail API** - Secure email access via OAuth 2.0
- **Google Auth Libraries** - Authentication and authorization

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Bootstrap 5** - Responsive UI framework
- **JavaScript** - Dynamic interactions and API calls
- **Font Awesome** - Icons and visual elements

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection for downloading dependencies
- Google Cloud Console account (for Gmail API integration)

## 🔧 Installation & Setup

### 1. Clone the Repository

\`\`\`bash
git clone https://github.com/yourusername/phishguard-ai.git
cd phishguard-ai
\`\`\`

### 2. Create Virtual Environment

\`\`\`bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
\`\`\`

### 3. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Download NLTK Data

\`\`\`bash
python scripts/download_nltk_data.py
\`\`\`

### 5. Configure Gmail API (Optional)

For inbox scanning functionality:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download `credentials.json` and place in project root
6. Configure OAuth consent screen with `gmail.readonly` scope
7. Add your email as a test user

### 6. Set Environment Variables

\`\`\`bash
# Set Flask secret key (recommended for production)
export FLASK_SECRET_KEY='your-super-secret-key-here'

# Optional: Set database URL (defaults to SQLite)
export DATABASE_URL='sqlite:///phishguard.db'
\`\`\`

## 🚀 Running the Application

1. **Start the Flask server:**
   \`\`\`bash
   python app.py
   \`\`\`

2. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

3. **First-time setup:**
   - Go to the "Train Model" tab and click "Train New Model"
   - Wait for training to complete
   - Now you can analyze emails or connect your Gmail for scanning

## 📖 Usage Guide

### Manual Email Analysis
1. Navigate to the "Analyze Email" tab
2. Enter sender email, subject, and body content
3. Click "Analyze Email" to get results
4. Review the detailed analysis report

### Gmail Inbox Scanning
1. Go to "Connect Inbox" tab
2. Click "Connect with Gmail" and authorize the application
3. Navigate to "Scan Emails" tab
4. Click "Scan Connected Accounts" to analyze recent emails

### Model Training
1. Access the "Train Model" tab
2. Click "Train New Model" to create a fresh ML model
3. The system will train multiple algorithms and select the best performer

## 🏗️ Project Structure

\`\`\`
phishguard-ai/
├── app.py                          # Main Flask application
├── models.py                       # Database models and schema
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore rules
├── scripts/
│   ├── download_nltk_data.py       # NLTK data setup
│   ├── model_training.py           # ML model training logic
│   ├── data_preprocessing.py       # Text preprocessing utilities
│   └── email_api_integration.py    # Gmail API integration
├── templates/
│   ├── index.html                  # Main application interface
│   ├── about.html                  # About page
│   ├── support.html                # Support page
│   └── feedback.html               # Feedback page
├── static/
│   └── logo.png                    # Application logo
└── docs/
    ├── user-manual.md              # Comprehensive user guide
    └── technical-explanation.md     # Technical documentation
\`\`\`

## 🔒 Security Considerations

- **OAuth 2.0**: Secure Gmail access with read-only permissions
- **Token Storage**: Encrypted token storage in database
- **Session Management**: Secure session handling with Flask
- **Input Validation**: Sanitized email content processing
- **Environment Variables**: Sensitive data stored in environment variables

## 🧪 Testing

The application includes sample datasets and test cases:

- **Phishing Examples**: Pre-loaded suspicious email samples
- **Legitimate Examples**: Safe email samples for comparison
- **Model Validation**: Cross-validation during training
- **API Testing**: Health check endpoints for system monitoring

## 📊 Model Performance

The ML model achieves:
- **Accuracy**: ~85-95% on sample dataset
- **Features**: 100+ TF-IDF features + 8 numerical features
- **Algorithms**: Random Forest, Logistic Regression, Naive Bayes
- **Validation**: Cross-validation for robust performance estimation

## 🤝 Contributing

This is a bachelor's project, but suggestions and feedback are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍🎓 Academic Context

This project was developed as a bachelor's degree final project, demonstrating:
- **Machine Learning Application**: Practical implementation of ML in cybersecurity
- **Full-Stack Development**: Complete web application with frontend and backend
- **API Integration**: Third-party service integration (Gmail API)
- **Database Design**: Relational database modeling and management
- **Software Engineering**: Version control, documentation, and project structure

## 🙏 Acknowledgments

- **NLTK Team** for natural language processing tools
- **Scikit-learn Contributors** for machine learning algorithms
- **Flask Community** for the web framework
- **Google** for Gmail API access
- **Bootstrap Team** for responsive UI components

## 📞 Contact

For questions about this project:
- **Email**: your.email@example.com
- **LinkedIn**: [Your LinkedIn Profile]
- **University**: [Your University Name]

---

**⚠️ Disclaimer**: This tool is for educational and research purposes. While it demonstrates effective phishing detection techniques, it should not be relied upon as the sole security measure for email protection in production environments.
\`\`\`

Now, let's create a proper `.gitignore` file to exclude sensitive and unnecessary files:

```plaintext file=".gitignore"
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Project-specific files
# Sensitive files - DO NOT COMMIT
credentials.json
token.json
*.pkl
*.joblib

# Database files
*.db
*.sqlite
*.sqlite3
phishguard.db

# Log files
*.log
logs/

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# NLTK data (will be downloaded by script)
scripts/nltk_data/

# Model files (will be generated)
phishing_detection_model.pkl
confusion_matrix.png
model_comparison.png

# Temporary files
tmp/
temp/
