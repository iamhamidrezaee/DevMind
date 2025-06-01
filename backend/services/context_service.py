"""
Context Service - Core business logic for DevMind
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from models.database import Project, ContextEntry, Decision, Query, Integration
from models.schemas import (
    ProjectCreate, ProjectUpdate, IntegrationCreate,
    SourceType, QueryHistory, Insight, SystemStatus,
    ContextMatch, InsightType
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class ContextService:
    """Core service for handling development context"""
    
    def __init__(self):
        self.vector_service = VectorService()
        
    async def process_query(
        self,
        query_id: UUID,
        query_text: str,
        project_id: Optional[UUID] = None,
        context_limit: int = 10,
        include_sources: List[SourceType] = None
    ) -> Dict[str, Any]:
        """Process a context query and return AI-generated response"""
        
        # Search for relevant context
        context_matches = await self._search_context_entries(
            query_text=query_text,
            project_id=project_id,
            limit=context_limit,
            include_sources=include_sources or list(SourceType)
        )
        
        # Get relevant decisions
        decisions = await self._search_decisions(
            query_text=query_text,
            project_id=project_id,
            limit=5
        )
        
        # Generate AI response (mock for now)
        response = await self._generate_ai_response(
            query_text=query_text,
            context_matches=context_matches,
            decisions=decisions
        )
        
        sources_used = list(set(match["source"] for match in context_matches))
        
        return {
            "answer": response,
            "context_matches": [self._format_context_match(match) for match in context_matches],
            "sources_used": sources_used,
            "confidence_score": self._calculate_confidence(context_matches),
            "timestamp": datetime.utcnow()
        }

    async def _search_context_entries(
        self,
        query_text: str,
        project_id: Optional[UUID] = None,
        limit: int = 10,
        include_sources: List[SourceType] = None
    ) -> List[Dict[str, Any]]:
        """Search context entries using vector similarity"""
        
        # For demo purposes, return mock data
        # In production, this would use vector similarity search
        mock_entries = [
            {
                "id": "entry1",
                "source": "github",
                "entry_type": "commit",
                "title": "Fix authentication bug in login service",
                "content": "Resolved issue where JWT tokens were not properly validated, causing authentication failures for users with special characters in usernames.",
                "author": "john_doe",
                "timestamp": datetime.utcnow() - timedelta(hours=2),
                "url": "https://github.com/example/repo/commit/abc123",
                "score": 0.95
            },
            {
                "id": "entry2",
                "source": "slack",
                "entry_type": "message",
                "title": "Discussion about Redis vs PostgreSQL for caching",
                "content": "Team discussion concluded that Redis provides better performance for our caching needs. Decision made to migrate from PostgreSQL-based caching to Redis cluster.",
                "author": "sarah_smith",
                "timestamp": datetime.utcnow() - timedelta(days=7),
                "url": "https://slack.com/channel/tech-discussions",
                "score": 0.88
            },
            {
                "id": "entry3",
                "source": "jira",
                "entry_type": "issue",
                "title": "API Rate Limiting Implementation",
                "content": "Implement rate limiting for public API endpoints to prevent abuse. Use Redis for distributed rate limiting across multiple server instances.",
                "author": "mike_wilson",
                "timestamp": datetime.utcnow() - timedelta(days=14),
                "url": "https://jira.example.com/PROJ-123",
                "score": 0.82
            }
        ]
        
        # Filter by query relevance (simple keyword matching for demo)
        relevant_entries = []
        query_words = query_text.lower().split()
        
        for entry in mock_entries:
            content_words = (entry["content"] + " " + entry["title"]).lower()
            relevance = sum(1 for word in query_words if word in content_words)
            
            if relevance > 0:
                entry["score"] = min(0.95, entry["score"] * (relevance / len(query_words)))
                relevant_entries.append(entry)
        
        # Sort by score and return top results
        relevant_entries.sort(key=lambda x: x["score"], reverse=True)
        return relevant_entries[:limit]

    async def _search_decisions(
        self,
        query_text: str,
        project_id: Optional[UUID] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search architectural decisions"""
        
        # Mock decisions for demo
        mock_decisions = [
            {
                "id": "decision1",
                "title": "Database Technology Choice",
                "decision": "Use PostgreSQL as primary database",
                "rationale": "PostgreSQL provides ACID compliance, excellent performance, and strong ecosystem support for our use case.",
                "alternatives": ["MySQL", "MongoDB"],
                "consequences": ["Need PostgreSQL expertise", "Better data consistency"],
                "timestamp": datetime.utcnow() - timedelta(days=30)
            },
            {
                "id": "decision2", 
                "title": "Caching Strategy",
                "decision": "Implement Redis for application caching",
                "rationale": "Redis provides high performance in-memory caching with good scalability options.",
                "alternatives": ["Memcached", "Application-level caching"],
                "consequences": ["Additional infrastructure complexity", "Improved response times"],
                "timestamp": datetime.utcnow() - timedelta(days=7)
            }
        ]
        
        # Simple relevance filtering
        query_words = query_text.lower().split()
        relevant_decisions = []
        
        for decision in mock_decisions:
            content = (decision["title"] + " " + decision["decision"] + " " + decision["rationale"]).lower()
            relevance = sum(1 for word in query_words if word in content)
            
            if relevance > 0:
                relevant_decisions.append(decision)
        
        return relevant_decisions[:limit]

    async def _generate_ai_response(
        self,
        query_text: str,
        context_matches: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]]
    ) -> str:
        """Generate AI response based on context (mock implementation)"""
        
        # In production, this would use OpenAI/Anthropic API
        # For demo, return a contextual response
        
        if "redis" in query_text.lower() and "postgresql" in query_text.lower():
            return """Based on your team's recent discussions and decisions:

**Why Redis was chosen over PostgreSQL for caching:**

Your team made this decision 7 days ago after a thorough discussion in the #tech-discussions Slack channel. Here are the key factors:

1. **Performance**: Redis provides significantly better performance for caching operations due to its in-memory architecture
2. **Scalability**: Redis clustering allows for horizontal scaling of cache operations
3. **Use Case Fit**: For your specific caching needs, Redis's data structures (strings, hashes, sets) are more appropriate than PostgreSQL's relational model

**Implementation Details:**
- The team is implementing distributed rate limiting using Redis clusters
- This aligns with the recent API Rate Limiting project (PROJ-123) that Mike Wilson is working on
- The migration is part of the broader performance optimization initiative

**Context Sources:**
- Slack discussion in #tech-discussions (Sarah Smith led the conversation)
- Related Jira ticket PROJ-123 for API rate limiting
- Recent commits show Redis integration work

This decision supports your overall architecture goals of improving API performance and scalability."""

        elif "authentication" in query_text.lower() or "login" in query_text.lower():
            return """**Recent Authentication System Updates:**

Based on recent activity, here's what's happening with your authentication system:

**Latest Fix (2 hours ago):**
John Doe just resolved a critical authentication bug where JWT tokens weren't properly validating usernames with special characters. This was causing login failures for certain users.

**Current Implementation:**
- JWT-based authentication system
- Token validation improvements just deployed
- Focus on handling edge cases in username formats

**Recent Issues Addressed:**
- Special character handling in usernames
- Token validation logic improvements
- Enhanced error handling for authentication failures

The fix has been deployed and should resolve the login issues some users were experiencing."""

        else:
            # Generic response based on available context
            if context_matches:
                context_summary = "\n".join([
                    f"- {match['title']} (from {match['source']})"
                    for match in context_matches[:3]
                ])
                
                return f"""Based on your recent development activity, here's what I found:

**Recent Context:**
{context_summary}

**Key Information:**
{context_matches[0]['content'][:300]}...

This information comes from your connected tools (GitHub, Slack, Jira) and should help answer your question. Would you like me to dive deeper into any specific aspect?"""
            else:
                return "I couldn't find specific context related to your question. This might be because the relevant information hasn't been synced yet, or you might need to rephrase your question. Try asking about specific technologies, recent changes, or team decisions."

    def _format_context_match(self, match: Dict[str, Any]) -> ContextMatch:
        """Format context match for API response"""
        return ContextMatch(
            entry_id=match["id"],
            score=match["score"],
            source=match["source"],
            entry_type=match["entry_type"],
            title=match["title"],
            content=match["content"][:500] + "..." if len(match["content"]) > 500 else match["content"],
            author=match["author"],
            timestamp=match["timestamp"],
            url=match["url"]
        )

    def _calculate_confidence(self, context_matches: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on context quality"""
        if not context_matches:
            return 0.0
        
        # Simple confidence calculation based on top matches
        top_scores = [match["score"] for match in context_matches[:3]]
        return sum(top_scores) / len(top_scores)

    # Project management methods
    async def list_projects(self, db: AsyncSession) -> List[Project]:
        """List all projects"""
        # Mock data for demo
        return []

    async def create_project(self, db: AsyncSession, project: ProjectCreate) -> Project:
        """Create a new project"""
        # Mock implementation
        from uuid import uuid4
        return Project(
            id=uuid4(),
            name=project.name,
            description=project.description,
            repository_url=project.repository_url,
            slack_channel=project.slack_channel,
            jira_project_key=project.jira_project_key,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
            is_active=True
        )

    async def get_project(self, db: AsyncSession, project_id: UUID) -> Optional[Project]:
        """Get project by ID"""
        # Mock implementation
        return None

    async def update_project(self, db: AsyncSession, project_id: UUID, project_update: ProjectUpdate) -> Optional[Project]:
        """Update project"""
        # Mock implementation
        return None

    # Integration methods
    async def list_integrations(self, db: AsyncSession, project_id: Optional[UUID] = None) -> List[Integration]:
        """List integrations"""
        # Mock data for demo
        return []

    async def create_integration(self, db: AsyncSession, integration: IntegrationCreate) -> Integration:
        """Create integration"""
        # Mock implementation
        from uuid import uuid4
        return Integration(
            id=uuid4(),
            project_id=integration.project_id,
            integration_type=integration.integration_type,
            is_active=True,
            last_sync=None,
            sync_status="pending",
            error_message=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def get_integration(self, db: AsyncSession, integration_id: UUID) -> Optional[Integration]:
        """Get integration by ID"""
        # Mock implementation
        return None

    async def sync_integration(self, integration_id: UUID):
        """Sync integration data"""
        # Mock implementation
        logger.info(f"Syncing integration {integration_id}")

    # Insights and system status
    async def get_live_insights(self, project_id: Optional[UUID] = None, limit: int = 10) -> List[Insight]:
        """Get live insights"""
        # Mock insights for demo
        from uuid import uuid4
        
        mock_insights = [
            Insight(
                id=uuid4(),
                type=InsightType.CRITICAL_ISSUE,
                title="Critical Bug in Authentication Service",
                description="Authentication failures detected for users with special characters in usernames",
                source=SourceType.GITHUB,
                priority="high",
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                url="https://github.com/example/repo/issues/123",
                metadata={"affected_users": 15, "fix_status": "resolved"}
            ),
            Insight(
                id=uuid4(),
                type=InsightType.TEAM_MENTION,
                title="Team standup scheduled for 10:00 AM",
                description="Daily standup meeting reminder in #general channel",
                source=SourceType.SLACK,
                priority="medium",
                timestamp=datetime.utcnow() - timedelta(minutes=45),
                url="https://slack.com/channel/general",
                metadata={"channel": "general", "attendees": 8}
            ),
            Insight(
                id=uuid4(),
                type=InsightType.DEPLOYMENT,
                title="API rate limit optimization completed",
                description="Rate limiting implementation deployed to production",
                source=SourceType.JIRA,
                priority="low",
                timestamp=datetime.utcnow() - timedelta(hours=2),
                url="https://jira.example.com/PROJ-124",
                metadata={"deployment_status": "success", "performance_improvement": "25%"}
            )
        ]
        
        return mock_insights[:limit]

    async def get_system_status(self) -> SystemStatus:
        """Get system status"""
        return SystemStatus(
            mcp_connections=3,
            active_integrations=3,
            context_freshness="Real-time",
            avg_query_time=1.2,
            last_sync=datetime.utcnow() - timedelta(minutes=5),
            health_status="healthy"
        )

    async def check_integrations(self) -> Dict[str, str]:
        """Check integration status"""
        return {
            "github": "healthy",
            "slack": "healthy", 
            "jira": "healthy"
        }

    # Query history methods
    async def get_query_history(
        self,
        db: AsyncSession,
        project_id: Optional[UUID] = None,
        limit: int = 20
    ) -> List[QueryHistory]:
        """Get query history"""
        # Mock implementation
        from uuid import uuid4
        
        mock_queries = [
            QueryHistory(
                id=uuid4(),
                query_text="What's the status of the user authentication refactor?",
                confidence_score=0.92,
                execution_time=1.4,
                created_at=datetime.utcnow() - timedelta(hours=1),
                project_id=project_id
            ),
            QueryHistory(
                id=uuid4(),
                query_text="Show me recent deployment issues",
                confidence_score=0.88,
                execution_time=0.9,
                created_at=datetime.utcnow() - timedelta(hours=3),
                project_id=project_id
            ),
            QueryHistory(
                id=uuid4(),
                query_text="Summarize today's team discussions",
                confidence_score=0.85,
                execution_time=2.1,
                created_at=datetime.utcnow() - timedelta(hours=5),
                project_id=project_id
            )
        ]
        
        return mock_queries[:limit]

    async def store_query(
        self,
        db: AsyncSession,
        query_id: UUID,
        query_text: str,
        project_id: Optional[UUID],
        response: Dict[str, Any],
        execution_time: float
    ):
        """Store query in history"""
        # Mock implementation
        logger.info(f"Storing query {query_id}: {query_text[:50]}...")

    # Additional helper methods
    async def search_context(
        self,
        query: str,
        project_id: Optional[UUID] = None,
        sources: List[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search context (public API method)"""
        context_matches = await self._search_context_entries(
            query_text=query,
            project_id=project_id,
            limit=limit,
            include_sources=[SourceType(s) for s in (sources or [])]
        )
        
        return {
            "query": query,
            "matches": [self._format_context_match(match) for match in context_matches],
            "total_count": len(context_matches)
        }

    async def get_project_timeline(
        self,
        project_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get project timeline"""
        # Mock timeline data
        timeline_events = [
            {
                "date": datetime.utcnow() - timedelta(hours=2),
                "type": "commit",
                "title": "Fix authentication bug",
                "author": "john_doe",
                "source": "github"
            },
            {
                "date": datetime.utcnow() - timedelta(days=1),
                "type": "deployment",
                "title": "Production deployment v2.1.4",
                "author": "deploy_bot",
                "source": "github"
            },
            {
                "date": datetime.utcnow() - timedelta(days=7),
                "type": "decision",
                "title": "Redis vs PostgreSQL for caching",
                "author": "sarah_smith",
                "source": "slack"
            }
        ]
        
        return {
            "project_id": project_id,
            "time_range": f"{days} days",
            "events": timeline_events
        }