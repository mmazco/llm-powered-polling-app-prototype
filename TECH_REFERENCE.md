# 📋 LLM-Powered Community Polling App - Technical Reference

## 🏗️ Architecture Overview

### **Current Tech Stack**
- **Frontend**: Next.js 14 + React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.13
- **LLM**: OpenAI GPT-4 (with demo fallback)
- **Development**: localhost:3000 (frontend) + localhost:8001 (backend)

### **LLM Configuration**
- **Primary**: OpenAI GPT-4 (requires `OPENAI_API_KEY`)
- **Fallback**: Rich demo topics (Transportation, Housing, Education)
- **No Web Search**: Currently uses LLM training data only

## 📊 Our Current Approach vs Pol.is Comparison

| Feature | Our App | Pol.is |
|---------|---------|---------|
| **Topic Generation** | ✅ LLM-powered | ❌ Manual creation |
| **Clustering** | 🔄 Basic/predicted | ✅ ML-powered real-time |
| **Scale** | 👥 Small groups | 🏟️ Thousands |
| **Setup Complexity** | 🟢 Simple | 🟡 Complex |
| **Customization** | 🟢 Full control | 🟡 Limited |
| **Real-time Analysis** | ❌ Not implemented | ✅ Advanced |
| **Government Use** | 🔄 Possible | ✅ Proven (Taiwan, Estonia) |
| **Consensus Finding** | 🔄 Basic | ✅ Sophisticated algorithms |
| **Development Speed** | 🟢 Fast MVP | 🟡 Slower integration |
| **Maintenance** | 🟢 Simple | 🟡 Complex platform |

## 🎯 Pol.is Assessment

### **Pol.is Strengths**
- ✅ **Proven real-world use** (Taiwan digital democracy, Estonia participatory budgeting)
- ✅ **Sophisticated opinion clustering** using machine learning
- ✅ **Scales to thousands** of participants simultaneously
- ✅ **Finds consensus** across political divides
- ✅ **Real-time visualization** of opinion landscapes
- ✅ **Government adoption** for policy making

### **Pol.is Good For**
- 🏛️ **Government/civic engagement** at scale
- 🤝 **Building consensus** on divisive topics
- 📊 **Large-scale opinion mapping** (100s-1000s participants)
- 🔍 **Discovering unexpected agreement** across groups
- 🎯 **Policy development** with broad community input

### **Our App's Advantages**
- 🚀 **AI-powered topic generation** (unique value)
- 🛠️ **Full customization** control
- ⚡ **Rapid development** and iteration
- 🎨 **Custom UI/UX** tailored to specific needs
- 🏢 **Easier deployment** for small organizations

## 🔄 User Flow (Current)

```
localhost:3000 → Community Context Form → Generate Topic → Display Results → Launch Poll (WIP)
     ↓                    ↓                    ↓              ↓               ↓
  Next.js UI        Fill location,       Backend API    Show topic &     Navigate to
                   population, issues   (GPT-4/demo)   statements       voting interface
```

## 🗺️ Domain Detection Algorithm

```python
def determine_domain_from_issues(issues):
    # Housing keywords → Housing domain
    if any(keyword in issues for keyword in ['housing', 'rent', 'affordable', 'development']):
        return "housing"
    
    # Education keywords → Education domain  
    if any(keyword in issues for keyword in ['school', 'education', 'teacher', 'student']):
        return "education"
    
    # Default → Transportation domain
    return "transportation"
```

## 📈 Development Path

### **Phase 1: MVP (Current)**
- ✅ Topic generation working
- ✅ Complete polling interface
- ✅ Basic results display

### **Phase 2: Enhanced Features**
- 🔄 Web search integration for current events
- 🔄 Advanced clustering visualization
- 🔄 Export functionality

### **Phase 3: Scale (Optional)**
- 🔄 Pol.is integration for large-scale use
- 🔄 Database persistence
- 🔄 Multi-tenant deployment

## 🎛️ Configuration

### **Environment Variables**
```bash
OPENAI_API_KEY=your_openai_key_here    # Optional - uses demo if missing
PORT=3000                              # Frontend port
BACKEND_PORT=8001                      # Backend port
```

### **Demo Topics Available**
1. **Transportation** - Transit, bike lanes, parking policies
2. **Housing** - Development, affordability, zoning
3. **Education** - Funding, programs, class sizes

---
*Last Updated: 2025-07-10*
*Status: Active Development - MVP Phase* 