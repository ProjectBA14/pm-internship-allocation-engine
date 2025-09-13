#!/usr/bin/env python3
"""
API Keys Configuration Helper
This script helps you securely configure API keys for the PM Internship Allocation Engine
"""

import os
import json
from pathlib import Path

def main():
    print("🔑 PM Internship Allocation Engine - API Keys Setup")
    print("=" * 60)
    
    backend_env_path = Path("backend/.env")
    frontend_env_path = Path("frontend/.env")
    
    # Collect API keys
    print("\n1. Google Gemini API Key:")
    print("   Get from: https://aistudio.google.com/")
    gemini_key = input("   Enter your Gemini API key: ").strip()
    
    print("\n2. Hugging Face API Token:")
    print("   Get from: https://huggingface.co/settings/tokens")
    hf_key = input("   Enter your Hugging Face token: ").strip()
    
    print("\n3. Firebase Configuration:")
    print("   Download service account JSON from Firebase Console")
    firebase_json_path = input("   Enter path to Firebase service account JSON file: ").strip()
    
    # Load Firebase config
    firebase_config = {}
    if firebase_json_path and os.path.exists(firebase_json_path):
        with open(firebase_json_path, 'r') as f:
            firebase_config = json.load(f)
    else:
        print("   ⚠️  Firebase JSON file not found. Using placeholder values.")
        firebase_config = {
            "project_id": "pm-internship-dev",
            "private_key_id": "placeholder",
            "private_key": "-----BEGIN PRIVATE KEY-----\nplaceholder\n-----END PRIVATE KEY-----\n",
            "client_email": "placeholder@pm-internship-dev.iam.gserviceaccount.com",
            "client_id": "placeholder",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/placeholder"
        }
    
    # Update backend .env
    backend_env_content = f"""# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-for-testing-only
PORT=5000

# Google AI Configuration
GOOGLE_API_KEY={gemini_key}

# Hugging Face Configuration
HUGGINGFACE_API_KEY={hf_key}

# Firebase Configuration
FIREBASE_PROJECT_ID={firebase_config.get('project_id', 'pm-internship-dev')}
FIREBASE_PRIVATE_KEY_ID={firebase_config.get('private_key_id', 'placeholder')}
FIREBASE_PRIVATE_KEY="{firebase_config.get('private_key', '').replace(chr(10), chr(92) + 'n')}"
FIREBASE_CLIENT_EMAIL={firebase_config.get('client_email', 'placeholder@pm-internship-dev.iam.gserviceaccount.com')}
FIREBASE_CLIENT_ID={firebase_config.get('client_id', 'placeholder')}
FIREBASE_CLIENT_X509_CERT_URL={firebase_config.get('client_x509_cert_url', 'https://www.googleapis.com/robot/v1/metadata/x509/placeholder')}
"""
    
    # Update frontend .env
    frontend_env_content = f"""# API Configuration
REACT_APP_API_BASE_URL=http://localhost:5000

# Firebase Configuration (for frontend)
REACT_APP_FIREBASE_API_KEY={firebase_config.get('api_key', 'development_key')}
REACT_APP_FIREBASE_AUTH_DOMAIN={firebase_config.get('project_id', 'pm-internship-dev')}.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID={firebase_config.get('project_id', 'pm-internship-dev')}
REACT_APP_FIREBASE_STORAGE_BUCKET={firebase_config.get('project_id', 'pm-internship-dev')}.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID={firebase_config.get('messaging_sender_id', '123456789')}
REACT_APP_FIREBASE_APP_ID={firebase_config.get('app_id', '1:123456789:web:abcdef123456')}
"""
    
    # Write the files
    try:
        with open(backend_env_path, 'w') as f:
            f.write(backend_env_content)
        print(f"✅ Backend .env updated: {backend_env_path}")
        
        with open(frontend_env_path, 'w') as f:
            f.write(frontend_env_content)
        print(f"✅ Frontend .env updated: {frontend_env_path}")
        
        print("\n🎉 Configuration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your backend server: python backend/app.py")
        print("   2. Restart your frontend server: npm start (in frontend directory)")
        print("   3. Test CV upload at: http://localhost:3000/cv-upload")
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")

if __name__ == "__main__":
    main()
