"""
Main API routes for DevMind Backend
"""
import asyncio
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
import time

from models.database import get_db
from models.schemas import (
    QueryRequest, QueryResponse, QueryHistory,
    Project, ProjectCreate, ProjectUpdate,
    ContextEntry, ContextEntryCreate,
    Integration, IntegrationCreate,
    Insight, SystemStatus,
    ErrorResponse
)
from services.context_service import ContextService
from services.vector_service import VectorService

logger = logging.getLogger(__name__)
router = APIRouter()

# Global services (will be properly injected in production)
context_service = ContextService()
vector_service = VectorService()

@router.get("/")
async def api_info():
    """API information and health"""
    return {
        "name": "DevMind API",
        "version": "1.0.0",
        "status": "🚀 Ready to win the hackathon!",
        "endpoints": [
            "/query - Submit context queries",
            "/projects - Manage projects",
            "/integrations - Manage tool integrations",
            "/insights - Get live insights",
            "/system - System status"
        ]
    }

# Query endpoints
@router.post("/query", response_model=QueryResponse)
async def submit_query(
    query_request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Submit a context query and get AI-powered response"""
    start_time = time.time()
    
    try:
        logger.info(f"Processing query: {query_request.query[:100]}...")
        
        # Generate query ID
        query_id = uuid4()
        
        # Process query through context service
        response = await context_service.process_query(
            query_id=query_id,
            query_text=query_request.query,
            project_id=query_request.project_id,
            context_limit=query_request.context_limit,
            include_sources=query_request.include_sources
        )
        
        execution_time = time.time() - start_time
        
        # Store query in background
        background_tasks.add_task(
            _store_query_history,
            db, query_id, query_request, response, execution_time
        )
        
        logger.info(f"Query processed successfully in {execution_time:.2f}s")
        
        return QueryResponse(
            query_id=query_id,
            query=query_request.query,
            response=response["answer"],
            sources_used=response["sources_used"],
            context_matches=response["context_matches"],
            confidence_score=response["confidence_score"],
            execution_time=execution_time,
            timestamp=response["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@router.get("/query/history", response_model=List[QueryHistory])
async def get_query_history(
    project_id: Optional[UUID] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get query history"""
    try:
        history = await context_service.get_query_history(
            db=db,
            project_id=project_id,
            limit=limit
        )
        return history
    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Project endpoints
@router.get("/projects", response_model=List[Project])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects"""
    try:
        projects = await context_service.list_projects(db)
        return projects
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects", response_model=Project)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    try:
        new_project = await context_service.create_project(db, project)
        logger.info(f"Created project: {new_project.name}")
        return new_project
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get project by ID"""
    try:
        project = await context_service.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update project"""
    try:
        updated_project = await context_service.update_project(
            db, project_id, project_update
        )
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Integration endpoints
@router.get("/integrations", response_model=List[Integration])
async def list_integrations(
    project_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """List integrations"""
    try:
        integrations = await context_service.list_integrations(db, project_id)
        return integrations
    except Exception as e:
        logger.error(f"Failed to list integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations", response_model=Integration)
async def create_integration(
    integration: IntegrationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a new integration"""
    try:
        new_integration = await context_service.create_integration(db, integration)
        
        # Start initial sync in background
        background_tasks.add_task(
            _sync_integration,
            new_integration.id
        )
        
        logger.info(f"Created integration: {integration.integration_type}")
        return new_integration
    except Exception as e:
        logger.error(f"Failed to create integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations/{integration_id}/sync")
async def sync_integration(
    integration_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger integration sync"""
    try:
        integration = await context_service.get_integration(db, integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Start sync in background
        background_tasks.add_task(_sync_integration, integration_id)
        
        return {"message": "Sync started", "integration_id": integration_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Insights endpoints
@router.get("/insights", response_model=List[Insight])
async def get_insights(
    project_id: Optional[UUID] = None,
    limit: int = 10
):
    """Get live insights"""
    try:
        insights = await context_service.get_live_insights(
            project_id=project_id,
            limit=limit
        )
        return insights
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System endpoints
@router.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status"""
    try:
        status = await context_service.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/health")
async def system_health():
    """Simple health check"""
    return {"status": "healthy", "message": "🚀 System is ready!"}

# Context endpoints
@router.get("/context/search")
async def search_context(
    query: str,
    project_id: Optional[UUID] = None,
    sources: Optional[List[str]] = None,
    limit: int = 10
):
    """Search through development context"""
    try:
        results = await context_service.search_context(
            query=query,
            project_id=project_id,
            sources=sources or [],
            limit=limit
        )
        return results
    except Exception as e:
        logger.error(f"Context search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context/timeline")
async def get_context_timeline(
    project_id: UUID,
    days: int = 30
):
    """Get project context timeline"""
    try:
        timeline = await context_service.get_project_timeline(
            project_id=project_id,
            days=days
        )
        return timeline
    except Exception as e:
        logger.error(f"Failed to get timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def _store_query_history(
    db: AsyncSession,
    query_id: UUID,
    query_request: QueryRequest,
    response: dict,
    execution_time: float
):
    """Store query in history"""
    try:
        await context_service.store_query(
            db=db,
            query_id=query_id,
            query_text=query_request.query,
            project_id=query_request.project_id,
            response=response,
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Failed to store query history: {e}")

async def _sync_integration(integration_id: UUID):
    """Sync integration data"""
    try:
        await context_service.sync_integration(integration_id)
        logger.info(f"Integration {integration_id} synced successfully")
    except Exception as e:
        logger.error(f"Integration sync failed: {e}")