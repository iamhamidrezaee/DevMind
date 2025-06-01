"""
🏆 DevMind: AI Team Memory Oracle
Track 3: Agentic Demo Showcase

An intelligent development context oracle that creates a living memory of your team's decisions,
code changes, and discussions. Goes beyond simple search to provide predictive insights and
visual knowledge graphs of how decisions impact your codebase.

INNOVATION FEATURES:
- 🧠 Predictive Impact Analysis: AI predicts how decisions will affect future development
- 📊 Visual Knowledge Graph: See how code, decisions, and discussions interconnect  
- 🔮 Pattern Recognition: Identifies recurring issues before they become problems
- 🤝 Real-time Team Context: Collaborative memory that learns from team interactions
- 🎯 Decision Impact Tracking: Shows consequences of past architectural choices

Built for Agents & MCP Hackathon 2025 - Track 3
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import requests
import json
import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import asyncio
import anthropic
import os
from pathlib import Path

# Configure for Hugging Face Spaces
os.environ.setdefault('GRADIO_TEMP_DIR', '/tmp')

@dataclass
class ContextItem:
    """Represents a piece of development context"""
    id: str
    source: str
    type: str
    title: str
    content: str
    author: str
    timestamp: str
    tags: List[str]
    impact_score: float
    connections: List[str]

class GitHubIntegrator:
    """Real GitHub API integration"""
    
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://api.github.com"
    
    def get_repo_context(self, repo_url: str) -> List[ContextItem]:
        """Fetch real repository context"""
        try:
            # Extract owner/repo from URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return []
            
            owner, repo = parts[0], parts[1]
            
            # Fetch recent commits, issues, PRs
            context_items = []
            
            # Get recent commits
            commits_url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            headers = {"Authorization": f"token {self.token}"} if self.token else {}
            
            try:
                response = requests.get(commits_url, headers=headers, params={"per_page": 10})
                if response.status_code == 200:
                    commits = response.json()
                    for commit in commits[:5]:  # Latest 5 commits
                        context_items.append(ContextItem(
                            id=f"commit_{commit['sha'][:8]}",
                            source="github",
                            type="commit",
                            title=f"Commit: {commit['commit']['message'][:60]}...",
                            content=commit['commit']['message'],
                            author=commit['commit']['author']['name'],
                            timestamp=commit['commit']['author']['date'],
                            tags=["code", "development"],
                            impact_score=0.7,
                            connections=[]
                        ))
            except Exception as e:
                print(f"Error fetching commits: {e}")
            
            # Get recent issues
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            try:
                response = requests.get(issues_url, headers=headers, params={"per_page": 10, "state": "all"})
                if response.status_code == 200:
                    issues = response.json()
                    for issue in issues[:5]:
                        context_items.append(ContextItem(
                            id=f"issue_{issue['number']}",
                            source="github",
                            type="issue",
                            title=f"Issue #{issue['number']}: {issue['title']}",
                            content=issue['body'] or "No description",
                            author=issue['user']['login'],
                            timestamp=issue['created_at'],
                            tags=["bug", "feature"] if "bug" in issue['title'].lower() else ["feature"],
                            impact_score=0.8 if issue['state'] == 'open' else 0.5,
                            connections=[]
                        ))
            except Exception as e:
                print(f"Error fetching issues: {e}")
                
            return context_items
            
        except Exception as e:
            print(f"Error in GitHub integration: {e}")
            return []

class DevMindAgent:
    """Agentic AI that analyzes development context and provides predictive insights"""
    
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.github = GitHubIntegrator()
        self.context_memory = []
        
    def analyze_context(self, query: str, github_repo: str = None) -> Dict[str, Any]:
        """Main agentic analysis function"""
        
        # 1. Gather context from multiple sources
        context_items = []
        
        if github_repo:
            github_context = self.github.get_repo_context(github_repo)
            context_items.extend(github_context)
        
        # Add some demo context for hackathon purposes
        context_items.extend(self._get_demo_context())
        
        # 2. Create knowledge graph
        knowledge_graph = self._build_knowledge_graph(context_items)
        
        # 3. Get AI analysis with predictive insights
        ai_analysis = self._get_ai_insights(query, context_items)
        
        # 4. Generate visual representations
        graph_viz = self._create_graph_visualization(knowledge_graph)
        impact_chart = self._create_impact_timeline(context_items)
        
        return {
            "ai_response": ai_analysis,
            "context_items": context_items,
            "knowledge_graph": graph_viz,
            "impact_timeline": impact_chart,
            "predictions": self._generate_predictions(context_items),
            "recommendations": self._generate_recommendations(context_items)
        }
    
    def _get_demo_context(self) -> List[ContextItem]:
        """Rich demo context for hackathon demonstration"""
        return [
            ContextItem(
                id="decision_auth",
                source="slack",
                type="decision",
                title="Authentication Architecture Decision",
                content="Team decided to use JWT tokens with Redis for session management after security review",
                author="sarah_dev",
                timestamp="2024-05-28T10:30:00Z",
                tags=["security", "architecture", "authentication"],
                impact_score=0.9,
                connections=["commit_auth_impl", "issue_session_bug"]
            ),
            ContextItem(
                id="commit_auth_impl",
                source="github", 
                type="commit",
                title="Implement JWT authentication system",
                content="Added JWT middleware, Redis session store, and authentication routes",
                author="mike_backend",
                timestamp="2024-05-29T14:15:00Z",
                tags=["implementation", "security"],
                impact_score=0.8,
                connections=["decision_auth", "issue_session_bug"]
            ),
            ContextItem(
                id="issue_session_bug",
                source="github",
                type="issue", 
                title="Users randomly logged out - session persistence issue",
                content="Multiple users reporting unexpected logouts. Possibly related to Redis configuration",
                author="lisa_qa",
                timestamp="2024-05-30T09:20:00Z",
                tags=["bug", "session", "urgent"],
                impact_score=0.95,
                connections=["decision_auth", "commit_auth_impl"]
            ),
            ContextItem(
                id="meeting_performance",
                source="confluence",
                type="meeting",
                title="Performance Review - API Response Times",
                content="Database queries taking 2-3s average. Need to implement caching layer",
                author="team_lead",
                timestamp="2024-05-27T16:00:00Z", 
                tags=["performance", "database", "optimization"],
                impact_score=0.7,
                connections=["commit_cache_impl"]
            ),
            ContextItem(
                id="commit_cache_impl",
                source="github",
                type="commit",
                title="Add Redis caching for database queries",
                content="Implemented Redis caching middleware for frequent database operations",
                author="alex_dev",
                timestamp="2024-05-31T11:45:00Z",
                tags=["performance", "caching"],
                impact_score=0.6,
                connections=["meeting_performance"]
            )
        ]
    
    def _build_knowledge_graph(self, context_items: List[ContextItem]) -> nx.Graph:
        """Build network graph of how context items relate"""
        G = nx.Graph()
        
        # Add nodes
        for item in context_items:
            G.add_node(item.id, 
                      title=item.title,
                      type=item.type,
                      source=item.source,
                      impact=item.impact_score,
                      author=item.author)
        
        # Add edges based on connections and semantic similarity
        for item in context_items:
            for connection in item.connections:
                if connection in [other.id for other in context_items]:
                    G.add_edge(item.id, connection, weight=0.8)
            
            # Add semantic connections (simplified)
            for other in context_items:
                if item.id != other.id:
                    shared_tags = set(item.tags) & set(other.tags)
                    if shared_tags:
                        weight = len(shared_tags) * 0.3
                        if weight > 0.5:
                            G.add_edge(item.id, other.id, weight=weight)
        
        return G
    
    def _get_ai_insights(self, query: str, context_items: List[ContextItem]) -> str:
        """Get AI analysis with predictive insights"""
        
        context_text = "\n\n".join([
            f"[{item.source.upper()}] {item.type}: {item.title}\n"
            f"Author: {item.author} | Impact: {item.impact_score}\n"
            f"Content: {item.content}\n"
            f"Tags: {', '.join(item.tags)}"
            for item in context_items
        ])
        
        prompt = f"""You are DevMind, an advanced AI development oracle. Analyze the development context and provide insights that go beyond simple search.

