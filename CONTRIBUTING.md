# Contributing to PhishGuard AI

Thank you for your interest in contributing to PhishGuard AI! This document provides guidelines for contributing to this bachelor's project.

## 🎓 Academic Context

This is primarily a bachelor's degree final project. While the project is open for educational purposes and feedback, please note that major changes may not be incorporated as this represents academic work.

## 🐛 Reporting Issues

If you find bugs or have suggestions:

1. **Check existing issues** first to avoid duplicates
2. **Create a detailed issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Screenshots if applicable

## 💡 Suggesting Enhancements

For feature suggestions:

1. **Check if it aligns** with the project's educational goals
2. **Provide detailed description** of the enhancement
3. **Explain the use case** and potential benefits
4. **Consider implementation complexity**

## 🔧 Development Setup

If you want to contribute code:

1. **Fork the repository**
2. **Clone your fork**:
   \`\`\`bash
   git clone https://github.com/yourusername/phishguard-ai.git
   \`\`\`
3. **Create a virtual environment**:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   \`\`\`
4. **Install dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
5. **Download NLTK data**:
   \`\`\`bash
   python scripts/download_nltk_data.py
   \`\`\`

## 📝 Code Style

- Follow **PEP 8** Python style guidelines
- Use **meaningful variable names**
- Add **comments** for complex logic
- Include **docstrings** for functions and classes
- Keep **functions focused** and reasonably sized

## 🧪 Testing

Before submitting changes:

1. **Test the application** thoroughly
2. **Verify model training** works correctly
3. **Check Gmail integration** (if applicable)
4. **Test on different browsers** for frontend changes
5. **Ensure no sensitive data** is committed

## 📋 Pull Request Process

1. **Create a feature branch**:
   \`\`\`bash
   git checkout -b feature/your-feature-name
   \`\`\`
2. **Make your changes** with clear, focused commits
3. **Update documentation** if necessary
4. **Test your changes** thoroughly
5. **Submit a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Testing notes

## 🚫 What Not to Contribute

Please avoid:
- **Major architectural changes** (this is an academic project)
- **Unrelated features** outside the scope of phishing detection
- **Breaking changes** without discussion
- **Sensitive data** or credentials
- **Large datasets** (use external links instead)

## 📚 Educational Value

When contributing, consider:
- **Learning opportunities** for other students
- **Code clarity** and educational value
- **Documentation quality**
- **Best practices** demonstration

## 🤝 Code of Conduct

- Be **respectful** and constructive
- **Help others learn** from your contributions
- **Acknowledge** the academic nature of this project
- **Provide helpful feedback** on issues and PRs

## 📞 Questions?

If you have questions about contributing:
- **Open an issue** for discussion
- **Check existing documentation**
- **Review the project structure**

Thank you for helping make this project better while respecting its academic context!
\`\`\`

Finally, let's create a simple deployment guide:
