// app/page.tsx
"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ThemeToggle } from "@/components/theme-toggle"
import {
  Search, MessageSquare, Activity, Clock, GitBranch, MessageCircle, FileText, Zap, ChevronRight, Brain, AlertTriangle, CheckCircle2, Info
} from "lucide-react"

// MCP Tool Components
const MCPToolIndicator = ({ tool, isActive, isQuerying }: { tool: string; isActive: boolean; isQuerying: boolean; }) => {
  const getIcon = () => {
    switch (tool.toLowerCase()) { // Ensure lowercase comparison for safety
      case "github": return <GitBranch className="w-3 h-3" />;
      case "slack": return <MessageCircle className="w-3 h-3" />;
      case "jira": return <FileText className="w-3 h-3" />;
      case "confluence": return <FileText className="w-3 h-3" /> // Added Confluence
      default: return <Activity className="w-3 h-3" />;
    }
  };
  return (
    <div
      title={`MCP Tool: ${tool}`}
      className={`
      flex items-center justify-center w-6 h-6 rounded-full border transition-all duration-200 ease-out
      ${isActive || isQuerying ? "bg-accent border-accent text-accent-foreground shadow-md" : "bg-card border-border text-muted-foreground hover:border-muted-foreground/50"}
      ${isQuerying ? "animate-pulse ring-2 ring-accent ring-offset-1 ring-offset-background" : ""}
    `}
    >
      {getIcon()}
    </div>
  );
};

// Define types for API response
interface ContextMatch {
  entry_id: string; // UUID as string
  score: number;
  source: string; // e.g., "github", "slack"
  entry_type: string; // e.g., "commit", "message"
  title?: string;
  content: string;
  author?: string;
  timestamp: string; // ISO string date
  url?: string;
}

interface QueryApiResponse {
  query_id: string; // UUID as string
  query: string;
  answer: string; // This is the AI-generated summary from backend
  sources_used: string[]; // Array of source strings like "github", "slack"
  context_matches: ContextMatch[];
  confidence_score: number;
  execution_time: number; // in seconds
  timestamp: string; // ISO string date from backend
}


