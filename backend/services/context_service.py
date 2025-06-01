"""
Context Service - Core business logic for DevMind
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID # Ensure UUID is imported
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from models.database import Project, ContextEntry, Decision, Query, Integration
from models.schemas import (
    ProjectCreate, ProjectUpdate, IntegrationCreate,
    SourceType, QueryHistory, Insight, SystemStatus, # Ensure SourceType is imported
    ContextMatch, InsightType, EntryType # Ensure EntryType is imported
)
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class ContextService:
    """Core service for handling development context"""
    
    def __init__(self):
        self.vector_service = VectorService() # Assuming VectorService is defined elsewhere
        
    async def process_query(
        self,
        query_id: UUID,
        query_text: str,
        project_id: Optional[UUID] = None,
        context_limit: int = 10,
        include_sources: Optional[List[SourceType]] = None # Made Optional
    ) -> Dict[str, Any]:
        """Process a context query and return AI-generated response"""
        
        logger.info(f"Processing query '{query_text}' with ID {query_id}, project_id: {project_id}, limit: {context_limit}")
        
        # Ensure include_sources is a list of SourceType enum members if provided
        processed_include_sources = []
        if include_sources:
            for src_str in include_sources:
                try:
                    processed_include_sources.append(SourceType(src_str))
                except ValueError:
                    logger.warning(f"Invalid source type string '{src_str}' received. Ignoring.")
        if not processed_include_sources: # If empty or None after processing
             processed_include_sources = list(SourceType) # Default to all sources

        # Search for relevant context
        context_entries_found = await self._search_context_entries(
            query_text=query_text,
            project_id=project_id,
            limit=context_limit,
            include_sources=processed_include_sources
        )
        
        # Get relevant decisions
        decisions_found = await self._search_decisions(
            query_text=query_text,
            project_id=project_id,
            limit=5 # Arbitrary limit for decisions
        )
        
        # Generate AI response
        ai_answer = await self._generate_ai_response(
            query_text=query_text,
            context_matches=context_entries_found, # Pass the found entries
            decisions=decisions_found
        )
        
        # Format context matches for the response
        formatted_context_matches = [
            self._format_context_match(entry) for entry in context_entries_found
        ]
        
        sources_actually_used = list(set(match.source for match in formatted_context_matches if match.source))
        
        response_payload = {
            "answer": ai_answer,
            "context_matches": formatted_context_matches,
            "sources_used": sources_actually_used, # Use actual sources from matches
            "confidence_score": self._calculate_confidence(context_entries_found),
            "timestamp": datetime.utcnow()
        }
        logger.info(f"Query {query_id} processed. Answer: '{ai_answer[:50]}...', Matches: {len(formatted_context_matches)}")
        return response_payload

    async def _search_context_entries(
        self,
        query_text: str,
        project_id: Optional[UUID] = None,
        limit: int = 10,
        include_sources: Optional[List[SourceType]] = None # Use SourceType enum
    ) -> List[Dict[str, Any]]:
        """Search context entries using vector similarity (mocked with keyword search for demo)"""
        logger.info(f"Searching context for: '{query_text}' with limit {limit}, sources: {include_sources}")

        # Extended mock data for better demo
        mock_data_store = [
            {
                "id": UUID("11111111-1111-1111-1111-111111111111"), 
                "source": SourceType.GITHUB,
                "entry_type": EntryType.COMMIT, # Use EntryType enum
                "title": "Fix authentication bug in login service (GitHub)",
                "content": "Resolved issue where JWT tokens were not properly validated, causing authentication failures for users with special characters in usernames. This was a critical fix for the login flow.",
                "author": "john_doe",
                "timestamp": datetime.utcnow() - timedelta(hours=2),
                "url": "https://github.com/example/repo/commit/abc123",
                "score": 0.95 # Base score
            },
            {
                "id": UUID("22222222-2222-2222-2222-222222222222"),
                "source": SourceType.SLACK,
                "entry_type": EntryType.MESSAGE,
                "title": "Discussion about Redis vs PostgreSQL for caching (Slack)",
                "content": "Team discussion in #tech-discussions concluded that Redis provides significantly better performance for our caching needs. Decision made to migrate from PostgreSQL-based caching to Redis cluster. Sarah Smith led this.",
                "author": "sarah_smith",
                "timestamp": datetime.utcnow() - timedelta(days=7),
                "url": "https://slack.com/channel/tech-discussions/p123456789",
                "score": 0.88
            },
            {
                "id": UUID("33333333-3333-3333-3333-333333333333"),
                "source": SourceType.JIRA,
                "entry_type": EntryType.ISSUE,
                "title": "API Rate Limiting Implementation (Jira)",
                "content": "Implement rate limiting for public API endpoints to prevent abuse. Use Redis for distributed rate limiting across multiple server instances. Task PROJ-123 assigned to Mike Wilson.",
                "author": "mike_wilson",
                "timestamp": datetime.utcnow() - timedelta(days=14),
                "url": "https://jira.example.com/browse/PROJ-123",
                "score": 0.82
            },
            {
                "id": UUID("44444444-4444-4444-4444-444444444444"),
                "source": SourceType.CONFLUENCE, 
                "entry_type": EntryType.DOCUMENT,
                "title": "Architecture Decision Record: Caching Strategy (Confluence)",
                "content": "This document outlines the decision to use Redis for caching. Alternatives considered: Memcached, Hazelcast. Rationale: Performance, scalability, existing team familiarity with Redis.",
                "author": "architecture_team",
                "timestamp": datetime.utcnow() - timedelta(days=6),
                "url": "https://confluence.example.com/display/DEV/ADR005-Caching-Strategy",
                "score": 0.90
            },
            {
                "id": UUID("55555555-5555-5555-5555-555555555555"),
                "source": SourceType.GITHUB,
                "entry_type": EntryType.PULL_REQUEST,
                "title": "Refactor User Service to use Redis Cache (GitHub PR)",
                "content": "This pull request introduces Redis caching for frequently accessed user data, significantly improving API response times for user profile endpoints. Includes updates to deployment scripts for Redis.",
                "author": "jane_dev",
                "timestamp": datetime.utcnow() - timedelta(days=3),
                "url": "https://github.com/example/repo/pull/42",
                "score": 0.85
            }
        ]

        # Filter by project_id if provided (not implemented in this mock, would be a DB query)
        # For now, all mock data is considered for any project or no project.

        # Filter by include_sources
        if include_sources: # Should be a list of SourceType enum members
            entries_from_sources = [entry for entry in mock_data_store if entry["source"] in include_sources]
        else: # If None or empty, use all
            entries_from_sources = mock_data_store

        # Simple keyword matching for demo relevance
        relevant_entries = []
        query_words = query_text.lower().split()
        
        if not query_words: # If query is empty or just spaces
            return []

        for entry in entries_from_sources:
            searchable_text = (entry.get("title", "") + " " + entry.get("content", "")).lower()
            match_count = sum(1 for word in query_words if word in searchable_text)
            
            if match_count > 0:
                # Adjust score based on relevance (simple approach)
                dynamic_score = entry["score"] * (match_count / len(query_words)) * 1.5 # Boost relevant
                entry_copy = entry.copy() 
                entry_copy["score"] = min(0.99, dynamic_score) 
                relevant_entries.append(entry_copy)
        
        relevant_entries.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"Found {len(relevant_entries)} relevant entries for query '{query_text}'. Returning top {limit}.")
        return relevant_entries[:limit]

    async def _search_decisions(
        self,
        query_text: str,
        project_id: Optional[UUID] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search architectural decisions (mocked)"""
        logger.info(f"Searching decisions for: '{query_text}', project_id: {project_id}, limit: {limit}")
        mock_decisions = [
            {
                "id": UUID("dec11111-1111-1111-1111-111111111111"),
                "title": "Database Technology Choice: PostgreSQL",
                "decision": "Use PostgreSQL as primary database for DevMind.",
                "rationale": "PostgreSQL provides ACID compliance, excellent performance, pgvector for embeddings, and strong ecosystem support.",
                "alternatives": ["MySQL", "MongoDB", "SQLite for demo"],
                "consequences": ["Requires PostgreSQL expertise", "Better data consistency and search capabilities"],
                "timestamp": datetime.utcnow() - timedelta(days=30),
                "score": 0.9
            },
            {
                "id": UUID("dec22222-2222-2222-2222-222222222222"), 
                "title": "Caching Strategy: Redis",
                "decision": "Implement Redis for application caching and real-time features.",
                "rationale": "Redis provides high performance in-memory caching, pub/sub for WebSockets, and good scalability options.",
                "alternatives": ["Memcached", "In-memory Python dicts for demo", "Application-level caching"],
                "consequences": ["Additional infrastructure (Redis container)", "Improved response times and real-time capabilities"],
                "timestamp": datetime.utcnow() - timedelta(days=7),
                "score": 0.88
            },
            {
                "id": UUID("dec33333-3333-3333-3333-333333333333"),
                "title": "Backend Framework: FastAPI",
                "decision": "Utilize FastAPI for the Python backend.",
                "rationale": "FastAPI offers high performance, async support, automatic data validation and serialization with Pydantic, and OpenAPI documentation generation, which is ideal for rapid development in a hackathon.",
                "alternatives": ["Flask", "Django"],
                "consequences": ["Steeper learning curve for those unfamiliar with asyncio or Pydantic", "Excellent performance and developer experience"],
                "timestamp": datetime.utcnow() - timedelta(days=25),
                "score": 0.92
            }
        ]
        
        relevant_decisions = []
        query_words = query_text.lower().split()
        if not query_words: return []

        for decision in mock_decisions:
            searchable_text = (decision.get("title", "") + " " + decision.get("decision", "") + " " + decision.get("rationale", "")).lower()
            match_count = sum(1 for word in query_words if word in searchable_text)
            if match_count > 0:
                dynamic_score = decision["score"] * (match_count / len(query_words)) * 1.2
                decision_copy = decision.copy()
                decision_copy["score"] = min(0.99, dynamic_score)
                relevant_decisions.append(decision_copy)
        
        relevant_decisions.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"Found {len(relevant_decisions)} relevant decisions. Returning top {limit}.")
        return relevant_decisions[:limit]

    async def _generate_ai_response(
        self,
        query_text: str,
        context_matches: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]]
    ) -> str:
        """Generate AI response based on context (enhanced mock implementation)"""
        logger.info(f"Generating AI response for query: '{query_text}'")
        
        if not context_matches and not decisions:
            return "I couldn't find specific context related to your question in the knowledge base. Please try rephrasing or ask about a different topic. For example, you could ask about 'Redis caching' or 'authentication issues'."

        response_parts = [f"Okay, I've looked into '{query_text}'. Here's what I found:\n"]

        if decisions:
            response_parts.append("\n**Key Decisions Relevant to Your Query:**")
            for dec in decisions[:2]: # Show top 2 decisions
                response_parts.append(f"- **{dec.get('title', 'N/A')}**: {dec.get('decision', 'N/A')} (Rationale: {dec.get('rationale', 'N/A')[:100]}...)")
        
        if context_matches:
            response_parts.append("\n**Related Context Entries:**")
            for match in context_matches[:3]: # Show top 3 context matches
                source_info = f"From {match.get('source').value if hasattr(match.get('source'), 'value') else match.get('source', 'N/A')}"
                title_info = f"'{match.get('title', 'Context Snippet')}'"
                content_preview = match.get('content', 'No content available.')[:150]
                response_parts.append(f"- {source_info} - {title_info}: \"{content_preview}...\" (Score: {match.get('score', 0):.2f})")
        
        response_parts.append("\nThis information was retrieved by querying our integrated development tools and decision logs via the Model Context Protocol (MCP).")

        # Specific canned responses for demo magic
        if "redis" in query_text.lower() and "postgresql" in query_text.lower() and "caching" in query_text.lower():
            return """Based on team discussions and architectural decisions, here's why Redis was chosen over PostgreSQL for caching:

**Primary Reason: Performance & Suitability**
The team decided (around 7 days ago, as per Slack discussions and ADRs) that Redis offers significantly better performance for caching due to its in-memory nature. While PostgreSQL can cache, Redis is purpose-built for it and provides more advanced caching patterns and data structures (like hashes, sets, sorted sets) beneficial for this use case.

**Key Supporting Points:**
- **Slack Discussion (#tech-discussions):** Sarah Smith initiated a discussion highlighting Redis's 3x benchmark improvement for your specific caching scenario.
- **Architecture Decision Record (ADR005-Caching-Strategy):** This document formally outlines the choice of Redis, citing performance, scalability, and team familiarity as key factors. Alternatives like Memcached were considered.
- **Jira Task (PROJ-123 - API Rate Limiting):** This task, assigned to Mike Wilson, leverages Redis for distributed rate limiting, further cementing its role in your caching/fast-access data strategy.
- **GitHub PR (#42 - Refactor User Service):** Jane Dev's recent pull request integrated Redis for caching user data, demonstrating practical application and resulting in improved API response times.

This decision aligns with the broader goal of enhancing API performance and scalability across the DevMind application.
"""
        elif "authentication" in query_text.lower() and ("bug" in query_text.lower() or "issue" in query_text.lower()):
             return """Regarding authentication issues:

**Recent Critical Fix (GitHub Commit by john_doe, ~2 hours ago):**
A significant bug in the login service related to JWT token validation for usernames with special characters was resolved. This was causing authentication failures for some users.

**Details:**
- The commit `abc123...` (hypothetical SHA) addressed improper JWT validation.
- This fix was critical for the main login flow.

If users are still reporting authentication problems, it might be unrelated to this specific fix or a new issue. Check recent error logs and ensure the deployment containing this fix is live.
"""
        return "\n".join(response_parts)

    def _format_context_match(self, match_dict: Dict[str, Any]) -> ContextMatch:
        """Format context match dictionary to Pydantic model for API response"""
        # Ensure 'source' and 'entry_type' are valid enum members or strings
        source_value = match_dict.get("source")
        entry_type_value = match_dict.get("entry_type")

        # Convert to enum if possible, otherwise keep as string (or handle error)
        try:
            source_enum = SourceType(source_value) if not isinstance(source_value, SourceType) else source_value
        except ValueError:
            logger.warning(f"Invalid source value '{source_value}' in context match. Defaulting to 'custom'.")
            source_enum = SourceType.CUSTOM # Or handle as an error

        try:
            entry_type_enum = EntryType(entry_type_value) if not isinstance(entry_type_value, EntryType) else entry_type_value
        except ValueError:
            logger.warning(f"Invalid entry_type value '{entry_type_value}' in context match. Defaulting to 'document'.")
            entry_type_enum = EntryType.DOCUMENT # Or handle as an error
            
        return ContextMatch(
            entry_id=match_dict.get("id", UUID("00000000-0000-0000-0000-000000000000")), # Default UUID if missing
            score=float(match_dict.get("score", 0.0)),
            source=source_enum,
            entry_type=entry_type_enum,
            title=match_dict.get("title"),
            content=match_dict.get("content", "")[:500] + ("..." if len(match_dict.get("content", "")) > 500 else ""),
            author=match_dict.get("author"),
            timestamp=match_dict.get("timestamp", datetime.utcnow()),
            url=match_dict.get("url")
        )

    def _calculate_confidence(self, context_matches: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on context quality"""
        if not context_matches:
            return 0.0
        
        top_scores = [match.get("score", 0.0) for match in context_matches[:3]] # Use .get for safety
        if not top_scores:
            return 0.0
            
        avg_score = sum(top_scores) / len(top_scores)
        # Normalize to a 0-1 range, assuming scores are already somewhat normalized (e.g. cosine similarity)
        # For this mock, scores are between 0 and 1.
        return min(max(avg_score, 0.0), 1.0)


    # Project management methods
    async def list_projects(self, db: AsyncSession) -> List[Project]:
        """List all projects (mocked)"""
        logger.info("Listing projects (mocked)")
        # In a real app, this would query the database:
        # result = await db.execute(select(Project).order_by(Project.name))
        # return result.scalars().all()
        return [
            Project(id=UUID("prj11111-1111-1111-1111-111111111111"), name="DevMind Core Application", description="Main project for DevMind development context oracle.", is_active=True, created_at=datetime.utcnow()-timedelta(days=30)),
            Project(id=UUID("prj22222-2222-2222-2222-222222222222"), name="Frontend UI Overhaul", description="Project for redesigning the DevMind user interface.", is_active=True, created_at=datetime.utcnow()-timedelta(days=10))
        ]

    async def create_project(self, db: AsyncSession, project_data: ProjectCreate) -> Project:
        """Create a new project (mocked)"""
        logger.info(f"Creating project: {project_data.name} (mocked)")
        new_project_id = UUID(int=sum(ord(c) for c in project_data.name)) # Simple deterministic UUID for mock
        # db_project = Project(**project_data.model_dump(), id=new_project_id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        # db.add(db_project)
        # await db.commit()
        # await db.refresh(db_project)
        # return db_project
        return Project(
            id=new_project_id,
            name=project_data.name,
            description=project_data.description,
            repository_url=str(project_data.repository_url) if project_data.repository_url else None,
            slack_channel=project_data.slack_channel,
            jira_project_key=project_data.jira_project_key,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
            is_active=True
        )

    async def get_project(self, db: AsyncSession, project_id: UUID) -> Optional[Project]:
        """Get project by ID (mocked)"""
        logger.info(f"Getting project by ID: {project_id} (mocked)")
        # result = await db.execute(select(Project).where(Project.id == project_id))
        # return result.scalars().first()
        if project_id == UUID("prj11111-1111-1111-1111-111111111111"):
            return Project(id=project_id, name="DevMind Core Application", description="Main project.", is_active=True, created_at=datetime.utcnow()-timedelta(days=30))
        return None

    async def update_project(self, db: AsyncSession, project_id: UUID, project_update_data: ProjectUpdate) -> Optional[Project]:
        """Update project (mocked)"""
        logger.info(f"Updating project ID: {project_id} (mocked)")
        # db_project = await self.get_project(db, project_id)
        # if not db_project:
        #     return None
        # update_data = project_update_data.model_dump(exclude_unset=True)
        # for key, value in update_data.items():
        #     setattr(db_project, key, value)
        # db_project.updated_at = datetime.utcnow()
        # await db.commit()
        # await db.refresh(db_project)
        # return db_project
        mock_project = await self.get_project(db, project_id)
        if mock_project:
            if project_update_data.name: mock_project.name = project_update_data.name
            if project_update_data.description: mock_project.description = project_update_data.description
            # ... and so on for other fields
            mock_project.updated_at = datetime.utcnow()
            return mock_project
        return None

    # Integration methods
    async def list_integrations(self, db: AsyncSession, project_id: Optional[UUID] = None) -> List[Integration]:
        """List integrations (mocked)"""
        logger.info(f"Listing integrations for project_id: {project_id} (mocked)")
        # query = select(Integration)
        # if project_id:
        #     query = query.where(Integration.project_id == project_id)
        # result = await db.execute(query)
        # return result.scalars().all()
        return [
            Integration(id=UUID("int11111-1111-1111-1111-111111111111"), project_id=project_id or UUID("prj11111-1111-1111-1111-111111111111"), integration_type=SourceType.GITHUB, is_active=True, sync_status="success", created_at=datetime.utcnow()-timedelta(days=5)),
            Integration(id=UUID("int22222-2222-2222-2222-222222222222"), project_id=project_id or UUID("prj11111-1111-1111-1111-111111111111"), integration_type=SourceType.SLACK, is_active=True, sync_status="pending", created_at=datetime.utcnow()-timedelta(days=2))
        ]

    async def create_integration(self, db: AsyncSession, integration_data: IntegrationCreate) -> Integration:
        """Create integration (mocked)"""
        logger.info(f"Creating integration type: {integration_data.integration_type} for project {integration_data.project_id} (mocked)")
        new_integration_id = UUID(int=sum(ord(c) for c in integration_data.integration_type.value)) # Simple deterministic UUID
        # db_integration = Integration(**integration_data.model_dump(), id=new_integration_id, created_at=datetime.utcnow(), updated_at=datetime.utcnow(), sync_status="pending")
        # db.add(db_integration)
        # await db.commit()
        # await db.refresh(db_integration)
        # return db_integration
        return Integration(
            id=new_integration_id,
            project_id=integration_data.project_id,
            integration_type=integration_data.integration_type,
            # configuration=integration_data.configuration.model_dump(), # Pydantic v2
            is_active=True,
            last_sync=None,
            sync_status="pending",
            error_message=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    async def get_integration(self, db: AsyncSession, integration_id: UUID) -> Optional[Integration]:
        """Get integration by ID (mocked)"""
        logger.info(f"Getting integration by ID: {integration_id} (mocked)")
        # result = await db.execute(select(Integration).where(Integration.id == integration_id))
        # return result.scalars().first()
        if integration_id == UUID("int11111-1111-1111-1111-111111111111"):
            return Integration(id=integration_id, project_id=UUID("prj11111-1111-1111-1111-111111111111"), integration_type=SourceType.GITHUB, is_active=True, sync_status="success")
        return None

    async def sync_integration(self, integration_id: UUID, db: AsyncSession = None): # Added db session for potential future use
        """Sync integration data (mocked)"""
        logger.info(f"Syncing integration {integration_id} (mocked process started)")
        # Simulate sync process
        await asyncio.sleep(5) # Simulate some work
        # In a real app, update the integration status in the DB:
        # integration = await self.get_integration(db, integration_id)
        # if integration:
        #     integration.last_sync = datetime.utcnow()
        #     integration.sync_status = "success" # or "error" with message
        #     await db.commit()
        logger.info(f"Mock sync for integration {integration_id} completed.")


    # Insights and system status
    async def get_live_insights(self, project_id: Optional[UUID] = None, limit: int = 10) -> List[Insight]:
        """Get live insights (mocked)"""
        logger.info(f"Getting live insights for project_id: {project_id}, limit: {limit} (mocked)")
        
        mock_insights_data = [
            Insight(
                id=UUID("ins11111-1111-1111-1111-111111111111"),
                type=InsightType.CRITICAL_ISSUE,
                title="Critical Bug in Authentication Service (GitHub)",
                description="Authentication failures detected for users with special characters in usernames. Fix committed.",
                source=SourceType.GITHUB,
                priority="high",
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                url="https://github.com/example/repo/issues/123", # Example URL
                metadata={"affected_users": 15, "fix_status": "resolved", "commit_id": "abc123xyz"}
            ),
            Insight(
                id=UUID("ins22222-2222-2222-2222-222222222222"),
                type=InsightType.TEAM_MENTION,
                title="Team standup scheduled for 10:00 AM (Slack)",
                description="Daily standup meeting reminder in #general channel. Discuss Redis caching progress.",
                source=SourceType.SLACK,
                priority="medium",
                timestamp=datetime.utcnow() - timedelta(minutes=45),
                url="https://slack.com/channel/general/p987654321", # Example URL
                metadata={"channel": "general", "attendees_expected": 8, "topic": "Redis Caching"}
            ),
            Insight(
                id=UUID("ins33333-3333-3333-3333-333333333333"),
                type=InsightType.DEPLOYMENT,
                title="API rate limit optimization completed (Jira/CI)",
                description="Rate limiting implementation (PROJ-123) deployed to production. Monitoring performance.",
                source=SourceType.JIRA, # Could also be a CI/CD tool source
                priority="low", # Assuming successful deployment is informational
                timestamp=datetime.utcnow() - timedelta(hours=2),
                url="https://jira.example.com/browse/PROJ-123", # Example URL
                metadata={"deployment_status": "success", "performance_improvement_expected": "25%", "version": "v2.1.5"}
            )
        ]
        
        return mock_insights_data[:limit]

    async def get_system_status(self) -> SystemStatus:
        """Get system status (mocked)"""
        logger.info("Getting system status (mocked)")
        return SystemStatus(
            mcp_connections=3, # Mocked: GitHub, Slack, Jira
            active_integrations=2, # From list_integrations mock
            context_freshness="Real-time (mocked)", # Or "Last synced: X minutes ago"
            avg_query_time=1.15, # Mocked average
            last_sync=datetime.utcnow() - timedelta(minutes=5), # Mocked
            health_status="healthy"
        )

    async def check_integrations(self) -> Dict[str, str]:
        """Check integration status (mocked)"""
        logger.info("Checking integration health (mocked)")
        return {
            SourceType.GITHUB.value: "healthy",
            SourceType.SLACK.value: "healthy", 
            SourceType.JIRA.value: "healthy",
            SourceType.CONFLUENCE.value: "not_configured" # Example
        }

    # Query history methods
    async def get_query_history(
        self,
        db: AsyncSession,
        project_id: Optional[UUID] = None,
        limit: int = 20
    ) -> List[QueryHistory]:
        """Get query history (mocked)"""
        logger.info(f"Getting query history for project_id: {project_id}, limit: {limit} (mocked)")
        # query_stmt = select(Query).order_by(Query.created_at.desc()).limit(limit)
        # if project_id:
        #     query_stmt = query_stmt.where(Query.project_id == project_id)
        # result = await db.execute(query_stmt)
        # queries_db = result.scalars().all()
        # return [QueryHistory.from_orm(q) for q in queries_db] # Pydantic v1 style
        # return [QueryHistory.model_validate(q) for q in queries_db] # Pydantic v2 style
        
        mock_queries_data = [
            QueryHistory(
                id=UUID("qh111111-1111-1111-1111-111111111111"),
                query_text="Why did we choose Redis over PostgreSQL for caching?",
                confidence_score=0.92,
                execution_time=1.45,
                created_at=datetime.utcnow() - timedelta(hours=1),
                project_id=project_id # Will be None if project_id is None
            ),
            QueryHistory(
                id=UUID("qh222222-2222-2222-2222-222222222222"),
                query_text="Show me recent deployment issues related to authentication.",
                confidence_score=0.88,
                execution_time=0.93,
                created_at=datetime.utcnow() - timedelta(hours=3),
                project_id=project_id
            ),
            QueryHistory(
                id=UUID("qh333333-3333-3333-3333-333333333333"),
                query_text="Summarize today's team discussions on Slack about the new UI.",
                confidence_score=0.85,
                execution_time=2.11,
                created_at=datetime.utcnow() - timedelta(hours=5),
                project_id=project_id
            )
        ]
        return mock_queries_data[:limit]

    async def store_query(
        self,
        db: AsyncSession,
        query_id: UUID,
        query_text: str,
        project_id: Optional[UUID],
        response: Dict[str, Any], # This is the full dict from process_query
        execution_time: float
    ):
        """Store query in history (mocked, but shows structure for DB insert)"""
        logger.info(f"Storing query {query_id}: '{query_text[:50]}...' (mocked)")
        # query_to_store = Query(
        #     id=query_id,
        #     query_text=query_text,
        #     project_id=project_id,
        #     response=response, # Store the whole response dict as JSON
        #     sources_used=response.get("sources_used", []),
        #     confidence_score=response.get("confidence_score"),
        #     execution_time=execution_time,
        #     created_at=datetime.utcnow() 
        #     # embedding would be generated here if storing query embeddings
        # )
        # db.add(query_to_store)
        # await db.commit()
        # logger.info(f"Query {query_id} stored in history.")
        pass # Mocked, no actual DB operation

    # Additional helper methods (public API facing)
    async def search_context(
        self,
        query: str,
        project_id: Optional[UUID] = None,
        sources: Optional[List[str]] = None, # List of source strings
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search context (public API method, enhanced mock)"""
        logger.info(f"Public API search_context called with query: '{query}', project: {project_id}, sources: {sources}")
        
        processed_sources: Optional[List[SourceType]] = None
        if sources:
            processed_sources = []
            for src_str in sources:
                try:
                    processed_sources.append(SourceType(src_str))
                except ValueError:
                    logger.warning(f"Invalid source string '{src_str}' in search_context. Ignoring.")
        
        context_entries = await self._search_context_entries(
            query_text=query,
            project_id=project_id,
            limit=limit,
            include_sources=processed_sources # Pass the processed list of enums
        )
        
        formatted_matches = [self._format_context_match(match) for match in context_entries]
        
        return {
            "query": query,
            "matches": formatted_matches,
            "total_found_in_mock_subset": len(formatted_matches) # Clarify this is from the mock subset
        }

    async def get_project_timeline(
        self,
        project_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get project timeline (mocked)"""
        logger.info(f"Getting project timeline for project_id: {project_id}, last {days} days (mocked)")
        
        # Simulate fetching events within the last 'days'
        start_date = datetime.utcnow() - timedelta(days=days)
        
        mock_timeline_events = [
            {
                "id": UUID("evt11111-1111-1111-1111-111111111111"),
                "timestamp": datetime.utcnow() - timedelta(hours=2), # Within 30 days
                "type": EntryType.COMMIT.value,
                "source": SourceType.GITHUB.value,
                "title": "Fix authentication bug in JWT validation",
                "description": "Resolved special character handling in usernames.",
                "author": "john_doe",
                "url": "https://github.com/example/repo/commit/abc123"
            },
            {
                "id": UUID("evt22222-2222-2222-2222-222222222222"),
                "timestamp": datetime.utcnow() - timedelta(days=1), # Within 30 days
                "type": EntryType.PULL_REQUEST.value, # Changed to PULL_REQUEST
                "source": SourceType.GITHUB.value,
                "title": "Deployment of v2.1.4 to production",
                "description": "Deployed authentication fixes and performance improvements.",
                "author": "deploy_bot", # Or a user if manual PR
                "url": "https://github.com/example/repo/pull/210"
            },
            {
                "id": UUID("evt33333-3333-3333-3333-333333333333"),
                "timestamp": datetime.utcnow() - timedelta(days=7), # Within 30 days
                "type": EntryType.DECISION.value, # Changed to DECISION
                "source": SourceType.SLACK.value, # Or could be 'internal', 'confluence'
                "title": "Decision: Use Redis for Caching",
                "description": "Team consensus reached in #tech-discussions to adopt Redis for primary caching layer.",
                "author": "sarah_smith", # Or 'Architecture Review Board'
                "url": "https://slack.com/channel/tech-discussions/p1234567890"
            },
            {
                "id": UUID("evt44444-4444-4444-4444-444444444444"),
                "timestamp": datetime.utcnow() - timedelta(days=45), # Outside 30 days by default
                "type": EntryType.ISSUE.value,
                "source": SourceType.JIRA.value,
                "title": "Initial project setup and planning",
                "description": "Task to define initial project scope and infrastructure.",
                "author": "project_manager",
                "url": "https://jira.example.com/browse/PROJ-001"
            }
        ]
        
        # Filter events by date
        filtered_events = [event for event in mock_timeline_events if event["timestamp"] >= start_date]
        
        return {
            "project_id": str(project_id),
            "time_range_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "events": sorted(filtered_events, key=lambda x: x["timestamp"], reverse=True) # Newest first
        }