QUERY: {query}

DEVELOPMENT CONTEXT:
{context_text}

Provide a comprehensive analysis that includes:
1. **Direct Answer**: Address the specific query
2. **Pattern Recognition**: Identify patterns across different sources
3. **Predictive Insights**: Predict potential future issues based on current trends
4. **Decision Impact**: How past decisions are affecting current state
5. **Actionable Recommendations**: Specific next steps

Be insightful, predictive, and focus on connecting the dots across different pieces of context.
"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"AI Analysis unavailable: {e}"
    
    def _create_graph_visualization(self, graph: nx.Graph) -> go.Figure:
        """Create interactive knowledge graph visualization"""
        if len(graph.nodes()) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No data to display", x=0.5, y=0.5)
            return fig
        
        # Use spring layout for positioning
        pos = nx.spring_layout(graph, k=3, iterations=50)
        
        # Extract node info
        node_x = [pos[node][0] for node in graph.nodes()]
        node_y = [pos[node][1] for node in graph.nodes()]
        node_text = [graph.nodes[node]['title'][:30] + "..." for node in graph.nodes()]
        node_color = [graph.nodes[node]['impact'] for node in graph.nodes()]
        node_type = [graph.nodes[node]['type'] for node in graph.nodes()]
        
        # Create edges
        edge_x = []
        edge_y = []
        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create the plot
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y,
                                line=dict(width=1, color='rgba(136,136,136,0.5)'),
                                hoverinfo='none',
                                mode='lines',
                                showlegend=False))
        
        # Add nodes
        fig.add_trace(go.Scatter(x=node_x, y=node_y,
                                mode='markers+text',
                                hoverinfo='text',
                                text=node_text,
                                textposition="middle center",
                                hovertext=[f"{node_type[i]}<br>{node_text[i]}" for i in range(len(node_text))],
                                marker=dict(size=50,
                                          color=node_color,
                                          colorscale='Viridis',
                                          colorbar=dict(title="Impact Score"),
                                          line=dict(width=2, color='white')),
                                showlegend=False))
        
        fig.update_layout(
            title="🧠 Development Knowledge Graph",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Nodes represent development artifacts. Lines show relationships. Color indicates impact level.",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor="left", yanchor="bottom",
                font=dict(color="gray", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def _create_impact_timeline(self, context_items: List[ContextItem]) -> go.Figure:
        """Create impact timeline visualization"""
        
        # Sort by timestamp
        sorted_items = sorted(context_items, key=lambda x: x.timestamp)
        
        dates = [datetime.datetime.fromisoformat(item.timestamp.replace('Z', '+00:00')) for item in sorted_items]
        impacts = [item.impact_score for item in sorted_items]
        titles = [item.title[:40] + "..." for item in sorted_items]
        types = [item.type for item in sorted_items]
        
        # Create color map for different types
        type_colors = {
            'commit': '#28a745',
            'issue': '#dc3545', 
            'decision': '#007bff',
            'meeting': '#ffc107',
            'discussion': '#6f42c1'
        }
        
        colors = [type_colors.get(t, '#6c757d') for t in types]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=impacts,
            mode='markers+lines',
            marker=dict(
                size=15,
                color=colors,
                line=dict(width=2, color='white')
            ),
            line=dict(width=2, color='rgba(136,136,136,0.6)'),
            text=titles,
            hovertemplate='<b>%{text}</b><br>Impact: %{y}<br>Date: %{x}<extra></extra>',
            name="Development Timeline"
        ))
        
        fig.update_layout(
            title="📈 Development Impact Timeline",
            xaxis_title="Time",
            yaxis_title="Impact Score",
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def _generate_predictions(self, context_items: List[ContextItem]) -> List[str]:
        """Generate predictive insights based on patterns"""
        predictions = []
        
        # Analyze patterns
        bug_items = [item for item in context_items if 'bug' in item.tags]
        high_impact_items = [item for item in context_items if item.impact_score > 0.8]
        
        if len(bug_items) > 2:
            predictions.append("🔮 Pattern Alert: High bug frequency detected. Consider implementing additional testing.")
        
        if len(high_impact_items) > 3:
            predictions.append("⚡ Impact Warning: Multiple high-impact changes in short timeframe. Monitor for system stability.")
        
        # Check for authentication-related patterns
        auth_items = [item for item in context_items if any(tag in ['authentication', 'security', 'session'] for tag in item.tags)]
        if len(auth_items) > 1:
            predictions.append("🔐 Security Focus: Authentication system undergoing changes. Ensure thorough security testing.")
        
        if not predictions:
            predictions.append("✅ System Stable: No concerning patterns detected in recent development activity.")
        
        return predictions
    
    def _generate_recommendations(self, context_items: List[ContextItem]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Analyze context for recommendations
        performance_items = [item for item in context_items if 'performance' in item.tags]
        if performance_items:
            recommendations.append("🚀 Performance: Consider implementing comprehensive performance monitoring and alerts.")
        
        bug_items = [item for item in context_items if 'bug' in item.tags]
        if bug_items:
            recommendations.append("🐛 Quality: Establish automated testing for areas showing frequent bugs.")
        
        security_items = [item for item in context_items if 'security' in item.tags]
        if security_items:
            recommendations.append("🔒 Security: Conduct security audit of authentication and session management.")
        
        recommendations.append("📊 Monitoring: Set up real-time alerts for critical system components.")
        recommendations.append("📝 Documentation: Ensure all architectural decisions are documented for team reference.")
        
        return recommendations

def create_devmind_interface():
    """Create the main Gradio interface"""
    
    def process_query(query: str, anthropic_key: str, github_repo: str = None):
        """Main processing function for Gradio interface"""
        
        if not anthropic_key:
            return "❌ Please provide your Anthropic API key", None, None, [], []
        
        if not query.strip():
            return "❌ Please enter a query", None, None, [], []
        
        try:
            # Initialize agent
            agent = DevMindAgent(anthropic_key)
            
            # Process query
            results = agent.analyze_context(query, github_repo)
            
            # Format context for display
            context_display = []
            for item in results["context_items"]:
                context_display.append({
                    "Source": item.source.upper(),
                    "Type": item.type,
                    "Title": item.title,
                    "Author": item.author,
                    "Impact": f"{item.impact_score:.2f}",
                    "Tags": ", ".join(item.tags)
                })
            
            return (
                results["ai_response"],
                results["knowledge_graph"],
                results["impact_timeline"],
                results["predictions"],
                results["recommendations"]
            )
            
        except Exception as e:
            error_msg = f"❌ Error processing query: {str(e)}"
            return error_msg, None, None, [], []
    
    # Create the interface
    with gr.Blocks(
        title="🧠 DevMind: AI Team Memory Oracle",
        theme=gr.themes.Soft(primary_hue="blue"),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .prediction-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🧠 DevMind: AI Team Memory Oracle
        ### *Predictive Development Context Intelligence*
        
        DevMind creates a living memory of your team's development decisions, connecting code changes,
        discussions, and issues to provide **predictive insights** about your project's future.
        
        **🎯 Track 3: Agentic Demo Showcase | Agents & MCP Hackathon 2025**
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="💭 Ask DevMind",
                    placeholder="e.g., 'What authentication issues are we facing?' or 'Show me performance bottlenecks'",
                    lines=3
                )
                
                with gr.Row():
                    anthropic_key = gr.Textbox(
                        label="🔑 Anthropic API Key",
                        type="password",
                        placeholder="sk-ant-..."
                    )
                    github_repo = gr.Textbox(
                        label="📚 GitHub Repository (optional)",
                        placeholder="https://github.com/owner/repo"
                    )
                
                submit_btn = gr.Button("🚀 Analyze Context", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                gr.Markdown("""
                ### 🎯 Example Queries
                - *"What decisions led to our current authentication issues?"*
                - *"Show me how performance optimizations connect to user complaints"*
                - *"What patterns indicate future scaling problems?"*
                - *"How do recent commits relate to open bugs?"*
                """)
        
        with gr.Row():
            ai_response = gr.Textbox(
                label="🤖 AI Analysis & Insights",
                lines=12,
                max_lines=20
            )
        
        with gr.Row():
            with gr.Column():
                knowledge_graph = gr.Plot(
                    label="🧠 Knowledge Graph - How Everything Connects"
                )
            with gr.Column():
                impact_timeline = gr.Plot(
                    label="📈 Impact Timeline - Development Activity"
                )
        
        with gr.Row():
            with gr.Column():
                predictions = gr.JSON(
                    label="🔮 Predictive Insights",
                    elem_classes=["prediction-box"]
                )
            with gr.Column():
                recommendations = gr.JSON(
                    label="💡 AI Recommendations"
                )
        
        # Example queries for quick testing
        gr.Examples(
            examples=[
                ["What authentication issues are we facing?", "", ""],
                ["Show me performance bottlenecks and their impact", "", ""],
                ["How do recent commits connect to open bugs?", "", ""],
                ["What patterns indicate future scaling problems?", "", ""]
            ],
            inputs=[query_input, anthropic_key, github_repo]
        )
        
        submit_btn.click(
            fn=process_query,
            inputs=[query_input, anthropic_key, github_repo],
            outputs=[ai_response, knowledge_graph, impact_timeline, predictions, recommendations]
        )
        
        gr.Markdown("""
        ---
        ### 🏆 Why DevMind Wins
        
        **Beyond Simple Search**: DevMind doesn't just find information - it predicts future problems and shows how decisions cascade through your development process.
        
        **Key Innovations**:
        - 🧠 **Visual Knowledge Graphs**: See how code, decisions, and discussions interconnect
        - 🔮 **Predictive Analytics**: AI identifies patterns that indicate future issues  
        - 📊 **Impact Tracking**: Understand how past decisions affect current problems
        - 🤝 **Team Memory**: Creates persistent context that learns from your team's interactions
        
        *Built for the Agents & MCP Hackathon 2025 - Showcasing the future of agentic development tools.*
        """)
    
    return demo

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_devmind_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
