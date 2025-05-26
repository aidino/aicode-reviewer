"""
Unit tests for TaskQueueService.

This module contains comprehensive tests for the task queue service
including task creation, execution, status tracking, and error handling.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.webapp.backend.services.task_queue_service import (
    TaskQueueService, TaskInfo, TaskStatus, get_task_queue_service
)
from src.webapp.backend.models.scan_models import ScanRequest, ScanType


class TestTaskQueueService:
    """Test cases for TaskQueueService class."""
    
    @pytest.fixture
    def task_queue_service(self):
        """Create a TaskQueueService instance for testing."""
        return TaskQueueService()
    
    @pytest.fixture
    def sample_scan_request(self):
        """Create a sample ScanRequest for testing."""
        return ScanRequest(
            repo_url="https://github.com/test/repo",
            scan_type=ScanType.PR,
            pr_id=123,
            branch="feature/test",
            target_branch="main"
        )
    
    def test_task_queue_service_initialization(self, task_queue_service):
        """Test TaskQueueService initialization."""
        assert isinstance(task_queue_service._tasks, dict)
        assert isinstance(task_queue_service._running_tasks, dict)
        assert len(task_queue_service._tasks) == 0
        assert len(task_queue_service._running_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_initiate_scan_success(self, task_queue_service, sample_scan_request):
        """Test successful scan initiation."""
        scan_id, job_id = await task_queue_service.initiate_scan(sample_scan_request)
        
        # Check returned IDs
        assert scan_id.startswith("pr_")
        assert job_id.startswith("job_")
        
        # Check task was created
        assert job_id in task_queue_service._tasks
        task_info = task_queue_service._tasks[job_id]
        assert task_info.scan_id == scan_id
        assert task_info.scan_request == sample_scan_request
        assert task_info.status == TaskStatus.PENDING
        
        # Check running task was created
        assert job_id in task_queue_service._running_tasks
        
        # Wait for task to complete
        await asyncio.sleep(0.1)
    
    @pytest.mark.asyncio
    async def test_initiate_scan_with_callback(self, task_queue_service, sample_scan_request):
        """Test scan initiation with orchestrator callback."""
        mock_callback = AsyncMock(return_value={"status": "success"})
        
        scan_id, job_id = await task_queue_service.initiate_scan(
            sample_scan_request, 
            orchestrator_callback=mock_callback
        )
        
        # Wait for task to complete
        await asyncio.sleep(7)  # Give enough time for the task to complete
        
        # Check callback was called
        mock_callback.assert_called_once_with(sample_scan_request)
        
        # Check task completed
        task_info = task_queue_service._tasks[job_id]
        assert task_info.status == TaskStatus.COMPLETED
        assert task_info.result == {"status": "success"}
    
    def test_get_task_status_existing(self, task_queue_service, sample_scan_request):
        """Test getting status of existing task."""
        # Create a task manually
        job_id = "test_job_123"
        task_info = TaskInfo(job_id, "test_scan_123", sample_scan_request)
        task_info.status = TaskStatus.RUNNING
        task_info.progress = 50
        task_info.started_at = datetime.now()
        task_queue_service._tasks[job_id] = task_info
        
        status = task_queue_service.get_task_status(job_id)
        
        assert status is not None
        assert status["job_id"] == job_id
        assert status["scan_id"] == "test_scan_123"
        assert status["status"] == "running"
        assert status["progress"] == 50
        assert status["repository"] == sample_scan_request.repo_url
        assert status["scan_type"] == sample_scan_request.scan_type.value
    
    def test_get_task_status_nonexistent(self, task_queue_service):
        """Test getting status of non-existent task."""
        status = task_queue_service.get_task_status("nonexistent_job")
        assert status is None
    
    def test_get_scan_status_by_scan_id_existing(self, task_queue_service, sample_scan_request):
        """Test getting scan status by scan ID."""
        # Create a task manually
        job_id = "test_job_123"
        scan_id = "test_scan_123"
        task_info = TaskInfo(job_id, scan_id, sample_scan_request)
        task_queue_service._tasks[job_id] = task_info
        
        status = task_queue_service.get_scan_status_by_scan_id(scan_id)
        
        assert status is not None
        assert status["scan_id"] == scan_id
        assert status["job_id"] == job_id
    
    def test_get_scan_status_by_scan_id_nonexistent(self, task_queue_service):
        """Test getting scan status for non-existent scan ID."""
        status = task_queue_service.get_scan_status_by_scan_id("nonexistent_scan")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_cancel_task_running(self, task_queue_service, sample_scan_request):
        """Test cancelling a running task."""
        scan_id, job_id = await task_queue_service.initiate_scan(sample_scan_request)
        
        # Ensure task is running
        await asyncio.sleep(0.1)
        
        # Cancel the task
        result = await task_queue_service.cancel_task(job_id)
        assert result is True
        
        # Wait for cancellation to process
        await asyncio.sleep(0.1)
        
        # Check task status
        task_info = task_queue_service._tasks[job_id]
        assert task_info.status == TaskStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_task_nonexistent(self, task_queue_service):
        """Test cancelling a non-existent task."""
        result = await task_queue_service.cancel_task("nonexistent_job")
        assert result is False
    
    def test_cleanup_old_tasks(self, task_queue_service, sample_scan_request):
        """Test cleaning up old completed tasks."""
        # Create old completed task
        old_job_id = "old_job_123"
        old_task_info = TaskInfo(old_job_id, "old_scan_123", sample_scan_request)
        old_task_info.status = TaskStatus.COMPLETED
        old_task_info.created_at = datetime.now() - timedelta(hours=25)  # 25 hours old
        task_queue_service._tasks[old_job_id] = old_task_info
        
        # Create recent task
        recent_job_id = "recent_job_456"
        recent_task_info = TaskInfo(recent_job_id, "recent_scan_456", sample_scan_request)
        recent_task_info.status = TaskStatus.COMPLETED
        recent_task_info.created_at = datetime.now() - timedelta(hours=1)  # 1 hour old
        task_queue_service._tasks[recent_job_id] = recent_task_info
        
        # Cleanup tasks older than 24 hours
        cleaned_count = task_queue_service.cleanup_old_tasks(max_age_hours=24)
        
        assert cleaned_count == 1
        assert old_job_id not in task_queue_service._tasks
        assert recent_job_id in task_queue_service._tasks
    
    @pytest.mark.asyncio
    async def test_execute_scan_task_failure(self, task_queue_service, sample_scan_request):
        """Test scan task execution with failure."""
        def failing_callback(request):
            raise Exception("Test failure")
        
        scan_id, job_id = await task_queue_service.initiate_scan(
            sample_scan_request,
            orchestrator_callback=failing_callback
        )
        
        # Wait for task to complete
        await asyncio.sleep(7)
        
        # Check task failed
        task_info = task_queue_service._tasks[job_id]
        assert task_info.status == TaskStatus.FAILED
        assert task_info.error_message == "Test failure"
    
    def test_task_info_initialization(self, sample_scan_request):
        """Test TaskInfo initialization."""
        task_id = "test_task_123"
        scan_id = "test_scan_123"
        
        task_info = TaskInfo(task_id, scan_id, sample_scan_request)
        
        assert task_info.task_id == task_id
        assert task_info.scan_id == scan_id
        assert task_info.scan_request == sample_scan_request
        assert task_info.status == TaskStatus.PENDING
        assert isinstance(task_info.created_at, datetime)
        assert task_info.started_at is None
        assert task_info.completed_at is None
        assert task_info.error_message is None
        assert task_info.progress == 0
        assert task_info.result is None


class TestTaskQueueServiceSingleton:
    """Test cases for task queue service singleton pattern."""
    
    def test_get_task_queue_service_singleton(self):
        """Test that get_task_queue_service returns the same instance."""
        service1 = get_task_queue_service()
        service2 = get_task_queue_service()
        
        assert service1 is service2
        assert isinstance(service1, TaskQueueService)
    
    @patch('src.webapp.backend.services.task_queue_service._task_queue_service', None)
    def test_get_task_queue_service_creates_instance(self):
        """Test that get_task_queue_service creates new instance when None."""
        service = get_task_queue_service()
        assert isinstance(service, TaskQueueService)


class TestTaskStatus:
    """Test cases for TaskStatus enum."""
    
    def test_task_status_values(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


@pytest.mark.asyncio
async def test_integration_full_scan_workflow():
    """Integration test for complete scan workflow."""
    task_queue = TaskQueueService()
    
    scan_request = ScanRequest(
        repo_url="https://github.com/integration/test",
        scan_type=ScanType.PROJECT,
        branch="main"
    )
    
    # Mock orchestrator callback
    mock_callback = AsyncMock(return_value={
        "scan_completed": True,
        "findings_count": 10,
        "status": "success"
    })
    
    # Initiate scan
    scan_id, job_id = await task_queue.initiate_scan(scan_request, mock_callback)
    
    # Check initial status
    initial_status = task_queue.get_task_status(job_id)
    assert initial_status["status"] == "pending"
    
    # Wait for completion
    await asyncio.sleep(7)
    
    # Check final status
    final_status = task_queue.get_task_status(job_id)
    assert final_status["status"] == "completed"
    assert final_status["progress"] == 100
    
    # Check by scan ID
    scan_status = task_queue.get_scan_status_by_scan_id(scan_id)
    assert scan_status["scan_id"] == scan_id
    assert scan_status["status"] == "completed"
    
    # Verify callback was called
    mock_callback.assert_called_once_with(scan_request) 