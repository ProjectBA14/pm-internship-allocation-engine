# PM Internship Allocation Engine

An AI-powered smart allocation system for matching students to internship opportunities under the PM Internship Scheme, built for Smart India Hackathon 2025.

## 🚀 Overview

This project delivers a functional prototype that automates candidate-internship matching using cutting-edge AI models, ensuring inclusivity and affirmative action while providing a modern web interface for both applicants and administrators.

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React.js with TypeScript, modern hooks and real-time updates
- **Backend**: Flask (Python) with RESTful APIs and advanced services
- **Database**: Firebase Firestore for real-time data storage
- **Web Scraping**: BeautifulSoup, Requests with intelligent fallback mechanisms
- **AI Services**: 
  - Google Gemini API for CV parsing and content generation
  - Advanced matching algorithms with success prediction
  - Company data enrichment and sentiment analysis
- **Authentication**: Firebase Auth

### Key Features
- 🤖 AI-powered CV parsing and information extraction
- 🎯 Intelligent candidate-opportunity matching with detailed success prediction
- 📊 Affirmative action and diversity prioritization
- 🌐 Modern web interface for applicants and admins
- 📈 Real-time analytics and reporting
- 🔄 Manual correction and feedback loops
- 🔍 Live web scraping from Internshala, Indeed and other job platforms
- 🏢 Company data enrichment with ratings, reviews and internship insights
- 🔗 Real application URLs for seamless application process

## 🛠️ Setup Instructions

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- Git

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create `.env` files in both backend and frontend directories:

**Backend (.env)**
```
GOOGLE_API_KEY=your_gemini_api_key
HUGGINGFACE_API_KEY=your_hf_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
```

**Frontend (.env)**
```
REACT_APP_API_BASE_URL=http://localhost:5000
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
REACT_APP_FIREBASE_PROJECT_ID=your_firebase_project_id
```

## 📁 Project Structure

```
pm-internship-allocation-engine/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── __init__.py
│   ├── services/
│   │   ├── gemini_service.py
│   │   ├── matching_service.py
│   │   └── firebase_service.py
│   ├── models/
│   ├── utils/
│   ├── config/
│   ├── requirements.txt
│   └── app.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── docs/
├── tests/
├── data/
└── README.md
```

## 🎯 Key Workflows

1. **Application Registration**: Students upload CVs, AI parses information, manual correction for missing data
2. **Internship Posting**: Admins post opportunities with detailed requirements
3. **AI Matching**: Automated scoring and ranking with diversity considerations
4. **Allocation Review**: Admin dashboard for reviewing and finalizing allocations

## 🧪 Testing

The project includes comprehensive test data based on Kaggle datasets for realistic scenarios and edge case validation.

## 🚀 Deployment

Deployment configurations are provided for both development and production environments.

## 📋 Future Enhancements

- Advanced ML model fine-tuning for Indian context
- Enhanced analytics and reporting
- Mobile app integration
- Live pilot integration

## 👥 Team

Built by college students in NCR, India for Smart India Hackathon 2025.

## 📄 License

This project is developed for Smart India Hackathon 2025.
