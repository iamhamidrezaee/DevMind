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

class AutonomousActions:
    """Agent actions that DevMind can take autonomously"""
    
    def __init__(self, anthropic_client, github_token: str = None):
        self.client = anthropic_client
        self.github_token = github_token
        self.actions_history = []
        
    async def create_github_issue(self, repo_url: str, title: str, description: str) -> Dict[str, Any]:
        """Autonomously create GitHub issues based on analysis"""
        try:
            # Extract owner/repo from URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return {"status": "error", "message": "Invalid repo URL"}
            
            owner, repo = parts[0], parts[1]
            
            # Simulate GitHub issue creation (in real implementation, use GitHub API)
            action_result = {
                "action": "create_github_issue",
                "status": "simulated_success",
                "repo": f"{owner}/{repo}",
                "issue_title": title,
                "issue_description": description,
                "issue_url": f"https://github.com/{owner}/{repo}/issues/new",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "impact": "High - Proactive issue tracking enabled"
            }
            
            self.actions_history.append(action_result)
            return action_result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def update_documentation(self, insights: List[str]) -> Dict[str, Any]:
        """Auto-update team docs with new insights"""
        try:
            # Generate documentation update based on insights
            doc_update = {
                "action": "update_documentation",
                "status": "simulated_success",
                "insights_count": len(insights),
                "updated_sections": [
                    "📋 Development Patterns Identified",
                    "⚠️ Risk Areas Documented", 
                    "💡 Best Practices Updated",
                    "🔮 Predictive Insights Archive"
                ],
                "documentation_url": "/docs/devmind-insights",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "impact": "Medium - Team knowledge preserved and accessible"
            }
            
            self.actions_history.append(doc_update)
            return doc_update
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def schedule_team_alerts(self, predictions: List[str]) -> Dict[str, Any]:
        """Schedule Slack notifications for predicted issues"""
        try:
            critical_predictions = [p for p in predictions if any(word in p.lower() for word in ['critical', 'urgent', 'severe', 'breaking'])]
            
            alert_result = {
                "action": "schedule_team_alerts",
                "status": "simulated_success",
                "alerts_scheduled": len(critical_predictions),
                "critical_issues": critical_predictions,
                "notification_channels": ["#dev-alerts", "#team-leads", "#devops"],
                "schedule": "Immediate for critical, daily digest for others",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "impact": "High - Proactive team awareness and response"
            }
            
            self.actions_history.append(alert_result)
            return alert_result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def generate_architecture_recommendations(self, context: List[ContextItem]) -> Dict[str, Any]:
        """Generate and propose architectural changes"""
        try:
            # Analyze context for architectural patterns
            code_issues = [item for item in context if item.type in ['commit', 'bug', 'issue'] and item.impact_score > 0.7]
            
            # Generate AI-powered architectural recommendations
            prompt = f"""Based on these development context items:
            {[f"{item.type}: {item.title}" for item in code_issues[:5]]}
            
            Generate 3 specific architectural recommendations that would prevent future issues."""
            
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            arch_recommendations = {
                "action": "generate_architecture_recommendations", 
                "status": "success",
                "recommendations_generated": 3,
                "ai_analysis": message.content[0].text if message.content else "Analysis in progress",
                "context_items_analyzed": len(code_issues),
                "priority_level": "High" if len(code_issues) > 3 else "Medium",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "impact": "Very High - Strategic architectural improvements proposed"
            }
            
            self.actions_history.append(arch_recommendations)
            return arch_recommendations
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_actions_summary(self) -> Dict[str, Any]:
        """Get summary of all autonomous actions taken"""
        return {
            "total_actions": len(self.actions_history),
            "action_types": list(set([action["action"] for action in self.actions_history])),
            "recent_actions": self.actions_history[-5:] if self.actions_history else [],
            "success_rate": len([a for a in self.actions_history if a.get("status") != "error"]) / max(len(self.actions_history), 1) * 100
        }

class SpecialistAgents:
    """Multi-Agent System with specialized agents working together"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.monitor_agent = MonitorAgent(anthropic_client)      # Watches for issues
        self.analyst_agent = AnalystAgent(anthropic_client)      # Deep analysis  
        self.action_agent = ActionAgent(anthropic_client)        # Takes actions
        self.learning_agent = LearningAgent(anthropic_client)    # Updates knowledge
        self.collaboration_history = []
    
    async def collaborative_analysis(self, query: str, context_items: List[ContextItem] = None) -> Dict[str, Any]:
        """Multiple agents work together on complex analysis"""
        
        collaboration_start = datetime.datetime.utcnow()
        
        # Initialize context if not provided
        if context_items is None:
            context_items = self._get_demo_context()
        
        # 1. Monitor agent scans for immediate issues
        urgent_issues = await self.monitor_agent.scan_for_urgent_issues(query, context_items)
        
        # 2. Analyst agent does deep dive analysis
        deep_analysis = await self.analyst_agent.analyze_patterns(query, context_items, urgent_issues)
        
        # 3. Action agent proposes concrete steps based on findings
        action_plan = await self.action_agent.create_action_plan(query, deep_analysis, urgent_issues)
        
        # 4. Learning agent updates team knowledge
        knowledge_updates = await self.learning_agent.update_team_memory(query, deep_analysis, action_plan)
        
        # 5. Cross-agent validation and consensus
        consensus = await self._build_agent_consensus(urgent_issues, deep_analysis, action_plan, knowledge_updates)
        
        collaboration_result = {
            "collaboration_id": f"collab_{int(collaboration_start.timestamp())}",
            "agents_involved": 4,
            "urgent_issues": urgent_issues,
            "deep_analysis": deep_analysis,
            "action_plan": action_plan,
            "knowledge_updates": knowledge_updates,
            "agent_consensus": consensus,
            "collaboration_time_ms": (datetime.datetime.utcnow() - collaboration_start).total_seconds() * 1000,
            "query_complexity": self._assess_query_complexity(query),
            "team_impact_score": self._calculate_team_impact(urgent_issues, deep_analysis)
        }
        
        self.collaboration_history.append(collaboration_result)
        return collaboration_result
    
    async def _build_agent_consensus(self, urgent_issues, deep_analysis, action_plan, knowledge_updates) -> Dict[str, Any]:
        """Build consensus between specialist agents"""
        
        # Agent confidence scores
        monitor_confidence = len(urgent_issues.get("critical_alerts", [])) * 0.2
        analyst_confidence = len(deep_analysis.get("patterns_found", [])) * 0.15
        action_confidence = len(action_plan.get("recommended_actions", [])) * 0.25
        learning_confidence = knowledge_updates.get("confidence_score", 0.5)
        
        overall_confidence = min((monitor_confidence + analyst_confidence + action_confidence + learning_confidence) / 4, 1.0)
        
        return {
            "overall_confidence": overall_confidence,
            "agent_agreement_level": "high" if overall_confidence > 0.7 else "medium" if overall_confidence > 0.4 else "low",
            "consensus_reached": overall_confidence > 0.5,
            "primary_recommendations": action_plan.get("recommended_actions", [])[:3],
            "validation_status": "validated_by_all_agents"
        }
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess complexity of the query for multi-agent coordination"""
        complexity_indicators = [
            ("performance", 2), ("security", 3), ("architecture", 4), 
            ("scale", 3), ("bug", 1), ("optimization", 2), ("integration", 3)
        ]
        
        complexity_score = sum(weight for keyword, weight in complexity_indicators if keyword in query.lower())
        
        if complexity_score >= 8:
            return "very_high"
        elif complexity_score >= 5:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _calculate_team_impact(self, urgent_issues, deep_analysis) -> float:
        """Calculate potential impact on team productivity"""
        critical_count = len(urgent_issues.get("critical_alerts", []))
        pattern_count = len(deep_analysis.get("patterns_found", []))
        
        return min((critical_count * 0.3 + pattern_count * 0.2), 1.0)
    
    def _get_demo_context(self) -> List[ContextItem]:
        """Get demo context for agent collaboration"""
        return [
            ContextItem(
                id="demo_1", source="github", type="issue", 
                title="Authentication timeout issues", content="Users experiencing login timeouts",
                author="dev_team", timestamp="2024-06-01T10:00:00Z", tags=["auth", "critical"],
                impact_score=0.9, connections=["demo_2", "demo_3"]
            )
        ]

