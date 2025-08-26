import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Import EmailPreprocessor from data_preprocessing.py
from data_preprocessing import EmailPreprocessor, create_sample_dataset

class PhishingDetectionModel:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'naive_bayes': MultinomialNB()
        }
        self.best_model = None
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english', min_df=1)
        self.preprocessor = EmailPreprocessor()
        
    def create_sample_dataset(self):
        """Create a sample dataset using the function from data_preprocessing"""
        return create_sample_dataset()
    
    def prepare_features(self, df):
        """Prepare features with better error handling"""
        processed_df = self.preprocessor.prepare_dataset(df)
        text_features = processed_df['combined_text']
        
        # TF-IDF features with error handling
        try:
            tfidf_features = self.vectorizer.fit_transform(text_features)
            # Convert sparse matrix to dense to avoid scipy issues
            tfidf_dense = tfidf_features.toarray()
        except Exception as e:
            print(f"TF-IDF error: {e}")
            # Fallback: create simple features
            tfidf_dense = np.zeros((len(text_features), self.vectorizer.max_features or 100))
        
        # Numerical features
        numerical_cols = ['length', 'word_count', 'char_count', 'suspicious_word_count',
                         'url_count', 'email_count', 'exclamation_count', 'capital_ratio']
        
        numerical_features = processed_df[numerical_cols].fillna(0).values
        
        # Combine features
        combined_features = np.hstack([tfidf_dense, numerical_features])
        
        return combined_features, processed_df['label'].values
    
    def train_models(self, X, y):
        """Train models with cross-validation"""
        print(f"Training with {len(X)} samples...")
        
        results = {}
        
        for name, model in self.models.items():
            print(f"Training {name}...")
            
            try:
                # Use cross-validation for small datasets
                cv_scores = cross_val_score(model, X, y, cv=3, scoring='accuracy')
                mean_accuracy = cv_scores.mean()
                
                # Train on full dataset
                model.fit(X, y)
                
                results[name] = {
                    'model': model,
                    'accuracy': mean_accuracy,
                    'cv_scores': cv_scores
                }
                
                print(f"{name} CV accuracy: {mean_accuracy:.4f} (+/- {cv_scores.std() * 2:.4f})")
                
            except Exception as e:
                print(f"Error training {name}: {e}")
                continue
        
        if not results:
            raise ValueError("No models could be trained successfully")
        
        # Find best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        self.best_model = results[best_model_name]['model']
        
        print(f"\nBest model: {best_model_name} with accuracy: {results[best_model_name]['accuracy']:.4f}")
        
        return results
    
    def save_model(self, filename='phishing_detection_model.pkl'):
        """Save the trained model"""
        model_data = {
            'model': self.best_model,
            'vectorizer': self.vectorizer,
            'preprocessor': self.preprocessor
        }
        joblib.dump(model_data, filename)
        print(f"Model saved to {filename}")
    
    def load_model(self, filename='phishing_detection_model.pkl'):
        """Load a trained model"""
        model_data = joblib.load(filename)
        self.best_model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.preprocessor = model_data['preprocessor']
        print(f"Model loaded from {filename}")
    
    def predict(self, subject, body, sender_email=""):
        """Predict if an email is phishing and provide detailed analysis"""
        if not self.best_model:
            raise ValueError("No model trained. Please train a model first.")
        
        # Create DataFrame for prediction
        df = pd.DataFrame({'subject': [subject], 'body': [body]})
        
        # Preprocess for ML prediction
        processed_df = self.preprocessor.prepare_dataset(df)
        text_features = processed_df['combined_text']
        
        # TF-IDF features
        try:
            tfidf_features = self.vectorizer.transform(text_features)
            tfidf_dense = tfidf_features.toarray()
        except:
            tfidf_dense = np.zeros((1, self.vectorizer.max_features or 100))
        
        # Numerical features
        numerical_cols = ['length', 'word_count', 'char_count', 'suspicious_word_count',
                         'url_count', 'email_count', 'exclamation_count', 'capital_ratio']
        numerical_features = processed_df[numerical_cols].fillna(0).values
        
        # Combine features
        combined_features = np.hstack([tfidf_dense, numerical_features])
        
        # Predict
        prediction = self.best_model.predict(combined_features)[0]
        
        # Get probability if available
        try:
            probability = self.best_model.predict_proba(combined_features)[0]
            confidence = float(max(probability))
            phishing_probability = float(probability[1] if len(probability) > 1 else 0)
        except:
            confidence = 0.8
            phishing_probability = 0.8 if prediction == 1 else 0.2
        
        # Get detailed analysis
        detailed_analysis = self.preprocessor.get_detailed_analysis(subject, body, sender_email)
        
        return {
            'is_phishing': bool(prediction),
            'confidence': confidence,
            'phishing_probability': phishing_probability,
            **detailed_analysis # Add detailed analysis results
        }

if __name__ == "__main__":
    print("Starting Email Phishing Detection Model Training...")
    
    # Initialize model
    detector = PhishingDetectionModel()
    
    # Create dataset
    df = detector.create_sample_dataset()
    print(f"Created dataset with {len(df)} samples")
    print(f"Class distribution:\n{df['label'].value_counts()}")
    
    # Prepare features
    try:
        X, y = detector.prepare_features(df)
        print(f"Feature matrix shape: {X.shape}")
        
        # Train models
        results = detector.train_models(X, y)
        
        # Save model
        detector.save_model()
        
        # Test prediction
        print("\n" + "="*50)
        print("TESTING MODEL PREDICTIONS")
        print("="*50)
        
        test_cases = [
            ("URGENT: Account Suspended!", "Your account will be suspended unless you verify immediately!", "support@bad-domain.xyz"),
            ("Meeting Reminder", "Don't forget about our meeting tomorrow at 2 PM.", "john.doe@company.com")
        ]
        
        for subject, body, sender in test_cases:
            prediction = detector.predict(subject, body, sender)
            status = "🚨 PHISHING" if prediction['is_phishing'] else "✅ SAFE"
            print(f"\nEmail: '{subject}' (From: {sender})")
            print(f"Result: {status}")
            print(f"Confidence: {prediction['confidence']:.2f}")
            print(f"Phishing Probability: {prediction['phishing_probability']:.2f}")
            print(f"Urgency Score: {prediction.get('urgency_score', 'N/A')}")
            print(f"Grammar Quality: {prediction.get('grammar_quality', 'N/A')}")
            print(f"Personal Info Requests: {prediction.get('personal_info_requests', 'N/A')}")
            print(f"Suspicious Keywords Count: {prediction.get('suspicious_keywords_count', 0)}")
            print(f"Keywords: {', '.join(prediction.get('extracted_keywords', []))}")
            print(f"URLs: {', '.join(prediction.get('extracted_urls', []))}")
            print(f"Domain Reputation: {prediction.get('domain_reputation', 'N/A')}")
            print(f"Spoofing Risk: {prediction.get('spoofing_risk', 'N/A')}")
        
        print("\n✅ Model training completed successfully!")
        print("You can now run the Flask app with: python app.py")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        print("Please check your dependencies and try again.")
