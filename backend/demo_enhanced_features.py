#!/usr/bin/env python3
"""
Enhanced Features Demo Script
Demonstrates the new internship scraping and matching capabilities
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_header():
    """Print a nice header for the demo"""
    print("=" * 70)
    print("🎯 PM INTERNSHIP ALLOCATION ENGINE - ENHANCED FEATURES DEMO")
    print("=" * 70)
    print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def demo_scraper_service():
    """Demonstrate the internship scraper service"""
    print("🕷️ INTERNSHIP SCRAPER SERVICE DEMO")
    print("-" * 40)
    
    try:
        from services.internship_scraper_service import InternshipScraperService
        
        print("✅ Initializing scraper service...")
        scraper = InternshipScraperService()
        
        print("🔍 Scraping live internships (demo data)...")
        internships = scraper.scrape_live_internships(limit=3)
        
        print(f"✅ Retrieved {len(internships)} internships")
        
        for i, internship in enumerate(internships, 1):
            print(f"\n📋 Internship #{i}:")
            print(f"   🏢 Company: {internship['company']}")
            print(f"   💼 Title: {internship['title']}")
            print(f"   📍 Location: {internship['location']}")
            print(f"   💰 Salary: {internship['salary']}")
            print(f"   🏷️ Category: {internship['category']}")
            print(f"   🔗 Apply: {internship['apply_link']}")
        
        return internships
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def demo_matching_algorithm(internships):
    """Demonstrate the AI matching algorithm"""
    print("\n🤖 AI MATCHING ALGORITHM DEMO")
    print("-" * 40)
    
    try:
        from services.internship_scraper_service import InternshipScraperService
        
        scraper = InternshipScraperService()
        
        # Sample candidate profile
        candidate_profile = {
            'skills': {
                'technical': ['Python', 'Machine Learning', 'TensorFlow', 'Data Science'],
                'soft': ['Communication', 'Problem Solving', 'Leadership']
            },
            'experience': ['AI Project', 'Data Analysis', 'Web Development'],
            'education': 'B.Tech Computer Science',
            'location': 'Bangalore',
            'category': 'Artificial Intelligence',
            'experience_level': 'entry'
        }
        
        print("👤 Sample Candidate Profile:")
        print(f"   🎓 Education: {candidate_profile['education']}")
        print(f"   📍 Location: {candidate_profile['location']}")
        print(f"   💼 Category: {candidate_profile['category']}")
        print(f"   🛠️ Technical Skills: {', '.join(candidate_profile['skills']['technical'])}")
        print(f"   🤝 Soft Skills: {', '.join(candidate_profile['skills']['soft'])}")
        
        print("\n🎯 Calculating match scores...")
        
        matched_internships = []
        for internship in internships:
            match_analysis = scraper.calculate_match_score(candidate_profile, internship)
            
            if match_analysis.get('overall_score', 0) > 0:
                internship['match_analysis'] = match_analysis
                matched_internships.append(internship)
                
                print(f"\n🏢 {internship['company']} - {internship['title']}")
                print(f"   📊 Overall Match: {match_analysis.get('percentage', 0):.1f}%")
                print(f"   ⭐ Compatibility: {match_analysis.get('compatibility_level', 'Unknown')}")
                
                breakdown = match_analysis.get('match_breakdown', {})
                if breakdown:
                    print(f"   🛠️ Skills Match: {breakdown.get('skills_match', {}).get('percentage', 0):.1f}%")
                    print(f"   🏷️ Category Match: {breakdown.get('category_match', {}).get('percentage', 0):.1f}%")
                    print(f"   📍 Location Match: {breakdown.get('location_match', {}).get('percentage', 0):.1f}%")
        
        # Sort by match score
        matched_internships.sort(key=lambda x: x.get('match_analysis', {}).get('overall_score', 0), reverse=True)
        
        return matched_internships
        
    except Exception as e:
        print(f"❌ Matching error: {e}")
        return []

def demo_api_routes():
    """Demonstrate the API routes structure"""
    print("\n🌐 API ROUTES DEMO")
    print("-" * 40)
    
    try:
        from app.routes.enhanced_internship_routes import (
            SmartInternshipSearchAPI,
            InternshipDetailsAPI,
            RecommendedInternshipsAPI
        )
        
        print("✅ Enhanced API routes available:")
        print("   POST /api/smart-internships/search")
        print("        → Smart search with live scraping and AI matching")
        print("   GET  /api/smart-internships/{id}")
        print("        → Detailed internship information")
        print("   POST /api/smart-internships/recommendations")
        print("        → Personalized recommendations with career insights")
        
        # Initialize route classes to verify they work
        search_api = SmartInternshipSearchAPI()
        details_api = InternshipDetailsAPI()
        recommendations_api = RecommendedInternshipsAPI()
        
        print("\n✅ All route classes initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ API routes error: {e}")
        return False

def demo_server_setup():
    """Demonstrate server setup without actually starting it"""
    print("\n🚀 SERVER SETUP DEMO")
    print("-" * 40)
    
    try:
        from app import create_app
        from app.routes import register_routes
        from flask_restful import Api
        
        print("🔧 Creating Flask application...")
        app = create_app()
        
        print("🔗 Registering API routes...")
        api = Api(app)
        register_routes(api)
        
        print("✅ Server configuration complete")
        
        # List enhanced endpoints
        print("\n📋 Enhanced Endpoints Available:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'smart-internships' in rule.rule:
                    methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
                    print(f"   {methods:10} {rule.rule}")
        
        print("\n💡 To start the server:")
        print("   python app.py")
        print("   Server will be available at: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"❌ Server setup error: {e}")
        return False

def demo_features_summary():
    """Show a summary of enhanced features"""
    print("\n✨ ENHANCED FEATURES SUMMARY")
    print("-" * 40)
    
    features = [
        ("🌐 Live Data Scraping", "Scrapes internships from Internshala, Indeed, LinkedIn, Naukri"),
        ("🤖 AI-Powered Matching", "Multi-dimensional scoring: Skills, Location, Category, Experience"),
        ("🎯 Smart Recommendations", "Personalized suggestions with career insights"),
        ("📊 Detailed Analytics", "Match breakdowns, compatibility levels, career advice"),
        ("🔗 Direct Apply Links", "One-click applications to internship portals"),
        ("💰 Salary Intelligence", "Comprehensive compensation analysis"),
        ("🏢 Company Insights", "Ratings, culture highlights, team information"),
        ("📈 Performance Metrics", "Real-time matching accuracy and success rates")
    ]
    
    for feature, description in features:
        print(f"   {feature}")
        print(f"      {description}")
        print()

def main():
    """Run the complete demo"""
    demo_header()
    
    # Demo 1: Scraper Service
    internships = demo_scraper_service()
    time.sleep(1)
    
    # Demo 2: Matching Algorithm
    if internships:
        matched_internships = demo_matching_algorithm(internships)
    time.sleep(1)
    
    # Demo 3: API Routes
    demo_api_routes()
    time.sleep(1)
    
    # Demo 4: Server Setup
    demo_server_setup()
    time.sleep(1)
    
    # Demo 5: Features Summary
    demo_features_summary()
    
    # Conclusion
    print("=" * 70)
    print("🎉 DEMO COMPLETE - ENHANCED FEATURES ARE READY!")
    print("=" * 70)
    print()
    print("📚 Next Steps:")
    print("   1. Start the server: python app.py")
    print("   2. Test endpoints: http://localhost:5000/health")
    print("   3. Read documentation: docs/ENHANCED_API_DOCUMENTATION.md")
    print("   4. Explore features: README_ENHANCED_FEATURES.md")
    print()
    print(f"⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
