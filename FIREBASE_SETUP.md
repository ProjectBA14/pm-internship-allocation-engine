# 🔥 Firebase Setup Guide

## Quick Setup for Demo (5 minutes)

### 1. Create Firebase Project
1. Go to https://console.firebase.google.com/
2. Click "Create a project"
3. Name it "PM Internship Engine" 
4. Disable Google Analytics (for faster setup)
5. Click "Create project"

### 2. Setup Firestore Database
1. In your Firebase project, click "Firestore Database"
2. Click "Create database"
3. **Start in test mode** (for demo purposes)
4. Choose your location (closest to you)
5. Click "Done"

### 3. Get Service Account (Optional for full functionality)
1. Go to Project Settings (⚙️ icon)
2. Click "Service accounts" tab
3. Click "Generate new private key"
4. Download the JSON file
5. Run the setup script again with the JSON file path

### 4. Enable Authentication (Optional)
1. Click "Authentication" in sidebar
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Enable "Email/Password"

## 🚀 Test Without Full Firebase Setup

The system will work with Google Gemini and Hugging Face APIs even without Firebase. Firebase is mainly used for:
- Storing applicant profiles
- Saving match results
- Admin dashboard data

For demo purposes, the system will show mock data and still demonstrate:
- ✅ CV Upload and AI parsing
- ✅ AI-powered matching
- ✅ Affirmative action algorithms
- ✅ Admin dashboard interface

## Current Status
- ✅ Google Gemini API: Configured
- ✅ Hugging Face API: Configured  
- ⚠️ Firebase: Using mock data (works for demo)
