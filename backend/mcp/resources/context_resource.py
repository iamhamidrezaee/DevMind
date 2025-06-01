"""
Context Resource for MCP Server
Provides access to development context data
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ContextResource:
    """Context resource for MCP protocol"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Execute context resource operations"""
        try:
            if tool_name == "context_search":
                return await self._search_context(arguments)
            elif tool_name == "context_get_decisions":
                return await self._get_decisions(arguments)
            elif tool_name == "context_get_timeline":
                return await self._get_timeline(arguments)
            else:
                return MCPToolResult(
                    success=False,
                    content="",
                    error=f"Unknown context resource operation: {tool_name}"
                )
        except Exception as e:
            logger.error(f"Context resource execution failed: {e}")
            return MCPToolResult(
                success=False,
                content="",
                error=str(e)
            )

    async def search_context(self, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Search through development context"""
        args = arguments or {}
        query = args.get("query", "")
        project_id = args.get("project_id")
        time_range = args.get("time_range", "30d")
        limit = args.get("limit", 20)
        
        # Mock context search results
        context_data = {
            "query": query,
            "results": [
                {
                    "id": "ctx_001",
                    "source": "github",
                    "type": "commit",
                    "title": "Fix authentication service JWT validation",
                    "content": "Resolved issue where JWT tokens with special characters in usernames were not properly validated",
                    "author": "john_doe",
                    "timestamp": datetime.utcnow() - timedelta(hours=2),
                    "relevance_score": 0.95
                },
                {
                    "id": "ctx_002", 
                    "source": "slack",
                    "type": "discussion",
                    "title": "Redis vs PostgreSQL caching decision",
                    "content": "Team discussion concluded Redis provides better performance for caching needs",
                    "author": "sarah_smith",
                    "timestamp": datetime.utcnow() - timedelta(days=7),
                    "relevance_score": 0.88
                },
                {
                    "id": "ctx_003",
                    "source": "jira",
                    "type": "issue",
                    "title": "API Rate Limiting Implementation",
                    "content": "Implement distributed rate limiting using Redis clusters",
                    "author": "mike_wilson",
                    "timestamp": datetime.utcnow() - timedelta(days=14),
                    "relevance_score": 0.82
                }
            ],
            "total_count": 3,
            "search_time": "0.15s"
        }
        
        return json.dumps(context_data, default=str, indent=2)

    async def get_decisions(self, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Get architectural decisions"""
        args = arguments or {}
        topic = args.get("topic", "")
        project_id = args.get("project_id")
        
        # Mock architectural decisions
        decisions_data = {
            "topic": topic,
            "decisions": [
                {
                    "id": "dec_001",
                    "title": "Database Technology Choice",
                    "decision": "Use PostgreSQL as primary database",
                    "rationale": "ACID compliance, performance, and ecosystem support",
                    "alternatives": ["MySQL", "MongoDB"],
                    "consequences": ["Need PostgreSQL expertise", "Better data consistency"],
                    "status": "active",
                    "date": datetime.utcnow() - timedelta(days=90),
                    "stakeholders": ["sarah_smith", "mike_wilson", "john_doe"]
                },
                {
                    "id": "dec_002",
                    "title": "Caching Strategy",
                    "decision": "Implement Redis for application caching",
                    "rationale": "High performance in-memory caching with good scalability",
                    "alternatives": ["Memcached", "Application-level caching"],
                    "consequences": ["Additional infrastructure", "Improved response times"],
                    "status": "active",
                    "date": datetime.utcnow() - timedelta(days=7),
                    "stakeholders": ["sarah_smith", "mike_wilson"]
                },
                {
                    "id": "dec_003",
                    "title": "Authentication Method",
                    "decision": "Use JWT tokens for API authentication",
                    "rationale": "Stateless, scalable, and widely supported",
                    "alternatives": ["Session-based auth", "OAuth only"],
                    "consequences": ["Token management complexity", "Better scalability"],
                    "status": "active",
                    "date": datetime.utcnow() - timedelta(days=120),
                    "stakeholders": ["john_doe", "alice_johnson"]
                }
            ],
            "total_count": 3
        }
        
        return json.dumps(decisions_data, default=str, indent=2)

    async def get_timeline(self, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Get project timeline"""
        args = arguments or {}
        project_id = args.get("project_id")
        time_range = args.get("time_range", "30d")
        
        # Parse time range
        if time_range.endswith('d'):
            days = int(time_range[:-1])
        else:
            days = 30
        
        # Mock timeline events
        timeline_data = {
            "project_id": project_id,
            "time_range": time_range,
            "events": [
                {
                    "id": "evt_001",
                    "timestamp": datetime.utcnow() - timedelta(hours=2),
                    "type": "commit",
                    "source": "github",
                    "title": "Fix authentication bug in JWT validation",
                    "description": "Resolved special character handling in usernames",
                    "author": "john_doe",
                    "impact": "high",
                    "url": "https://github.com/example/repo/commit/abc123"
                },
                {
                    "id": "evt_002",
                    "timestamp": datetime.utcnow() - timedelta(hours=6),
                    "type": "deployment",
                    "source": "github",
                    "title": "Production deployment v2.1.4",
                    "description": "Deployed authentication fixes and performance improvements",
                    "author": "deploy_bot",
                    "impact": "medium",
                    "url": "https://github.com/example/repo/releases/tag/v2.1.4"
                },
                {
                    "id": "evt_003",
                    "timestamp": datetime.utcnow() - timedelta(days=1),
                    "type": "issue_created",
                    "source": "jira",
                    "title": "Performance optimization for API endpoints",
                    "description": "Investigate and implement caching for frequently accessed endpoints",
                    "author": "sarah_smith",
                    "impact": "medium",
                    "url": "https://jira.example.com/PROJ-129"
                },
                {
                    "id": "evt_004",
                    "timestamp": datetime.utcnow() - timedelta(days=7),
                    "type": "decision",
                    "source": "slack",
                    "title": "Redis caching architecture decision",
                    "description": "Team decided to use Redis for distributed caching",
                    "author": "sarah_smith",
                    "impact": "high",
                    "url": "https://slack.com/channels/tech-discussions"
                },
                {
                    "id": "evt_005",
                    "timestamp": datetime.utcnow() - timedelta(days=14),
                    "type": "issue_created",
                    "source": "jira",
                    "title": "API Rate Limiting Implementation",
                    "description": "Implement rate limiting for public API endpoints",
                    "author": "mike_wilson",
                    "impact": "high",
                    "url": "https://jira.example.com/PROJ-123"
                }
            ],
            "total_events": 5,
            "generated_at": datetime.utcnow()
        }
        
        return json.dumps(timeline_data, default=str, indent=2)

    async def get_live_insights(self, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Get live insights from recent activity"""
        args = arguments or {}
        project_id = args.get("project_id")
        limit = args.get("limit", 10)
        
        # Mock live insights
        insights_data = {
            "project_id": project_id,
            "insights": [
                {
                    "id": "insight_001",
                    "type": "critical_issue",
                    "title": "Authentication Service Alert",
                    "description": "High number of authentication failures detected",
                    "severity": "high",
                    "source": "github",
                    "timestamp": datetime.utcnow() - timedelta(minutes=30),
                    "affected_components": ["authentication", "api"],
                    "recommended_actions": [
                        "Review recent authentication changes",
                        "Check error logs for patterns",
                        "Monitor user impact"
                    ],
                    "status": "resolved"
                },
                {
                    "id": "insight_002",
                    "type": "performance_trend",
                    "title": "API Response Time Improvement",
                    "description": "Average response time decreased by 25% after Redis implementation",
                    "severity": "low",
                    "source": "monitoring",
                    "timestamp": datetime.utcnow() - timedelta(hours=4),
                    "metrics": {
                        "avg_response_time": "120ms",
                        "improvement": "25%",
                        "affected_endpoints": 15
                    },
                    "status": "active"
                },
                {
                    "id": "insight_003",
                    "type": "team_activity",
                    "title": "High Development Velocity",
                    "description": "Team completed 8 issues this week, 20% above average",
                    "severity": "low",
                    "source": "jira",
                    "timestamp": datetime.utcnow() - timedelta(hours=8),
                    "metrics": {
                        "issues_completed": 8,
                        "average_completion": 6.5,
                        "velocity_increase": "20%"
                    },
                    "status": "active"
                }
            ],
            "total_insights": 3,
            "generated_at": datetime.utcnow()
        }
        
        return json.dumps(insights_data, default=str, indent=2)

    async def _search_context(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Internal search context method"""
        result = await self.search_context(arguments)
        return MCPToolResult(
            success=True,
            content=result,
            metadata={"operation": "context_search"}
        )

    async def _get_decisions(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Internal get decisions method"""
        result = await self.get_decisions(arguments)
        return MCPToolResult(
            success=True,
            content=result,
            metadata={"operation": "get_decisions"}
        )

    async def _get_timeline(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Internal get timeline method"""
        result = await self.get_timeline(arguments)
        return MCPToolResult(
            success=True,
            content=result,
            metadata={"operation": "get_timeline"}
        )

    async def cleanup(self):
        """Cleanup resources"""
        self.cache.clear()
        logger.info("✅ Context resource cleaned up")

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key].get("timestamp", 0)
        return (datetime.utcnow().timestamp() - cached_time) < self.cache_ttl

    def _set_cache(self, key: str, data: Any):
        """Set cache entry with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.utcnow().timestamp()
        }

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cache entry if valid"""
        if self._is_cache_valid(key):
            return self.cache[key]["data"]
        return None

# Import MCPToolResult from parent module
from mcp.server import MCPToolResult