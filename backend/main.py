from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime
import os
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI setup - set your API key as environment variable
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

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
                {"name": "Community Investment", "description": "Ensure development benefits residents"},
                {"name": "Sustainability Focus", "description": "Prioritize environmental and energy considerations"}
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

async def generate_topic_with_llm(context: CommunityContext) -> GeneratedTopic:
    """Generate a polling topic using OpenAI's GPT model"""
    
    prompt = f"""
    Create a community polling topic for {context.location} with a population of {context.population_size or 'unknown'}.
    
    Current issues in the community: {', '.join(context.current_issues or [])}
    Previous topics covered: {', '.join(context.previous_topics or [])}
    
    Generate a JSON response with:
    1. A compelling title for the polling topic
    2. A brief description of what the poll will explore
    3. A main theme question
    4. 8-12 diverse statements that represent different viewpoints on the topic
    5. 4-6 expected opinion clusters that voters might fall into
    
    Each statement should:
    - Be specific and actionable
    - Represent a distinct viewpoint
    - Be relevant to the community context
    - Have a category and expected cluster
    
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
                {"role": "system", "content": "You are an expert in community engagement and polling design. Generate thoughtful, balanced polling topics that encourage civic participation."},
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
            "model": "gpt-4"
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
        
        # Debug logging
        logger.info(f"Received request - topic_domain: {request.topic_domain}, location: {request.community_context.location}")
        
        # Try OpenAI LLM first, fallback to demo if no API key or error
        if openai_client:
            try:
                logger.info("Using OpenAI LLM generation")
                return await generate_topic_with_llm(request.community_context)
            except Exception as e:
                logger.warning(f"OpenAI generation failed, falling back to demo: {str(e)}")
                return await topic_generator.generate_topic(request)
        else:
            logger.info("No OpenAI API key, using demo generation")
            return await topic_generator.generate_topic(request)
        
    except Exception as e:
        logger.error(f"Error generating topic: {str(e)}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 