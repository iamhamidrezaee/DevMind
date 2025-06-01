"""
DevMind Backend - AI-Powered Development Context Oracle
FastAPI application with MCP protocol implementation
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings, get_cors_origins
from models.database import init_db, close_db
from api.routes import router as api_router
from api.websocket import router as ws_router
from mcp.server import MCPServer
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global MCP server instance
mcp_server: MCPServer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global mcp_server
    
    logger.info("🚀 Starting DevMind Backend...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized")
        
        # Initialize MCP server
        mcp_server = MCPServer()
        await mcp_server.start()
        logger.info("✅ MCP Server started")
        
        # Initialize vector service
        from services.vector_service import VectorService
        vector_service = VectorService()
        await vector_service.initialize()
        logger.info("✅ Vector service initialized")
        
        logger.info("🎉 DevMind Backend is ready to dominate!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🛑 Shutting down DevMind Backend...")
        
        if mcp_server:
            await mcp_server.stop()
            logger.info("✅ MCP Server stopped")
        
        await close_db()
        logger.info("✅ Database connections closed")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Development Context Oracle with MCP Protocol",
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/ws")

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "🚀 Ready to win the hackathon!",
        "mcp_status": "active" if mcp_server and mcp_server.is_running else "inactive",
        "endpoints": {
            "api": "/api/v1",
            "websocket": "/ws",
            "docs": "/docs",
            "mcp": "/mcp"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    try:
        # Check database
        from models.database import check_db_health
        db_healthy = await check_db_health()
        
        # Check MCP server
        mcp_healthy = mcp_server and mcp_server.is_running
        
        # Check integrations
        from services.context_service import ContextService
        context_service = ContextService()
        integrations_status = await context_service.check_integrations()
        
        return {
            "status": "healthy" if all([db_healthy, mcp_healthy]) else "unhealthy",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "mcp_server": "healthy" if mcp_healthy else "unhealthy",
                "integrations": integrations_status
            },
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error responses"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong. Our team has been notified.",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )