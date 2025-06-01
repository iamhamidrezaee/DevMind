"""
WebSocket implementation for real-time updates in DevMind
"""
import asyncio
import json
import logging
from typing import Dict, Set, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from datetime import datetime
from uuid import UUID

from models.schemas import WSMessage, WSQueryUpdate, WSIntegrationUpdate, QueryStatus, IntegrationStatus

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Project subscriptions - which connections are listening to which projects
        self.project_subscriptions: Dict[UUID, Set[str]] = {}
        # General subscriptions (system-wide updates)
        self.general_subscriptions: Set[str] = set()
        
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "data": {
                "connection_id": connection_id,
                "message": "🚀 Connected to DevMind real-time updates!",
                "server_time": datetime.utcnow().isoformat()
            }
        }, connection_id)

    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        # Remove from active connections
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from all subscriptions
        self.general_subscriptions.discard(connection_id)
        for project_id, subscribers in self.project_subscriptions.items():
            subscribers.discard(connection_id)
        
        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def subscribe_to_project(self, connection_id: str, project_id: UUID):
        """Subscribe connection to project updates"""
        if project_id not in self.project_subscriptions:
            self.project_subscriptions[project_id] = set()
        
        self.project_subscriptions[project_id].add(connection_id)
        
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "data": {
                "project_id": str(project_id),
                "message": f"Subscribed to project {project_id} updates"
            }
        }, connection_id)
        
        logger.info(f"Connection {connection_id} subscribed to project {project_id}")

    async def subscribe_to_general(self, connection_id: str):
        """Subscribe connection to general system updates"""
        self.general_subscriptions.add(connection_id)
        
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "data": {
                "subscription_type": "general",
                "message": "Subscribed to system-wide updates"
            }
        }, connection_id)

    async def broadcast_to_project(self, project_id: UUID, message: dict):
        """Broadcast message to all connections subscribed to a project"""
        if project_id in self.project_subscriptions:
            disconnected = []
            for connection_id in self.project_subscriptions[project_id]:
                try:
                    if connection_id in self.active_connections:
                        websocket = self.active_connections[connection_id]
                        await websocket.send_text(json.dumps(message, default=str))
                except Exception as e:
                    logger.error(f"Failed to broadcast to {connection_id}: {e}")
                    disconnected.append(connection_id)
            
            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id)

    async def broadcast_general(self, message: dict):
        """Broadcast message to all general subscribers"""
        disconnected = []
        for connection_id in self.general_subscriptions:
            try:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Failed to broadcast general to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)

    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "general_subscriptions": len(self.general_subscriptions),
            "project_subscriptions": {
                str(project_id): len(subscribers)
                for project_id, subscribers in self.project_subscriptions.items()
            }
        }

# Global connection manager
manager = ConnectionManager()

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time updates"""
    
    # Generate connection ID
    import uuid
    connection_id = str(uuid.uuid4())
    
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_client_message(message, connection_id)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                }, connection_id)
            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                await manager.send_personal_message({
                    "type": "error", 
                    "data": {"message": "Message processing failed"}
                }, connection_id)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)

async def handle_client_message(message: dict, connection_id: str):
    """Handle incoming client messages"""
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "subscribe_project":
        project_id = data.get("project_id")
        if project_id:
            try:
                project_uuid = UUID(project_id)
                await manager.subscribe_to_project(connection_id, project_uuid)
            except ValueError:
                await manager.send_personal_message({
                    "type": "error",
                    "data": {"message": "Invalid project ID format"}
                }, connection_id)
    
    elif message_type == "subscribe_general":
        await manager.subscribe_to_general(connection_id)
    
    elif message_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "data": {"timestamp": datetime.utcnow().isoformat()}
        }, connection_id)
    
    elif message_type == "get_stats":
        stats = manager.get_stats()
        await manager.send_personal_message({
            "type": "stats",
            "data": stats
        }, connection_id)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": f"Unknown message type: {message_type}"}
        }, connection_id)

# API endpoints for triggering WebSocket updates (used by backend services)

@router.post("/trigger/query_update")
async def trigger_query_update(update: WSQueryUpdate):
    """Trigger query processing update"""
    message = {
        "type": "query_update",
        "data": {
            "query_id": str(update.query_id),
            "status": update.status.value,
            "progress": update.progress,
            "message": update.message,
            "partial_response": update.partial_response,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Broadcast to all general subscribers
    await manager.broadcast_general(message)
    
    return {"message": "Query update sent"}

@router.post("/trigger/integration_update")
async def trigger_integration_update(update: WSIntegrationUpdate):
    """Trigger integration status update"""
    message = {
        "type": "integration_update",
        "data": {
            "integration_id": str(update.integration_id),
            "status": update.status.value,
            "message": update.message,
            "last_sync": update.last_sync.isoformat() if update.last_sync else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Broadcast to all general subscribers
    await manager.broadcast_general(message)
    
    return {"message": "Integration update sent"}

@router.post("/trigger/insight")
async def trigger_new_insight(insight_data: dict):
    """Trigger new insight notification"""
    message = {
        "type": "new_insight",
        "data": {
            **insight_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Broadcast to relevant project or general
    project_id = insight_data.get("project_id")
    if project_id:
        try:
            project_uuid = UUID(project_id)
            await manager.broadcast_to_project(project_uuid, message)
        except ValueError:
            await manager.broadcast_general(message)
    else:
        await manager.broadcast_general(message)
    
    return {"message": "Insight notification sent"}

@router.post("/trigger/activity")
async def trigger_activity_update(activity_data: dict):
    """Trigger activity feed update"""
    message = {
        "type": "activity_update",
        "data": {
            **activity_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Broadcast based on project or general
    project_id = activity_data.get("project_id")
    if project_id:
        try:
            project_uuid = UUID(project_id)
            await manager.broadcast_to_project(project_uuid, message)
        except ValueError:
            await manager.broadcast_general(message)
    else:
        await manager.broadcast_general(message)
    
    return {"message": "Activity update sent"}

@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_stats()

# Utility functions for other services to use

async def notify_query_progress(query_id: UUID, status: QueryStatus, progress: int = 0, message: str = None):
    """Notify about query processing progress"""
    update = WSQueryUpdate(
        query_id=query_id,
        status=status,
        progress=progress,
        message=message
    )
    await trigger_query_update(update)

async def notify_integration_status(integration_id: UUID, status: IntegrationStatus, message: str = None):
    """Notify about integration status change"""
    update = WSIntegrationUpdate(
        integration_id=integration_id,
        status=status,
        message=message,
        last_sync=datetime.utcnow() if status == IntegrationStatus.ACTIVE else None
    )
    await trigger_integration_update(update)

async def notify_new_activity(activity_type: str, title: str, project_id: UUID = None, metadata: dict = None):
    """Notify about new development activity"""
    activity_data = {
        "type": activity_type,
        "title": title,
        "project_id": str(project_id) if project_id else None,
        "metadata": metadata or {}
    }
    await trigger_activity_update(activity_data)