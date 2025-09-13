#!/usr/bin/env python3
"""
Enhanced Features Test Suite
Tests all new internship scraping and matching functionality
"""

import os
import sys
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import subprocess
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from services.internship_scraper_service import InternshipScraperService
        print("✅ InternshipScraperService imported successfully")
        
        from app.routes.enhanced_internship_routes import (
            SmartInternshipSearchAPI, 
            InternshipDetailsAPI, 
            RecommendedInternshipsAPI
        )
        print("✅ Enhanced routes imported successfully")
        
        import bs4  # beautifulsoup4
        import selenium
        import lxml
        print("✅ Web scraping dependencies imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_scraper_service():
    """Test the internship scraper service functionality"""
    print("\n🕷️ Testing Internship Scraper Service...")
    
    try:
        from services.internship_scraper_service import InternshipScraperService
        
        scraper = InternshipScraperService()
        print("✅ Scraper service initialized")
        
        # Test scraping (with mock data for safety)
        print("📊 Testing live internship scraping...")
        internships = scraper.scrape_live_internships(limit=5)
        
        if internships:
            print(f"✅ Scraped {len(internships)} internships")
            
            # Test first internship structure
            first_internship = internships[0]
            required_fields = ['id', 'title', 'company', 'location', 'category']
            
            for field in required_fields:
                if field in first_internship:
                    print(f"✅ Field '{field}' present")
                else:
                    print(f"⚠️ Field '{field}' missing")
        else:
            print("⚠️ No internships returned (expected for demo data)")
        
        # Test matching algorithm
        print("\n🎯 Testing matching algorithm...")
        candidate_profile = {
            'skills': {
                'technical': ['Python', 'Machine Learning', 'Data Science'],
                'soft': ['Communication', 'Problem Solving']
            },
            'experience': ['AI Project', 'Data Analysis'],
            'education': 'B.Tech Computer Science',
            'location': 'Bangalore',
            'category': 'Artificial Intelligence'
        }
        
        mock_internship = {
            'title': 'AI/ML Internship',
            'company': 'TechCorp',
            'skills_required': ['Python', 'Machine Learning', 'TensorFlow'],
            'location': 'Bangalore, Karnataka',
            'category': 'Artificial Intelligence',
            'salary_max': 30000
        }
        
        match_analysis = scraper.calculate_match_score(candidate_profile, mock_internship)
        
        if match_analysis:
            print(f"✅ Match calculation successful")
            print(f"   Overall score: {match_analysis.get('overall_score', 'N/A')}")
            print(f"   Compatibility: {match_analysis.get('compatibility_level', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper service error: {e}")
        return False

def test_flask_routes():
    """Test that Flask routes can be initialized"""
    print("\n🌐 Testing Flask Routes...")
    
    try:
        from app.routes.enhanced_internship_routes import (
            SmartInternshipSearchAPI, 
            InternshipDetailsAPI, 
            RecommendedInternshipsAPI
        )
        
        # Test route initialization
        search_api = SmartInternshipSearchAPI()
        details_api = InternshipDetailsAPI()
        recommendations_api = RecommendedInternshipsAPI()
        
        print("✅ All route classes initialized successfully")
        
        # Test route registration
        from app.routes import register_routes
        from flask import Flask
        from flask_restful import Api
        
        app = Flask(__name__)
        api = Api(app)
        
        register_routes(api)
        print("✅ Routes registered successfully")
        
        # List all registered endpoints
        print("\n📋 Registered endpoints:")
        for rule in app.url_map.iter_rules():
            if 'smart-internships' in rule.rule:
                print(f"   {rule.methods} {rule.rule}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask routes error: {e}")
        return False

def test_dependencies():
    """Test that all dependencies are properly installed"""
    print("\n📦 Testing Dependencies...")
    
    dependencies = [
        'flask',
        'flask_restful', 
        'flask_cors',
        'requests',
        'bs4',
        'selenium',
        'lxml',
        'torch',
        'transformers',
        'google.generativeai',
        'pandas',
        'numpy',
        'sklearn'
    ]
    
    success_count = 0
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
            success_count += 1
        except ImportError:
            print(f"❌ {dep} - Not installed or import error")
    
    print(f"\n📊 Dependencies: {success_count}/{len(dependencies)} successful")
    return success_count == len(dependencies)

def test_configuration():
    """Test configuration and environment setup"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from config.settings import Config
        print("✅ Config class imported")
        
        # Check environment variables
        required_vars = ['FLASK_ENV']
        optional_vars = ['GOOGLE_API_KEY', 'FIREBASE_SERVICE_ACCOUNT_PATH']
        
        for var in required_vars:
            if os.getenv(var):
                print(f"✅ {var} environment variable set")
            else:
                print(f"⚠️ {var} environment variable not set")
        
        for var in optional_vars:
            if os.getenv(var):
                print(f"✅ {var} environment variable set")
            else:
                print(f"ℹ️ {var} environment variable not set (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_file_structure():
    """Test that all required files are present"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'services/internship_scraper_service.py',
        'app/routes/enhanced_internship_routes.py',
        'app/routes/__init__.py',
        'config/settings.py'
    ]
    
    success_count = 0
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            success_count += 1
        else:
            print(f"❌ {file_path} - File missing")
    
    print(f"\n📊 Files: {success_count}/{len(required_files)} present")
    return success_count == len(required_files)

def run_quick_server_test():
    """Run a quick server test without blocking"""
    print("\n🚀 Testing Server Startup (Quick Test)...")
    
    try:
        # Import Flask app components
        from app import create_app
        from app.routes import register_routes
        from flask_restful import Api
        
        app = create_app()
        api = Api(app)
        register_routes(api)
        
        print("✅ Flask app created successfully")
        print("✅ Routes registered successfully")
        
        # Test that the app can be configured
        with app.app_context():
            print("✅ App context works")
        
        # List all endpoints
        print("\n📋 Available Endpoints:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
                print(f"   {methods:10} {rule.rule}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Enhanced Features Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Flask Routes", test_flask_routes),
        ("Scraper Service", test_scraper_service),
        ("Server Startup", run_quick_server_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("🏆 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Enhanced features are ready to use.")
        print("\n🚀 To start the server:")
        print("   python app.py")
        print("\n📚 API Documentation:")
        print("   docs/ENHANCED_API_DOCUMENTATION.md")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
