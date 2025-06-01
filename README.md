# 🧠 DevMind Backend

**AI-Powered Development Context Oracle with MCP Protocol**

DevMind is a winning hackathon project that creates a "living memory" for software development teams by automatically capturing, connecting, and contextualizing all development activities across tools (GitHub, Slack, Jira, docs, error logs) to provide instant, intelligent context to any team member.

## 🏆 Hackathon Winning Features

### ✨ **Technical Innovation**
- **MCP Protocol Integration**: First-class Model Context Protocol implementation
- **Vector Search**: Semantic search across all development context
- **Real-time Updates**: WebSocket-based live insights
- **Multi-source Integration**: GitHub, Slack, Jira unified context

### 🎯 **Real-World Impact**
- **Context Switching Hell**: Eliminates the $billion problem of lost tribal knowledge
- **Team Onboarding**: New developers get full context in minutes, not weeks
- **Decision Tracking**: Never lose track of "why" decisions were made
- **Living Documentation**: Self-updating project knowledge base

## 🚀 Quick Start

### 1. **Clone and Setup**
```bash
# Clone the repository (assuming you have the frontend)
cd backend

# Run the automated setup
python setup.py
```

### 2. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (optional for demo)
nano .env
```

### 3. **Start with Docker (Recommended)**
```bash
# Start all services
docker-compose up -d

# Or start just backend dependencies
docker-compose up -d postgres redis
```

### 4. **Run Backend**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

### 5. **Verify Installation**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🛠️ Architecture

### **Core Components**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   MCP Server    │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Protocol)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                       ┌────────▼────────┐    ┌────────▼────────┐
                       │   PostgreSQL    │    │  Integration    │
                       │   + pgvector    │    │     Tools       │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                       ┌────────▼────────┐    ┌────────▼────────┐
                       │     Redis       │    │ GitHub/Slack/   │
                       │   (Caching)     │    │     Jira        │
                       └─────────────────┘    └─────────────────┘
```

### **Tech Stack**
- **Backend**: Python 3.11 + FastAPI + AsyncIO
- **Database**: PostgreSQL 15 + pgvector for embeddings
- **Cache**: Redis 7 for real-time features
- **MCP**: Official Python SDK for protocol compliance
- **AI**: Sentence Transformers for embeddings
- **WebSockets**: Real-time updates and notifications

## 📡 API Endpoints

### **Core Queries**
- `POST /api/v1/query` - Submit context queries
- `GET /api/v1/query/history` - Query history
- `GET /api/v1/context/search` - Search development context

### **Project Management**
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `PUT /api/v1/projects/{id}` - Update project

### **Integrations**
- `GET /api/v1/integrations` - List integrations
- `POST /api/v1/integrations` - Create integration
- `POST /api/v1/integrations/{id}/sync` - Trigger sync

### **Real-time**
- `WS /ws/live` - WebSocket for live updates
- `GET /api/v1/insights` - Live development insights

## 🔌 MCP Protocol Implementation

### **Tools Available**
- **github_search**: Search repositories, issues, PRs
- **slack_search**: Search messages and channels  
- **jira_search**: Search issues and projects
- **context_search**: Search across all sources

### **Resources Provided**
- **devmind://context/search**: Development context search
- **devmind://decisions/list**: Architectural decisions
- **devmind://timeline/project**: Project timeline
- **devmind://insights/live**: Real-time insights

### **Prompts Supported**
- **analyze_context**: Analyze context for specific questions
- **get_decision_context**: Get architectural decision context
- **onboard_team_member**: Generate onboarding materials

## 🧪 Testing the Application

### **1. Basic Health Check**
```bash
curl http://localhost:8000/health
```

### **2. Submit a Query**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Why did we choose Redis over PostgreSQL for caching?",
    "context_limit": 10
  }'
