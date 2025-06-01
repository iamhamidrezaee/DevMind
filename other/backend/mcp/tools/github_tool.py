"""
GitHub Tool for MCP Server
Handles GitHub API interactions for DevMind
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
import json

from config import settings

logger = logging.getLogger(__name__)

class GitHubTool:
    """GitHub integration tool for MCP"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DevMind/1.0"
        }
        
        if settings.github_token:
            self.headers["Authorization"] = f"token {settings.github_token}"
        
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
        """Execute GitHub tool based on tool name"""
        try:
            if tool_name == "github_search":
                return await self.search(arguments)
            elif tool_name == "github_get_pr":
                return await self.get_pull_request(arguments)
            elif tool_name == "github_get_commits":
                return await self.get_commits(arguments)
            else:
                return MCPToolResult(
                    success=False,
                    content="",
                    error=f"Unknown GitHub tool: {tool_name}"
                )
        except Exception as e:
            logger.error(f"GitHub tool execution failed: {e}")
            return MCPToolResult(
                success=False,
                content="",
                error=str(e)
            )

    async def search(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Search GitHub repositories, issues, and pull requests"""
        query = arguments.get("query", "")
        repository = arguments.get("repository", "")
        search_type = arguments.get("type", "issues")
        
        if not query:
            return MCPToolResult(
                success=False,
                content="",
                error="Query parameter is required"
            )
        
        client = await self._get_client()
        
        try:
            # Build search query
            search_query = query
            if repository:
                search_query += f" repo:{repository}"
            
            # Search based on type
            if search_type == "issues":
                url = f"{self.base_url}/search/issues"
                search_query += " type:issue"
            elif search_type == "prs":
                url = f"{self.base_url}/search/issues"
                search_query += " type:pr"
            elif search_type == "commits":
                url = f"{self.base_url}/search/commits"
            elif search_type == "code":
                url = f"{self.base_url}/search/code"
            else:
                return MCPToolResult(
                    success=False,
                    content="",
                    error=f"Invalid search type: {search_type}"
                )
            
            params = {
                "q": search_query,
                "sort": "updated",
                "order": "desc",
                "per_page": 20
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = self._format_search_results(data, search_type)
            
            return MCPToolResult(
                success=True,
                content=results,
                metadata={
                    "total_count": data.get("total_count", 0),
                    "search_type": search_type,
                    "repository": repository
                }
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API error: {e}")
            return MCPToolResult(
                success=False,
                content="",
                error=f"GitHub API error: {e.response.status_code}"
            )

    async def get_pull_request(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Get detailed pull request information"""
        repository = arguments.get("repository", "")
        pr_number = arguments.get("pr_number")
        
        if not repository or not pr_number:
            return MCPToolResult(
                success=False,
                content="",
                error="Repository and PR number are required"
            )
        
        client = await self._get_client()
        
        try:
            # Get PR details
            url = f"{self.base_url}/repos/{repository}/pulls/{pr_number}"
            response = await client.get(url)
            response.raise_for_status()
            
            pr_data = response.json()
            
            # Get PR reviews
            reviews_url = f"{url}/reviews"
            reviews_response = await client.get(reviews_url)
            reviews_data = reviews_response.json() if reviews_response.status_code == 200 else []
            
            # Get PR comments
            comments_url = f"{url}/comments"
            comments_response = await client.get(comments_url)
            comments_data = comments_response.json() if comments_response.status_code == 200 else []
            
            result = self._format_pull_request(pr_data, reviews_data, comments_data)
            
            return MCPToolResult(
                success=True,
                content=result,
                metadata={
                    "pr_number": pr_number,
                    "repository": repository,
                    "state": pr_data.get("state")
                }
            )
            
        except httpx.HTTPStatusError as e:
            return MCPToolResult(
                success=False,
                content="",
                error=f"Failed to get PR: {e.response.status_code}"
            )

    async def get_commits(self, arguments: Dict[str, Any]) -> 'MCPToolResult':
        """Get commit history for a repository"""
        repository = arguments.get("repository", "")
        branch = arguments.get("branch", "main")
        since = arguments.get("since")  # ISO 8601 date
        limit = arguments.get("limit", 50)
        
        if not repository:
            return MCPToolResult(
                success=False,
                content="",
                error="Repository is required"
            )
        
        client = await self._get_client()
        
        try:
            url = f"{self.base_url}/repos/{repository}/commits"
            params = {
                "sha": branch,
                "per_page": min(limit, 100)
            }
            
            if since:
                params["since"] = since
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            commits_data = response.json()
            result = self._format_commits(commits_data)
            
            return MCPToolResult(
                success=True,
                content=result,
                metadata={
                    "repository": repository,
                    "branch": branch,
                    "commit_count": len(commits_data)
                }
            )
            
        except httpx.HTTPStatusError as e:
            return MCPToolResult(
                success=False,
                content="",
                error=f"Failed to get commits: {e.response.status_code}"
            )

    def _format_search_results(self, data: Dict[str, Any], search_type: str) -> str:
        """Format search results for display"""
        items = data.get("items", [])
        if not items:
            return f"No {search_type} found matching the search criteria."
        
        results = [f"Found {len(items)} {search_type}:\n"]
        
        for item in items[:10]:  # Limit to top 10 results
            if search_type in ["issues", "prs"]:
                title = item.get("title", "")
                number = item.get("number", "")
                state = item.get("state", "")
                author = item.get("user", {}).get("login", "")
                url = item.get("html_url", "")
                created = item.get("created_at", "")
                
                results.append(f"""
📋 #{number}: {title}
   State: {state} | Author: {author}
   Created: {created}
   URL: {url}
""")
            elif search_type == "commits":
                commit = item.get("commit", {})
                message = commit.get("message", "")
                author = commit.get("author", {}).get("name", "")
                date = commit.get("author", {}).get("date", "")
                sha = item.get("sha", "")[:8]
                url = item.get("html_url", "")
                
                results.append(f"""
🔧 {sha}: {message.split('\n')[0]}
   Author: {author} | Date: {date}
   URL: {url}
""")
            elif search_type == "code":
                name = item.get("name", "")
                path = item.get("path", "")
                repository = item.get("repository", {}).get("full_name", "")
                url = item.get("html_url", "")
                
                results.append(f"""
📄 {name} in {path}
   Repository: {repository}
   URL: {url}
""")
        
        return "".join(results)

    def _format_pull_request(self, pr_data: Dict[str, Any], reviews: List[Dict], comments: List[Dict]) -> str:
        """Format pull request details"""
        title = pr_data.get("title", "")
        number = pr_data.get("number", "")
        state = pr_data.get("state", "")
        author = pr_data.get("user", {}).get("login", "")
        body = pr_data.get("body", "")
        created = pr_data.get("created_at", "")
        updated = pr_data.get("updated_at", "")
        url = pr_data.get("html_url", "")
        
        # Base info
        result = f"""
Pull Request #{number}: {title}

Author: {author}
State: {state}
Created: {created}
Updated: {updated}
URL: {url}

Description:
{body or 'No description provided'}
"""
        
        # Add reviews
        if reviews:
            result += "\n\nReviews:\n"
            for review in reviews[-5:]:  # Last 5 reviews
                reviewer = review.get("user", {}).get("login", "")
                review_state = review.get("state", "")
                review_body = review.get("body", "")
                review_date = review.get("submitted_at", "")
                
                result += f"""
🔍 {reviewer} ({review_state}) - {review_date}
{review_body or 'No comment'}
"""
        
        # Add comments
        if comments:
            result += "\n\nComments:\n"
            for comment in comments[-5:]:  # Last 5 comments
                commenter = comment.get("user", {}).get("login", "")
                comment_body = comment.get("body", "")
                comment_date = comment.get("created_at", "")
                
                result += f"""
💬 {commenter} - {comment_date}
{comment_body}
"""
        
        return result

    def _format_commits(self, commits_data: List[Dict]) -> str:
        """Format commit history"""
        if not commits_data:
            return "No commits found."
        
        result = [f"Recent commits ({len(commits_data)}):\n"]
        
        for commit in commits_data:
            commit_info = commit.get("commit", {})
            message = commit_info.get("message", "")
            author = commit_info.get("author", {}).get("name", "")
            date = commit_info.get("author", {}).get("date", "")
            sha = commit.get("sha", "")[:8]
            url = commit.get("html_url", "")
            
            # Get first line of commit message
            first_line = message.split('\n')[0]
            
            result.append(f"""
🔧 {sha}: {first_line}
   Author: {author} | Date: {date}
   URL: {url}
""")
        
        return "".join(result)

# Import MCPToolResult from parent module
from mcp.server import MCPToolResult