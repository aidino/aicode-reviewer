"""
Task queue service for handling asynchronous scan operations.

This module provides task queue functionality for processing code scans
in the background using asyncio task management.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from ..models.scan_models import ScanRequest, ScanStatus, ScanType

# Configure logging
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Enumeration for task statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInfo:
    """Information about a background task."""
    
    def __init__(self, task_id: str, scan_id: str, scan_request: ScanRequest):
        """
        Initialize task info.
        
        Args:
            task_id (str): Unique task identifier
            scan_id (str): Associated scan identifier
            scan_request (ScanRequest): Original scan request
        """
        self.task_id = task_id
        self.scan_id = scan_id
        self.scan_request = scan_request
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.progress: int = 0
        self.result: Optional[Any] = None


class TaskQueueService:
    """
    Service for managing background scan tasks.
    
    This service handles the creation, execution, and monitoring of
    background scan tasks using asyncio.
    """
    
    def __init__(self):
        """Initialize the task queue service."""
        logger.info("Initializing TaskQueueService")
        self._tasks: Dict[str, TaskInfo] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        
    async def initiate_scan(
        self, 
        scan_request: ScanRequest, 
        orchestrator_callback: Optional[Callable] = None
    ) -> tuple[str, str]:
        """
        Initiate a new scan task.
        
        Args:
            scan_request (ScanRequest): Scan configuration
            orchestrator_callback (Optional[Callable]): Callback to actual orchestrator
            
        Returns:
            tuple[str, str]: (scan_id, job_id)
        """
        # Generate unique identifiers
        scan_id = f"{scan_request.scan_type.value}_{uuid.uuid4().hex[:8]}"
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Initiating scan: scan_id={scan_id}, job_id={job_id}")
        
        # Create task info
        task_info = TaskInfo(job_id, scan_id, scan_request)
        self._tasks[job_id] = task_info
        
        # Create and start the background task
        async_task = asyncio.create_task(
            self._execute_scan_task(task_info, orchestrator_callback)
        )
        self._running_tasks[job_id] = async_task
        
        logger.info(f"Started background task for scan_id={scan_id}")
        return scan_id, job_id
    
    async def _execute_scan_task(
        self, 
        task_info: TaskInfo, 
        orchestrator_callback: Optional[Callable] = None
    ) -> None:
        """
        Execute a scan task in the background.
        
        Args:
            task_info (TaskInfo): Task information
            orchestrator_callback (Optional[Callable]): Callback to orchestrator
        """
        task_info.status = TaskStatus.RUNNING
        task_info.started_at = datetime.now()
        
        try:
            logger.info(f"Executing scan task: {task_info.task_id}")
            
            # Simulate scan progress
            for progress in [10, 30, 50, 70, 90, 100]:
                await asyncio.sleep(1)  # Simulate work
                task_info.progress = progress
                logger.debug(f"Task {task_info.task_id} progress: {progress}%")
            
            # TODO: Call actual LangGraph orchestrator
            if orchestrator_callback:
                result = await orchestrator_callback(task_info.scan_request)
                task_info.result = result
            else:
                # Mock result for now
                task_info.result = {
                    "scan_id": task_info.scan_id,
                    "status": "completed",
                    "findings_count": 5,
                    "message": "Scan completed successfully"
                }
            
            task_info.status = TaskStatus.COMPLETED
            task_info.completed_at = datetime.now()
            logger.info(f"Task {task_info.task_id} completed successfully")
            
        except asyncio.CancelledError:
            task_info.status = TaskStatus.CANCELLED
            logger.info(f"Task {task_info.task_id} was cancelled")
            
        except Exception as e:
            task_info.status = TaskStatus.FAILED
            task_info.error_message = str(e)
            logger.error(f"Task {task_info.task_id} failed: {str(e)}")
            
        finally:
            # Clean up running task reference
            if task_info.task_id in self._running_tasks:
                del self._running_tasks[task_info.task_id]
    
    def get_task_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task.
        
        Args:
            job_id (str): Task job identifier
            
        Returns:
            Optional[Dict[str, Any]]: Task status information
        """
        task_info = self._tasks.get(job_id)
        if not task_info:
            return None
        
        duration = None
        if task_info.started_at:
            end_time = task_info.completed_at or datetime.now()
            duration = (end_time - task_info.started_at).total_seconds()
        
        return {
            "job_id": job_id,
            "scan_id": task_info.scan_id,
            "status": task_info.status.value,
            "progress": task_info.progress,
            "created_at": task_info.created_at.isoformat(),
            "started_at": task_info.started_at.isoformat() if task_info.started_at else None,
            "completed_at": task_info.completed_at.isoformat() if task_info.completed_at else None,
            "duration_seconds": duration,
            "error_message": task_info.error_message,
            "repository": task_info.scan_request.repo_url,
            "scan_type": task_info.scan_request.scan_type.value
        }
    
    def get_scan_status_by_scan_id(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get scan status by scan ID.
        
        Args:
            scan_id (str): Scan identifier
            
        Returns:
            Optional[Dict[str, Any]]: Task status information
        """
        for task_info in self._tasks.values():
            if task_info.scan_id == scan_id:
                return self.get_task_status(task_info.task_id)
        return None
    
    async def cancel_task(self, job_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            job_id (str): Task job identifier
            
        Returns:
            bool: True if task was cancelled, False if not found or not running
        """
        if job_id in self._running_tasks:
            task = self._running_tasks[job_id]
            task.cancel()
            logger.info(f"Cancelled task: {job_id}")
            return True
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed/failed tasks.
        
        Args:
            max_age_hours (int): Maximum age in hours for keeping tasks
            
        Returns:
            int: Number of tasks cleaned up
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        tasks_to_remove = []
        
        for job_id, task_info in self._tasks.items():
            if (task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
                and task_info.created_at < cutoff_time):
                tasks_to_remove.append(job_id)
        
        for job_id in tasks_to_remove:
            del self._tasks[job_id]
        
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
        return len(tasks_to_remove)


# Global task queue service instance
_task_queue_service: Optional[TaskQueueService] = None


def get_task_queue_service() -> TaskQueueService:
    """
    Get the global task queue service instance.
    
    Returns:
        TaskQueueService: Global task queue service
    """
    global _task_queue_service
    if _task_queue_service is None:
        _task_queue_service = TaskQueueService()
    return _task_queue_service 