```

### **3. Test WebSocket Connection**
```javascript
// In browser console or Node.js
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe_general'
  }));
};
ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};
```

### **4. Test MCP Integration**
```bash
# Test context search
curl "http://localhost:8000/api/v1/context/search?query=authentication&limit=5"

# Get system insights  
curl "http://localhost:8000/api/v1/insights"
```

## 🔧 Configuration

### **Required Environment Variables**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/devmind

# API Keys (Optional for demo)
GITHUB_TOKEN=your_github_token
SLACK_TOKEN=your_slack_bot_token
JIRA_URL=https://company.atlassian.net
JIRA_USERNAME=your_email
JIRA_TOKEN=your_jira_token
```

### **Optional AI Enhancement**
```bash
# For enhanced AI responses
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## 🎭 Demo Data

The backend includes rich mock data for demonstration:

### **Mock GitHub Data**
- Commit: "Fix authentication bug in login service"
- Issue: "API Rate Limiting Implementation" 
- PR: Authentication improvements

### **Mock Slack Data**
- Team discussion about Redis vs PostgreSQL
- Deployment notifications
- Technical architecture decisions

### **Mock Jira Data**
- PROJ-123: API Rate Limiting Implementation
- PROJ-124: Authentication service bug fix
- PROJ-125: Redis caching implementation

## 🔍 Debugging & Monitoring

### **Logs Location**
- Application logs: `logs/devmind_YYYYMMDD.log`
- Error logs: `logs/devmind_errors_YYYYMMDD.log`

### **Health Monitoring**
- Health check: `GET /health`
- System status: `GET /api/v1/system/status`
- WebSocket stats: `GET /ws/stats`

### **Database Admin (Optional)**
```bash
# Start admin interfaces
docker-compose --profile admin up -d

# PostgreSQL Admin: http://localhost:5050
# Redis Commander: http://localhost:8081
```

## 🚀 Production Deployment

### **Environment Variables**
```bash
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db/devmind
REDIS_URL=redis://prod-redis:6379
SECRET_KEY=your-super-secure-secret-key
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### **Docker Production**
```bash
# Build production image
docker build -t devmind-backend .

# Run with production config
docker run -d \
  --name devmind-backend \
  -p 8000:8000 \
  --env-file .env.production \
  devmind-backend
```

## 🏆 Hackathon Demo Script

### **1. Opening (30 seconds)**
- Show frontend loading with neural command center design
- Highlight the unique glassmorphism and bento grid layout

### **2. The Problem (30 seconds)**
- "Sarah joins the team, asks: 'Why Redis over PostgreSQL for caching?'"
- Show traditional workflow: searching emails, Slack, docs

### **3. The Magic (60 seconds)**
- Submit query in DevMind interface
- Show real-time MCP tool activation (GitHub, Slack, Jira)
- Watch context assembly and AI response generation
- Display comprehensive answer with full decision context

### **4. Technical Deep Dive (60 seconds)**
- Show MCP protocol in action via API docs
- Demonstrate WebSocket real-time updates
- Highlight vector search and knowledge graph
- Show live insights and system status

### **5. Impact Statement (30 seconds)**
- "From weeks of onboarding to minutes of context"
- "Never lose tribal knowledge again"
- "AI-powered development intelligence"

## 📞 Support & Development

### **Common Issues**

**Port Already in Use**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Database Connection Issues**
```bash
# Reset Docker volumes
docker-compose down -v
docker-compose up -d postgres redis
```

**Missing Dependencies**
```bash
# Reinstall with specific versions
pip install -r requirements.txt --force-reinstall
```

### **Development Mode**
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

This backend provides a production-ready, technically impressive foundation that showcases:

✅ **Advanced Architecture** - MCP protocol, vector search, real-time updates  
✅ **Real-world Problem** - Solves $billion context switching problem  
✅ **Technical Depth** - Complex multi-modal data fusion with LLMs  
✅ **Demo Magic** - Instant context retrieval that wows judges  
✅ **Scalable Design** - Production-ready with proper error handling  