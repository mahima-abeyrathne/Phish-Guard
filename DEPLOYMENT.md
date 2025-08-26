# Deployment Guide for PhishGuard AI

This guide covers different deployment options for the PhishGuard AI application.

## 🚀 Local Development

Already covered in the main README.md file.

## 🌐 Production Deployment Options

### Option 1: Heroku (Recommended for beginners)

1. **Install Heroku CLI**
2. **Create a Heroku app**:
   \`\`\`bash
   heroku create your-app-name
   \`\`\`
3. **Set environment variables**:
   \`\`\`bash
   heroku config:set FLASK_SECRET_KEY='your-secret-key'
   heroku config:set DATABASE_URL='your-database-url'
   \`\`\`
4. **Deploy**:
   \`\`\`bash
   git push heroku main
   \`\`\`

### Option 2: Vercel (Good for Flask apps)

1. **Install Vercel CLI**:
   \`\`\`bash
   npm i -g vercel
   \`\`\`
2. **Deploy**:
   \`\`\`bash
   vercel
   \`\`\`
3. **Configure environment variables** in Vercel dashboard

### Option 3: DigitalOcean App Platform

1. **Connect your GitHub repository**
2. **Configure build settings**
3. **Set environment variables**
4. **Deploy**

## 🔧 Production Considerations

### Environment Variables
\`\`\`bash
FLASK_SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
GMAIL_CREDENTIALS_JSON=base64-encoded-credentials
\`\`\`

### Database
- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

### Security
- Use HTTPS in production
- Set secure session cookies
- Validate all inputs
- Keep dependencies updated

## 📊 Monitoring

Consider adding:
- Application performance monitoring
- Error tracking (e.g., Sentry)
- Log aggregation
- Health check endpoints

## 🔄 CI/CD Pipeline

Example GitHub Actions workflow:

\`\`\`yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "your-app-name"
        heroku_email: "your-email@example.com"
