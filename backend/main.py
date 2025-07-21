from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime
import os
import sqlite3
import uuid
from contextlib import contextmanager
from openai import OpenAI

app = FastAPI(title="Community Polling Topic Generator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Activity tracking
import json
from datetime import datetime
import os

def log_user_activity(activity_type: str, details: Dict[str, Any], request_ip: str = "unknown"):
    """Log user activity for analytics"""
    activity = {
        "timestamp": datetime.now().isoformat(),
        "activity_type": activity_type,
        "details": details,
        "request_ip": request_ip
    }
    
    # Log to console (will be captured by deployment platforms)
    logger.info(f"USER_ACTIVITY: {json.dumps(activity)}")
    
    # Optionally write to file for local development
    if os.getenv("ENVIRONMENT") != "production":
        try:
            with open("user_activity.log", "a") as f:
                f.write(f"{json.dumps(activity)}\n")
        except Exception as e:
            logger.warning(f"Failed to write activity log: {e}")

# OpenAI setup - set your API key as environment variable
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

# Database setup for poll sharing - use persistent volume in production
if os.getenv("RAILWAY_ENVIRONMENT"):
    # In Railway, use persistent volume
    DATABASE_PATH = "/data/polls.db"
    # Ensure data directory exists
    os.makedirs("/data", exist_ok=True)
else:
    # Local development
    DATABASE_PATH = os.getenv("DATABASE_PATH", "polls.db")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database with required tables"""
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    logger.info(f"Database absolute path: {os.path.abspath(DATABASE_PATH)}")
    logger.info(f"Directory exists: {os.path.exists(os.path.dirname(DATABASE_PATH))}")
    logger.info(f"Directory writable: {os.access(os.path.dirname(DATABASE_PATH), os.W_OK)}")
    
    try:
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shared_polls (
                    poll_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    main_theme TEXT NOT NULL,
                    statements TEXT NOT NULL,
                    expected_clusters TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    creator_name TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS poll_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    poll_id TEXT NOT NULL,
                    participant_name TEXT,
                    statement_index INTEGER NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    participant_session_id TEXT,
                    FOREIGN KEY (poll_id) REFERENCES shared_polls (poll_id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
            
            # Check if database file exists after creation
            if os.path.exists(DATABASE_PATH):
                file_size = os.path.getsize(DATABASE_PATH)
                logger.info(f"Database file created: {DATABASE_PATH} (size: {file_size} bytes)")
            else:
                logger.error(f"Database file not found after creation: {DATABASE_PATH}")
                
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

# Initialize database on startup
init_database()

class CommunityContext(BaseModel):
    location: str
    demographics: Optional[Dict[str, Any]] = None
    population_size: Optional[int] = None
    current_issues: Optional[List[str]] = None
    previous_topics: Optional[List[str]] = None

class Statement(BaseModel):
    text: str
    category: str
    expected_cluster: str

class GeneratedTopic(BaseModel):
    title: str
    description: str
    main_theme: str
    statements: List[Statement]
    expected_clusters: List[Dict[str, str]]
    metadata: Dict[str, Any]

class TopicRequest(BaseModel):
    community_context: CommunityContext
    topic_domain: Optional[str] = None
    statement_count: int = 10
    language: str = "en"

# Legacy support for old API format
class GenerateTopicRequest(BaseModel):
    community_context: CommunityContext

# Poll sharing models
class SharedPoll(BaseModel):
    poll_id: str
    title: str
    description: str
    main_theme: str
    statements: List[Statement]
    expected_clusters: List[Dict[str, str]]
    metadata: Dict[str, Any]
    created_at: str
    creator_name: Optional[str] = None

class SavePollRequest(BaseModel):
    topic: GeneratedTopic
    creator_name: Optional[str] = None

class PollResponse(BaseModel):
    poll_id: str
    participant_name: Optional[str] = None
    statement_index: int
    response: str  # 'agree', 'disagree', 'skip'
    timestamp: str

class SubmitPollResponseRequest(BaseModel):
    poll_id: str
    participant_name: Optional[str] = None
    responses: List[Dict[str, Any]]  # List of {statementIndex, response}

class PollResultsResponse(BaseModel):
    poll: SharedPoll
    total_participants: int
    response_summary: Dict[str, Any]  # Aggregated response data
    cluster_analysis: List[Dict[str, Any]]

class DemoTopicGenerator:
    def __init__(self):
        # Demo topics for different domains
        self.demo_topics = {
            # Urban Community Domains (based on 2024 US community research)
            "crime-public-safety": {
                "title": "Public Safety and Crime Prevention",
                "description": "Balancing community safety with civil liberties and police accountability",
                "main_theme": "How should communities approach public safety and crime prevention?",
                "statements": [
                    {"text": "Increase police patrols in high-crime neighborhoods", "category": "enforcement", "expected_cluster": "Law & Order"},
                    {"text": "Invest in community programs to address root causes of crime", "category": "prevention", "expected_cluster": "Prevention Focus"},
                    {"text": "Install more security cameras in public spaces", "category": "surveillance", "expected_cluster": "Security First"},
                    {"text": "Expand mental health crisis response teams", "category": "health-response", "expected_cluster": "Health Approach"},
                    {"text": "Create neighborhood watch programs", "category": "community-engagement", "expected_cluster": "Community Involvement"},
                    {"text": "Improve street lighting in all neighborhoods", "category": "infrastructure", "expected_cluster": "Environmental Design"},
                    {"text": "Implement police body cameras and civilian oversight", "category": "accountability", "expected_cluster": "Reform Focus"},
                    {"text": "Ban certain types of weapons in city limits", "category": "weapons-policy", "expected_cluster": "Gun Control"},
                    {"text": "Focus on drug rehabilitation over incarceration", "category": "drug-policy", "expected_cluster": "Treatment First"},
                    {"text": "Increase penalties for repeat offenders", "category": "sentencing", "expected_cluster": "Tough on Crime"}
                ]
            },
            "housing-affordability": {
                "title": "Housing Affordability Crisis",
                "description": "Addressing the growing gap between incomes and housing costs",
                "main_theme": "How should communities tackle the housing affordability crisis?",
                "statements": [
                    {"text": "Require 20% affordable units in all new developments", "category": "inclusion", "expected_cluster": "Housing Justice"},
                    {"text": "Limit rent increases to inflation rate plus 2%", "category": "rent-control", "expected_cluster": "Tenant Protection"},
                    {"text": "Offer tax incentives for developers building affordable housing", "category": "incentives", "expected_cluster": "Market Solutions"},
                    {"text": "Prevent displacement by giving existing residents first right to purchase", "category": "anti-displacement", "expected_cluster": "Community Stability"},
                    {"text": "Allow higher density development near transit", "category": "zoning", "expected_cluster": "Smart Growth"},
                    {"text": "Create community land trusts to maintain affordability", "category": "land-trust", "expected_cluster": "Community Ownership"},
                    {"text": "Invest in existing neighborhoods without displacement", "category": "equitable-development", "expected_cluster": "Inclusive Development"},
                    {"text": "Provide down payment assistance for first-time homebuyers", "category": "homeownership", "expected_cluster": "Ownership Support"},
                    {"text": "Rehabilitate existing housing stock before building new", "category": "preservation", "expected_cluster": "Conservation First"},
                    {"text": "Link housing assistance to local job opportunities", "category": "workforce-housing", "expected_cluster": "Economic Integration"}
                ]
            },
            "infrastructure": {
                "title": "Infrastructure and Public Services",
                "description": "Maintaining and improving essential city services and infrastructure",
                "main_theme": "How should cities prioritize infrastructure investments and service delivery?",
                "statements": [
                    {"text": "Fix roads and sidewalks before building new ones", "category": "maintenance", "expected_cluster": "Maintenance First"},
                    {"text": "Upgrade water and sewer systems to handle climate change", "category": "utilities", "expected_cluster": "Climate Resilience"},
                    {"text": "Invest in high-speed internet as a public utility", "category": "broadband", "expected_cluster": "Digital Equity"},
                    {"text": "Extend public transit to underserved neighborhoods", "category": "transit-equity", "expected_cluster": "Service Equity"},
                    {"text": "Build more parks and recreational facilities", "category": "recreation", "expected_cluster": "Quality of Life"},
                    {"text": "Prioritize green infrastructure for stormwater management", "category": "green-infrastructure", "expected_cluster": "Environmental Solutions"},
                    {"text": "Increase frequency of trash and recycling pickup", "category": "waste-management", "expected_cluster": "Basic Services"},
                    {"text": "Expand library hours and services", "category": "library-services", "expected_cluster": "Public Resources"},
                    {"text": "Improve emergency response times", "category": "emergency-services", "expected_cluster": "Safety & Security"},
                    {"text": "Use smart city technology to optimize services", "category": "smart-city", "expected_cluster": "Technology Solutions"}
                ]
            },
            "local-economy": {
                "title": "Local Economy and Jobs",
                "description": "Supporting economic development while ensuring benefits reach all residents",
                "main_theme": "How should cities promote economic growth that benefits everyone?",
                "statements": [
                    {"text": "Provide low-interest loans to small businesses", "category": "small-business", "expected_cluster": "Local Business Support"},
                    {"text": "Require living wages for all city-funded projects", "category": "wage-policy", "expected_cluster": "Worker Rights"},
                    {"text": "Create job training programs for green economy jobs", "category": "job-training", "expected_cluster": "Future Skills"},
                    {"text": "Support local hiring requirements for major developments", "category": "local-hire", "expected_cluster": "Community Benefits"},
                    {"text": "Invest in startup incubators and innovation hubs", "category": "innovation", "expected_cluster": "Entrepreneurship"},
                    {"text": "Protect existing affordable commercial spaces", "category": "commercial-preservation", "expected_cluster": "Anti-Displacement"},
                    {"text": "Expand public markets and support local farmers", "category": "local-food", "expected_cluster": "Local Economy"},
                    {"text": "Create worker cooperative development programs", "category": "cooperatives", "expected_cluster": "Democratic Economy"},
                    {"text": "Attract major employers with tax incentives", "category": "business-incentives", "expected_cluster": "Corporate Attraction"},
                    {"text": "Invest in tourism and cultural attractions", "category": "tourism", "expected_cluster": "Cultural Economy"}
                ]
            },
            
            # Suburban Town Domains
            "traffic-school-safety": {
                "title": "Traffic Congestion and School Safety",
                "description": "Managing traffic flow while ensuring student safety",
                "main_theme": "How should suburban communities balance traffic efficiency with school safety?",
                "statements": [
                    {"text": "Install traffic lights at all school crossings", "category": "safety-infrastructure", "expected_cluster": "Safety First"},
                    {"text": "Create car-free zones around schools during pickup/dropoff", "category": "pedestrian-zones", "expected_cluster": "Pedestrian Priority"},
                    {"text": "Require speed bumps on all residential streets near schools", "category": "traffic-calming", "expected_cluster": "Slow Traffic"},
                    {"text": "Build dedicated school bus lanes on main roads", "category": "bus-infrastructure", "expected_cluster": "Transit Solutions"},
                    {"text": "Implement variable speed limits during school hours", "category": "dynamic-limits", "expected_cluster": "Flexible Systems"},
                    {"text": "Increase police presence during school hours", "category": "enforcement", "expected_cluster": "Law Enforcement"},
                    {"text": "Build underground parking for school events", "category": "parking-solutions", "expected_cluster": "Infrastructure Investment"},
                    {"text": "Encourage walking school buses and bike trains", "category": "active-transport", "expected_cluster": "Community Organizing"},
                    {"text": "Install smart traffic signals that respond to pedestrians", "category": "smart-systems", "expected_cluster": "Technology Solutions"},
                    {"text": "Create neighborhood traffic committees with enforcement power", "category": "community-control", "expected_cluster": "Local Governance"}
                ]
            },
            
            "property-taxes": {
                "title": "Property Tax Policy and Equity",
                "description": "Balancing municipal revenue needs with taxpayer burden",
                "main_theme": "How should property taxes be structured to be fair and sustainable?",
                "statements": [
                    {"text": "Cap annual property tax increases at 2% regardless of home value", "category": "tax-caps", "expected_cluster": "Taxpayer Protection"},
                    {"text": "Provide property tax exemptions for seniors and disabled residents", "category": "exemptions", "expected_cluster": "Vulnerable Protection"},
                    {"text": "Tax commercial properties at higher rates than residential", "category": "differential-rates", "expected_cluster": "Business Burden"},
                    {"text": "Use property taxes primarily for schools and essential services", "category": "spending-priorities", "expected_cluster": "Essential Services"},
                    {"text": "Implement income-based property tax relief programs", "category": "income-adjustment", "expected_cluster": "Progressive Taxation"},
                    {"text": "Regular reassessment to ensure current market values", "category": "assessment-frequency", "expected_cluster": "Fair Assessment"},
                    {"text": "Create tax increment financing for development projects", "category": "tif-policy", "expected_cluster": "Development Tools"},
                    {"text": "Transparent budget process with public input on tax rates", "category": "transparency", "expected_cluster": "Democratic Process"},
                    {"text": "Regional property tax sharing to reduce inequality", "category": "regional-sharing", "expected_cluster": "Regional Equity"},
                    {"text": "Phase in tax increases for long-term residents", "category": "phase-in", "expected_cluster": "Stability Focus"}
                ]
            },
            
            # Rural Area Domains
            "digital-infrastructure": {
                "title": "Digital Infrastructure and Connectivity Gap",
                "description": "Bridging the rural-urban digital divide",
                "main_theme": "How should rural communities address internet and digital access gaps?",
                "statements": [
                    {"text": "Treat high-speed internet as a public utility like electricity", "category": "public-utility", "expected_cluster": "Digital Rights"},
                    {"text": "Use federal grants to build fiber optic networks", "category": "federal-funding", "expected_cluster": "Infrastructure Investment"},
                    {"text": "Partner with private companies for service expansion", "category": "public-private", "expected_cluster": "Market Partnership"},
                    {"text": "Create community-owned broadband cooperatives", "category": "cooperatives", "expected_cluster": "Community Ownership"},
                    {"text": "Provide free wifi hotspots in all public buildings", "category": "public-access", "expected_cluster": "Public Access"},
                    {"text": "Require internet service as condition for new development", "category": "development-requirements", "expected_cluster": "Growth Management"},
                    {"text": "Subsidize internet costs for low-income rural families", "category": "affordability", "expected_cluster": "Digital Equity"},
                    {"text": "Build cell towers to improve mobile coverage first", "category": "mobile-priority", "expected_cluster": "Mobile First"},
                    {"text": "Focus on satellite internet solutions for remote areas", "category": "satellite-solutions", "expected_cluster": "Alternative Technology"},
                    {"text": "Train residents in digital literacy and tech skills", "category": "digital-literacy", "expected_cluster": "Education Focus"}
                ]
            },
            
            # University Town Domains
            "student-housing-shortage": {
                "title": "Student Housing Crisis and Community Impact",
                "description": "Addressing housing shortages while maintaining community character",
                "main_theme": "How should university towns manage student housing needs?",
                "statements": [
                    {"text": "Require universities to house 100% of students on campus", "category": "on-campus-mandate", "expected_cluster": "University Responsibility"},
                    {"text": "Build high-density student housing near campus only", "category": "zoning-restrictions", "expected_cluster": "Containment Strategy"},
                    {"text": "Allow housing conversion in all residential neighborhoods", "category": "citywide-conversion", "expected_cluster": "Market Solutions"},
                    {"text": "Create rent stabilization for student housing", "category": "rent-control", "expected_cluster": "Price Protection"},
                    {"text": "Tax university endowment to fund community housing", "category": "university-taxation", "expected_cluster": "University Pays"},
                    {"text": "Limit the number of unrelated students per household", "category": "occupancy-limits", "expected_cluster": "Neighborhood Protection"},
                    {"text": "Build public transit from campus to affordable areas", "category": "transit-solutions", "expected_cluster": "Transportation Focus"},
                    {"text": "Partner with developers on mixed-income housing", "category": "mixed-income", "expected_cluster": "Integration Approach"},
                    {"text": "Create housing cooperatives for students and families", "category": "housing-coops", "expected_cluster": "Alternative Models"},
                    {"text": "Require landlord registration and regular inspections", "category": "housing-standards", "expected_cluster": "Quality Control"}
                ]
            },
            
            "transportation": {
                "title": "Transportation Policy & Equity",
                "description": "Balancing transportation options, costs, and accessibility",
                "main_theme": "How should communities prioritize different transportation modes and policies?",
                "statements": [
                    {"text": "Public transit should be free for all residents, funded by higher parking fees", "category": "transit-equity", "expected_cluster": "Transit Advocates"},
                    {"text": "Cities should prioritize bike lanes over car parking spaces", "category": "active-transport", "expected_cluster": "Active Transportation"},
                    {"text": "Ride-sharing services should be regulated like traditional taxis", "category": "ride-share", "expected_cluster": "Traditional Regulation"},
                    {"text": "New housing developments must include car-free options with transit passes", "category": "transit-oriented", "expected_cluster": "Transit Advocates"},
                    {"text": "Electric scooters should have designated parking areas, not sidewalk placement", "category": "micro-mobility", "expected_cluster": "Order & Safety"},
                    {"text": "Highway expansion should stop in favor of regional rail investment", "category": "infrastructure", "expected_cluster": "Transit Advocates"},
                    {"text": "Low-income residents should get transportation vouchers for any mode", "category": "equity", "expected_cluster": "Equity Focus"},
                    {"text": "Autonomous vehicles will solve traffic better than public transit", "category": "tech-solutions", "expected_cluster": "Tech Optimists"},
                    {"text": "Neighborhood streets should prioritize pedestrians over car flow", "category": "street-design", "expected_cluster": "Active Transportation"},
                    {"text": "Parking fees should be based on income with sliding scale pricing", "category": "economic-equity", "expected_cluster": "Equity Focus"}
                ]
            },
            "housing": {
                "title": "Housing Development & Community Character",
                "description": "Managing growth, affordability, and neighborhood identity",
                "main_theme": "How should communities balance new housing with existing character?",
                "statements": [
                    {"text": "New developments should match existing neighborhood density and size", "category": "character", "expected_cluster": "Character Preservationists"},
                    {"text": "Single-family zoning should be eliminated to allow duplexes", "category": "zoning", "expected_cluster": "Housing Advocates"},
                    {"text": "All developments should include 15% affordable housing units", "category": "affordability", "expected_cluster": "Affordability Focus"},
                    {"text": "Property taxes should fund first-time homebuyer programs", "category": "homeownership", "expected_cluster": "Community Support"},
                    {"text": "Short-term rentals should be banned in residential areas", "category": "str-policy", "expected_cluster": "Neighborhood Stability"},
                    {"text": "Developers should pay fees to fund schools and infrastructure", "category": "impact-fees", "expected_cluster": "Community Investment"},
                    {"text": "Homeowners should get tax credits for installing solar panels", "category": "energy", "expected_cluster": "Sustainability Focus"},
                    {"text": "All new homes should be required to include solar power systems", "category": "energy-mandate", "expected_cluster": "Sustainability Focus"},
                    {"text": "Community solar gardens should be prioritized over individual systems", "category": "community-energy", "expected_cluster": "Community Investment"},
                    {"text": "Energy-efficient home retrofits should be funded by utility rebates", "category": "efficiency", "expected_cluster": "Sustainability Focus"}
                ]
            },
            "education": {
                "title": "Education Funding & Priorities",
                "description": "Allocating limited resources among competing educational needs",
                "main_theme": "How should public schools prioritize spending to serve all students?",
                "statements": [
                    {"text": "Reduce class sizes even if it means cutting art and music programs", "category": "class-size", "expected_cluster": "Basic Academics"},
                    {"text": "Technology spending should be prioritized over building renovations", "category": "tech-vs-facilities", "expected_cluster": "Innovation Focus"},
                    {"text": "Schools should offer full-day pre-K funded by higher property taxes", "category": "early-childhood", "expected_cluster": "Early Investment"},
                    {"text": "Eliminate gifted programs to focus resources on struggling students", "category": "equity-vs-excellence", "expected_cluster": "Equity Focus"},
                    {"text": "Charter schools improve education more than increased traditional funding", "category": "school-choice", "expected_cluster": "Choice Advocates"},
                    {"text": "Teacher pay should be based on student performance metrics", "category": "merit-pay", "expected_cluster": "Accountability Focus"},
                    {"text": "Schools should provide free meals and supplies to all students", "category": "universal-services", "expected_cluster": "Universal Support"},
                    {"text": "Vocational programs should get equal funding to college prep", "category": "career-paths", "expected_cluster": "Practical Skills"},
                    {"text": "School districts should consolidate to reduce administrative costs", "category": "consolidation", "expected_cluster": "Efficiency Focus"},
                    {"text": "Mental health counselors should be prioritized over tutoring", "category": "wellness", "expected_cluster": "Whole Child"}
                ]
            }
        }
        
        # Expected clusters for each domain
        self.demo_clusters = {
            "crime-public-safety": [
                {"name": "Law & Order", "description": "Support traditional policing and enforcement"},
                {"name": "Prevention Focus", "description": "Address root causes through community programs"},
                {"name": "Reform Focus", "description": "Police accountability and criminal justice reform"},
                {"name": "Health Approach", "description": "Treat crime as public health issue"}
            ],
            "housing-affordability": [
                {"name": "Housing Justice", "description": "Housing as a human right requiring strong protections"},
                {"name": "Market Solutions", "description": "Use incentives and market mechanisms"},
                {"name": "Community Stability", "description": "Prevent displacement of existing residents"},
                {"name": "Smart Growth", "description": "Increase density and development strategically"}
            ],
            "traffic-school-safety": [
                {"name": "Safety First", "description": "Prioritize student safety over traffic convenience"},
                {"name": "Slow Traffic", "description": "Use infrastructure to reduce vehicle speeds"},
                {"name": "Community Organizing", "description": "Grassroots solutions and active transportation"},
                {"name": "Technology Solutions", "description": "Smart systems and dynamic traffic management"}
            ],
            "property-taxes": [
                {"name": "Taxpayer Protection", "description": "Keep taxes low and predictable for residents"},
                {"name": "Progressive Taxation", "description": "Tax based on ability to pay and income"},
                {"name": "Essential Services", "description": "Focus spending on core municipal functions"},
                {"name": "Democratic Process", "description": "Transparent decision-making with public input"}
            ],
            "digital-infrastructure": [
                {"name": "Digital Rights", "description": "Internet access as fundamental public service"},
                {"name": "Infrastructure Investment", "description": "Major public investment in fiber networks"},
                {"name": "Community Ownership", "description": "Local control through cooperatives"},
                {"name": "Market Partnership", "description": "Work with private sector for solutions"}
            ],
            "student-housing-shortage": [
                {"name": "University Responsibility", "description": "Universities should solve their own housing needs"},
                {"name": "Neighborhood Protection", "description": "Preserve residential character and family housing"},
                {"name": "Market Solutions", "description": "Allow development and conversion where needed"},
                {"name": "Integration Approach", "description": "Mix students and families in same neighborhoods"}
            ],
            "infrastructure": [
                {"name": "Maintenance First", "description": "Fix existing infrastructure before building new"},
                {"name": "Climate Resilience", "description": "Prepare infrastructure for climate change"},
                {"name": "Service Equity", "description": "Ensure all neighborhoods get quality services"},
                {"name": "Technology Solutions", "description": "Use smart city tech to improve efficiency"}
            ],
            "local-economy": [
                {"name": "Local Business Support", "description": "Prioritize small and local businesses"},
                {"name": "Worker Rights", "description": "Focus on wages and working conditions"},
                {"name": "Community Benefits", "description": "Ensure development benefits existing residents"},
                {"name": "Innovation Economy", "description": "Attract tech and knowledge-based industries"}
            ],
            "transportation": [
                {"name": "Transit Advocates", "description": "Support public transit investment and car alternatives"},
                {"name": "Active Transportation", "description": "Prioritize walking, cycling, and human-scale mobility"},
                {"name": "Equity Focus", "description": "Emphasize access for low-income residents"},
                {"name": "Tech Optimists", "description": "Believe technology will solve transportation challenges"}
            ],
            "housing": [
                {"name": "Character Preservationists", "description": "Protect existing neighborhood character"},
                {"name": "Housing Advocates", "description": "Increase supply through zoning reform"},
                {"name": "Affordability Focus", "description": "Prevent displacement and reduce costs"},
                {"name": "Community Investment", "description": "Ensure development benefits residents"}
            ],
            "education": [
                {"name": "Basic Academics", "description": "Focus on core subjects and fundamentals"},
                {"name": "Equity Focus", "description": "Prioritize struggling and disadvantaged students"},
                {"name": "Innovation Focus", "description": "Invest in technology and modern approaches"},
                {"name": "Whole Child", "description": "Support student wellness and development"}
            ]
        }
    
    def determine_domain_from_issues(self, issues: List[str]) -> str:
        """Determine the most relevant domain based on community issues"""
        if not issues:
            return "transportation"
        
        issue_text = " ".join(issues).lower()
        
        # Check for housing-related keywords (expanded)
        housing_keywords = [
            'housing', 'rent', 'affordable', 'development', 'zoning', 'homelessness',
            'home', 'house', 'property', 'real estate', 'mortgage', 'landlord', 'tenant',
            'apartment', 'condo', 'neighborhood', 'residential', 'gentrification',
            'solar', 'energy', 'power', 'electricity', 'utilities', 'hvac', 'heating',
            'cooling', 'insulation', 'renovation', 'construction', 'building'
        ]
        if any(keyword in issue_text for keyword in housing_keywords):
            return "housing"
        
        # Check for education-related keywords (expanded)
        education_keywords = [
            'school', 'education', 'teacher', 'student', 'learning',
            'classroom', 'curriculum', 'graduation', 'college', 'university',
            'kindergarten', 'elementary', 'middle school', 'high school',
            'academic', 'literacy', 'math', 'science', 'arts', 'sports',
            'extracurricular', 'funding', 'budget', 'principal', 'administrator'
        ]
        if any(keyword in issue_text for keyword in education_keywords):
            return "education"
        
        # Check for transportation-related keywords (explicit)
        transportation_keywords = [
            'transportation', 'transit', 'bus', 'train', 'subway', 'metro',
            'car', 'vehicle', 'traffic', 'parking', 'road', 'highway',
            'bike', 'bicycle', 'pedestrian', 'walkability', 'commute',
            'rideshare', 'uber', 'lyft', 'taxi', 'scooter', 'infrastructure'
        ]
        if any(keyword in issue_text for keyword in transportation_keywords):
            return "transportation"
        
        # Default to housing for general community issues
        return "housing"
    
    def map_frontend_domain_to_backend(self, frontend_domain: str) -> str:
        """Map frontend domain values to backend demo topic keys"""
        domain_mapping = {
            # Urban Community mappings
            'crime-public-safety': 'crime-public-safety',
            'housing-affordability': 'housing-affordability', 
            'economic-development': 'local-economy',
            'infrastructure-services': 'infrastructure',
            'transportation': 'transportation',
            
            # Suburban Town mappings
            'traffic-school-safety': 'traffic-school-safety',
            'infrastructure-maintenance': 'infrastructure',
            'school-quality': 'education',
            'property-taxes': 'property-taxes',
            'environmental-concerns': 'infrastructure',
            
            # Rural Area mappings
            'digital-infrastructure': 'digital-infrastructure',
            'healthcare-access': 'infrastructure',  # Could create specific healthcare domain later
            'economic-opportunities': 'local-economy',
            'aging-population': 'infrastructure',  # Could create specific aging services domain later
            'infrastructure-decay': 'infrastructure',
            
            # University Town mappings
            'student-housing-shortage': 'student-housing-shortage',
            'town-gown-relations': 'local-economy',  # Could create specific domain later
            'parking-transportation': 'transportation',
            'noise-disruption': 'crime-public-safety',  # Maps to public safety
            'economic-dependence': 'local-economy',
            
            # Direct mappings for backend keys
            'housing': 'housing',
            'education': 'education',
            'local-economy': 'local-economy',
            'infrastructure': 'infrastructure'
        }
        
        mapped_result = domain_mapping.get(frontend_domain, frontend_domain)
        logger.info(f"Domain mapping: '{frontend_domain}' -> '{mapped_result}'")
        return mapped_result

    async def generate_topic(self, request: TopicRequest) -> GeneratedTopic:
        """Generate a demo topic based on community context"""
        
        try:
            # Determine topic domain
            if request.topic_domain and request.topic_domain != 'auto':
                # Map frontend domain to backend key
                mapped_domain = self.map_frontend_domain_to_backend(request.topic_domain)
                if mapped_domain in self.demo_topics:
                    domain = mapped_domain
                else:
                    # If mapped domain still doesn't exist, use a sensible default
                    domain = 'housing'  # Default to housing instead of random
            else:
                # For 'auto' or None, select based on community context
                if request.community_context.current_issues:
                    domain = self.determine_domain_from_issues(request.community_context.current_issues)
                else:
                    # Select a domain based on community type if no issues provided
                    import random
                    available_domains = list(self.demo_topics.keys())
                    domain = random.choice(available_domains)
            
            # Get the appropriate demo topic
            topic_data = self.demo_topics[domain]
            clusters = self.demo_clusters[domain]
            
            # Customize title for the specific location
            customized_title = f"{request.community_context.location} {topic_data['title']}"
            customized_description = f"{topic_data['description']} in {request.community_context.location}"
            
            # Convert statements to Statement objects
            statements = [
                Statement(
                    text=stmt["text"],
                    category=stmt["category"],
                    expected_cluster=stmt["expected_cluster"]
                )
                for stmt in topic_data["statements"][:request.statement_count]
            ]
            
            # Create metadata
            metadata = {
                "generated_at": datetime.now().isoformat(),
                "community_location": request.community_context.location,
                "statement_count": len(statements),
                "language": request.language,
                "generation_method": "demo",
                "domain": domain
            }
            
            logger.info(f"Generated demo topic: {customized_title} (domain: {domain}, frontend_domain: {request.topic_domain})")
            
            return GeneratedTopic(
                title=customized_title,
                description=customized_description,
                main_theme=topic_data["main_theme"],
                statements=statements,
                expected_clusters=clusters,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error generating demo topic: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Demo topic generation failed: {str(e)}")

async def generate_topic_with_llm(context: CommunityContext, topic_domain: str = None) -> GeneratedTopic:
    """Generate a polling topic using OpenAI's GPT model"""
    
    # Map topic domain to specific focus areas
    domain_prompts = {
        "housing": "Focus on housing affordability, development, zoning, and community character",
        "transportation": "Focus on public transit, traffic, parking, bike/pedestrian infrastructure",
        "education": "Focus on school funding, curriculum, teacher resources, and student outcomes", 
        "crime-public-safety": "Focus on policing, crime prevention, community safety, and justice reform",
        "economic-development": "Focus on local business, jobs, economic growth, and workforce development",
        "infrastructure-services": "Focus on utilities, roads, public services, and municipal infrastructure",
        "local-economy": "Focus on small business support, economic opportunities, and community development"
    }
    
    domain_guidance = domain_prompts.get(topic_domain, "Focus on the most pressing community issues")
    
    prompt = f"""
    Create a community polling topic for {context.location} with a population of {context.population_size or 'unknown'}.
    
    Topic Domain: {topic_domain or 'General Community Issues'}
    Specific Focus: {domain_guidance}
    
    Current issues in the community: {', '.join(context.current_issues or [])}
    Previous topics covered: {', '.join(context.previous_topics or [])}
    
    Generate a JSON response with:
    1. A compelling title for the polling topic specific to {context.location} and {topic_domain or 'community issues'}
    2. A brief description of what the poll will explore
    3. A main theme question
    4. 8-12 diverse statements that represent different viewpoints on the topic
    5. Exactly 4 expected opinion clusters that voters might fall into
    
    Each statement should:
    - Be specific and actionable for {context.location}
    - Represent a distinct viewpoint on {topic_domain or 'community issues'}
    - Be relevant to the community context and demographics
    - Have a category and expected cluster
    
    Make the content unique and specific to {context.location} rather than generic.
    
    Format the response as JSON with this structure:
    {{
        "title": "Topic Title",
        "description": "Brief description of the poll",
        "main_theme": "Main theme question",
        "statements": [
            {{
                "text": "Statement text",
                "category": "category-name",
                "expected_cluster": "Cluster Name"
            }}
        ],
        "expected_clusters": [
            {{
                "name": "Cluster Name",
                "description": "Description of this opinion cluster"
            }}
        ]
    }}
    """
    
    try:
        if not openai_client:
            raise Exception("OpenAI client not initialized (API key missing)")
            
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in community engagement and polling design. Generate thoughtful, balanced polling topics that encourage civic participation. Make content specific to the location and topic domain provided."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        topic_data = json.loads(content)
        
        # Convert to our model
        statements = [
            Statement(
                text=stmt["text"],
                category=stmt["category"],
                expected_cluster=stmt["expected_cluster"]
            )
            for stmt in topic_data["statements"]
        ]
        
        # Create metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "community_location": context.location,
            "statement_count": len(statements),
            "generation_method": "llm",
            "model": "gpt-4",
            "topic_domain": topic_domain
        }
        
        return GeneratedTopic(
            title=topic_data["title"],
            description=topic_data["description"],
            main_theme=topic_data.get("main_theme", "Community perspective question"),
            statements=statements,
            expected_clusters=topic_data["expected_clusters"],
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error generating topic with LLM: {e}")
        # Fallback to demo topic generator
        demo_generator = DemoTopicGenerator()
        return await demo_generator.generate_topic(TopicRequest(
            community_context=context,
            topic_domain=topic_domain,
            statement_count=10
        ))

# Initialize the demo topic generator
topic_generator = DemoTopicGenerator()

@app.post("/generate-topic", response_model=GeneratedTopic)
async def generate_topic_endpoint(request: TopicRequest):
    """Generate a community-relevant polling topic"""
    try:
        if not request.community_context.location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        # Log user activity
        log_user_activity("topic_generation_request", {
            "location": request.community_context.location,
            "topic_domain": request.topic_domain,
            "population_size": request.community_context.population_size,
            "has_current_issues": bool(request.community_context.current_issues),
            "has_previous_topics": bool(request.community_context.previous_topics)
        })
        
        # Debug logging
        logger.info(f"Received request - topic_domain: {request.topic_domain}, location: {request.community_context.location}")
        
        # Try OpenAI LLM first, fallback to demo if no API key or error
        if openai_client:
            try:
                logger.info("Using OpenAI LLM generation")
                topic = await generate_topic_with_llm(request.community_context, request.topic_domain)
                
                # Log successful LLM generation
                log_user_activity("topic_generated", {
                    "method": "llm",
                    "location": request.community_context.location,
                    "topic_title": topic.title,
                    "statement_count": len(topic.statements),
                    "cluster_count": len(topic.expected_clusters)
                })
                
                return topic
            except Exception as e:
                logger.warning(f"OpenAI generation failed, falling back to demo: {str(e)}")
                
                # Log LLM failure
                log_user_activity("topic_generation_fallback", {
                    "reason": str(e),
                    "location": request.community_context.location
                })
                
                topic = await topic_generator.generate_topic(request)
                
                # Log demo generation
                log_user_activity("topic_generated", {
                    "method": "demo",
                    "location": request.community_context.location,
                    "topic_title": topic.title,
                    "statement_count": len(topic.statements),
                    "cluster_count": len(topic.expected_clusters)
                })
                
                return topic
        else:
            logger.info("No OpenAI API key, using demo generation")
            topic = await topic_generator.generate_topic(request)
            
            # Log demo generation
            log_user_activity("topic_generated", {
                "method": "demo",
                "location": request.community_context.location,
                "topic_title": topic.title,
                "statement_count": len(topic.statements),
                "cluster_count": len(topic.expected_clusters)
            })
            
            return topic
        
    except Exception as e:
        logger.error(f"Error generating topic: {str(e)}")
        
        # Log error
        log_user_activity("topic_generation_error", {
            "error": str(e),
            "location": request.community_context.location if request.community_context else "unknown"
        })
        
        raise HTTPException(status_code=500, detail=f"Error generating topic: {str(e)}")

# Legacy endpoint for backward compatibility
@app.post("/generate-topic-legacy", response_model=GeneratedTopic)
async def generate_topic_legacy(request: GenerateTopicRequest):
    """Generate a polling topic based on community context (legacy format)"""
    
    # Convert legacy request to new format
    topic_request = TopicRequest(
        community_context=request.community_context,
        statement_count=10
    )
    
    return await generate_topic_endpoint(topic_request)

@app.get("/demo-domains")
async def get_demo_domains():
    """Get available demo domains"""
    return {
        "available_domains": list(topic_generator.demo_topics.keys()),
        "description": "Available topic domains for demo generation"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "community-topic-generator", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Community Polling Topic Generator",
        "version": "1.0.0",
        "description": "Generate community-relevant polling topics using LLM or demo data",
        "endpoints": {
            "generate": "/generate-topic",
            "legacy": "/generate-topic-legacy", 
            "health": "/health",
            "domains": "/demo-domains",
            "docs": "/docs"
        },
        "features": {
            "llm_generation": bool(os.getenv("OPENAI_API_KEY")),
            "demo_domains": list(topic_generator.demo_topics.keys())
        }
    }

# Poll sharing endpoints
@app.post("/save-poll", response_model=Dict[str, str])
async def save_poll(request: SavePollRequest):
    """Save a poll for sharing"""
    try:
        poll_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        logger.info(f"Attempting to save poll with ID: {poll_id}")
        logger.info(f"Poll title: {request.topic.title}")
        
        # Convert topic to database format
        statements_json = json.dumps([stmt.dict() for stmt in request.topic.statements])
        clusters_json = json.dumps(request.topic.expected_clusters)
        metadata_json = json.dumps(request.topic.metadata)
        
        logger.info(f"Converted data - statements: {len(request.topic.statements)} items")
        logger.info(f"Database file: {DATABASE_PATH}")
        
        with get_db_connection() as conn:
            logger.info("Database connection established")
            conn.execute("""
                INSERT INTO shared_polls 
                (poll_id, title, description, main_theme, statements, expected_clusters, metadata, created_at, creator_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                poll_id,
                request.topic.title,
                request.topic.description,
                request.topic.main_theme,
                statements_json,
                clusters_json,
                metadata_json,
                created_at,
                request.creator_name
            ))
            conn.commit()
            logger.info(f"Poll {poll_id} successfully saved to database")
            
            # Verify the save worked
            cursor = conn.execute("SELECT poll_id FROM shared_polls WHERE poll_id = ?", (poll_id,))
            if cursor.fetchone():
                logger.info(f"Verification: Poll {poll_id} found in database")
            else:
                logger.error(f"Verification failed: Poll {poll_id} not found after save")
        
        # Log poll sharing activity
        log_user_activity("poll_saved", {
            "poll_id": poll_id,
            "title": request.topic.title,
            "creator_name": request.creator_name,
            "statement_count": len(request.topic.statements)
        })
        
        return {"poll_id": poll_id, "share_url": f"/poll/shared/{poll_id}"}
        
    except Exception as e:
        logger.error(f"Error saving poll: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error saving poll: {str(e)}")

@app.get("/poll/{poll_id}", response_model=SharedPoll)
async def get_shared_poll(poll_id: str):
    """Get a shared poll by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM shared_polls WHERE poll_id = ?
            """, (poll_id,))
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        # Convert back to objects
        statements = [Statement(**stmt) for stmt in json.loads(row['statements'])]
        expected_clusters = json.loads(row['expected_clusters'])
        metadata = json.loads(row['metadata'])
        
        # Log poll access
        log_user_activity("poll_accessed", {
            "poll_id": poll_id,
            "title": row['title'],
            "creator_name": row['creator_name']
        })
        
        return SharedPoll(
            poll_id=row['poll_id'],
            title=row['title'],
            description=row['description'],
            main_theme=row['main_theme'],
            statements=statements,
            expected_clusters=expected_clusters,
            metadata=metadata,
            created_at=row['created_at'],
            creator_name=row['creator_name']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shared poll: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting shared poll: {str(e)}")

@app.get("/polls/stats")
async def get_poll_stats():
    """Get basic statistics about shared polls"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total_polls FROM shared_polls")
            total_polls = cursor.fetchone()['total_polls']
            
            cursor = conn.execute("""
                SELECT poll_id, title, created_at FROM shared_polls 
                ORDER BY created_at DESC LIMIT 5
            """)
            recent_polls = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_shared_polls": total_polls,
            "recent_polls": recent_polls,
            "database_working": True
        }
        
    except Exception as e:
        logger.error(f"Error getting poll stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/debug/database")
