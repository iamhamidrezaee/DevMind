"""
Database setup and models for DevMind
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from config import get_database_url, settings

logger = logging.getLogger(__name__)

# Database engine and session
engine = create_async_engine(
    get_database_url(),
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Database Models
class Project(Base):
    """Project information and metadata"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repository_url = Column(String(512))
    slack_channel = Column(String(255))
    jira_project_key = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    metadata = Column(JSON, default={})
    is_active = Column(Boolean, default=True)

class ContextEntry(Base):
    """Individual context entries from various sources"""
    __tablename__ = "context_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    source = Column(String(50), nullable=False)  # github, slack, jira, etc.
    source_id = Column(String(255), nullable=False)  # external ID
    entry_type = Column(String(50), nullable=False)  # commit, message, issue, etc.
    title = Column(String(512))
    content = Column(Text)
    author = Column(String(255))
    url = Column(String(512))
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON, default={})
    
    # Vector embedding for semantic search
    embedding = Column(Vector(settings.vector_dimension))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_context_project_source', 'project_id', 'source'),
        Index('idx_context_timestamp', 'timestamp'),
        Index('idx_context_source_id', 'source', 'source_id'),
    )

class Decision(Base):
    """Architecture decisions and important choices"""
    __tablename__ = "decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(512), nullable=False)
    description = Column(Text)
    decision = Column(Text, nullable=False)
    rationale = Column(Text)
    alternatives = Column(JSON, default=[])
    consequences = Column(JSON, default=[])
    status = Column(String(50), default='active')  # active, superseded, deprecated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    related_entries = Column(ARRAY(UUID), default=[])
    
    # Vector embedding for semantic search
    embedding = Column(Vector(settings.vector_dimension))

class Query(Base):
    """User queries and responses for learning"""
    __tablename__ = "queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True))
    query_text = Column(Text, nullable=False)
    response = Column(JSON)
    sources_used = Column(ARRAY(String), default=[])
    confidence_score = Column(Float)
    execution_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_feedback = Column(JSON)  # thumbs up/down, corrections, etc.
    
    # Vector embedding for query similarity
    embedding = Column(Vector(settings.vector_dimension))

class Integration(Base):
    """Integration status and configuration"""
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    integration_type = Column(String(50), nullable=False)  # github, slack, jira
    configuration = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default='pending')  # pending, success, error
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Database session dependency
async def get_db() -> AsyncSession:
    """Database session dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database and create tables"""
    try:
        async with engine.begin() as conn:
            # Create pgvector extension if not exists
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("✅ Database connections closed")

async def check_db_health() -> bool:
    """Check database health"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Import text for raw SQL queries
from sqlalchemy import text