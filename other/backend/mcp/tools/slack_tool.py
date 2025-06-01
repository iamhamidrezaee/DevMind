"""
Slack Tool for MCP Server
Handles Slack API interactions for DevMind
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
import json

from config import settings

logger = logging.getLogger(__name__)

class SlackTool:
    """Slack integration tool for MCP"""
    
    def __init__(self):
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "DevMind/1.0"
        }
        
        if settings.slack_token:
            self.headers["Authorization"] = f"Bearer {settings.slack_token}"
        
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
        """Execute Slack tool based on tool name"""
        try:
            if tool_name == "slack_search":
                return await self.search_messages(arguments)
            elif tool_name == "slack_get_messages":
                return await self.get_channel_messages(arguments)
            elif tool_name == "slack_get_channels":
                return await self.get_channels(arguments)
            else:
                return MCPToolResult(
                    success=False,
                    content="",
                    error=f"Unknown Slack tool: {tool_name}"
                )
        except Exception as e:
            logger.error(f"Slack tool execution failed: {e}")
            return MCPToolResult(
                success=False,
                content="",
                error=str(e)
            )

    async def search_messages(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Search Slack messages across channels"""
        query = arguments.get("query", "")
        channel = arguments.get("channel", "")
        date_range = arguments.get("date_range", "7d")
        
        if not query:
            return MCPToolResult(
                success=False,
                content="",
                error="Query parameter is required"
            )
        
        # For demo purposes, return mock Slack data
        # In production, this would use the Slack Web API
        mock_messages = [
            {
                "text": "Hey team, I've been investigating the Redis vs PostgreSQL decision. After running some benchmarks, Redis shows 3x better performance for our caching use case. The memory usage is also more predictable.",
                "user": "sarah_smith",
                "channel": "tech-discussions",
                "timestamp": datetime.utcnow() - timedelta(days=7),
                "thread_ts": None,
                "permalink": "https://your-workspace.slack.com/archives/C1234567890/p1234567890123456"
            },
            {
                "text": "Authentication bug fix is now deployed to production. We resolved the issue with special characters in usernames. All tests are passing.",
                "user": "john_doe",
                "channel": "deployments",
                "timestamp": datetime.utcnow() - timedelta(hours=4),
                "thread_ts": None,
                "permalink": "https://your-workspace.slack.com/archives/C1234567891/p1234567890123457"
            },
            {
                "text": "Can someone explain the recent changes to the API rate limiting? I'm seeing some different behavior in the staging environment.",
                "user": "alice_johnson",
                "channel": "general",
                "timestamp": datetime.utcnow() - timedelta(hours=8),
                "thread_ts": None,
                "permalink": "https://your-workspace.slack.com/archives/C1234567892/p1234567890123458"
            }
        ]
        
        # Filter messages based on query
        query_words = query.lower().split()
        relevant_messages = []
        
        for message in mock_messages:
            message_text = message["text"].lower()
            if channel and channel.lower() not in message["channel"].lower():
                continue
                
            relevance = sum(1 for word in query_words if word in message_text)
            if relevance > 0:
                message["relevance_score"] = relevance / len(query_words)
                relevant_messages.append(message)
        
        # Sort by relevance
        relevant_messages.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Format results
        result = self._format_search_results(relevant_messages, query)
        
        return MCPToolResult(
            success=True,
            content=result,
            metadata={
                "query": query,
                "channel_filter": channel,
                "date_range": date_range,
                "message_count": len(relevant_messages)
            }
        )

    async def get_channel_messages(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Get recent messages from a specific channel"""
        channel = arguments.get("channel", "")
        limit = arguments.get("limit", 20)
        
        if not channel:
            return MCPToolResult(
                success=False,
                content="",
                error="Channel parameter is required"
            )
        
        client = await self._get_client()
        
        try:
            # In production, would call Slack API
            # Mock implementation for demo
            mock_messages = [
                {
                    "text": f"Message from {channel} channel - discussing recent developments",
                    "user": "team_member",
                    "timestamp": datetime.utcnow() - timedelta(minutes=30),
                    "thread_ts": None,
                    "permalink": f"https://your-workspace.slack.com/archives/{channel}/p1234567890123456"
                }
            ]
            
            result = self._format_channel_messages(mock_messages, channel)
            
            return MCPToolResult(
                success=True,
                content=result,
                metadata={
                    "channel": channel,
                    "message_count": len(mock_messages),
                    "limit": limit
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="",
                error=f"Failed to get channel messages: {str(e)}"
            )

    async def get_channels(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Get list of channels"""
        try:
            # Mock channels for demo
            mock_channels = [
                {
                    "id": "C1234567890",
                    "name": "general",
                    "is_private": False,
                    "member_count": 25,
                    "purpose": "General team discussions"
                },
                {
                    "id": "C1234567891", 
                    "name": "tech-discussions",
                    "is_private": False,
                    "member_count": 12,
                    "purpose": "Technical architecture and development discussions"
                },
                {
                    "id": "C1234567892",
                    "name": "deployments",
                    "is_private": False,
                    "member_count": 8,
                    "purpose": "Deployment notifications and status updates"
                }
            ]
            
            result = self._format_channels(mock_channels)
            
            return MCPToolResult(
                success=True,
                content=result,
                metadata={
                    "channel_count": len(mock_channels)
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="",
                error=f"Failed to get channels: {str(e)}"
            )

    def _format_search_results(self, messages: List[Dict], query: str) -> str:
        """Format search results for display"""
        if not messages:
            return f"No Slack messages found matching '{query}'"
        
        results = [f"Found {len(messages)} Slack messages matching '{query}':\n"]
        
        for message in messages[:10]:  # Limit to top 10
            user = message.get("user", "Unknown")
            channel = message.get("channel", "Unknown")
            text = message.get("text", "")
            timestamp = message.get("timestamp", datetime.utcnow())
            permalink = message.get("permalink", "")
            
            # Truncate long messages
            display_text = text[:200] + "..." if len(text) > 200 else text
            
            results.append(f"""
💬 #{channel} - {user}
   {display_text}
   🕒 {timestamp.strftime('%Y-%m-%d %H:%M')}
   🔗 {permalink}
""")
        
        return "".join(results)

    def _format_channel_messages(self, messages: List[Dict], channel: str) -> str:
        """Format channel messages for display"""
        if not messages:
            return f"No recent messages found in #{channel}"
        
        results = [f"Recent messages from #{channel}:\n"]
        
        for message in messages:
            user = message.get("user", "Unknown")
            text = message.get("text", "")
            timestamp = message.get("timestamp", datetime.utcnow())
            permalink = message.get("permalink", "")
            
            results.append(f"""
👤 {user} - {timestamp.strftime('%Y-%m-%d %H:%M')}
{text}
🔗 {permalink}
""")
        
        return "".join(results)

    def _format_channels(self, channels: List[Dict]) -> str:
        """Format channels list for display"""
        if not channels:
            return "No channels found"
        
        results = ["Available Slack channels:\n"]
        
        for channel in channels:
            name = channel.get("name", "")
            member_count = channel.get("member_count", 0)
            purpose = channel.get("purpose", "")
            is_private = channel.get("is_private", False)
            
            privacy_icon = "🔒" if is_private else "🌐"
            
            results.append(f"""
{privacy_icon} #{name} ({member_count} members)
   Purpose: {purpose}
""")
        
        return "".join(results)

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information"""
        # Mock user info for demo
        return {
            "id": user_id,
            "name": "Team Member",
            "real_name": "Team Member",
            "display_name": "Team Member",
            "email": "team@example.com"
        }

    async def post_message(self, channel: str, text: str, thread_ts: str = None) -> Dict[str, Any]:
        """Post a message to Slack (for notifications)"""
        # Mock implementation for demo
        logger.info(f"Would post to #{channel}: {text}")
        return {
            "ok": True,
            "ts": "1234567890.123456",
            "message": {
                "text": text,
                "user": "devmind_bot",
                "ts": "1234567890.123456"
            }
        }

# Import MCPToolResult from parent module
from mcp.server import MCPToolResult