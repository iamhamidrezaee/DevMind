"""
DevMind - Simplified Agentic Application with MCP & Claude Sonnet 4
A clean, hackathon-ready implementation focusing on core functionality
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
from anthropic import Anthropic
from urllib.parse import parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DevMind - AI Development Context Oracle",
    description="Agentic application using Claude Sonnet 4 with MCP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon - in production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
claude_client: Optional[Anthropic] = None
connected_websockets: List[WebSocket] = []

# Data models
class QueryRequest(BaseModel):
    query: str
    context_sources: List[str] = ["github", "slack", "jira"]
    use_agent: bool = True

class QueryResponse(BaseModel):
    query_id: str
    response: str
    context_used: List[Dict[str, Any]]
    agent_actions: List[Dict[str, Any]]
    timestamp: str

class ContextItem(BaseModel):
    id: str
    source: str
    type: str
    title: str
    content: str
    author: str
    timestamp: str
    url: Optional[str] = None
    score: float = 0.0

# Mock data for demonstration
MOCK_CONTEXT_DATA = [
    {
        "id": "gh_001",
        "source": "github",
        "type": "commit",
        "title": "Fix authentication bug in user login",
        "content": "Fixed issue where JWT tokens weren't being properly validated. Added proper error handling and updated tests.",
        "author": "john_dev",
        "timestamp": "2024-06-01T10:30:00Z",
        "url": "https://github.com/team/repo/commit/abc123",
        "score": 0.95
    },
    {
        "id": "sl_001", 
        "source": "slack",
        "type": "message",
        "title": "Authentication issue discussion",
        "content": "Hey team, we're seeing some users getting logged out unexpectedly. Looks like it might be related to the JWT validation logic. Can someone take a look?",
        "author": "sarah_pm",
        "timestamp": "2024-06-01T09:15:00Z",
        "url": "https://team.slack.com/messages/C123/p1234567890",
        "score": 0.88
    },
    {
        "id": "jira_001",
        "source": "jira", 
        "type": "ticket",
        "title": "BUG-123: Users getting logged out randomly",
        "content": "Multiple users report being logged out of the application without warning. This seems to happen after about 30 minutes of activity. Priority: High",
        "author": "qa_tester",
        "timestamp": "2024-05-31T16:45:00Z",
        "url": "https://team.atlassian.net/browse/BUG-123",
        "score": 0.92
    },
    {
        "id": "gh_002",
        "source": "github",
        "type": "pr",
        "title": "Add user session management improvements",
        "content": "This PR improves session handling by implementing proper token refresh logic and adding session persistence across browser refreshes.",
        "author": "alice_senior",
        "timestamp": "2024-06-01T14:20:00Z", 
        "url": "https://github.com/team/repo/pull/456",
        "score": 0.85
    },
    {
        "id": "confluence_001",
        "source": "confluence",
        "type": "doc",
        "title": "Authentication Architecture Documentation",
        "content": "Our authentication system uses JWT tokens with a 60-minute expiry. Tokens are stored in HTTP-only cookies for security. The refresh logic handles token renewal automatically.",
        "author": "tech_lead",
        "timestamp": "2024-05-25T11:00:00Z",
        "url": "https://team.atlassian.net/wiki/spaces/TECH/pages/123",
        "score": 0.78
    }
]

# MCP Tool implementations (simplified for hackathon)
class SimpleMCPTools:
    """Simplified MCP tools for hackathon demonstration"""
    
    @staticmethod
    async def github_search(query: str) -> List[Dict[str, Any]]:
        """Simulate GitHub search"""
        results = [item for item in MOCK_CONTEXT_DATA if item["source"] == "github"]
        # Simple keyword matching for demo
        if query.lower() in " ".join([item["title"] + " " + item["content"] for item in results]).lower():
            return results
        return []
    
    @staticmethod
    async def slack_search(query: str) -> List[Dict[str, Any]]:
        """Simulate Slack search"""
        results = [item for item in MOCK_CONTEXT_DATA if item["source"] == "slack"]
        return results
    
    @staticmethod
    async def jira_search(query: str) -> List[Dict[str, Any]]:
        """Simulate Jira search"""
        results = [item for item in MOCK_CONTEXT_DATA if item["source"] == "jira"]
        return results
    
    @staticmethod
    async def search_all_sources(query: str) -> List[Dict[str, Any]]:
        """Search across all sources"""
        all_results = []
        all_results.extend(await SimpleMCPTools.github_search(query))
        all_results.extend(await SimpleMCPTools.slack_search(query))
        all_results.extend(await SimpleMCPTools.jira_search(query))
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:10]  # Return top 10 results

# Claude Sonnet 4 Agent
class DevMindAgent:
    """AI Agent powered by Claude Sonnet 4"""
    
    def __init__(self, anthropic_client: Anthropic):
        self.client = anthropic_client
        self.mcp_tools = SimpleMCPTools()
    
    async def process_query(self, query: str, context_sources: List[str] = None) -> Dict[str, Any]:
        """Process user query using Claude Sonnet 4 with MCP context"""
        
        # Step 1: Gather context using MCP tools
        context_items = await self.mcp_tools.search_all_sources(query)
        
        # Step 2: Prepare context for Claude
        context_text = self._format_context_for_claude(context_items)
        
        # Step 3: Create the prompt for Claude Sonnet 4
        system_prompt = """You are DevMind, an AI development context oracle. You help developers understand their codebase, track decisions, and solve problems by analyzing development context from GitHub, Slack, Jira, and documentation.

