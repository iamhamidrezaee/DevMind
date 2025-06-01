# 🧠 DevMind - Simplified Hackathon Version

**AI-Powered Development Context Oracle with Claude Sonnet 4 & MCP**

This is a streamlined, hackathon-ready version of DevMind that showcases agentic AI capabilities using Claude Sonnet 4 with Model Context Protocol (MCP) integration.

## 🚀 Quick Start (30 seconds!)

### 1. Backend Setup
```bash
cd simplified_backend
python setup.py
python main.py
```

### 2. Frontend Setup
- Open `simplified_frontend/index.html` in your browser
- Enter your Anthropic API key when prompted
- Start asking questions!

## 🎯 What This Demo Does

DevMind is an **agentic AI assistant** that:

1. **🔍 Searches Development Context**: Uses MCP-style tools to search across GitHub, Slack, Jira, and documentation
2. **🧠 AI Analysis**: Leverages Claude Sonnet 4 to analyze and connect information across sources
3. **📊 Provides Insights**: Gives actionable insights and identifies patterns in your development workflow
4. **⚡ Real-time Updates**: WebSocket support for live query results

## 🛠️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │ Claude Sonnet 4 │
│   (HTML/JS)     │◄──►│   (FastAPI)     │◄──►│   (Agentic AI)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                        ┌───────▼────────┐    ┌────────▼────────┐
                        │  MCP Tools     │    │   Mock Data     │
                        │  (Simplified)  │    │  (GitHub/Slack/ │
                        └────────────────┘    │      Jira)      │
                                              └─────────────────┘
```

## 💡 Try These Queries

- "What authentication issues are we facing?"
- "Show me recent GitHub activity"  
- "What decisions were made about user sessions?"
- "Summarize all context about login problems"

## 🔧 Key Features for Hackathon

✅ **Claude Sonnet 4 Integration**: Latest AI model for intelligent analysis  
✅ **MCP-Style Tools**: Simulated integrations with development tools  
✅ **Mock Data**: Rich, realistic development context data  
✅ **Clean UI**: Beautiful, responsive frontend  
✅ **Real-time**: WebSocket support for live updates  
✅ **Agentic Behavior**: AI that takes actions and provides transparency  

## 📁 Project Structure

```
DevMind/
├── simplified_backend/
│   ├── main.py              # Main FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── setup.py            # Automated setup script
├── simplified_frontend/
│   └── index.html          # Complete frontend application
└── HACKATHON_README.md     # This file
```

## 🔑 API Key Setup

1. Get your Anthropic API key from: https://console.anthropic.com/
2. Enter it in the frontend interface (stored locally only)
3. Start querying!

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Example API Query
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What authentication issues are we facing?",
    "context_sources": ["github", "slack", "jira"]
  }'
```

### Mock Data Endpoint
```bash
curl http://localhost:8000/api/mock-data
```

## 🏆 Hackathon Highlights

1. **Agentic AI**: Claude Sonnet 4 acts autonomously to search, analyze, and provide insights
2. **MCP Integration**: Demonstrates Model Context Protocol concepts with tool usage
3. **Cross-Tool Intelligence**: Connects information across GitHub, Slack, and Jira
4. **Developer-Focused**: Solves real problems developers face with context switching
5. **Production-Ready Concepts**: Scales to real integrations and enterprise use

## 🐛 Troubleshooting

**Backend won't start?**
- Ensure Python 3.8+ is installed
- Run `python setup.py` to install dependencies
- Check the console for error messages

**Frontend can't connect?**
- Make sure backend is running on localhost:8000
- Check browser console for errors
- Ensure CORS is working (should be automatic)

**API key issues?**
- Get a valid Anthropic API key
- Ensure it starts with `sk-ant-`
- Check the format in the console

## 🎨 Customization

**Add New Mock Data**: Edit the `MOCK_CONTEXT_DATA` list in `main.py`

**Modify AI Behavior**: Update the system prompt in the `DevMindAgent` class

**Add New Sources**: Extend the `SimpleMCPTools` class with new search methods

## 📈 Next Steps

This simplified version demonstrates the core concepts. For production:

1. **Real Integrations**: Replace mock tools with actual GitHub/Slack/Jira APIs
2. **Vector Search**: Add proper semantic search with embeddings
3. **Database**: Implement PostgreSQL with pgvector for persistence  
4. **Authentication**: Add proper API key management and user auth
5. **Scaling**: Add Redis caching and async processing

---

**Built for the MCP Hackathon 2024** 🏆  
*Showcasing the future of agentic AI in development workflows*
