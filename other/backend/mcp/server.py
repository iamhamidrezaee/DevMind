"""
MCP Server Implementation for DevMind
Implements the Model Context Protocol for AI context sharing
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from mcp import create_server, Resource, Tool, Prompt
from mcp.server import Server
from mcp.types import (
    GetPromptRequest, GetPromptResult,
    ListPromptsRequest, ListPromptsResult,
    ListResourcesRequest, ListResourcesResult,
    ReadResourceRequest, ReadResourceResult,
    ListToolsRequest, ListToolsResult,
    CallToolRequest, CallToolResult,
    Prompt as MCPPrompt,
    Resource as MCPResource,
    Tool as MCPTool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

from config import settings
from mcp.tools.github_tool import GitHubTool
from mcp.tools.slack_tool import SlackTool
from mcp.tools.jira_tool import JiraTool
from mcp.resources.context_resource import ContextResource

logger = logging.getLogger(__name__)

@dataclass
class MCPToolResult:
    """Result from MCP tool execution"""
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MCPServer:
    """DevMind MCP Server implementation"""
    
    def __init__(self):
        self.server: Optional[Server] = None
        self.is_running = False
        
        # Initialize tools
        self.github_tool = GitHubTool()
        self.slack_tool = SlackTool()
        self.jira_tool = JiraTool()
        
        # Initialize resources
        self.context_resource = ContextResource()
        
        # Tool registry
        self.tools: Dict[str, Any] = {
            "github_search": self.github_tool,
            "github_get_pr": self.github_tool,
            "github_get_commits": self.github_tool,
            "slack_search": self.slack_tool,
            "slack_get_messages": self.slack_tool,
            "jira_search": self.jira_tool,
            "jira_get_issue": self.jira_tool,
            "context_search": self.context_resource,
            "context_get_decisions": self.context_resource,
            "context_get_timeline": self.context_resource
        }
        
        logger.info("🔧 MCP Server initialized with tools and resources")

    async def start(self):
        """Start the MCP server"""
        try:
            self.server = create_server(settings.mcp_server_name)
            
            # Register handlers
            await self._register_handlers()
            
            self.is_running = True
            logger.info(f"🚀 MCP Server '{settings.mcp_server_name}' started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {e}")
            raise

    async def stop(self):
        """Stop the MCP server"""
        try:
            if self.server:
                # Cleanup resources
                await self.context_resource.cleanup()
                await self.github_tool.cleanup()
                await self.slack_tool.cleanup()
                await self.jira_tool.cleanup()
                
                self.is_running = False
                logger.info("✅ MCP Server stopped successfully")
                
        except Exception as e:
            logger.error(f"❌ Error stopping MCP server: {e}")

    async def _register_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_prompts()
        async def list_prompts() -> List[MCPPrompt]:
            """List available prompts for context queries"""
            return [
                MCPPrompt(
                    name="analyze_context",
                    description="Analyze development context for a specific question",
                    arguments=[
                        {"name": "query", "description": "The question to analyze", "required": True},
                        {"name": "project_id", "description": "Project ID for context", "required": False},
                        {"name": "time_range", "description": "Time range for context (e.g., '7d', '1m')", "required": False}
                    ]
                ),
                MCPPrompt(
                    name="get_decision_context",
                    description="Get context for architectural decisions",
                    arguments=[
                        {"name": "decision_topic", "description": "Topic of the decision", "required": True},
                        {"name": "project_id", "description": "Project ID", "required": False}
                    ]
                ),
                MCPPrompt(
                    name="onboard_team_member",
                    description="Generate onboarding context for new team members",
                    arguments=[
                        {"name": "role", "description": "Role of the new team member", "required": True},
                        {"name": "project_id", "description": "Project ID", "required": True},
                        {"name": "focus_areas", "description": "Specific areas to focus on", "required": False}
                    ]
                )
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
            """Execute a prompt with given arguments"""
            try:
                if name == "analyze_context":
                    result = await self._analyze_context_prompt(arguments)
                elif name == "get_decision_context":
                    result = await self._get_decision_context_prompt(arguments)
                elif name == "onboard_team_member":
                    result = await self._onboard_team_member_prompt(arguments)
                else:
                    raise ValueError(f"Unknown prompt: {name}")
                
                return GetPromptResult(
                    description=f"Context analysis for: {arguments.get('query', name)}",
                    messages=[
                        {
                            "role": "user",
                            "content": TextContent(type="text", text=result)
                        }
                    ]
                )
            except Exception as e:
                logger.error(f"Error executing prompt {name}: {e}")
                raise

        @self.server.list_resources()
        async def list_resources() -> List[MCPResource]:
            """List available resources"""
            return [
                MCPResource(
                    uri="devmind://context/search",
                    name="Context Search",
                    description="Search through development context across all sources",
                    mimeType="application/json"
                ),
                MCPResource(
                    uri="devmind://decisions/list",
                    name="Architecture Decisions",
                    description="List of architectural decisions and their context",
                    mimeType="application/json"
                ),
                MCPResource(
                    uri="devmind://timeline/project",
                    name="Project Timeline",
                    description="Chronological timeline of project events",
                    mimeType="application/json"
                ),
                MCPResource(
                    uri="devmind://insights/live",
                    name="Live Insights",
                    description="Real-time insights from development activity",
                    mimeType="application/json"
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """Read a specific resource"""
            try:
                if uri.startswith("devmind://context/"):
                    content = await self.context_resource.search_context()
                elif uri.startswith("devmind://decisions/"):
                    content = await self.context_resource.get_decisions()
                elif uri.startswith("devmind://timeline/"):
                    content = await self.context_resource.get_timeline()
                elif uri.startswith("devmind://insights/"):
                    content = await self.context_resource.get_live_insights()
                else:
                    raise ValueError(f"Unknown resource URI: {uri}")
                
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=content
                        )
                    ]
                )
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise

        @self.server.list_tools()
        async def list_tools() -> List[MCPTool]:
            """List available tools"""
            return [
                MCPTool(
                    name="github_search",
                    description="Search GitHub repositories, issues, and pull requests",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "repository": {"type": "string", "description": "Repository name"},
                            "type": {"type": "string", "enum": ["issues", "prs", "commits", "code"]}
                        },
                        "required": ["query"]
                    }
                ),
                MCPTool(
                    name="slack_search",
                    description="Search Slack messages and channels",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "channel": {"type": "string", "description": "Channel name"},
                            "date_range": {"type": "string", "description": "Date range (e.g., '7d')"}
                        },
                        "required": ["query"]
                    }
                ),
                MCPTool(
                    name="jira_search",
                    description="Search Jira issues and projects",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "JQL query or text search"},
                            "project": {"type": "string", "description": "Project key"},
                            "status": {"type": "string", "description": "Issue status"}
                        },
                        "required": ["query"]
                    }
                ),
                MCPTool(
                    name="context_search",
                    description="Search through all development context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "sources": {"type": "array", "items": {"type": "string"}},
                            "limit": {"type": "integer", "default": 10}
                        },
                        "required": ["query"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Execute a tool with given arguments"""
            try:
                if name not in self.tools:
                    raise ValueError(f"Unknown tool: {name}")
                
                tool = self.tools[name]
                result = await tool.execute(name, arguments)
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=result.content if result.success else f"Error: {result.error}"
                        )
                    ],
                    isError=not result.success
                )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Tool execution failed: {str(e)}")],
                    isError=True
                )

    async def _analyze_context_prompt(self, arguments: Dict[str, str]) -> str:
        """Execute the analyze_context prompt"""
        query = arguments.get("query", "")
        project_id = arguments.get("project_id")
        time_range = arguments.get("time_range", "30d")
        
        # Search across all sources
        context_results = await self.context_resource.search_context({
            "query": query,
            "project_id": project_id,
            "time_range": time_range,
            "limit": 20
        })
        
        return f"""
Context Analysis for: "{query}"

{context_results}

This context has been gathered from GitHub, Slack, Jira, and internal decisions.
Use this information to provide a comprehensive answer to the user's question.
"""

    async def _get_decision_context_prompt(self, arguments: Dict[str, str]) -> str:
        """Execute the get_decision_context prompt"""
        topic = arguments.get("decision_topic", "")
        project_id = arguments.get("project_id")
        
        decisions = await self.context_resource.get_decisions({
            "topic": topic,
            "project_id": project_id
        })
        
        return f"""
Decision Context for: "{topic}"

{decisions}

This includes architectural decisions, their rationale, alternatives considered, and consequences.
"""

    async def _onboard_team_member_prompt(self, arguments: Dict[str, str]) -> str:
        """Execute the onboard_team_member prompt"""
        role = arguments.get("role", "")
        project_id = arguments.get("project_id", "")
        focus_areas = arguments.get("focus_areas", "")
        
        timeline = await self.context_resource.get_timeline({
            "project_id": project_id,
            "time_range": "90d"
        })
        
        decisions = await self.context_resource.get_decisions({
            "project_id": project_id
        })
        
        return f"""
Onboarding Package for: {role}
Project: {project_id}
Focus Areas: {focus_areas}

=== Project Timeline (Last 90 days) ===
{timeline}

=== Key Architectural Decisions ===
{decisions}

This package provides essential context for the new team member to get up to speed quickly.
"""

    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information and status"""
        return {
            "name": settings.mcp_server_name,
            "version": settings.mcp_server_version,
            "status": "running" if self.is_running else "stopped",
            "tools_count": len(self.tools),
            "capabilities": {
                "prompts": True,
                "resources": True,
                "tools": True,
                "logging": True
            }
        }