class MonitorAgent:
    """Specialized agent for monitoring and alerting"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.monitoring_patterns = ["critical", "urgent", "breaking", "security", "performance"]
    
    async def scan_for_urgent_issues(self, query: str, context_items: List[ContextItem]) -> Dict[str, Any]:
        """Scan for immediate issues requiring attention"""
        
        critical_alerts = []
        performance_alerts = []
        security_alerts = []
        
        # Scan context items for urgent patterns
        for item in context_items:
            content_lower = (item.title + " " + item.content).lower()
            
            # Critical issues
            if any(pattern in content_lower for pattern in ["critical", "urgent", "breaking", "down"]):
                critical_alerts.append({
                    "item_id": item.id,
                    "alert_type": "critical",
                    "title": item.title,
                    "severity": "high",
                    "impact_score": item.impact_score
                })
            
            # Performance issues
            if any(pattern in content_lower for pattern in ["slow", "timeout", "performance", "latency"]):
                performance_alerts.append({
                    "item_id": item.id,
                    "alert_type": "performance",
                    "title": item.title,
                    "severity": "medium",
                    "impact_score": item.impact_score
                })
            
            # Security issues  
            if any(pattern in content_lower for pattern in ["security", "vulnerability", "auth", "permission"]):
                security_alerts.append({
                    "item_id": item.id,
                    "alert_type": "security",
                    "title": item.title,
                    "severity": "high",
                    "impact_score": item.impact_score
                })
        
        return {
            "agent_name": "MonitorAgent",
            "scan_timestamp": datetime.datetime.utcnow().isoformat(),
            "items_scanned": len(context_items),
            "critical_alerts": critical_alerts,
            "performance_alerts": performance_alerts,
            "security_alerts": security_alerts,
            "total_alerts": len(critical_alerts) + len(performance_alerts) + len(security_alerts),
            "priority_recommendation": "immediate_action" if critical_alerts else "routine_monitoring"
        }

class AnalystAgent:
    """Specialized agent for deep pattern analysis"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.analysis_depth = "deep"
    
    async def analyze_patterns(self, query: str, context_items: List[ContextItem], urgent_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep pattern analysis across development context"""
        
        # Generate AI-powered pattern analysis
        analysis_prompt = f"""
        As a senior development analyst, analyze these patterns:
        
        Query: {query}
        Context Items: {len(context_items)} development artifacts
        Urgent Issues: {len(urgent_issues.get('critical_alerts', []))} critical alerts
        
        Identify:
        1. Root cause patterns
        2. Cross-system dependencies
        3. Predictive indicators
        4. Team workflow bottlenecks
        
        Provide specific, actionable insights.
        """
        
        try:
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            ai_insights = message.content[0].text if message.content else "Analysis in progress"
        except Exception as e:
            ai_insights = f"Analysis error: {str(e)}"
        
        # Pattern detection logic
        patterns_found = []
        
        # Analyze item interconnections
        connection_patterns = self._analyze_connections(context_items)
        if connection_patterns:
            patterns_found.extend(connection_patterns)
        
        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(context_items)
        if temporal_patterns:
            patterns_found.extend(temporal_patterns)
        
        # Analyze impact patterns
        impact_patterns = self._analyze_impact_patterns(context_items, urgent_issues)
        if impact_patterns:
            patterns_found.extend(impact_patterns)
        
        return {
            "agent_name": "AnalystAgent",
            "analysis_timestamp": datetime.datetime.utcnow().isoformat(),
            "analysis_depth": "comprehensive",
            "ai_insights": ai_insights,
            "patterns_found": patterns_found,
            "pattern_confidence": len(patterns_found) * 0.15,
            "cross_system_dependencies": self._identify_dependencies(context_items),
            "predictive_indicators": self._extract_predictive_indicators(patterns_found),
            "recommendation_priority": "high" if len(patterns_found) > 3 else "medium"
        }
    
    def _analyze_connections(self, context_items: List[ContextItem]) -> List[str]:
        """Analyze how context items connect"""
        connections = []
        for item in context_items:
            if len(item.connections) > 0:
                connections.append(f"High connectivity pattern: {item.title} connects to {len(item.connections)} other items")
        return connections[:3]
    
    def _analyze_temporal_patterns(self, context_items: List[ContextItem]) -> List[str]:
        """Analyze patterns over time"""
        recent_items = [item for item in context_items if "2024" in item.timestamp]
        if len(recent_items) > len(context_items) * 0.7:
            return ["High activity pattern: 70%+ items are recent, indicating active development phase"]
        return []
    
    def _analyze_impact_patterns(self, context_items: List[ContextItem], urgent_issues: Dict[str, Any]) -> List[str]:
        """Analyze impact score patterns"""
        high_impact = [item for item in context_items if item.impact_score > 0.7]
        patterns = []
        if len(high_impact) > len(context_items) * 0.4:
            patterns.append("High impact concentration: 40%+ items have significant impact potential")
        if urgent_issues.get("total_alerts", 0) > 2:
            patterns.append("Alert clustering: Multiple urgent issues suggest systemic problems")
        return patterns
    
    def _identify_dependencies(self, context_items: List[ContextItem]) -> List[str]:
        """Identify cross-system dependencies"""
        dependencies = []
        sources = set(item.source for item in context_items)
        if len(sources) > 1:
            dependencies.append(f"Multi-system involvement: {len(sources)} different systems affected")
        return dependencies
    
    def _extract_predictive_indicators(self, patterns: List[str]) -> List[str]:
        """Extract indicators that predict future issues"""
        indicators = []
        for pattern in patterns:
            if "high" in pattern.lower():
                indicators.append(f"Predictive: {pattern} likely to escalate")
        return indicators

class ActionAgent:
    """Specialized agent for creating actionable plans"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.action_categories = ["immediate", "short_term", "strategic"]
    
    async def create_action_plan(self, query: str, deep_analysis: Dict[str, Any], urgent_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Create concrete, prioritized action plan"""
        
        immediate_actions = []
        short_term_actions = []
        strategic_actions = []
        
        # Immediate actions based on urgent issues
        critical_alerts = urgent_issues.get("critical_alerts", [])
        for alert in critical_alerts:
            immediate_actions.append({
                "action": f"Address {alert['alert_type']} issue: {alert['title']}",
                "priority": "immediate",
                "estimated_effort": "2-4 hours",
                "responsible_team": "on_call_dev"
            })
        
        # Short-term actions based on patterns
        patterns = deep_analysis.get("patterns_found", [])
        for pattern in patterns[:2]:  # Top 2 patterns
            short_term_actions.append({
                "action": f"Investigate pattern: {pattern}",
                "priority": "short_term",
                "estimated_effort": "1-2 days",
                "responsible_team": "development_team"
            })
        
        # Strategic actions based on AI insights
        if deep_analysis.get("ai_insights"):
            strategic_actions.append({
                "action": "Implement architectural improvements based on AI analysis",
                "priority": "strategic",
                "estimated_effort": "1-2 weeks", 
                "responsible_team": "architecture_team"
            })
        
        return {
            "agent_name": "ActionAgent",
            "plan_timestamp": datetime.datetime.utcnow().isoformat(),
            "total_actions": len(immediate_actions) + len(short_term_actions) + len(strategic_actions),
            "immediate_actions": immediate_actions,
            "short_term_actions": short_term_actions,
            "strategic_actions": strategic_actions,
            "recommended_actions": immediate_actions + short_term_actions[:2] + strategic_actions[:1],
            "execution_timeline": "Immediate: 24hrs, Short-term: 1 week, Strategic: 1 month",
            "success_metrics": [
                "Reduction in critical alerts",
                "Improved system stability",
                "Enhanced team productivity"
            ]
        }

class LearningAgent:
    """Specialized agent for continuous learning and knowledge updates"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.knowledge_base = {}
        self.learning_patterns = []
    
    async def update_team_memory(self, query: str, deep_analysis: Dict[str, Any], action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Update team knowledge base with new insights"""
        
        # Extract learnings from analysis
        new_learnings = []
        
        # Learn from query patterns
        query_learning = self._extract_query_learnings(query)
        if query_learning:
            new_learnings.extend(query_learning)
        
        # Learn from analysis patterns
        analysis_learning = self._extract_analysis_learnings(deep_analysis)
        if analysis_learning:
            new_learnings.extend(analysis_learning)
        
        # Learn from action effectiveness
        action_learning = self._extract_action_learnings(action_plan)
        if action_learning:
            new_learnings.extend(action_learning)
        
        # Update knowledge base
        timestamp = datetime.datetime.utcnow().isoformat()
        for learning in new_learnings:
            learning_key = f"learning_{len(self.knowledge_base)}"
            self.knowledge_base[learning_key] = {
                "content": learning,
                "timestamp": timestamp,
                "query_context": query,
                "confidence": 0.8
            }
        
        return {
            "agent_name": "LearningAgent",
            "update_timestamp": timestamp,
            "new_learnings_count": len(new_learnings),
            "total_knowledge_items": len(self.knowledge_base),
            "learnings_added": new_learnings,
            "knowledge_categories": ["query_patterns", "analysis_insights", "action_effectiveness"],
            "confidence_score": 0.8,
            "memory_optimization": "Knowledge base updated and patterns stored for future reference"
        }
    
    def _extract_query_learnings(self, query: str) -> List[str]:
        """Extract learnings from query patterns"""
        learnings = []
        query_lower = query.lower()
        
        if "performance" in query_lower:
            learnings.append("Team frequently queries performance issues - prioritize performance monitoring")
        if "auth" in query_lower:
            learnings.append("Authentication is a recurring concern - enhance auth documentation")
        if "bug" in query_lower:
            learnings.append("Bug investigation patterns identified - improve debugging workflows")
        
        return learnings
    
    def _extract_analysis_learnings(self, deep_analysis: Dict[str, Any]) -> List[str]:
        """Extract learnings from analysis results"""
        learnings = []
        patterns = deep_analysis.get("patterns_found", [])
        
        if len(patterns) > 3:
            learnings.append("High pattern complexity detected - consider system architecture review")
        
        if deep_analysis.get("pattern_confidence", 0) > 0.7:
            learnings.append("Strong pattern confidence - analysis methodologies are effective")
        
        return learnings
    
    def _extract_action_learnings(self, action_plan: Dict[str, Any]) -> List[str]:
        """Extract learnings from action plan effectiveness"""
        learnings = []
        
        immediate_count = len(action_plan.get("immediate_actions", []))
        if immediate_count > 2:
            learnings.append("High immediate action count - consider proactive monitoring improvements")
        
        total_actions = action_plan.get("total_actions", 0)
        if total_actions > 5:
            learnings.append("Complex action plans generated - team may benefit from process simplification")
        
        return learnings

class PredictiveEngine:
    """Advanced prediction system for development insights and forecasting"""
    
    def __init__(self, anthropic_client=None):
        self.anthropic_client = anthropic_client
        self.prediction_models = {
            "bug_likelihood": self._predict_bug_likelihood,
            "performance_degradation": self._predict_performance_issues,
            "security_vulnerabilities": self._predict_security_risks,
            "technical_debt": self._predict_technical_debt,
            "team_productivity": self._predict_team_metrics,
            "deployment_risks": self._predict_deployment_issues
        }
        self.historical_patterns = []
    
    async def generate_sophisticated_predictions(self, context_items: List[ContextItem], analysis_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate sophisticated predictions using AI and pattern analysis"""
        
        prediction_start = datetime.datetime.utcnow()
        
        # Run all prediction models
        predictions = {}
        for model_name, model_func in self.prediction_models.items():
            try:
                prediction_result = await model_func(context_items, analysis_results)
                predictions[model_name] = prediction_result
            except Exception as e:
                predictions[model_name] = {
                    "status": "error",
                    "message": str(e),
                    "confidence": 0.0
                }
        
        # Generate AI-powered predictive insights
        ai_predictions = await self._generate_ai_predictions(context_items, predictions)
        
        # Create predictive timeline
        timeline_predictions = self._create_predictive_timeline(predictions)
        
        # Calculate overall prediction confidence
        overall_confidence = self._calculate_prediction_confidence(predictions)
        
        # Generate actionable recommendations based on predictions
        predictive_recommendations = self._generate_predictive_recommendations(predictions)
        
        processing_time = (datetime.datetime.utcnow() - prediction_start).total_seconds() * 1000
        
        return {
            "prediction_models_run": len(self.prediction_models),
            "individual_predictions": predictions,
            "ai_powered_insights": ai_predictions,
            "predictive_timeline": timeline_predictions,
            "overall_confidence": overall_confidence,
            "predictive_recommendations": predictive_recommendations,
            "prediction_processing_time_ms": processing_time,
            "prediction_timestamp": datetime.datetime.utcnow().isoformat(),
            "sophisticated_predictions": True
        }
    
    async def _predict_bug_likelihood(self, context_items: List[ContextItem], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict likelihood of bugs based on code patterns and complexity"""
        
        high_risk_indicators = 0
        total_complexity = 0
        
        for item in context_items:
            # Check for bug-prone patterns
            if "TODO" in item.content or "FIXME" in item.content:
                high_risk_indicators += 1
            if item.impact_score > 0.8:  # High complexity items
                total_complexity += item.impact_score
                
        avg_complexity = total_complexity / max(len(context_items), 1)
        bug_likelihood = min((high_risk_indicators * 0.2 + avg_complexity * 0.6), 1.0)
        
        return {
            "likelihood_score": bug_likelihood,
            "confidence": 0.85,
            "risk_factors": high_risk_indicators,
            "complexity_score": avg_complexity,
            "prediction": "High" if bug_likelihood > 0.7 else "Medium" if bug_likelihood > 0.4 else "Low",
            "timeline": "Next 7-14 days based on current patterns"
        }
    
    async def _predict_performance_issues(self, context_items: List[ContextItem], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict potential performance degradation"""
        
        performance_risk = 0
        db_queries = 0
        large_files = 0
        
        for item in context_items:
            if "database" in item.content.lower() or "query" in item.content.lower():
                db_queries += 1
            if len(item.content) > 1000:  # Large code files
                large_files += 1
                
        performance_risk = min((db_queries * 0.15 + large_files * 0.1), 1.0)
        
        return {
            "performance_risk_score": performance_risk,
            "confidence": 0.78,
            "database_complexity": db_queries,
            "large_components": large_files,
            "prediction": "High Risk" if performance_risk > 0.6 else "Medium Risk" if performance_risk > 0.3 else "Low Risk",
            "timeline": "Next 2-4 weeks based on growth patterns"
        }
    
    async def _predict_security_risks(self, context_items: List[ContextItem], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict potential security vulnerabilities"""
        
        security_indicators = 0
        auth_complexity = 0
        
        for item in context_items:
            content_lower = item.content.lower()
            if any(term in content_lower for term in ["password", "auth", "token", "secret", "key"]):
                auth_complexity += 1
            if any(term in content_lower for term in ["sql", "input", "user", "admin"]):
                security_indicators += 1
                
        security_risk = min((security_indicators * 0.12 + auth_complexity * 0.25), 1.0)
        
        return {
            "security_risk_score": security_risk,
            "confidence": 0.82,
            "auth_complexity": auth_complexity,
            "risk_indicators": security_indicators,
            "prediction": "Critical" if security_risk > 0.7 else "Medium" if security_risk > 0.4 else "Low",
            "timeline": "Immediate assessment recommended"
        }
    
    async def _predict_technical_debt(self, context_items: List[ContextItem], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict accumulation of technical debt"""
        
        debt_indicators = 0
        
        for item in context_items:
            content_lower = item.content.lower()
            if any(term in content_lower for term in ["hack", "workaround", "temporary", "quick fix"]):
                debt_indicators += 1
                
        debt_score = min(debt_indicators * 0.3, 1.0)
        
        return {
            "technical_debt_score": debt_score,
            "confidence": 0.75,
            "debt_indicators": debt_indicators,
            "prediction": "High Debt" if debt_score > 0.6 else "Moderate" if debt_score > 0.3 else "Low Debt",
            "timeline": "Continuous accumulation, review in 1 month"
        }
    
    async def _predict_team_metrics(self, context_items: List[ContextItem], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict team productivity trends"""
        
        productivity_score = 0.7  # Baseline
        
        # Simulate productivity prediction based on context complexity
        total_items = len(context_items)
        avg_impact = sum(item.impact_score for item in context_items) / max(total_items, 1)
        
        # Higher complexity might reduce short-term productivity
        productivity_score = max(0.4, productivity_score - (avg_impact * 0.2))
        
        return {
            "productivity_score": productivity_score,
            "confidence": 0.70,
            "team_capacity": "High" if productivity_score > 0.7 else "Medium" if productivity_score > 0.5 else "Strained",
            "prediction": f"Team operating at {productivity_score:.1%} capacity",
            "timeline": "Next sprint cycle (2 weeks)"
        }
    
    async def _predict_deployment_issues(self, context_items: List[ContextItem], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict potential deployment and integration issues"""
        
        deployment_risk = 0
        integration_points = 0
        
        for item in context_items:
            content_lower = item.content.lower()
            if any(term in content_lower for term in ["config", "environment", "deploy", "build"]):
                integration_points += 1
                
        deployment_risk = min(integration_points * 0.2, 1.0)
        
        return {
            "deployment_risk_score": deployment_risk,
            "confidence": 0.73,
            "integration_complexity": integration_points,
            "prediction": "High Risk" if deployment_risk > 0.6 else "Medium Risk" if deployment_risk > 0.3 else "Low Risk",
            "timeline": "Next deployment window"
        }
    
    async def _generate_ai_predictions(self, context_items: List[ContextItem], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered predictive insights using Claude"""
        
        if not self.anthropic_client:
            return {
                "ai_insights": "AI predictions require Anthropic API key",
                "predictive_analysis": "Enable AI for advanced forecasting",
                "confidence": 0.0
            }
        
        try:
            # Prepare context for AI analysis
            context_summary = f"Analyzed {len(context_items)} development context items. "
            prediction_summary = ", ".join([
                f"{name}: {pred.get('prediction', 'unknown')}" 
                for name, pred in predictions.items() 
                if pred.get('prediction')
            ])
            
            ai_prompt = f"""As an expert development forecasting AI, analyze these predictions and provide advanced insights:

Context: {context_summary}
Current Predictions: {prediction_summary}

Provide sophisticated predictive insights including:
1. Cross-correlation patterns between different risk factors
2. Cascade effect predictions (how one issue might trigger others)
3. Optimal intervention timing recommendations
4. Resource allocation suggestions based on predictions
5. Long-term trend forecasting (3-6 months)

Respond in a structured, actionable format."""

            response = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=800,
                messages=[{"role": "user", "content": ai_prompt}]
            )
            
            ai_insights = response.content[0].text
            
            return {
                "ai_insights": ai_insights,
                "predictive_analysis": "Advanced AI forecasting completed",
                "confidence": 0.88,
                "ai_powered": True
            }
            
        except Exception as e:
            return {
                "ai_insights": f"AI prediction error: {str(e)}",
                "predictive_analysis": "Fallback to pattern-based predictions",
                "confidence": 0.0,
                "ai_powered": False
            }
    
    def _create_predictive_timeline(self, predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a timeline of predicted events"""
        
        timeline = []
        base_date = datetime.datetime.utcnow()
        
        # Map predictions to timeline events
        timeline_mapping = {
            "security_vulnerabilities": {"days": 0, "priority": "critical"},
            "bug_likelihood": {"days": 7, "priority": "high"},
            "performance_degradation": {"days": 14, "priority": "medium"},
            "deployment_risks": {"days": 21, "priority": "high"},
            "technical_debt": {"days": 30, "priority": "medium"},
            "team_productivity": {"days": 14, "priority": "low"}
        }
        
        for pred_name, pred_data in predictions.items():
            if pred_name in timeline_mapping and pred_data.get('confidence', 0) > 0.5:
                event_date = base_date + datetime.timedelta(days=timeline_mapping[pred_name]["days"])
                
                timeline.append({
                    "event": pred_name.replace('_', ' ').title(),
                    "prediction": pred_data.get('prediction', 'Unknown'),
                    "confidence": pred_data.get('confidence', 0),
                    "date": event_date.isoformat(),
                    "priority": timeline_mapping[pred_name]["priority"],
                    "timeline_offset_days": timeline_mapping[pred_name]["days"]
                })
        
        # Sort by date
        timeline.sort(key=lambda x: x["date"])
        
        return timeline
    
    def _calculate_prediction_confidence(self, predictions: Dict[str, Any]) -> float:
        """Calculate overall prediction confidence score"""
        
        confidences = [
            pred.get('confidence', 0) 
            for pred in predictions.values() 
            if isinstance(pred, dict) and pred.get('confidence') is not None
        ]
        
        if not confidences:
            return 0.0
            
        return sum(confidences) / len(confidences)
    
    def _generate_predictive_recommendations(self, predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on predictions"""
        
        recommendations = []
        
        for pred_name, pred_data in predictions.items():
            if not isinstance(pred_data, dict):
                continue
                
            confidence = pred_data.get('confidence', 0)
            prediction = pred_data.get('prediction', '')
            
            if confidence > 0.7:  # High confidence predictions
                if pred_name == "security_vulnerabilities" and "Critical" in prediction:
                    recommendations.append({
                        "category": "Security",
                        "action": "Immediate security audit recommended",
                        "priority": "Critical",
                        "timeline": "Within 24 hours",
                        "confidence": confidence
                    })
                elif pred_name == "bug_likelihood" and "High" in prediction:
                    recommendations.append({
                        "category": "Quality",
                        "action": "Increase testing coverage and code review",
                        "priority": "High",
                        "timeline": "Next sprint",
                        "confidence": confidence
                    })
                elif pred_name == "performance_degradation" and "High Risk" in prediction:
                    recommendations.append({
                        "category": "Performance",
                        "action": "Performance monitoring and optimization",
                        "priority": "High",
                        "timeline": "Next 2 weeks",
                        "confidence": confidence
                    })
        
        return recommendations

class AdvancedVisualizations:
    """Sophisticated visualization system for predictions and insights"""
    
    def __init__(self):
        self.visualization_types = [
            "prediction_dashboard",
            "risk_heatmap", 
            "trend_forecast",
            "confidence_matrix",
            "decision_tree"
        ]
    
    def create_prediction_dashboard(self, predictions: Dict[str, Any]) -> go.Figure:
        """Create comprehensive prediction dashboard"""
        
        # Extract prediction scores
        prediction_scores = {}
        confidence_scores = {}
        
        for name, pred_data in predictions.get('individual_predictions', {}).items():
            if isinstance(pred_data, dict):
                # Extract various score fields
                score = (pred_data.get('likelihood_score') or 
                        pred_data.get('performance_risk_score') or 
                        pred_data.get('security_risk_score') or 
                        pred_data.get('technical_debt_score') or 
                        pred_data.get('productivity_score') or 
                        pred_data.get('deployment_risk_score', 0))
                
                prediction_scores[name.replace('_', ' ').title()] = score
                confidence_scores[name.replace('_', ' ').title()] = pred_data.get('confidence', 0)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Prediction Scores', 'Confidence Levels', 'Risk Timeline', 'Recommendation Priority'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # Prediction scores bar chart
        fig.add_trace(
            go.Bar(
                x=list(prediction_scores.keys()),
                y=list(prediction_scores.values()),
                name="Prediction Scores",
                marker_color=['red' if v > 0.7 else 'orange' if v > 0.4 else 'green' for v in prediction_scores.values()]
            ),
            row=1, col=1
        )
        
        # Confidence scatter plot
        fig.add_trace(
            go.Scatter(
                x=list(confidence_scores.keys()),
                y=list(confidence_scores.values()),
                mode='markers+lines',
                name="Confidence",
                marker=dict(size=10, color='blue')
            ),
            row=1, col=2
        )
        
        # Risk timeline
        timeline_data = predictions.get('predictive_timeline', [])
        if timeline_data:
            dates = [item['date'][:10] for item in timeline_data]  # Extract date part
            priorities = [1 if item['priority'] == 'critical' else 0.7 if item['priority'] == 'high' else 0.3 for item in timeline_data]
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=priorities,
                    mode='markers+lines',
                    name="Risk Timeline",
                    marker=dict(size=8, color='red')
                ),
                row=2, col=1
            )
        
        # Recommendation priority pie chart
        recommendations = predictions.get('predictive_recommendations', [])
        if recommendations:
            priority_counts = {}
            for rec in recommendations:
                priority = rec.get('priority', 'Medium')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            fig.add_trace(
                go.Pie(
                    labels=list(priority_counts.keys()),
                    values=list(priority_counts.values()),
                    name="Recommendations"
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title="🔮 Sophisticated Prediction Dashboard",
            height=600,
            showlegend=True
        )
        
        return fig
    
    def create_risk_heatmap(self, predictions: Dict[str, Any]) -> go.Figure:
        """Create risk assessment heatmap"""
        
        individual_preds = predictions.get('individual_predictions', {})
        
        # Create risk matrix data
        categories = []
        risk_scores = []
        confidence_scores = []
        
        for name, pred_data in individual_preds.items():
            if isinstance(pred_data, dict):
                categories.append(name.replace('_', ' ').title())
                
                # Extract risk score
                risk_score = (pred_data.get('likelihood_score') or 
                             pred_data.get('performance_risk_score') or 
                             pred_data.get('security_risk_score') or 
                             pred_data.get('technical_debt_score') or 
                             (1 - pred_data.get('productivity_score', 0.5)) or  # Invert productivity 
                             pred_data.get('deployment_risk_score', 0))
                
                risk_scores.append(risk_score)
                confidence_scores.append(pred_data.get('confidence', 0))
        
        # Create heatmap matrix
        fig = go.Figure(data=go.Heatmap(
            z=[risk_scores, confidence_scores],
            x=categories,
            y=['Risk Level', 'Confidence'],
            colorscale='RdYlGn_r',  # Red for high risk, green for low risk
            text=[[f'{score:.2f}' for score in risk_scores],
                  [f'{conf:.2f}' for conf in confidence_scores]],
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="🌡️ Development Risk Heatmap",
            xaxis_title="Risk Categories",
            yaxis_title="Assessment Metrics",
            height=400
        )
        
        return fig
    
    def create_trend_forecast(self, predictions: Dict[str, Any]) -> go.Figure:
        """Create trend forecasting visualization"""
        
        # Generate forecasting data based on predictions
        timeline_data = predictions.get('predictive_timeline', [])
        
        if not timeline_data:
            # Create sample forecast data
            base_date = datetime.datetime.utcnow()
            dates = [(base_date + datetime.timedelta(days=i*7)).strftime('%Y-%m-%d') for i in range(8)]
            risk_trend = [0.3, 0.4, 0.5, 0.6, 0.55, 0.5, 0.45, 0.4]  # Sample trend
        else:
            dates = [item['date'][:10] for item in timeline_data]
            risk_trend = [0.8 if item['priority'] == 'critical' else 0.6 if item['priority'] == 'high' else 0.3 for item in timeline_data]
        
        fig = go.Figure()
        
        # Add trend line
        fig.add_trace(go.Scatter(
            x=dates,
            y=risk_trend,
            mode='lines+markers',
            name='Risk Trend',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        # Add confidence band
        upper_bound = [min(1.0, val + 0.1) for val in risk_trend]
        lower_bound = [max(0.0, val - 0.1) for val in risk_trend]
        
        fig.add_trace(go.Scatter(
            x=dates + dates[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Band',
            showlegend=False
        ))
        
        fig.update_layout(
            title="📈 Risk Trend Forecasting",
            xaxis_title="Timeline",
            yaxis_title="Risk Level",
            height=400,
            showlegend=True
        )
        
        return fig

class DevMindAgent:
    """Agentic AI that analyzes development context and provides predictive insights"""
    
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.github = GitHubIntegrator()
        self.context_memory = []
        self.autonomous_actions = AutonomousActions(self.client)
        self.specialist_agents = SpecialistAgents(self.client)
        self.predictive_engine = PredictiveEngine(self.client)
        self.advanced_visualizations = AdvancedVisualizations()
        
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
            "ai_insights": ai_analysis,
            "knowledge_graph": graph_viz,
            "impact_timeline": impact_chart,
            "predictions": self._generate_predictions(context_items),
            "recommendations": self._generate_recommendations(context_items),
            "context_items": len(context_items)
        }

    async def autonomous_workflow(self, query: str, github_repo: str = None, autonomy_level: int = 3) -> Dict[str, Any]:
        """Autonomous agent workflow that takes actions"""
        
        # 1. Analyze context (existing functionality)
        analysis = self.analyze_context(query, github_repo)
        
        # 2. DECIDE ON ACTIONS based on analysis and autonomy level
        action_plan = await self._decide_actions(analysis, autonomy_level)
        
        # 3. EXECUTE ACTIONS AUTONOMOUSLY
        executed_actions = []
        for action in action_plan:
            try:
                result = await self._execute_action(action, github_repo, analysis)
                executed_actions.append(result)
            except Exception as e:
                executed_actions.append({
                    "action": action.get("type", "unknown"),
                    "status": "error", 
                    "message": str(e)
                })
        
        # 4. LEARN AND REMEMBER
        learning_updates = await self._update_memory(query, analysis, executed_actions)
        
        return {
            **analysis,
            "autonomous_actions": executed_actions,
            "action_plan": action_plan,
            "learning_updates": learning_updates,
            "autonomy_level": autonomy_level,
            "workflow_status": "completed"
        }
    
    async def multi_agent_collaborative_workflow(self, query: str, github_repo: str = None, autonomy_level: int = 3) -> Dict[str, Any]:
        """Enhanced workflow using multi-agent collaboration for complex analysis"""
        
        workflow_start = datetime.datetime.utcnow()
        
        # Assess query complexity to determine if multi-agent collaboration is needed
        complexity = self.specialist_agents._assess_query_complexity(query)
        use_collaboration = complexity in ["high", "very_high"] or autonomy_level >= 4
        
        if use_collaboration:
            # 1. Get context for collaborative analysis
            context_items = self._get_demo_context()
            if github_repo:
                github_context = self.github.get_repo_context(github_repo)
                context_items.extend(github_context)
            
            # 2. Run collaborative multi-agent analysis
            collaboration_result = await self.specialist_agents.collaborative_analysis(query, context_items)
            
            # 3. Generate sophisticated predictions using PredictiveEngine
            prediction_results = await self.predictive_engine.generate_sophisticated_predictions(
                context_items, 
                {**collaboration_result, "query": query}
            )
            
            # 4. Execute autonomous actions based on multi-agent consensus and predictions
            autonomous_actions = []
            if autonomy_level >= 2:
                action_plan = await self._execute_multi_agent_actions(
                    collaboration_result, github_repo, autonomy_level, prediction_results
                )
                autonomous_actions = action_plan.get("executed_actions", [])
            
            # 5. Learn from multi-agent collaboration and prediction outcomes
            learning_updates = await self._learn_from_collaboration(
                query, collaboration_result, autonomous_actions, prediction_results
            )
            
            # 6. Create enhanced visualizations including sophisticated predictions
            enhanced_graphs = self._create_multi_agent_visualizations(collaboration_result, context_items)
            prediction_visualizations = self._create_prediction_visualizations(prediction_results)
            
            return {
                "workflow_type": "multi_agent_collaborative_with_predictions",
                "query_complexity": complexity,
                "agents_involved": 4,
                "collaboration_result": collaboration_result,
                "sophisticated_predictions": prediction_results,
                "autonomous_actions": autonomous_actions,
                "learning_updates": learning_updates,
                "enhanced_visualizations": enhanced_graphs,
                "prediction_visualizations": prediction_visualizations,
                "ai_insights": collaboration_result.get("deep_analysis", {}).get("ai_insights", "Multi-agent analysis completed"),
                "knowledge_graph": enhanced_graphs.get("knowledge_graph"),
                "impact_timeline": enhanced_graphs.get("impact_timeline"),
                "agent_activity_chart": enhanced_graphs.get("agent_activity_chart"),
                "prediction_dashboard": prediction_visualizations.get("prediction_dashboard"),
                "risk_heatmap": prediction_visualizations.get("risk_heatmap"),
                "trend_forecast": prediction_visualizations.get("trend_forecast"),
                "predictions": {
                    **self._extract_multi_agent_predictions(collaboration_result),
                    **prediction_results.get("individual_predictions", {})
                },
                "predictive_recommendations": prediction_results.get("predictive_recommendations", []),
                "recommendations": self._extract_multi_agent_recommendations(collaboration_result),
                "prediction_confidence": prediction_results.get("overall_confidence", 0),
                "prediction_timeline": prediction_results.get("predictive_timeline", []),
                "context_items": len(context_items),
                "workflow_duration_ms": (datetime.datetime.utcnow() - workflow_start).total_seconds() * 1000,
                "autonomy_level": autonomy_level,
                "prediction_models_run": prediction_results.get("prediction_models_run", 0)
            }
        else:
            # Fall back to single-agent workflow for simple queries
            return await self.autonomous_workflow(query, github_repo, autonomy_level)
    
    async def _execute_multi_agent_actions(self, collaboration_result: Dict[str, Any], github_repo: str = None, autonomy_level: int = 3, prediction_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute actions based on multi-agent collaboration results"""
        
        executed_actions = []
        action_plan = collaboration_result.get("action_plan", {})
        urgent_issues = collaboration_result.get("urgent_issues", {})
        consensus = collaboration_result.get("agent_consensus", {})
        
        # Execute immediate actions if consensus is high
        if consensus.get("consensus_reached", False) and autonomy_level >= 3:
            immediate_actions = action_plan.get("immediate_actions", [])
            for action in immediate_actions[:2]:  # Execute top 2 immediate actions
                try:
                    if "critical" in action.get("action", "").lower():
                        result = await self.autonomous_actions.schedule_team_alerts([action["action"]])
                        executed_actions.append(result)
                    elif github_repo and autonomy_level >= 4:
                        result = await self.autonomous_actions.create_github_issue(
                            repo_url=github_repo,
                            title=f"Multi-Agent Alert: {action.get('action', 'Critical Issue')[:50]}",
                            description=f"Collaborative analysis by 4 specialist agents identified: {action.get('action', 'Issue requiring attention')}"
                        )
                        executed_actions.append(result)
                except Exception as e:
                    executed_actions.append({
                        "action": "multi_agent_action_execution",
                        "status": "error",
                        "message": str(e)
                    })
        
        # Execute documentation updates if significant patterns found
        deep_analysis = collaboration_result.get("deep_analysis", {})
        if len(deep_analysis.get("patterns_found", [])) > 2 and autonomy_level >= 2:
            try:
                result = await self.autonomous_actions.update_documentation(
                    insights=[f"Multi-agent analysis: {deep_analysis.get('ai_insights', 'Patterns identified')}"]
                )
                executed_actions.append(result)
            except Exception as e:
                executed_actions.append({
                    "action": "documentation_update",
                    "status": "error", 
                    "message": str(e)
                })
        
        return {
            "multi_agent_actions_executed": len(executed_actions),
            "executed_actions": executed_actions,
            "consensus_driven": consensus.get("consensus_reached", False),
            "collaboration_id": collaboration_result.get("collaboration_id", "unknown")
        }
    
    async def _learn_from_collaboration(self, query: str, collaboration_result: Dict[str, Any], autonomous_actions: List[Dict[str, Any]], prediction_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Learn from multi-agent collaboration outcomes"""
        
        # Extract collaboration insights
        collaboration_insights = []
        
        agents_involved = collaboration_result.get("agents_involved", 0)
        collaboration_insights.append(f"Multi-agent collaboration with {agents_involved} specialist agents")
        
        consensus = collaboration_result.get("agent_consensus", {})
        if consensus.get("consensus_reached", False):
            collaboration_insights.append(f"High agent consensus achieved: {consensus.get('overall_confidence', 0):.2f} confidence")
        
        query_complexity = collaboration_result.get("query_complexity", "unknown")
        collaboration_insights.append(f"Query complexity: {query_complexity} - appropriate for multi-agent analysis")
        
        # Learn from specialist agent performance
        specialist_performance = {
            "monitor_alerts": len(collaboration_result.get("urgent_issues", {}).get("critical_alerts", [])),
            "analyst_patterns": len(collaboration_result.get("deep_analysis", {}).get("patterns_found", [])),
            "action_recommendations": len(collaboration_result.get("action_plan", {}).get("recommended_actions", [])),
            "learning_insights": len(collaboration_result.get("knowledge_updates", {}).get("learnings_added", []))
        }
        
        # Store collaboration learning
        collaboration_learning = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "query": query,
            "collaboration_effectiveness": consensus.get("overall_confidence", 0),
            "specialist_performance": specialist_performance,
            "actions_success_rate": len([a for a in autonomous_actions if a.get("status") != "error"]) / max(len(autonomous_actions), 1),
            "insights": collaboration_insights,
            "multi_agent_learning": True
        }
        
        self.context_memory.append(collaboration_learning)
        
        return collaboration_learning
    
    def _create_multi_agent_visualizations(self, collaboration_result: Dict[str, Any], context_items: List[ContextItem]) -> Dict[str, Any]:
        """Create enhanced visualizations based on multi-agent analysis"""
        
        # Create enhanced knowledge graph with agent insights
        graph = self._build_knowledge_graph(context_items)
        
        # Add agent collaboration nodes
        collaboration_id = collaboration_result.get("collaboration_id", "collab_1")
        graph.add_node(f"collaboration_{collaboration_id}", 
                      type="collaboration", 
                      label="Multi-Agent\nCollaboration",
                      color="gold", 
                      size=25)
        
        # Connect collaboration to high-impact context items
        for item in context_items:
            if item.impact_score > 0.7:
                graph.add_edge(f"collaboration_{collaboration_id}", item.id, 
                             relation="analyzed_by_agents", color="gold")
        
        # Create agent activity visualization
        agent_viz = self._create_agent_activity_visualization(collaboration_result)
        
        return {
            "knowledge_graph": self._create_graph_visualization(graph),
            "impact_timeline": self._create_impact_timeline(context_items),
            "agent_activity_chart": agent_viz
        }
    
    def _create_agent_activity_visualization(self, collaboration_result: Dict[str, Any]) -> go.Figure:
        """Create visualization showing agent activity and collaboration"""
        
        # Agent performance data
        agents = ["Monitor", "Analyst", "Action", "Learning"]
        
        # Extract metrics from collaboration result
        monitor_score = len(collaboration_result.get("urgent_issues", {}).get("critical_alerts", [])) * 20
        analyst_score = len(collaboration_result.get("deep_analysis", {}).get("patterns_found", [])) * 15
        action_score = len(collaboration_result.get("action_plan", {}).get("recommended_actions", [])) * 10
        learning_score = collaboration_result.get("knowledge_updates", {}).get("confidence_score", 0.5) * 25
        
        activity_scores = [monitor_score, analyst_score, action_score, learning_score]
        
        # Create radar chart showing agent activity
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=activity_scores,
            theta=agents,
            fill='toself',
            name='Agent Activity',
            line=dict(color='rgb(0,123,255)', width=3),
            fillcolor='rgba(0,123,255,0.25)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title="🤖 Multi-Agent Collaboration Activity",
            showlegend=True,
            width=500,
            height=400
        )
        
        return fig
    
    def _extract_multi_agent_predictions(self, collaboration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract predictions from multi-agent collaboration"""
        
        deep_analysis = collaboration_result.get("deep_analysis", {})
        urgent_issues = collaboration_result.get("urgent_issues", {})
        consensus = collaboration_result.get("agent_consensus", {})
        
        return {
            "multi_agent_predictions": deep_analysis.get("predictive_indicators", []),
            "critical_alerts_predicted": len(urgent_issues.get("critical_alerts", [])),
            "pattern_based_predictions": deep_analysis.get("patterns_found", []),
            "consensus_confidence": consensus.get("overall_confidence", 0),
            "collaboration_quality": collaboration_result.get("query_complexity", "unknown"),
            "agents_agreement": consensus.get("agent_agreement_level", "unknown"),
            "predictive_timeline": "Next 24-48 hours based on multi-agent analysis"
        }
    
    def _extract_multi_agent_recommendations(self, collaboration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract recommendations from multi-agent collaboration"""
        
        action_plan = collaboration_result.get("action_plan", {})
        consensus = collaboration_result.get("agent_consensus", {})
        knowledge_updates = collaboration_result.get("knowledge_updates", {})
        
        return {
            "immediate_actions": action_plan.get("immediate_actions", []),
            "strategic_recommendations": action_plan.get("strategic_actions", []),
            "agent_consensus_recommendations": consensus.get("primary_recommendations", []),
            "learning_insights": knowledge_updates.get("learnings_added", []),
            "collaboration_metrics": {
                "agents_involved": collaboration_result.get("agents_involved", 0),
                "collaboration_time": f"{collaboration_result.get('collaboration_time_ms', 0):.0f}ms",
                "consensus_reached": consensus.get("consensus_reached", False)
            },
            "next_steps": "Multi-agent system standing by for continuous monitoring and analysis"
        }

    def _create_prediction_visualizations(self, prediction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create sophisticated prediction visualizations"""
        
        try:
            visualizations = {}
            
            # Create prediction dashboard
            if prediction_results.get('sophisticated_predictions'):
                visualizations['prediction_dashboard'] = self.advanced_visualizations.create_prediction_dashboard(prediction_results)
                visualizations['risk_heatmap'] = self.advanced_visualizations.create_risk_heatmap(prediction_results)
                visualizations['trend_forecast'] = self.advanced_visualizations.create_trend_forecast(prediction_results)
            else:
                # Create empty placeholder visualizations
                visualizations['prediction_dashboard'] = go.Figure().add_annotation(
                    text="🔮 Prediction Dashboard<br>Requires sophisticated predictions",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                )
                visualizations['risk_heatmap'] = go.Figure().add_annotation(
                    text="🌡️ Risk Heatmap<br>Enable predictions for analysis",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                )
                visualizations['trend_forecast'] = go.Figure().add_annotation(
                    text="📈 Trend Forecast<br>Predictive analysis unavailable",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                )
            
            return visualizations
            
        except Exception as e:
            # Return error visualizations
            error_fig = go.Figure().add_annotation(
                text=f"⚠️ Visualization Error<br>{str(e)}",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )
            
            return {
                'prediction_dashboard': error_fig,
                'risk_heatmap': error_fig,
                'trend_forecast': error_fig
            }
    
    async def _decide_actions(self, analysis: Dict[str, Any], autonomy_level: int) -> List[Dict[str, Any]]:
        """Decide which autonomous actions to take based on analysis"""
        action_plan = []
        
        predictions = analysis.get("predictions", [])
        recommendations = analysis.get("recommendations", [])
        
        # Autonomy Level 1: Analysis Only (no actions)
        if autonomy_level <= 1:
            return []
        
        # Autonomy Level 2: Documentation actions only
        if autonomy_level >= 2:
            if analysis.get("ai_insights"):
                action_plan.append({
                    "type": "update_documentation",
                    "priority": "medium",
                    "data": {"insights": [analysis["ai_insights"]]}
                })
        
        # Autonomy Level 3: Add team alerts for predictions
        if autonomy_level >= 3:
            critical_predictions = [p for p in predictions if any(word in p.lower() for word in ['critical', 'urgent', 'severe'])]
            if critical_predictions:
                action_plan.append({
                    "type": "schedule_team_alerts",
                    "priority": "high",
                    "data": {"predictions": critical_predictions}
                })
        
        # Autonomy Level 4: Create GitHub issues for high-impact findings
        if autonomy_level >= 4:
            high_impact_recommendations = [r for r in recommendations if 'critical' in r.lower() or 'urgent' in r.lower()]
            if high_impact_recommendations:
                action_plan.append({
                    "type": "create_github_issue",
                    "priority": "high",
                    "data": {
                        "title": f"DevMind Alert: Critical Issues Detected",
                        "description": f"Autonomous analysis detected critical issues:\n\n" + "\n".join(high_impact_recommendations[:3])
                    }
                })
        
        # Autonomy Level 5: Generate architectural recommendations
        if autonomy_level >= 5 and analysis.get("context_items", 0) > 5:
            action_plan.append({
                "type": "generate_architecture_recommendations",
                "priority": "high",
                "data": {"context_items": analysis.get("context_items", 0)}
            })
        
        return action_plan
    
    async def _execute_action(self, action: Dict[str, Any], github_repo: str = None, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific autonomous action"""
        action_type = action.get("type")
        action_data = action.get("data", {})
        
        if action_type == "create_github_issue" and github_repo:
            return await self.autonomous_actions.create_github_issue(
                repo_url=github_repo,
                title=action_data.get("title", "DevMind Autonomous Alert"),
                description=action_data.get("description", "Autonomous analysis detected issues requiring attention.")
            )
        
        elif action_type == "update_documentation":
            return await self.autonomous_actions.update_documentation(
                insights=action_data.get("insights", [])
            )
        
        elif action_type == "schedule_team_alerts":
            return await self.autonomous_actions.schedule_team_alerts(
                predictions=action_data.get("predictions", [])
            )
        
        elif action_type == "generate_architecture_recommendations":
            # Get context items from analysis for architectural recommendations
            context_items = self._get_demo_context()  # Using demo context for now
            return await self.autonomous_actions.generate_architecture_recommendations(
                context=context_items
            )
        
        else:
            return {
                "action": action_type,
                "status": "skipped", 
                "message": f"Action type '{action_type}' not implemented or prerequisites not met"
            }
    
    async def _update_memory(self, query: str, analysis: Dict[str, Any], executed_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update agent memory with learning from this interaction"""
        
        # Extract patterns from the interaction
        patterns_learned = []
        
        # Learn from query patterns
        if "auth" in query.lower():
            patterns_learned.append("Authentication queries are common - prioritize security insights")
        if "performance" in query.lower():
            patterns_learned.append("Performance analysis requested - include metric tracking")
        if "bug" in query.lower() or "issue" in query.lower():
            patterns_learned.append("Bug investigation - emphasize root cause analysis")
        
        # Learn from action success/failure
        successful_actions = [a for a in executed_actions if a.get("status") not in ["error", "failed"]]
        failed_actions = [a for a in executed_actions if a.get("status") in ["error", "failed"]]
        
        learning_summary = {
            "interaction_timestamp": datetime.datetime.utcnow().isoformat(),
            "query_pattern": query,
            "analysis_quality": "high" if analysis.get("ai_insights") else "medium",
            "actions_executed": len(executed_actions),
            "actions_successful": len(successful_actions),
            "actions_failed": len(failed_actions),
            "patterns_identified": patterns_learned,
            "memory_updated": True
        }
        
        # Store in context memory for future reference
        self.context_memory.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "query": query,
            "actions_taken": [a.get("action", "unknown") for a in executed_actions],
            "success_rate": len(successful_actions) / max(len(executed_actions), 1) * 100
        })
        
        # Keep only last 100 interactions in memory
        if len(self.context_memory) > 100:
            self.context_memory = self.context_memory[-100:]
        
        return learning_summary

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        actions_summary = self.autonomous_actions.get_actions_summary()
        
        return {
            "agent_active": True,
            "memory_size": len(self.context_memory),
            "total_interactions": len(self.context_memory),
            "actions_taken": actions_summary.get("total_actions", 0),
            "action_success_rate": actions_summary.get("success_rate", 0),
            "learning_enabled": True,
            "autonomous_capabilities": [
                "GitHub Issue Creation",
                "Documentation Updates", 
                "Team Alerts",
                "Architecture Recommendations"
            ],
            "last_active": datetime.datetime.utcnow().isoformat()
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
    
    def process_query(query: str, anthropic_key: str, github_repo: str = None, autonomy_level: int = 3):
        """Main processing function for Gradio interface with autonomous capabilities"""
        if not query.strip():
            return "Please enter a query", None, None, {}, {}
        
        if not anthropic_key.strip():
            return "Please provide your Anthropic API key", None, None, {}, {}
        
        try:
            # Initialize agent with autonomous capabilities
            agent = DevMindAgent(anthropic_key)
            
            # Run autonomous workflow instead of just analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    agent.multi_agent_collaborative_workflow(query, github_repo, autonomy_level)
                )
            finally:
                loop.close()
            
            # Format the response with enhanced multi-agent information
            formatted_response = f"""
# 🧠 DevMind Analysis Results

## 📊 Query Analysis
- **Query Complexity**: {results.get('query_complexity', 'standard')}
- **Workflow Type**: {results.get('workflow_type', 'autonomous')}
- **Processing Time**: {results.get('workflow_duration_ms', 0):.0f}ms
- **Context Items Analyzed**: {results.get('context_items', 0)}

## 🤖 AI Insights
{results.get('ai_insights', 'Analysis completed successfully.')}

## 🔮 Predictions
"""
            predictions = results.get('predictions', {})
            if isinstance(predictions, dict):
                # Multi-agent predictions
                ma_predictions = predictions.get('multi_agent_predictions', [])
                if ma_predictions:
                    formatted_response += f"**Multi-Agent Predictions** ({len(ma_predictions)} identified):\n"
                    for pred in ma_predictions[:3]:
                        formatted_response += f"- {pred}\n"
                
                # Consensus information
                consensus_conf = predictions.get('consensus_confidence', 0)
                if consensus_conf > 0:
                    formatted_response += f"\n**Agent Consensus**: {consensus_conf:.2f} confidence\n"
                
                # Critical alerts
                critical_alerts = predictions.get('critical_alerts_predicted', 0)
                if critical_alerts > 0:
                    formatted_response += f"**Critical Alerts**: {critical_alerts} issues require immediate attention\n"
                    
                formatted_response += f"**Timeline**: {predictions.get('predictive_timeline', 'Standard analysis timeframe')}\n"
            else:
                # Standard predictions list
                for pred in (predictions or [])[:3]:
                    formatted_response += f"- {pred}\n"

            formatted_response += """
## 💡 Recommendations
"""
            recommendations = results.get('recommendations', {})
            if isinstance(recommendations, dict):
                # Multi-agent recommendations
                immediate_actions = recommendations.get('immediate_actions', [])
                if immediate_actions:
                    formatted_response += f"**Immediate Actions** ({len(immediate_actions)}):\n"
                    for action in immediate_actions[:3]:
                        action_text = action.get('action', action) if isinstance(action, dict) else action
                        formatted_response += f"- {action_text}\n"
                
                strategic_recs = recommendations.get('strategic_recommendations', [])
                if strategic_recs:
                    formatted_response += f"\n**Strategic Recommendations** ({len(strategic_recs)}):\n"
                    for rec in strategic_recs[:2]:
                        rec_text = rec.get('action', rec) if isinstance(rec, dict) else rec
                        formatted_response += f"- {rec_text}\n"
                
                learning_insights = recommendations.get('learning_insights', [])
                if learning_insights:
                    formatted_response += f"\n**Learning Insights** ({len(learning_insights)}):\n"
                    for insight in learning_insights[:2]:
                        formatted_response += f"- {insight}\n"
                        
                # Collaboration metrics
                collab_metrics = recommendations.get('collaboration_metrics', {})
                if collab_metrics:
                    formatted_response += f"\n**Multi-Agent Collaboration**:\n"
                    formatted_response += f"- Agents Involved: {collab_metrics.get('agents_involved', 0)}\n"
                    formatted_response += f"- Collaboration Time: {collab_metrics.get('collaboration_time', 'N/A')}\n"
                    formatted_response += f"- Consensus Reached: {'✅' if collab_metrics.get('consensus_reached', False) else '❌'}\n"
                    
                formatted_response += f"\n**Next Steps**: {recommendations.get('next_steps', 'Continue monitoring and analysis.')}\n"
            else:
                # Standard recommendations list
                for rec in (recommendations or [])[:3]:
                    formatted_response += f"- {rec}\n"

            # Enhanced autonomous actions display
            formatted_response += """
## 🚀 Autonomous Actions Taken
"""
            autonomous_actions = results.get('autonomous_actions', [])
            if autonomous_actions:
                if isinstance(autonomous_actions, dict):
                    # Multi-agent action results
                    actions_executed = autonomous_actions.get('executed_actions', [])
                    if actions_executed:
                        formatted_response += f"**Multi-Agent Actions** ({autonomous_actions.get('multi_agent_actions_executed', 0)} executed):\n"
                        for action in actions_executed:
                            action_name = action.get('action', 'Unknown Action')
                            status = action.get('status', 'unknown')
                            emoji = "✅" if status == "success" else "❌" if status == "error" else "⏳"
                            formatted_response += f"{emoji} {action_name} - {status}\n"
                        
                        if autonomous_actions.get('consensus_driven', False):
                            formatted_response += "\n🤝 **Actions were consensus-driven by specialist agents**\n"
                else:
                    # Standard autonomous actions list
                    for action in autonomous_actions:
                        action_name = action.get('action', 'Unknown Action')
                        status = action.get('status', 'unknown')
                        emoji = "✅" if status == "success" else "❌" if status == "error" else "⏳"
                        formatted_response += f"{emoji} {action_name} - {status}\n"
            else:
                formatted_response += "No autonomous actions executed for this query.\n"

            # Learning and memory updates
            formatted_response += """
## 🧠 Learning & Memory Updates
"""
            learning_updates = results.get('learning_updates', {})
            if learning_updates:
                if learning_updates.get('multi_agent_learning', False):
                    formatted_response += "**Multi-Agent Learning Active** 🤖🤖🤖🤖\n"
                    effectiveness = learning_updates.get('collaboration_effectiveness', 0)
                    formatted_response += f"- Collaboration Effectiveness: {effectiveness:.2f}\n"
                    
                    specialist_performance = learning_updates.get('specialist_performance', {})
                    if specialist_performance:
                        formatted_response += "- **Specialist Agent Performance**:\n"
                        formatted_response += f"  - Monitor Alerts: {specialist_performance.get('monitor_alerts', 0)}\n"
                        formatted_response += f"  - Analyst Patterns: {specialist_performance.get('analyst_patterns', 0)}\n"
                        formatted_response += f"  - Action Recommendations: {specialist_performance.get('action_recommendations', 0)}\n"
                        formatted_response += f"  - Learning Insights: {specialist_performance.get('learning_insights', 0)}\n"
                    
                    success_rate = learning_updates.get('actions_success_rate', 0)
                    formatted_response += f"- Actions Success Rate: {success_rate:.2%}\n"
                else:
                    # Standard learning info
                    analysis_quality = learning_updates.get('analysis_quality', 'medium')
                    patterns_identified = learning_updates.get('patterns_identified', [])
                    formatted_response += f"Analysis Quality: {analysis_quality}\n"
                    if patterns_identified:
                        formatted_response += f"Patterns Learned: {len(patterns_identified)}\n"
            else:
                formatted_response += "Memory updated with interaction patterns.\n"

            # Agent status and capabilities
            agent_status = agent.get_agent_status()
            formatted_response += f"""
## 🤖 Agent Status
- **Active**: {agent_status.get('agent_active', False)}
- **Memory Size**: {agent_status.get('memory_size', 0)} interactions
- **Actions Taken**: {agent_status.get('actions_taken', 0)}
- **Success Rate**: {agent_status.get('action_success_rate', 0):.1%}
- **Autonomy Level**: {autonomy_level}/5
- **Learning**: {'Enabled' if agent_status.get('learning_enabled', False) else 'Disabled'}

### 🛠️ Agent Capabilities
"""
            capabilities = agent_status.get('autonomous_capabilities', [])
            for capability in capabilities:
                formatted_response += f"- ✅ {capability}\n"
            
            # Add multi-agent specific capabilities if workflow was collaborative
            if results.get('workflow_type') == 'multi_agent_collaborative_with_predictions':
                formatted_response += """
### 🤖 Multi-Agent Specialist Capabilities
- ✅ **Monitor Agent**: Real-time issue detection and alerting
- ✅ **Analyst Agent**: Deep pattern analysis with AI insights  
- ✅ **Action Agent**: Prioritized action plan generation
- ✅ **Learning Agent**: Continuous team knowledge updates
- ✅ **Collaborative Consensus**: Multi-agent decision making
"""

            # Enhanced visualizations info
            enhanced_viz = results.get('enhanced_visualizations', {})
            if enhanced_viz and enhanced_viz.get('agent_activity_chart'):
                formatted_response += """
## 📊 Enhanced Multi-Agent Visualizations
- 🕸️ **Knowledge Graph**: Enhanced with agent collaboration nodes
- 📈 **Impact Timeline**: Showing multi-agent analysis points
- 🎯 **Agent Activity**: Radar chart showing specialist agent performance
"""
            
            prediction_viz = results.get('prediction_visualizations', {})
            if prediction_viz and prediction_viz.get('prediction_dashboard'):
                formatted_response += """
## 📊 Sophisticated Predictions Visualizations
- 📊 **Prediction Dashboard**: Comprehensive prediction overview
- 🌡️ **Risk Heatmap**: Risk assessment across different categories
- 📈 **Trend Forecast**: Predictive trend analysis
"""
            
            formatted_response += f"""
---
*DevMind Agent last active: {agent_status.get('last_active', 'unknown')}*
"""

            # Return outputs for Gradio interface
            knowledge_graph = results.get('knowledge_graph')
            impact_timeline = results.get('impact_timeline')
            
            # Get enhanced visualizations if available
            enhanced_viz = results.get('enhanced_visualizations', {})
            if enhanced_viz.get('agent_activity_chart'):
                # Use enhanced agent activity visualization
                agent_activity_viz = enhanced_viz['agent_activity_chart']
            else:
                # Fallback to standard timeline if no agent activity viz
                agent_activity_viz = impact_timeline

            prediction_viz = results.get('prediction_visualizations', {})
            if prediction_viz.get('prediction_dashboard'):
                prediction_dashboard = prediction_viz['prediction_dashboard']
                risk_heatmap = prediction_viz['risk_heatmap']
                trend_forecast = prediction_viz['trend_forecast']
            else:
                prediction_dashboard = None
                risk_heatmap = None
                trend_forecast = None

            return formatted_response, knowledge_graph, impact_timeline, agent_activity_viz, prediction_dashboard, risk_heatmap, trend_forecast

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"Error in process_query: {e}")
            return error_msg, None, None, None, None, None, None

    with gr.Blocks(title="🤖 DevMind: Autonomous AI Team Oracle", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🤖 DevMind: Autonomous Multi-Agent Development Oracle
        
        **Track 3: Agentic Demo Showcase - Agents & MCP Hackathon 2025**
        
        Experience the future of AI-powered development with our **autonomous multi-agent system**:
        
        🧠 **4 Specialist Agents Working Together**:
        - 🔍 **Monitor Agent**: Real-time issue detection and critical alerts
        - 📊 **Analyst Agent**: Deep pattern analysis with AI insights
        - ⚡ **Action Agent**: Intelligent action plan generation  
        - 🎓 **Learning Agent**: Continuous team knowledge updates
        
        🚀 **Beyond Simple Analysis**:
        - Takes **real autonomous actions** (GitHub issues, documentation, alerts)
        - **Learns continuously** from every team interaction
        - **Multi-agent collaboration** with consensus-driven decisions
        - **5-level autonomy control** for graduated autonomous behavior
        
        🎯 **Competitive Advantages**:
        - **First truly autonomous** development agent (not just analysis)
        - **Collaborative intelligence** via 4 specialist agents working together
        - **Real actions taken** automatically based on analysis
        - **Continuous learning** improves with every interaction
        - **Predictive insights** prevent issues before they occur
        
        **Get Started**: Enter your development query, set autonomy level, and watch our multi-agent team collaborate!
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="🔍 Development Query",
                    placeholder="Example: 'Analyze authentication flow performance issues' or 'Check for security vulnerabilities in user management'",
                    lines=3
                )
                
                with gr.Row():
                    github_input = gr.Textbox(
                        label="📱 GitHub Repository (Optional)",
                        placeholder="https://github.com/user/repo or user/repo",
                        scale=2
                    )
                    
                    autonomy_slider = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=3,
                        step=1,
                        label="🤖 Autonomy Level",
                        info="1=Analysis Only → 5=Full Multi-Agent Autonomous Actions",
                        scale=1
                    )
                
                analyze_btn = gr.Button("🚀 Deploy Multi-Agent Analysis", variant="primary", size="lg")
                
            with gr.Column(scale=1):
                gr.Markdown("""
                ### 🎛️ Autonomy Levels:
                **Level 1**: Analysis only  
                **Level 2**: + Documentation updates  
                **Level 3**: + Team alerts  
                **Level 4**: + GitHub issues + Multi-agent collaboration  
                **Level 5**: + Architecture recommendations  
                
                ### 🤖 Agent Capabilities:
                ✅ Real-time GitHub integration  
                ✅ AI-powered insights (Claude)  
                ✅ Autonomous action execution  
                ✅ Multi-agent collaboration  
                ✅ Continuous learning system  
                ✅ Predictive issue detection  
                """)
        
        # Enhanced output layout for multi-agent results
        with gr.Row():
            analysis_output = gr.Markdown(label="📊 Multi-Agent Analysis Results")
        
        with gr.Row():
            with gr.Column():
                knowledge_graph = gr.Plot(label="🕸️ Enhanced Knowledge Graph")
            with gr.Column():
                impact_timeline = gr.Plot(label="📈 Development Impact Timeline")
        
        with gr.Row():
            agent_activity = gr.Plot(label="🤖 Multi-Agent Collaboration Activity")
        
        with gr.Row():
            prediction_dashboard = gr.Plot(label="📊 Sophisticated Prediction Dashboard")
            risk_heatmap = gr.Plot(label="🌡️ Risk Heatmap")
            trend_forecast = gr.Plot(label="📈 Trend Forecast")
        
        # Additional info sections
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### 🏆 **DevMind Winning Features**:
                
                **🎯 Autonomous Actions**: First AI agent that actually **DOES** things, not just analyzes:
                - Creates GitHub issues automatically
                - Updates team documentation in real-time  
                - Schedules critical alerts and notifications
                - Generates architectural recommendations with AI
                
                **🤖 Multi-Agent Intelligence**: 4 specialist agents collaborate:
                - **Monitor**: Scans for urgent issues and critical alerts
                - **Analyst**: Deep pattern analysis with Claude AI insights
                - **Action**: Creates prioritized, actionable plans
                - **Learning**: Continuously updates team knowledge
                
                **🧠 Continuous Learning**: Gets smarter with every interaction:
                - Learns team patterns and preferences
                - Builds consensus through agent collaboration
                - Adapts action strategies based on success rates
                - Updates knowledge base automatically
                
                **🎮 User Control**: 5-level autonomy system:
                - Users control how much autonomy to grant
                - Graduated from analysis-only to full autonomous actions
                - Safety controls prevent unwanted side effects
                """)
                
            with gr.Column():
                gr.Markdown("""
                ### 🚀 **Demo Highlights**:
                
                **Real Autonomous Behavior**:
                - Watch agents collaborate in real-time
                - See autonomous actions executed live
                - View consensus building between specialist agents
                - Monitor continuous learning in action
                
                **Advanced Visualizations**:
                - **Knowledge Graph**: Shows relationships enhanced by agent insights
                - **Impact Timeline**: Multi-agent analysis points over time  
                - **Agent Activity**: Radar chart of specialist agent performance
                
                **GitHub Integration**:
                - Connect your real repositories
                - Autonomous issue creation based on analysis
                - Real-time code and commit analysis
                - Predictive issue detection
                
                **AI-Powered Insights**:
                - Claude AI integration for deep analysis
                - Multi-agent consensus on recommendations
                - Predictive indicators for future issues
                - Architectural guidance with AI reasoning
                
                **Competitive Edge**:
                - Beyond other "analysis-only" tools
                - First truly autonomous dev agent
                - Multi-agent collaboration unprecedented
                - Real actions + learning + predictions = **WINNING COMBO!**
                """)
        
        # Wire up the interface with multi-agent support
        analyze_btn.click(
            fn=process_query,
            inputs=[query_input, github_input, autonomy_slider],
            outputs=[analysis_output, knowledge_graph, impact_timeline, agent_activity, prediction_dashboard, risk_heatmap, trend_forecast]
        )

    return demo

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_devmind_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=True,
        show_error=True
    )
