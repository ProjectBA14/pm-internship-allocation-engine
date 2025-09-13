#!/usr/bin/env python3
"""
CV Parsing Demo Script
Demonstrates the AI-powered CV parsing functionality using Google Gemini
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_cv_parsing():
    """Demonstrate CV parsing with sample CV text"""
    try:
        from services.gemini_service import GeminiService
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv("backend/.env")
        
        print("🤖 PM Internship Allocation Engine - CV Parsing Demo")
        print("=" * 60)
        print("Testing AI-powered CV parsing with Google Gemini...")
        print()
        
        # Sample CV text for testing
        sample_cv = """
        John Doe
        Email: john.doe@example.com
        Phone: +91-9876543210
        Location: Bangalore, Karnataka, India
        
        EDUCATION:
        Bachelor of Technology in Computer Science
        Indian Institute of Technology, Delhi
        Graduation Year: 2024
        CGPA: 8.5/10
        
        EXPERIENCE:
        Software Development Intern
        Tech Solutions Pvt Ltd
        Duration: June 2023 - August 2023
        - Developed web applications using React.js and Node.js
        - Collaborated with senior developers on API development
        - Implemented responsive UI components
        
        TECHNICAL SKILLS:
        Programming Languages: Python, JavaScript, Java, C++
        Web Technologies: React.js, Node.js, HTML, CSS
        Databases: MySQL, MongoDB
        Tools: Git, Docker, VS Code
        
        PROJECTS:
        E-commerce Website
        - Built full-stack web application with React and Node.js
        - Implemented user authentication and payment integration
        - Technologies: React.js, Express.js, MongoDB
        
        Machine Learning Classifier
        - Developed image classification model using Python
        - Achieved 92% accuracy on test dataset
        - Technologies: Python, TensorFlow, scikit-learn
        
        CERTIFICATIONS:
        - AWS Cloud Practitioner
        - Google Analytics Certified
        
        ACHIEVEMENTS:
        - Winner of college coding competition 2023
        - Published research paper on machine learning
        - Active member of Computer Science Society
        """
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        print("📄 Sample CV Text:")
        print("-" * 40)
        print(sample_cv.strip()[:300] + "...")
        print()
        
        print("🔍 Parsing CV with Google Gemini AI...")
        print("This may take a few seconds...")
        print()
        
        # Parse the CV
        parsed_data = gemini_service.parse_cv(sample_cv)
        
        print("✅ CV Parsing Completed!")
        print("=" * 40)
        print()
        
        # Display parsed results
        print("📊 Extracted Information:")
        print(f"Name: {parsed_data.get('name', 'Not found')}")
        print(f"Email: {parsed_data.get('email', 'Not found')}")
        print(f"Phone: {parsed_data.get('phone', 'Not found')}")
        print(f"Location: {parsed_data.get('location', 'Not found')}")
        print(f"Category: {parsed_data.get('category', 'Not determined')}")
        print(f"Experience Level: {parsed_data.get('experience_level', 'Not determined')}")
        print(f"Rural Background: {parsed_data.get('rural_background', False)}")
        print()
        
        # Education
        education = parsed_data.get('education', [])
        if education:
            print("🎓 Education:")
            for edu in education[:2]:  # Show first 2
                print(f"  - {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})")
        print()
        
        # Skills
        skills = parsed_data.get('skills', {})
        if skills:
            print("💡 Skills:")
            for skill_type, skill_list in skills.items():
                if skill_list:
                    print(f"  {skill_type.title()}: {', '.join(skill_list[:5])}")  # Show first 5
        print()
        
        # Key strengths
        strengths = parsed_data.get('key_strengths', [])
        if strengths:
            print("⭐ Key Strengths:")
            for strength in strengths:
                print(f"  - {strength}")
        print()
        
        # Confidence score
        confidence = parsed_data.get('confidence_score', 0)
        print(f"📈 Parsing Confidence: {confidence:.2%}")
        
        if confidence > 0.7:
            print("🎉 High confidence parsing - Ready for matching!")
        elif confidence > 0.5:
            print("⚠️  Moderate confidence - Some manual review may be needed")
        else:
            print("🔧 Low confidence - Manual correction recommended")
        
        print()
        print("🚀 Next Steps:")
        print("1. Start the backend server: python backend/app.py")
        print("2. Visit the frontend: http://localhost:3000")
        print("3. Try uploading a real CV at: http://localhost:3000/cv-upload")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in CV parsing demo: {str(e)}")
        print("\nTroubleshooting:")
        print("- Check if Google Gemini API key is set correctly")
        print("- Verify internet connection")
        print("- Run: python test_apis.py")
        return False

def main():
    success = test_cv_parsing()
    if success:
        print("\n✅ CV Parsing Demo Completed Successfully!")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
