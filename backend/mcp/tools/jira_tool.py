"""
Jira Tool for MCP Server
Handles Jira API interactions for DevMind
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
import json
import base64

from config import settings

logger = logging.getLogger(__name__)

class JiraTool:
    """Jira integration tool for MCP"""
    
    def __init__(self):
        self.base_url = settings.jira_url or "https://your-company.atlassian.net"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "DevMind/1.0"
        }
        
        # Setup authentication if credentials are available
        if settings.jira_username and settings.jira_token:
            auth_string = f"{settings.jira_username}:{settings.jira_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            self.headers["Authorization"] = f"Basic {auth_b64}"
        
        self.client: Optional[httpx.AsyncClient] = None
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=5)
            )
        return self.client
    
    async def cleanup(self):
        """Cleanup HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Execute Jira tool based on tool name"""
        try:
            if tool_name == "jira_search":
                return await self.search_issues(arguments)
            elif tool_name == "jira_get_issue":
                return await self.get_issue(arguments)
            elif tool_name == "jira_get_project":
                return await self.get_project(arguments)
            else:
                return MCPToolResult(
                    success=False,
                    content="",
                    error=f"Unknown Jira tool: {tool_name}"
                )
        except Exception as e:
            logger.error(f"Jira tool execution failed: {e}")
            return MCPToolResult(
                success=False,
                content="",
                error=str(e)
            )

    async def search_issues(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Search Jira issues using JQL or text search"""
        query = arguments.get("query", "")
        project = arguments.get("project", "")
        status = arguments.get("status", "")
        
        if not query:
            return MCPToolResult(
                success=False,
                content="",
                error="Query parameter is required"
            )
        
        # For demo purposes, return mock Jira data
        # In production, this would use the Jira REST API
        mock_issues = [
            {
                "id": "10001",
                "key": "PROJ-123",
                "summary": "API Rate Limiting Implementation",
                "description": "Implement rate limiting for public API endpoints to prevent abuse. Use Redis for distributed rate limiting across multiple server instances.",
                "status": "In Progress",
                "priority": "High",
                "assignee": "mike_wilson",
                "reporter": "sarah_smith",
                "created": datetime.utcnow() - timedelta(days=14),
                "updated": datetime.utcnow() - timedelta(hours=6),
                "project": "PROJ",
                "issue_type": "Story",
                "labels": ["api", "security", "performance"],
                "components": ["Backend", "Infrastructure"],
                "url": f"{self.base_url}/browse/PROJ-123"
            },
            {
                "id": "10002",
                "key": "PROJ-124",
                "summary": "Fix authentication service bug",
                "description": "Users with special characters in usernames are experiencing authentication failures. JWT token validation needs to be updated.",
                "status": "Done",
                "priority": "Critical",
                "assignee": "john_doe",
                "reporter": "alice_johnson",
                "created": datetime.utcnow() - timedelta(days=3),
                "updated": datetime.utcnow() - timedelta(hours=2),
                "project": "PROJ",
                "issue_type": "Bug",
                "labels": ["authentication", "security"],
                "components": ["Backend", "Authentication"],
                "url": f"{self.base_url}/browse/PROJ-124"
            },
            {
                "id": "10003",
                "key": "PROJ-125",
                "summary": "Redis caching implementation",
                "description": "Migrate from PostgreSQL-based caching to Redis for better performance. This includes setting up Redis cluster and updating application logic.",
                "status": "To Do",
                "priority": "Medium",
                "assignee": "sarah_smith",
                "reporter": "mike_wilson",
                "created": datetime.utcnow() - timedelta(days=5),
                "updated": datetime.utcnow() - timedelta(days=1),
                "project": "PROJ",
                "issue_type": "Task",
                "labels": ["performance", "infrastructure"],
                "components": ["Backend", "Cache"],
                "url": f"{self.base_url}/browse/PROJ-125"
            }
        ]
        
        # Filter issues based on query and filters
        relevant_issues = []
        query_words = query.lower().split()
        
        for issue in mock_issues:
            # Check project filter
            if project and project.upper() not in issue["key"]:
                continue
            
            # Check status filter
            if status and status.lower() not in issue["status"].lower():
                continue
            
            # Check text relevance
            searchable_text = (
                issue["summary"] + " " + 
                issue["description"] + " " + 
                " ".join(issue["labels"])
            ).lower()
            
            relevance = sum(1 for word in query_words if word in searchable_text)
            if relevance > 0:
                issue["relevance_score"] = relevance / len(query_words)
                relevant_issues.append(issue)
        
        # Sort by relevance
        relevant_issues.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Format results
        result = self._format_search_results(relevant_issues, query)
        
        return MCPToolResult(
            success=True,
            content=result,
            metadata={
                "query": query,
                "project_filter": project,
                "status_filter": status,
                "issue_count": len(relevant_issues)
            }
        )

    async def get_issue(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Get detailed information about a specific Jira issue"""
        issue_key = arguments.get("issue_key", "")
        
        if not issue_key:
            return MCPToolResult(
                success=False,
                content="",
                error="Issue key parameter is required"
            )
        
        client = await self._get_client()
        
        try:
            # In production, would call: GET /rest/api/3/issue/{issueIdOrKey}
            # Mock implementation for demo
            
            # Find the issue in our mock data
            mock_issue = {
                "id": "10001",
                "key": issue_key,
                "summary": "API Rate Limiting Implementation",
                "description": "Implement rate limiting for public API endpoints to prevent abuse. Use Redis for distributed rate limiting across multiple server instances.\n\nAcceptance Criteria:\n- Rate limiting based on API key\n- Redis-based storage for distributed systems\n- Configurable rate limits per endpoint\n- Proper error responses when limits exceeded",
                "status": "In Progress",
                "priority": "High",
                "assignee": "mike_wilson",
                "reporter": "sarah_smith",
                "created": datetime.utcnow() - timedelta(days=14),
                "updated": datetime.utcnow() - timedelta(hours=6),
                "project": "PROJ",
                "issue_type": "Story",
                "labels": ["api", "security", "performance"],
                "components": ["Backend", "Infrastructure"],
                "url": f"{self.base_url}/browse/{issue_key}",
                "comments": [
                    {
                        "author": "sarah_smith",
                        "body": "I've done some research on rate limiting approaches. Redis seems to be the best option for our distributed setup.",
                        "created": datetime.utcnow() - timedelta(days=10)
                    },
                    {
                        "author": "mike_wilson",
                        "body": "Started implementation. Using Redis sliding window algorithm for rate limiting.",
                        "created": datetime.utcnow() - timedelta(days=3)
                    }
                ],
                "subtasks": [
                    {"key": "PROJ-126", "summary": "Setup Redis cluster"},
                    {"key": "PROJ-127", "summary": "Implement rate limiting middleware"},
                    {"key": "PROJ-128", "summary": "Add rate limit configuration"}
                ]
            }
            
            result = self._format_issue_details(mock_issue)
            
            return MCPToolResult(
                success=True,
                content=result,
                metadata={
                    "issue_key": issue_key,
                    "status": mock_issue["status"],
                    "priority": mock_issue["priority"]
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="",
                error=f"Failed to get issue: {str(e)}"
            )

    async def get_project(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Get project information"""
        project_key = arguments.get("project_key", "")
        
        if not project_key:
            return MCPToolResult(
                success=False,
                content="",
                error="Project key parameter is required"
            )
        
        try:
            # Mock project data
            mock_project = {
                "key": project_key,
                "name": "Development Project",
                "description": "Main development project for DevMind application",
                "lead": "sarah_smith",
                "url": f"{self.base_url}/browse/{project_key}",
                "issue_types": ["Story", "Bug", "Task", "Epic"],
                "versions": ["1.0.0", "1.1.0", "2.0.0"],
                "components": ["Frontend", "Backend", "Authentication", "Infrastructure"]
            }
            
            result = self._format_project_details(mock_project)
            
            return MCPToolResult(
                success=True,
                content=result,
                metadata={
                    "project_key": project_key,
                    "project_name": mock_project["name"]
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="",
                error=f"Failed to get project: {str(e)}"
            )

    def _format_search_results(self, issues: List[Dict], query: str) -> str:
        """Format search results for display"""
        if not issues:
            return f"No Jira issues found matching '{query}'"
        
        results = [f"Found {len(issues)} Jira issues matching '{query}':\n"]
        
        for issue in issues[:10]:  # Limit to top 10
            key = issue.get("key", "")
            summary = issue.get("summary", "")
            status = issue.get("status", "")
            priority = issue.get("priority", "")
            assignee = issue.get("assignee", "Unassigned")
            updated = issue.get("updated", datetime.utcnow())
            url = issue.get("url", "")
            
            # Priority emoji
            priority_emoji = {
                "Critical": "🔴",
                "High": "🟠", 
                "Medium": "🟡",
                "Low": "🟢"
            }.get(priority, "⚪")
            
            results.append(f"""
🎫 {key}: {summary}
   Status: {status} | Priority: {priority_emoji} {priority}
   Assignee: {assignee} | Updated: {updated.strftime('%Y-%m-%d %H:%M')}
   🔗 {url}
""")
        
        return "".join(results)

    def _format_issue_details(self, issue: Dict) -> str:
        """Format detailed issue information"""
        key = issue.get("key", "")
        summary = issue.get("summary", "")
        description = issue.get("description", "")
        status = issue.get("status", "")
        priority = issue.get("priority", "")
        assignee = issue.get("assignee", "Unassigned")
        reporter = issue.get("reporter", "")
        created = issue.get("created", datetime.utcnow())
        updated = issue.get("updated", datetime.utcnow())
        labels = issue.get("labels", [])
        components = issue.get("components", [])
        url = issue.get("url", "")
        comments = issue.get("comments", [])
        subtasks = issue.get("subtasks", [])
        
        # Priority emoji
        priority_emoji = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡", 
            "Low": "🟢"
        }.get(priority, "⚪")
        
        result = f"""
Issue {key}: {summary}

📋 Details:
Status: {status}
Priority: {priority_emoji} {priority}
Assignee: {assignee}
Reporter: {reporter}
Created: {created.strftime('%Y-%m-%d %H:%M')}
Updated: {updated.strftime('%Y-%m-%d %H:%M')}

🏷️ Labels: {', '.join(labels)}
🔧 Components: {', '.join(components)}

📝 Description:
{description}
"""
        
        # Add comments
        if comments:
            result += "\n\n💬 Comments:\n"
            for comment in comments[-3:]:  # Last 3 comments
                author = comment.get("author", "")
                body = comment.get("body", "")
                created = comment.get("created", datetime.utcnow())
                
                result += f"""
{author} - {created.strftime('%Y-%m-%d %H:%M')}
{body}
"""
        
        # Add subtasks
        if subtasks:
            result += "\n\n📋 Subtasks:\n"
            for subtask in subtasks:
                subtask_key = subtask.get("key", "")
                subtask_summary = subtask.get("summary", "")
                result += f"- {subtask_key}: {subtask_summary}\n"
        
        result += f"\n🔗 {url}"
        
        return result

    def _format_project_details(self, project: Dict) -> str:
        """Format project information"""
        key = project.get("key", "")
        name = project.get("name", "")
        description = project.get("description", "")
        lead = project.get("lead", "")
        url = project.get("url", "")
        issue_types = project.get("issue_types", [])
        versions = project.get("versions", [])
        components = project.get("components", [])
        
        result = f"""
Project {key}: {name}

📝 Description:
{description}

👤 Project Lead: {lead}

🎫 Issue Types: {', '.join(issue_types)}
📦 Versions: {', '.join(versions)}
🔧 Components: {', '.join(components)}

🔗 {url}
"""
        
        return result

    async def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jira issue (for automation)"""
        # Mock implementation for demo
        logger.info(f"Would create Jira issue: {issue_data}")
        return {
            "id": "10999",
            "key": "PROJ-999",
            "self": f"{self.base_url}/rest/api/3/issue/10999"
        }

    async def update_issue(self, issue_key: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Jira issue"""
        # Mock implementation for demo
        logger.info(f"Would update Jira issue {issue_key}: {update_data}")
        return {"success": True}

# Import MCPToolResult from parent module
from mcp.server import MCPToolResult