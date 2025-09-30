# 🏛️ LLM-Powered Polling App Prototype

An LLM-powered polling app prototype that generates contextual polling topics and enables democratic participation in local governance.

## ✨ Features

- **🤖 AI-Powered Topic Generation**: Uses OpenAI GPT to create relevant polling topics based on community context
- **📚 Research-Based Domains**: Community-specific topic categories based on 2024-2025 US research data
- **🏘️ Multi-Community Support**: Tailored domains for Urban, Suburban, Rural, and University Town contexts
- **📊 Interactive Polling Interface**: Simplified 3-option voting (Agree, Disagree, Skip)
- **🎯 Community-Specific Context**: Generate topics tailored to specific locations, populations, and current issues
- **📱 Mobile-First Design**: Fully responsive design that works on all devices
- **🔍 Clustering Analysis**: Advanced opinion alignment analysis and visualization
- **🔄 Real-time Results**: See voting patterns and opinion clusters as they develop
- **📈 User Activity Tracking**: Comprehensive analytics to monitor engagement and usage patterns
- **🔗 Poll Sharing**: Create shareable links for polls with unique URLs and social sharing capabilities

## 📚 Research Foundation

This application is built upon comprehensive research analyzing community priorities across different geographic and demographic contexts in the United States (2024-2025). 

**Research Documentation**: See [RESEARCH_DATA_SOURCE.md](./RESEARCH_DATA_SOURCE.md) for detailed information about our data sources and methodology.