async def debug_database():
    """Debug endpoint to check database state"""
    try:
        with get_db_connection() as conn:
            # Check if tables exist
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row['name'] for row in cursor.fetchall()]
            
            # Get poll count
            cursor = conn.execute("SELECT COUNT(*) as count FROM shared_polls")
            poll_count = cursor.fetchone()['count']
            
            # Get response count
            cursor = conn.execute("SELECT COUNT(*) as count FROM poll_responses")
            response_count = cursor.fetchone()['count']
            
            return {
                "database_file": DATABASE_PATH,
                "tables": tables,
                "polls_count": poll_count,
                "responses_count": response_count,
                "status": "healthy"
            }
    except Exception as e:
        logger.error(f"Database debug error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "database_file": DATABASE_PATH
        }

@app.post("/poll/{poll_id}/responses")
async def submit_poll_responses(poll_id: str, request: SubmitPollResponseRequest):
    """Submit responses for a shared poll"""
    try:
        # Verify poll exists
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT poll_id FROM shared_polls WHERE poll_id = ?", (poll_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Poll not found")
        
        # Check if participant has already responded
        existing_session_id = None
        if request.participant_name:
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT participant_session_id 
                    FROM poll_responses 
                    WHERE poll_id = ? AND participant_name = ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (poll_id, request.participant_name))
                existing_row = cursor.fetchone()
                if existing_row:
                    existing_session_id = existing_row['participant_session_id']
        
        # If retaking, delete previous responses
        if existing_session_id:
            with get_db_connection() as conn:
                conn.execute("""
                    DELETE FROM poll_responses 
                    WHERE poll_id = ? AND participant_session_id = ?
                """, (poll_id, existing_session_id))
                conn.commit()
            
            log_user_activity("poll_retaken", {
                "poll_id": poll_id,
                "participant_name": request.participant_name,
                "previous_session_id": existing_session_id
            })
        
        # Generate a new session ID for this participant
        participant_session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Save all responses
        with get_db_connection() as conn:
            for response in request.responses:
                conn.execute("""
                    INSERT INTO poll_responses 
                    (poll_id, participant_name, statement_index, response, timestamp, participant_session_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    poll_id,
                    request.participant_name,
                    response["statementIndex"],
                    response["response"],
                    timestamp,
                    participant_session_id
                ))
            conn.commit()
        
        # Log the response submission
        log_user_activity("poll_responses_submitted", {
            "poll_id": poll_id,
            "participant_name": request.participant_name,
            "response_count": len(request.responses),
            "participant_session_id": participant_session_id,
            "is_retake": existing_session_id is not None
        })
        
        return {
            "success": True,
            "participant_session_id": participant_session_id,
            "responses_saved": len(request.responses),
            "is_retake": existing_session_id is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting poll responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting responses: {str(e)}")

@app.get("/poll/{poll_id}/participant/{participant_name}")
async def check_participant_status(poll_id: str, participant_name: str):
    """Check if a participant has already taken the poll"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as response_count, MAX(timestamp) as last_taken
                FROM poll_responses 
                WHERE poll_id = ? AND participant_name = ?
            """, (poll_id, participant_name))
            result = cursor.fetchone()
            
            has_responded = result['response_count'] > 0
            
            return {
                "has_responded": has_responded,
                "response_count": result['response_count'],
                "last_taken": result['last_taken'] if has_responded else None
            }
            
    except Exception as e:
        logger.error(f"Error checking participant status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking participant status: {str(e)}")

@app.get("/poll/{poll_id}/results", response_model=PollResultsResponse)
async def get_poll_results(poll_id: str):
    """Get aggregated results for a shared poll"""
    try:
        # Get poll data
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM shared_polls WHERE poll_id = ?
            """, (poll_id,))
            poll_row = cursor.fetchone()
            
            if not poll_row:
                raise HTTPException(status_code=404, detail="Poll not found")
            
            # Get all responses for this poll
            cursor = conn.execute("""
                SELECT participant_session_id, participant_name, statement_index, response, timestamp
                FROM poll_responses 
                WHERE poll_id = ?
                ORDER BY timestamp
            """, (poll_id,))
            responses = cursor.fetchall()
        
        # Convert poll data back to objects with error handling
        try:
            statements_data = json.loads(poll_row['statements'])
            statements = [Statement(**stmt) for stmt in statements_data]
            expected_clusters = json.loads(poll_row['expected_clusters'])
            metadata = json.loads(poll_row['metadata'])
        except Exception as e:
            logger.error(f"Error converting poll data for poll {poll_id}: {str(e)}")
            logger.error(f"Raw data - statements: {poll_row['statements']}")
            raise HTTPException(status_code=500, detail=f"Data conversion error: {str(e)}")
        
        poll = SharedPoll(
            poll_id=poll_row['poll_id'],
            title=poll_row['title'],
            description=poll_row['description'],
            main_theme=poll_row['main_theme'],
            statements=statements,
            expected_clusters=expected_clusters,
            metadata=metadata,
            created_at=poll_row['created_at'],
            creator_name=poll_row['creator_name']
        )
        
        # Calculate aggregated results - handle empty responses
        total_participants = len(set(row['participant_session_id'] for row in responses)) if responses else 0
        logger.info(f"Poll {poll_id} has {total_participants} participants and {len(responses)} total responses")
        
        # Response summary by statement - use string keys for Pydantic compatibility
        response_summary = {}
        for i, statement in enumerate(statements):
            statement_responses = [r for r in responses if r['statement_index'] == i]
            response_summary[str(i)] = {
                "statement": statement.text,
                "category": statement.category,
                "expected_cluster": statement.expected_cluster,
                "responses": {
                    "agree": len([r for r in statement_responses if r['response'] == 'agree']),
                    "disagree": len([r for r in statement_responses if r['response'] == 'disagree']),
                    "skip": len([r for r in statement_responses if r['response'] == 'skip'])
                },
                "total_responses": len(statement_responses)
            }
        
        # Cluster analysis
        cluster_analysis = []
        for cluster in expected_clusters:
            cluster_statements = [i for i, stmt in enumerate(statements) if stmt.expected_cluster == cluster['name']]
            cluster_responses = [r for r in responses if r['statement_index'] in cluster_statements]
            
            agree_count = len([r for r in cluster_responses if r['response'] == 'agree'])
            disagree_count = len([r for r in cluster_responses if r['response'] == 'disagree'])
            skip_count = len([r for r in cluster_responses if r['response'] == 'skip'])
            total_count = len(cluster_responses)
            
            cluster_analysis.append({
                "cluster_name": cluster['name'],
                "cluster_description": cluster['description'],
                "responses": {
                    "agree": agree_count,
                    "disagree": disagree_count,
                    "skip": skip_count
                },
                "total_responses": total_count,
                "agreement_percentage": round((agree_count / total_count * 100) if total_count > 0 else 0, 1)
            })
        
        # Log results access
        log_user_activity("poll_results_accessed", {
            "poll_id": poll_id,
            "total_participants": total_participants,
            "total_responses": len(responses)
        })
        
        return PollResultsResponse(
            poll=poll,
            total_participants=total_participants,
            response_summary=response_summary,
            cluster_analysis=cluster_analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting poll results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting poll results: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 