Your capabilities:
- Analyze code commits, PRs, and issues
- Understand team discussions and decisions
- Connect related issues across different tools
- Provide actionable insights and recommendations

Be concise, helpful, and focus on actionable insights. When referencing specific items, mention the source (GitHub, Slack, Jira, etc.)."""

        user_prompt = f"""Query: {query}

Relevant Development Context:
{context_text}

Please analyze this context and provide a helpful response that:
1. Directly answers the user's query
2. Highlights the most relevant information from the context
3. Identifies any patterns or connections across sources
4. Provides actionable next steps if applicable

Response:"""

        try:
            # Call Claude Sonnet 4
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Latest Claude Sonnet
                max_tokens=1500,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            agent_response = response.content[0].text
            
            # Step 4: Track agent actions for transparency
            agent_actions = [
                {
                    "action": "mcp_search",
                    "details": f"Searched {len(context_sources or ['all'])} sources",
                    "results_count": len(context_items)
                },
                {
                    "action": "claude_analysis", 
                    "details": "Analyzed context with Claude Sonnet 4",
                    "model": "claude-3-5-sonnet-20241022"
                }
            ]
            
            return {
                "response": agent_response,
                "context_used": context_items,
                "agent_actions": agent_actions,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query with Claude: {e}")
            return {
                "response": f"I encountered an error while processing your query: {str(e)}",
                "context_used": context_items,
                "agent_actions": [],
                "success": False
            }
    
    def _format_context_for_claude(self, context_items: List[Dict[str, Any]]) -> str:
        """Format context items for Claude consumption"""
        if not context_items:
            return "No relevant context found."
        
        formatted_context = []
        for item in context_items:
            context_piece = f"""
SOURCE: {item['source'].upper()} - {item['type']}
TITLE: {item['title']}
AUTHOR: {item['author']}
TIMESTAMP: {item['timestamp']}
CONTENT: {item['content']}
RELEVANCE: {item['score']:.2f}
---"""
            formatted_context.append(context_piece)
        
        return "\n".join(formatted_context)

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global claude_client
    
    logger.info("🚀 Starting DevMind Simplified Backend...")
    
    # Initialize Claude client (will be set via environment or config)
    # For now, we'll handle this in the query endpoint
    logger.info("✅ DevMind Backend ready for hackathon!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "DevMind AI Context Oracle",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "api": "running",
            "claude_integration": "ready",
            "mcp_tools": "active",
            "mock_data": f"{len(MOCK_CONTEXT_DATA)} items loaded"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/query", response_model=QueryResponse)
async def query_context(query_request: QueryRequest, request: Request):
    """Main query endpoint - processes user queries with AI agent"""
    
    # Handle API key from query parameter (for frontend compatibility)
    query_params = parse_qs(request.url.query)
    anthropic_api_key = query_params.get("anthropic_api_key", [None])[0]
    
    # Initialize Claude client if API key provided
    if anthropic_api_key:
        global claude_client
        claude_client = Anthropic(api_key=anthropic_api_key)
    
    if not claude_client:
        raise HTTPException(
            status_code=400, 
            detail="Anthropic API key required. Please provide it as a query parameter: ?anthropic_api_key=your_key"
        )
    
    try:
        # Create agent and process query
        agent = DevMindAgent(claude_client)
        result = await agent.process_query(query_request.query, query_request.context_sources)
        
        # Generate response
        query_id = f"q_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        response = QueryResponse(
            query_id=query_id,
            response=result["response"],
            context_used=result["context_used"],
            agent_actions=result["agent_actions"],
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Broadcast to WebSocket clients
        await broadcast_query_result(response.dict())
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/context/search")
async def search_context(q: str, sources: str = "all", limit: int = 10):
    """Search development context without AI analysis"""
    
    try:
        mcp_tools = SimpleMCPTools()
        results = await mcp_tools.search_all_sources(q)
        
        # Filter by sources if specified
        if sources != "all":
            source_list = sources.split(",")
            results = [r for r in results if r["source"] in source_list]
        
        return {
            "query": q,
            "results": results[:limit],
            "total_found": len(results),
            "sources_searched": sources
        }
        
    except Exception as e:
        logger.error(f"Error searching context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mock-data")
async def get_mock_data():
    """Get all mock data for frontend testing"""
    return {
        "total_items": len(MOCK_CONTEXT_DATA),
        "items": MOCK_CONTEXT_DATA,
        "sources": list(set(item["source"] for item in MOCK_CONTEXT_DATA))
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time query updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)

async def broadcast_query_result(result: Dict[str, Any]):
    """Broadcast query results to all connected WebSocket clients"""
    if connected_websockets:
        message = json.dumps({
            "type": "query_result",
            "data": result
        })
        
        # Send to all connected clients
        disconnected = []
        for websocket in connected_websockets:
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            connected_websockets.remove(ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
