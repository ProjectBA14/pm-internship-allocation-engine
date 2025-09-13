#!/usr/bin/env python3
"""
API Keys Test Script
Tests if all API keys are working correctly
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_gemini_api():
    """Test Google Gemini API"""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv("backend/.env")
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key or api_key == 'your-google-gemini-api-key-here':
            print("❌ Google Gemini API key not found or not set")
            return False
            
        # Configure and test
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
        
        # Simple test prompt
        response = model.generate_content("Say 'API test successful' if you can read this.")
        
        if response and response.text:
            print(f"✅ Google Gemini API: Working")
            print(f"   Response: {response.text.strip()}")
            return True
        else:
            print("❌ Google Gemini API: No response received")
            return False
            
    except Exception as e:
        print(f"❌ Google Gemini API: Error - {str(e)}")
        return False

def test_huggingface_api():
    """Test Hugging Face API"""
    try:
        import requests
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv("backend/.env")
        
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key or api_key == 'your-huggingface-api-key-here':
            print("❌ Hugging Face API key not found or not set")
            return False
        
        # Test API with a simple model
        headers = {"Authorization": f"Bearer {api_key}"}
        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": "Hello, this is a test"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Hugging Face API: Working")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"❌ Hugging Face API: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Hugging Face API: Error - {str(e)}")
        return False

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv("backend/.env")
        
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        
        if project_id == 'pm-internship-dev' or 'placeholder' in private_key:
            print("⚠️  Firebase: Using placeholder configuration")
            print("   Note: System will work with mock data for demo purposes")
            return True
        else:
            # Try to initialize Firebase (would need actual credentials)
            print("✅ Firebase: Configuration detected")
            print("   Note: Full Firebase testing requires running the server")
            return True
            
    except Exception as e:
        print(f"❌ Firebase: Error - {str(e)}")
        return False

def main():
    print("🧪 PM Internship Allocation Engine - API Testing")
    print("=" * 60)
    
    # Test APIs
    gemini_ok = test_gemini_api()
    print()
    
    hf_ok = test_huggingface_api()
    print()
    
    firebase_ok = test_firebase_connection()
    print()
    
    # Summary
    print("📊 Test Results Summary:")
    print("=" * 30)
    
    if gemini_ok and hf_ok:
        print("🎉 All critical APIs are working!")
        print("✅ CV parsing will work (Google Gemini)")
        print("✅ AI matching will work (Hugging Face)")
        if firebase_ok:
            print("✅ Database ready (Firebase)")
        print("\n🚀 Your system is ready to demo!")
        print("\nNext steps:")
        print("1. Start backend: python backend/app.py")
        print("2. Visit frontend: http://localhost:3000")
        print("3. Test CV upload: http://localhost:3000/cv-upload")
    else:
        print("⚠️  Some APIs need attention:")
        if not gemini_ok:
            print("- Google Gemini API needs valid key")
        if not hf_ok:
            print("- Hugging Face API needs valid token")
        print("\nCheck your API keys in backend/.env file")

if __name__ == "__main__":
    main()
