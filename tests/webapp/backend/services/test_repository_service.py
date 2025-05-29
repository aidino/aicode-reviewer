"""
Unit tests for repository service.

Tests cover:
- Repository type detection
- GitHub metadata fetching
- Local metadata parsing
- Error handling for various scenarios
"""

import pytest
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path

from src.webapp.backend.services.repository_service import (
    detect_repository_type,
    fetch_github_metadata,
    parse_local_metadata,
    clone_repository,
    add_repository_with_metadata
)


class TestDetectRepositoryType:
    """Test repository type detection from URLs."""
    
    def test_github_url_detection(self):
        """Test GitHub URL detection."""
        result = detect_repository_type("https://github.com/user/repo")
        assert result == ("github", "user", "repo")
        
        result = detect_repository_type("https://github.com/user/repo.git")
        assert result == ("github", "user", "repo")
    
    def test_gitlab_url_detection(self):
        """Test GitLab URL detection."""
        result = detect_repository_type("https://gitlab.com/user/repo")
        assert result == ("gitlab", "user", "repo")
    
    def test_bitbucket_url_detection(self):
        """Test Bitbucket URL detection."""
        result = detect_repository_type("https://bitbucket.org/user/repo")
        assert result == ("bitbucket", "user", "repo")
    
    def test_unknown_url_detection(self):
        """Test unknown repository type."""
        with pytest.raises(ValueError) as exc_info:
            detect_repository_type("https://example.com/user/repo")
        assert "Không hỗ trợ repo_url này" in str(exc_info.value)


class TestFetchGithubMetadata:
    """Test GitHub metadata fetching."""
    
    @patch('requests.get')
    def test_fetch_public_repo_metadata(self, mock_get):
        """Test fetching metadata for public repository."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Hello-World",
            "description": "My first repository on GitHub!",
            "language": "Python",
            "default_branch": "main",
            "private": False,
            "stargazers_count": 100,
            "forks_count": 50,
            "owner": {
                "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4"
            }
        }
        mock_get.return_value = mock_response
        
        metadata = fetch_github_metadata("octocat", "Hello-World")
        
        assert metadata["name"] == "Hello-World"
        assert metadata["description"] == "My first repository on GitHub!"
        assert metadata["language"] == "Python"
        assert metadata["default_branch"] == "main"
        assert metadata["is_private"] is False
        assert metadata["stars"] == 100
        assert metadata["forks"] == 50
    
    @patch('requests.get')
    def test_fetch_repo_not_found(self, mock_get):
        """Test handling of repository not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc_info:
            fetch_github_metadata("user", "nonexistent")
        assert "Không lấy được metadata từ GitHub API" in str(exc_info.value)


class TestParseLocalMetadata:
    """Test local repository metadata parsing."""
    
    def test_parse_git_repo_metadata(self):
        """Test parsing metadata from local git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create README.md
            readme_file = Path(temp_dir) / "README.md"
            readme_file.write_text("# Test Repository\n\nThis is a test repository.")
            
            metadata = parse_local_metadata(temp_dir)
            
            assert metadata["name"] == os.path.basename(temp_dir)
            assert metadata["description"] == "# Test Repository"
            assert metadata["is_private"] is False
            assert metadata["stars"] == 0
            assert metadata["forks"] == 0
    
    def test_parse_non_git_directory(self):
        """Test parsing metadata from non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata = parse_local_metadata(temp_dir)
            
            assert metadata["name"] == os.path.basename(temp_dir)
            assert metadata["description"] is None


class TestCloneRepository:
    """Test repository cloning functionality."""
    
    @patch('git.Repo.clone_from')
    def test_clone_public_repository(self, mock_clone):
        """Test cloning public repository."""
        mock_repo = Mock()
        mock_clone.return_value = mock_repo
        
        result = clone_repository("https://github.com/octocat/Hello-World")
        
        assert result.startswith("/tmp/repo_clone_")
        mock_clone.assert_called_once()
    
    @patch('git.Repo.clone_from')
    def test_clone_private_repository_with_token(self, mock_clone):
        """Test cloning private repository with access token."""
        mock_repo = Mock()
        mock_clone.return_value = mock_repo
        
        result = clone_repository(
            "https://github.com/user/private-repo",
            access_token="ghp_test_token"
        )
        
        assert result.startswith("/tmp/repo_clone_")
        
        # Verify URL was modified to include token
        call_args = mock_clone.call_args[0]
        expected_url = "https://ghp_test_token:x-oauth-basic@github.com/user/private-repo"
        assert call_args[0] == expected_url
    
    @patch('git.Repo.clone_from')
    def test_clone_repository_failure(self, mock_clone):
        """Test handling of clone failure."""
        from git.exc import GitCommandError
        
        mock_clone.side_effect = GitCommandError("git clone", 128, "Authentication failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            clone_repository("https://github.com/user/private-repo")
        
        assert "Clone repo thất bại" in str(exc_info.value)


class TestAddRepositoryWithMetadata:
    """Test the main add repository workflow."""
    
    @patch('src.webapp.backend.services.repository_service.clone_repository')
    @patch('src.webapp.backend.services.repository_service.fetch_github_metadata')
    @patch('src.webapp.backend.services.repository_service.Project')
    def test_add_github_repository_success(self, mock_project_class, mock_fetch, mock_clone):
        """Test successful addition of GitHub repository."""
        mock_db = Mock()
        
        # Mock clone
        mock_clone.return_value = "/tmp/test_repo"
        
        # Mock GitHub metadata
        mock_fetch.return_value = {
            "name": "test-repo",
            "description": "Test repository",
            "language": "Python",
            "default_branch": "main",
            "is_private": False,
            "stars": 10,
            "forks": 5,
            "avatar_url": "https://avatars.githubusercontent.com/u/123?v=4"
        }
        
        # Mock Project instance
        mock_project = Mock()
        mock_project.id = 1
        mock_project.name = "test-repo"
        mock_project.description = "Test repository"
        mock_project.language = "Python"
        mock_project.is_private = False
        mock_project.stars = 10
        mock_project.forks = 5
        mock_project.owner_id = 1
        mock_project.url = "https://github.com/user/test-repo"
        mock_project.avatar_url = "https://avatars.githubusercontent.com/u/123?v=4"
        mock_project.default_branch = "main"
        mock_project.created_at = "2023-01-01T00:00:00Z"
        mock_project.updated_at = "2023-01-01T00:00:00Z"
        mock_project.last_synced_at = "2023-01-01T00:00:00Z"
        
        mock_project_class.return_value = mock_project
        
        # Mock database operations
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        result = add_repository_with_metadata(
            mock_db,
            "https://github.com/user/test-repo",
            1
        )
        
        # Verify repository was created with correct data
        assert result["name"] == "test-repo"
        assert result["description"] == "Test repository"
        assert result["language"] == "Python"
        assert result["is_private"] is False
        assert result["stars"] == 10
        assert result["forks"] == 5
        assert result["owner_id"] == 1
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @patch('src.webapp.backend.services.repository_service.clone_repository')
    def test_add_repository_clone_failure(self, mock_clone):
        """Test handling of clone failure."""
        mock_db = Mock()
        
        # Mock clone failure
        mock_clone.side_effect = RuntimeError("Clone failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            add_repository_with_metadata(
                mock_db,
                "https://github.com/user/invalid-repo",
                1
            )
        
        assert "Clone failed" in str(exc_info.value) 