**Research Access**: [Complete Research Findings](https://claude.ai/share/e5976a97-8f11-49aa-92c7-b6c7b22e5c9b)

## 🏘️ Community Types & Topic Domains

Based on comprehensive 2024-2025 US community research, each community type has specific topic domains that reflect their unique challenges and priorities:

### 🏙️ Urban Community
*Dense, diverse areas with complex governance needs*

| Domain | Focus Area | Example Topics |
|--------|------------|----------------|
| **🚔 Crime and Public Safety** | Balancing safety with civil liberties | Police accountability, community programs, surveillance policies |
| **🏠 Housing Affordability** | Addressing cost and displacement | Affordable housing mandates, rent control, anti-displacement policies |
| **💼 Economic Development** | Supporting local economy | Small business loans, living wages, local hiring requirements |
| **🏗️ Infrastructure & City Services** | Essential services and maintenance | Public transit expansion, utility upgrades, smart city technology |
| **🚌 Transportation** | Multi-modal transportation equity | Transit funding, bike lanes, parking policies, accessibility |

### 🏘️ Suburban Town  
*Residential communities balancing growth with character*

| Domain | Focus Area | Example Topics |
|--------|------------|----------------|
| **🚸 Traffic Congestion & School Safety** | Managing traffic around schools | Speed limits, crossing guards, car-free zones during school hours |
| **🔧 Infrastructure Maintenance** | Preserving community assets | Road repair priorities, utility maintenance, public facilities |
| **🎓 School Quality & Segregation** | Educational equity and excellence | School funding, district boundaries, program accessibility |
| **💰 Property Taxes** | Balancing revenue and affordability | Tax caps, senior exemptions, assessment fairness |
| **🌱 Environmental Concerns** | Sustainability and conservation | Green infrastructure, development impact, conservation programs |

### 🌾 Rural Area
*Remote communities with unique infrastructure and economic challenges*

| Domain | Focus Area | Example Topics |
|--------|------------|----------------|
| **📶 Digital Infrastructure Gap** | Bridging connectivity divide | Broadband as utility, federal funding, community cooperatives |
| **🏥 Healthcare Access** | Essential service availability | Telemedicine, clinic funding, emergency response |
| **📈 Economic Opportunities** | Supporting local economy | Agricultural support, small business development, job training |
| **👴 Aging Population Services** | Senior care and support | Transportation services, healthcare access, community centers |
| **🛤️ Infrastructure Decay** | Maintaining basic services | Road maintenance, utilities, public safety facilities |

### 🎓 University Town
*Communities shaped by academic institutions*

| Domain | Focus Area | Example Topics |
|--------|------------|----------------|
| **🏠 Student Housing Shortage** | Managing housing demand | On-campus requirements, zoning restrictions, rent stabilization |
| **🤝 Town-Gown Relations** | University-community balance | Taxation of endowments, community benefit agreements |
| **🅿️ Parking and Transportation** | Managing campus-related traffic | Transit solutions, parking policies, bike infrastructure |
| **🔊 Noise and Disruption** | Quality of life balance | Party regulations, occupancy limits, noise ordinances |
| **🎓 Economic Dependence on University** | Diversifying local economy | Business development, tourism, alternative employers |

### 🎲 Auto-Select ("Surprise me!")
*Available for all community types - randomly selects an appropriate domain based on community context and research data.*

> **Note**: Each domain includes 8-12 carefully crafted statements representing diverse viewpoints, designed to reveal natural opinion clusters within your community. Topics are customized for your specific location and population size.

## 🏗️ Architecture

```
Frontend (Next.js + React + TypeScript)
├── Topic Generator Interface
├── Interactive Polling Interface
└── Results & Analytics

Backend (FastAPI + Python)
├── LLM Integration (OpenAI)
├── Topic Generation Endpoint
└── Data Models & Validation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- OpenAI API Key

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd llm-powered-polling-app-prototype
```

### 2. Install Dependencies

```bash
# Frontend dependencies
npm install

# Backend dependencies
npm run install-backend
# or manually:
cd backend && pip install -r requirements.txt
```

### 3. Environment Setup

```bash
# Create backend environment file
cp backend/.env.example backend/.env

# Add your OpenAI API key to backend/.env
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the Application

```bash
# Terminal 1: Start the backend server
npm run backend

# Terminal 2: Start the frontend development server
npm run dev
```

Visit [https://llm-powered-polling-app-prototype.replit.app](https://llm-powered-polling-app-prototype.replit.app) to see the app!

## 📖 Usage

### 1. Generate a Topic
- Enter your community details (location, population, current issues)
- Click "Generate Community Topic"
- The AI will create a relevant polling topic with statements and expected opinion clusters

### 2. Launch the Poll
- Click "Launch Community Poll" to start voting
- Enter your name (optional)
- Vote on each statement using the 5-point scale

### 3. Complete & Analyze
- View your voting summary
- Generate new topics or retake the poll

## 🛠️ Development

### Project Structure

```
llm-powered-polling-app-prototype/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Home page
│   ├── layout.tsx         # Root layout
│   ├── globals.css        # Global styles
│   └── poll/              # Polling interface
├── components/            # React components
│   └── CommunityTopicGenerator.tsx
├── backend/              # FastAPI backend
│   ├── main.py          # Main API server
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment template
└── public/              # Static assets
```

### API Endpoints

- `POST /generate-topic` - Generate a polling topic
- `GET /health` - Health check
- `GET /` - API info

### Tech Stack

**Frontend:**
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS for styling
- Lucide React for icons

**Backend:**
- FastAPI for API server
- Pydantic for data validation
- OpenAI for LLM integration
- Uvicorn for ASGI server

## 🎯 Features in Detail

### Topic Generation
- Context-aware topic creation based on community details
- Diverse statement generation representing multiple viewpoints
- Automatic opinion cluster prediction
- Fallback to mock data when LLM is unavailable

### Polling Interface
- Progressive question flow with visual progress tracking
- 5-point Likert scale with emoji feedback
- Statement categorization and clustering
- Navigation between questions
- Auto-advance after voting

### Results & Analytics
- Individual response summary
- Vote pattern visualization
- Opinion cluster analysis
- Export and sharing capabilities (planned)

## 🔧 Configuration

### Environment Variables

```bash
# Backend (.env)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Alternative LLM providers
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Customization

The app is designed to be easily customizable:

- **Community Types**: Modify the `communityTypes` array in the topic generator
- **Vote Options**: Adjust the `voteOptions` in the poll interface
- **LLM Prompts**: Edit the prompt in `backend/main.py` for different topic styles
- **UI Themes**: Customize colors and styling in `tailwind.config.js`

## 🧪 Testing

```bash
# Run frontend tests
npm run test

# Run backend tests
cd backend && pytest

# Run linting
npm run lint
```

## 🚢 Deployment

### Frontend (Vercel)
```bash
npm run build
# Deploy to Vercel, Netlify, or any static host
```

### Backend (Railway, Heroku, etc.)
```bash
# The backend is ready for container deployment
# Make sure to set environment variables in your deployment platform
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- The civic tech community for inspiration
- All contributors and testers

---

**Built with ❤️ for democratic participation and community engagement** 

## 🔗 Poll Sharing & Analytics

### 📊 User Activity Tracking
- **Google Tag Manager Integration**: Comprehensive tracking with GTM for flexible analytics management
- **Backend Activity Logging**: Comprehensive server-side tracking of API usage and user behavior
- **Event Tracking**: Monitor topic generation, poll launches, votes, and sharing activities
- **Performance Analytics**: Track generation methods (LLM vs demo), success rates, and error patterns

### 🔗 Poll Sharing System
- **Unique Poll URLs**: Each generated poll can be saved with a unique shareable URL
- **Database Storage**: SQLite-based storage for persistent poll data and all participant responses
- **Easy Sharing**: One-click sharing with copy-to-clipboard functionality
- **Shared Poll Interface**: Dedicated page for participants to access shared polls
- **Creator Attribution**: Optional creator names displayed on shared polls
- **Response Collection**: All participant votes automatically saved to database
- **Aggregated Results**: Community-wide analysis with individual and collective insights
- **Real-time Updates**: Results reflect all participants' responses as they vote

### 🎯 How to Share a Poll
1. **Generate a Poll** using the main interface
2. Click **"Share This Poll"** button after generation
3. **Copy the generated link** and share with your community
4. **Participants access** the poll via the shared URL
5. **All responses automatically collected** in database
6. **View aggregated results** showing community-wide data plus individual analysis

### 📈 Analytics Dashboard
The app tracks:
- **Topic Generation Requests**: Location, domain, population size
- **Generation Methods**: LLM success vs demo fallback usage
- **Poll Engagement**: Launch rates, completion rates, vote patterns
- **Sharing Activity**: Poll saves, link copies, shared poll access
- **Error Tracking**: Failed generations, API issues, user-reported problems 