export default function DevMindDashboard() {
  const [query, setQuery] = useState("")
  const [isQuerying, setIsQuerying] = useState(false)
  const [focusedInput, setFocusedInput] = useState(false)
  const [activeTools, setActiveTools] = useState<string[]>([]) // stores names of active tools e.g. ["github", "slack"]
  const [apiResponse, setApiResponse] = useState<QueryApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // It's good practice to use environment variables for URLs
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  const handleQuery = async () => {
    if (!query.trim()) return;

    setIsQuerying(true);
    setApiResponse(null); 
    setError(null); 
    
    // Initially, you might show all tools as "potentially active" or "pending"
    // This will be updated based on the actual sources_used from the API response.
    const potentialTools = ["github", "slack", "jira", "confluence"]; // Add all possible tools
    setActiveTools(potentialTools); 

    try {
      const response = await fetch(`${backendUrl}/api/v1/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          project_id: null, 
          context_limit: 10,
          include_sources: potentialTools // Send all tools you might query
        })
      });

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorData.message || errorDetail;
        } catch (e) {
            // If response is not JSON or empty
            const textError = await response.text();
            errorDetail = textError || errorDetail;
        }
        throw new Error(errorDetail);
      }
      
      const data: QueryApiResponse = await response.json();
      setApiResponse(data);
      
      // Update activeTools to reflect only those actually used by the backend
      setActiveTools(data.sources_used || []);

    } catch (err: any) {
      console.error('Query failed:', err);
      setError(err.message || "Failed to fetch response from DevMind.");
      setActiveTools([]); // Clear tools on error
    } finally {
      // Simulate a slight delay for visual feedback before isQuerying is set to false
      // This makes the UI feel a bit more responsive even if API is fast
      setTimeout(() => {
        setIsQuerying(false);
      }, 500); 
    }
  };

  // Mock data for sidebar (can be fetched or static)
  const insights = [
    { title: "Critical Bug in Auth Fixed", source: "github", time: "2m ago", priority: "high" },
    { title: "Team Standup @ 10 AM", source: "slack", time: "15m ago", priority: "medium" },
    { title: "API Rate Limit Deployed", source: "jira", time: "1h ago", priority: "low" },
  ];

  const recentQueries = [
    "Why Redis over PostgreSQL for caching?",
    "Recent authentication bugs",
    "Summarize Slack #dev channel",
  ];

  return (
    <div className="min-h-screen bg-background text-foreground font-sans transition-colors duration-300 flex flex-col">
      {/* Header */}
      <header className="border-b border-border px-4 sm:px-8 py-4 sm:py-6 sticky top-0 bg-background/80 backdrop-blur-md z-10">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-2 sm:gap-3">
             <Brain className="h-7 w-7 sm:h-8 sm:w-8 text-accent" />
            <div>
                <h1 className="text-xl sm:text-2xl font-semibold tracking-tight">DevMind</h1>
                <p className="text-muted-foreground text-xs sm:text-sm">Context Oracle</p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <div className="flex items-center gap-1 sm:gap-2">
              <span className="text-xs text-muted-foreground font-medium hidden md:inline">MCP:</span>
              {["github", "slack", "jira", "confluence"].map(toolName => (
                <MCPToolIndicator 
                  key={toolName}
                  tool={toolName} 
                  isActive={activeTools.includes(toolName.toLowerCase())} 
                  isQuerying={isQuerying && activeTools.includes(toolName.toLowerCase())} 
                />
              ))}
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-8 py-6 sm:py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          {/* === Main Query & Response Column === */}
          <div className="lg:col-span-2 space-y-6 sm:space-y-8">
            {/* Query Input Section */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg sm:text-xl">Ask DevMind</CardTitle>
                <CardDescription>What development context are you looking for?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 sm:space-y-4">
                <div className="relative">
                  <Input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => setFocusedInput(true)}
                    onBlur={() => setFocusedInput(false)}
                    onKeyDown={(e) => e.key === "Enter" && !isQuerying && handleQuery()}
                    placeholder="e.g., Why did we choose Redis over PostgreSQL for caching?"
                    className={`w-full pl-10 pr-4 py-3 text-sm sm:text-base border-border focus:ring-accent focus:border-accent transition-all duration-200 rounded-md ${focusedInput ? "ring-2 ring-accent border-accent" : "border"}`}
                    aria-label="DevMind Query Input"
                  />
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground" />
                </div>
                <Button
                  onClick={handleQuery}
                  disabled={!query.trim() || isQuerying}
                  className="w-full sm:w-auto bg-accent hover:bg-accent/90 text-accent-foreground px-5 py-2.5 sm:px-6 rounded-md font-medium transition-colors duration-200 text-sm sm:text-base"
                >
                  <Brain className="w-4 h-4 mr-2" />
                  {isQuerying ? "Thinking..." : "Ask DevMind"}
                </Button>
              </CardContent>
            </Card>
            
            {/* Context Response Area */}
            {error && (
              <Card className="border-destructive bg-destructive/10 text-destructive">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <AlertTriangle className="w-5 h-5" />
                    Query Error
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm sm:text-base">{error}</p>
                </CardContent>
              </Card>
            )}

            {(isQuerying || apiResponse) && (
              <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg sm:text-xl">
                    {isQuerying && !apiResponse ? "Processing Query..." : "DevMind's Response"}
                  </CardTitle>
                  {apiResponse && (
                    <CardDescription>
                      Confidence: <Badge variant={apiResponse.confidence_score > 0.7 ? "default" : "secondary"} className={apiResponse.confidence_score > 0.7 ? "bg-green-500/20 text-green-700 border-green-500/30 dark:bg-green-500/10 dark:text-green-400 dark:border-green-500/20" : "bg-amber-500/20 text-amber-700 border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20"}>{(apiResponse.confidence_score * 100).toFixed(0)}%</Badge>
                      <span className="mx-2 text-muted-foreground">|</span>
                      Time: <Badge variant="outline">{apiResponse.execution_time.toFixed(2)}s</Badge>
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="space-y-4 sm:space-y-6">
                  {isQuerying && !apiResponse && (
                    <div className="text-center text-muted-foreground py-10 space-y-2">
                      <Activity className="w-8 h-8 sm:w-10 sm:h-10 mx-auto opacity-70 animate-spin" />
                      <p className="text-md sm:text-lg font-medium">DevMind is analyzing context...</p>
                      <p className="text-xs sm:text-sm">Querying connected tools via MCP, please wait.</p>
                    </div>
                  )}
                  {apiResponse && (
                    <>
                      <div className="prose dark:prose-invert max-w-none p-3 bg-secondary/30 dark:bg-secondary/10 rounded-md border border-border">
                        <h3 className="text-md sm:text-lg font-semibold mb-2 text-foreground">Summary:</h3>
                        <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">{apiResponse.answer}</p>
                      </div>
                      
                      {apiResponse.context_matches && apiResponse.context_matches.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-md sm:text-lg mb-2 sm:mb-3">Key Context Sources ({apiResponse.context_matches.length}):</h4>
                          <div className="space-y-3 sm:space-y-4 max-h-[400px] sm:max-h-[500px] overflow-y-auto pr-2">
                            {apiResponse.context_matches.map((match) => (
                              <Card key={match.entry_id} className="bg-card border-border hover:shadow-md transition-shadow duration-200">
                                <CardHeader className="pb-1.5 pt-3 px-3 sm:px-4">
                                   <CardTitle className="text-xs sm:text-sm font-medium flex items-center gap-1.5 sm:gap-2">
                                    {match.source.toLowerCase() === 'github' && <GitBranch className="w-3.5 h-3.5 text-muted-foreground" />}
                                    {match.source.toLowerCase() === 'slack' && <MessageCircle className="w-3.5 h-3.5 text-muted-foreground" />}
                                    {match.source.toLowerCase() === 'jira' && <FileText className="w-3.5 h-3.5 text-muted-foreground" />}
                                    {match.source.toLowerCase() === 'confluence' && <FileText className="w-3.5 h-3.5 text-muted-foreground" />}
                                    <span className="truncate">{match.title || "Context Snippet"}</span>
                                  </CardTitle>
                                  <CardDescription className="text-xs flex flex-wrap gap-x-2 gap-y-0.5">
                                    <span>Src: <Badge variant="outline" className="px-1.5 py-0 text-xs">{match.source}</Badge></span>
                                    <span>Type: <Badge variant="outline" className="px-1.5 py-0 text-xs">{match.entry_type}</Badge></span>
                                    <span>Score: <Badge variant="outline" className="px-1.5 py-0 text-xs">{match.score.toFixed(2)}</Badge></span>
                                  </CardDescription>
                                </CardHeader>
                                <CardContent className="px-3 sm:px-4 pb-3">
                                  <p className="text-xs sm:text-sm text-muted-foreground line-clamp-2 sm:line-clamp-3 mb-1.5">{match.content}</p>
                                  <div className="flex items-center justify-between text-xs text-muted-foreground/80">
                                    <span className="truncate">By: {match.author || "N/A"}</span>
                                    <span>{new Date(match.timestamp).toLocaleDateString()}</span>
                                  </div>
                                  {match.url && <a href={match.url} target="_blank" rel="noopener noreferrer" className="text-xs text-accent hover:underline mt-1 inline-block">View Source &rarr;</a>}
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            )}
            
            {!isQuerying && !apiResponse && !error && (
                 <Card className="border-dashed border-border shadow-none">
                    <CardContent className="p-6 sm:p-8">
                        <div className="text-center text-muted-foreground py-10 space-y-2">
                        <Info className="w-8 h-8 sm:w-10 sm:h-10 mx-auto mb-3 opacity-50" />
                        <p className="text-md sm:text-lg font-medium">Welcome to DevMind</p>
                        <p className="text-xs sm:text-sm">Enter a query above to search your development context.</p>
                        </div>
                    </CardContent>
                </Card>
            )}
          </div>

          {/* === Sidebar Column === */}
          <div className="lg:col-span-1 space-y-6 sm:space-y-8">
            {/* Recent Queries Section */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-md sm:text-lg">Recent Queries</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {recentQueries.map((recentQuery, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    onClick={() => { setQuery(recentQuery); handleQuery(); }} // Also trigger query
                    className="w-full justify-start text-left p-2 sm:p-3 rounded-md group hover:bg-secondary"
                    disabled={isQuerying}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="text-xs sm:text-sm text-foreground group-hover:text-accent transition-colors duration-200 truncate">
                        {recentQuery}
                      </span>
                      <ChevronRight className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-muted-foreground group-hover:text-accent transition-colors duration-200" />
                    </div>
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* Live Insights Section */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-md sm:text-lg flex items-center gap-2">
                  <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-accent" />
                  Live Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2.5 sm:space-y-3">
                {insights.map((insight, index) => (
                  <Card
                    key={index}
                    className="border-border bg-card hover:bg-secondary/50 transition-colors duration-200"
                  >
                    <CardContent className="p-2.5 sm:p-3">
                      <div className="space-y-1">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-medium text-xs sm:text-sm leading-tight">{insight.title}</h4>
                          <Badge
                            variant={insight.priority === "high" ? "default" : "secondary"}
                            className={`text-[10px] sm:text-xs px-1.5 py-0.5 rounded-full ${insight.priority === "high" ? "bg-destructive/80 text-destructive-foreground" : "bg-secondary text-secondary-foreground"}`}
                          >
                            {insight.priority}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-1.5 text-[10px] sm:text-xs text-muted-foreground">
                          <MCPToolIndicator tool={insight.source} isActive={false} isQuerying={false} />
                          <Clock className="w-2.5 h-2.5 sm:w-3 sm:h-3" />
                          <span>{insight.time}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>

            {/* System Status Section */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-md sm:text-lg">System Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2.5 sm:space-y-3 text-xs sm:text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">MCP Connections:</span>
                  <div className="flex items-center gap-1">
                    <div className={`w-2 h-2 rounded-full ${apiResponse || !error ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <span className="font-medium">{apiResponse || !error ? 'Online' : 'Offline'}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Context Freshness:</span>
                  <span className="font-medium">Real-time</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Avg. Query Time:</span>
                  <span className="font-medium">~{(apiResponse?.execution_time || 1.2).toFixed(1)}s</span>
                </div>
                 <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Backend:</span>
                  <span className="font-medium text-green-600 dark:text-green-500">{backendUrl}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}