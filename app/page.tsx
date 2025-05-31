"use client"

import React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ThemeToggle } from "@/components/theme-toggle"
import {
  Search,
  MessageSquare,
  Activity,
  Clock,
  GitBranch,
  MessageCircle,
  FileText,
  Zap,
  ChevronRight,
} from "lucide-react"

// MCP Tool Components
const MCPToolIndicator = ({
  tool,
  isActive,
  isQuerying,
}: {
  tool: string
  isActive: boolean
  isQuerying: boolean
}) => {
  const getIcon = () => {
    switch (tool) {
      case "github":
        return <GitBranch className="w-3 h-3" />
      case "slack":
        return <MessageCircle className="w-3 h-3" />
      case "jira":
        return <FileText className="w-3 h-3" />
      default:
        return <Activity className="w-3 h-3" />
    }
  }

  return (
    <div
      className={`
      flex items-center justify-center w-6 h-6 rounded-full border transition-all duration-200 ease-out
      ${
        isActive || isQuerying
          ? "bg-accent border-accent text-accent-foreground"
          : "border-border text-muted-foreground hover:border-muted-foreground/50"
      }
      ${isQuerying ? "animate-pulse" : ""}
    `}
    >
      {getIcon()}
    </div>
  )
}

export default function DevMindDashboard() {
  const [query, setQuery] = useState("")
  const [isQuerying, setIsQuerying] = useState(false)
  const [focusedInput, setFocusedInput] = useState(false)
  const [activeTools, setActiveTools] = useState<string[]>([])

  const handleQuery = async () => {
    if (!query.trim()) return

    setIsQuerying(true)
    setActiveTools(["github", "slack", "jira"])

    // Simulate MCP tool querying
    setTimeout(() => {
      setActiveTools(["github"])
      setTimeout(() => {
        setActiveTools([])
        setIsQuerying(false)
      }, 1000)
    }, 2000)
  }

  const insights = [
    {
      title: "Critical Bug in Authentication Service",
      source: "github",
      time: "2 minutes ago",
      priority: "high",
    },
    {
      title: "Team standup scheduled for 10:00 AM",
      source: "slack",
      time: "15 minutes ago",
      priority: "medium",
    },
    {
      title: "API rate limit optimization completed",
      source: "jira",
      time: "1 hour ago",
      priority: "low",
    },
  ]

  const recentQueries = [
    "What's the status of the user authentication refactor?",
    "Show me recent deployment issues",
    "Summarize today's team discussions",
  ]

  return (
    <div className="min-h-screen bg-background text-foreground font-sans transition-colors duration-300">
      {/* Header */}
      <header className="border-b border-border px-8 py-6">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">DevMind</h1>
            <p className="text-muted-foreground text-sm mt-1">Development Context Oracle</p>
          </div>

          <div className="flex items-center gap-6">
            {/* MCP Status Bar */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground font-medium">MCP</span>
              <div className="flex items-center gap-2">
                <MCPToolIndicator
                  tool="github"
                  isActive={activeTools.includes("github")}
                  isQuerying={isQuerying && activeTools.includes("github")}
                />
                <MCPToolIndicator
                  tool="slack"
                  isActive={activeTools.includes("slack")}
                  isQuerying={isQuerying && activeTools.includes("slack")}
                />
                <MCPToolIndicator
                  tool="jira"
                  isActive={activeTools.includes("jira")}
                  isQuerying={isQuerying && activeTools.includes("jira")}
                />
              </div>
            </div>

            {/* Theme Toggle */}
            <ThemeToggle />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Main Query Interface */}
          <div className="lg:col-span-2 space-y-8">
            {/* Query Input */}
            <div className="space-y-6">
              <h2 className="text-2xl font-medium">Ask DevMind</h2>
              <div className="space-y-4">
                <div className="relative">
                  <Input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => setFocusedInput(true)}
                    onBlur={() => setFocusedInput(false)}
                    onKeyDown={(e) => e.key === "Enter" && handleQuery()}
                    placeholder="What would you like to know about your development context?"
                    className={`
                      w-full px-0 py-4 text-lg bg-transparent border-0 border-b-2 rounded-none
                      focus:ring-0 focus:outline-none transition-colors duration-200
                      ${focusedInput ? "border-accent" : "border-border"}
                    `}
                  />
                  <Search className="absolute right-0 top-4 w-5 h-5 text-muted-foreground" />
                </div>
                <Button
                  onClick={handleQuery}
                  disabled={!query.trim() || isQuerying}
                  className="bg-accent hover:bg-accent/90 text-accent-foreground border-0 px-8 py-2 rounded-lg font-medium transition-colors duration-200"
                >
                  {isQuerying ? "Querying..." : "Ask DevMind"}
                </Button>
              </div>
            </div>

            {/* Recent Queries */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Recent Queries</h3>
              <div className="space-y-2">
                {recentQueries.map((recentQuery, index) => (
                  <button
                    key={index}
                    onClick={() => setQuery(recentQuery)}
                    className="w-full text-left p-4 rounded-lg border border-border hover:border-muted-foreground/50 transition-colors duration-200 group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-foreground group-hover:text-accent transition-colors duration-200">
                        {recentQuery}
                      </span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors duration-200" />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Context Response Area */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Context Response</h3>
              <Card className="border border-border shadow-none">
                <CardContent className="p-8">
                  <div className="text-center text-muted-foreground py-12">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">Ask DevMind a question to see contextual insights</p>
                    <p className="text-sm mt-2">DevMind will query your connected tools via MCP</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Live Insights */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-accent" />
                <h3 className="text-lg font-medium">Live Insights</h3>
              </div>
              <div className="space-y-3">
                {insights.map((insight, index) => (
                  <Card
                    key={index}
                    className="border border-border shadow-none hover:border-muted-foreground/50 transition-colors duration-200"
                  >
                    <CardContent className="p-4">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-medium text-sm leading-tight">{insight.title}</h4>
                          <Badge
                            variant={insight.priority === "high" ? "default" : "secondary"}
                            className={`
                              text-xs px-2 py-1 rounded-full
                              ${insight.priority === "high" ? "bg-accent text-accent-foreground" : "bg-secondary text-secondary-foreground"}
                            `}
                          >
                            {insight.priority}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <MCPToolIndicator tool={insight.source} isActive={false} isQuerying={false} />
                          <Clock className="w-3 h-3" />
                          <span>{insight.time}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* System Status */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">System Status</h3>
              <Card className="border border-border shadow-none">
                <CardContent className="p-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">MCP Connections</span>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-accent rounded-full"></div>
                        <span className="text-xs text-muted-foreground">3 Active</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Context Freshness</span>
                      <span className="text-xs text-muted-foreground">Real-time</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Query Response</span>
                      <span className="text-xs text-muted-foreground">~1.2s avg</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
