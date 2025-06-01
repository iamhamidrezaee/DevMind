"""
Pydantic schemas for DevMind API
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID
from enum import Enum

# Enums
class SourceType(str, Enum):
    GITHUB = "github"
    SLACK = "slack"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    CUSTOM = "custom"

class EntryType(str, Enum):
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    MESSAGE = "message"
    DOCUMENT = "document"
    DECISION = "decision"
    COMMENT = "comment"

class QueryStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class IntegrationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

# Project schemas
class ProjectBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[HttpUrl] = None
    slack_channel: Optional[str] = None
    jira_project_key: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    repository_url: Optional[HttpUrl] = None
    slack_channel: Optional[str] = None
    jira_project_key: Optional[str] = None
    is_active: Optional[bool] = None

class Project(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    metadata: Dict[str, Any] = {}
    is_active: bool

# Context Entry schemas
class ContextEntryBase(BaseSchema):
    source: SourceType
    source_id: str
    entry_type: EntryType
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    timestamp: datetime

class ContextEntryCreate(ContextEntryBase):
    project_id: UUID

class ContextEntry(ContextEntryBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    metadata: Dict[str, Any] = {}

# Decision schemas
class DecisionBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=512)
    description: Optional[str] = None
    decision: str
    rationale: Optional[str] = None
    alternatives: List[str] = []
    consequences: List[str] = []
    status: str = "active"

class DecisionCreate(DecisionBase):
    project_id: UUID

class Decision(DecisionBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    related_entries: List[UUID] = []

# Query schemas
class QueryRequest(BaseSchema):
    query: str = Field(..., min_length=1, max_length=2000)
    project_id: Optional[UUID] = None
    context_limit: int = Field(default=10, ge=1, le=50)
    include_sources: List[SourceType] = Field(default_factory=lambda: list(SourceType))

class ContextMatch(BaseSchema):
    entry_id: UUID
    score: float
    source: SourceType
    entry_type: EntryType
    title: Optional[str]
    content: str
    author: Optional[str]
    timestamp: datetime
    url: Optional[str]

class QueryResponse(BaseSchema):
    query_id: UUID
    query: str
    response: str
    sources_used: List[SourceType]
    context_matches: List[ContextMatch]
    confidence_score: float
    execution_time: float
    timestamp: datetime

class QueryHistory(BaseSchema):
    id: UUID
    query_text: str
    confidence_score: Optional[float]
    execution_time: Optional[float]
    created_at: datetime
    project_id: Optional[UUID]

# Integration schemas
class IntegrationConfig(BaseSchema):
    """Base configuration for integrations"""
    pass

class GitHubConfig(IntegrationConfig):
    token: str
    repository: str
    organization: Optional[str] = None
    include_issues: bool = True
    include_pull_requests: bool = True
    include_commits: bool = True

class SlackConfig(IntegrationConfig):
    token: str
    channels: List[str]
    include_threads: bool = True
    bot_user_id: Optional[str] = None

class JiraConfig(IntegrationConfig):
    url: str
    username: str
    token: str
    project_keys: List[str]
    include_comments: bool = True

class IntegrationCreate(BaseSchema):
    project_id: UUID
    integration_type: SourceType
    configuration: Union[GitHubConfig, SlackConfig, JiraConfig]

class Integration(BaseSchema):
    id: UUID
    project_id: UUID
    integration_type: SourceType
    is_active: bool
    last_sync: Optional[datetime]
    sync_status: IntegrationStatus
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

# WebSocket schemas
class WSMessage(BaseSchema):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WSQueryUpdate(BaseSchema):
    query_id: UUID
    status: QueryStatus
    progress: int = Field(ge=0, le=100)
    message: Optional[str] = None
    partial_response: Optional[str] = None

class WSIntegrationUpdate(BaseSchema):
    integration_id: UUID
    status: IntegrationStatus
    message: Optional[str] = None
    last_sync: Optional[datetime] = None

# Insights and Analytics schemas
class InsightType(str, Enum):
    ACTIVITY_SPIKE = "activity_spike"
    CRITICAL_ISSUE = "critical_issue"
    TEAM_MENTION = "team_mention"
    DEPLOYMENT = "deployment"
    SECURITY_ALERT = "security_alert"

class Insight(BaseSchema):
    id: UUID
    type: InsightType
    title: str
    description: str
    source: SourceType
    priority: str = Field(regex="^(low|medium|high|critical)$")
    timestamp: datetime
    url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class SystemStatus(BaseSchema):
    mcp_connections: int
    active_integrations: int
    context_freshness: str
    avg_query_time: float
    last_sync: datetime
    health_status: str

# Error schemas
class ErrorResponse(BaseSchema):
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None