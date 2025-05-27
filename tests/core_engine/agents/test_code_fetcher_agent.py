"""
Unit tests for CodeFetcherAgent.

This module contains comprehensive tests for the CodeFetcherAgent functionality,
including repository cloning, PR diff fetching, and project file retrieval.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock, mock_open
from git import Repo, GitCommandError

from src.core_engine.agents.code_fetcher_agent import CodeFetcherAgent


class TestCodeFetcherAgent:
    """Test cases for CodeFetcherAgent class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = CodeFetcherAgent()
    
    def test_init(self):
        """Test CodeFetcherAgent initialization."""
        agent = CodeFetcherAgent()
        
        assert hasattr(agent, 'supported_extensions')
        assert hasattr(agent, 'supported_languages')
        assert 'python' in agent.supported_extensions
        assert '.py' in agent.supported_extensions['python']
    
    def test_get_supported_file_extensions(self):
        """Test getting supported file extensions."""
        extensions = self.agent._get_supported_file_extensions()
        
        assert isinstance(extensions, list)
        assert '.py' in extensions
        assert '.java' in extensions
        assert '.kt' in extensions
    
    def test_is_supported_file(self):
        """Test file extension checking."""
        # Test supported files
        assert self.agent._is_supported_file("main.py") == True
        assert self.agent._is_supported_file("src/utils.java") == True
        assert self.agent._is_supported_file("app/MainActivity.kt") == True
        
        # Test unsupported files
        assert self.agent._is_supported_file("README.md") == False
        assert self.agent._is_supported_file("config.json") == False
        assert self.agent._is_supported_file("style.css") == False
        
        # Test case insensitive
        assert self.agent._is_supported_file("Main.PY") == True
        assert self.agent._is_supported_file("Utils.JAVA") == True
    
    @patch('src.core_engine.agents.code_fetcher_agent.Repo.clone_from')
    def test_clone_repository_success(self, mock_clone):
        """Test successful repository cloning."""
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        repo_url = "https://github.com/test/repo.git"
        target_dir = "/tmp/test"
        
        result = self.agent._clone_repository(repo_url, target_dir)
        
        assert result == mock_repo
        mock_clone.assert_called_once_with(
            repo_url, 
            target_dir,
            multi_options=['--no-single-branch']
        )
    
    @patch('src.core_engine.agents.code_fetcher_agent.Repo.clone_from')
    def test_clone_repository_failure(self, mock_clone):
        """Test repository cloning failure."""
        mock_clone.side_effect = GitCommandError("clone", "error")
        
        repo_url = "https://github.com/invalid/repo.git"
        target_dir = "/tmp/test"
        
        with pytest.raises(GitCommandError):
            self.agent._clone_repository(repo_url, target_dir)
    
    def test_checkout_branch_success(self):
        """Test successful branch checkout."""
        mock_repo = MagicMock()
        mock_git = MagicMock()
        mock_repo.git = mock_git
        
        self.agent._checkout_branch(mock_repo, "main")
        
        mock_git.checkout.assert_called_with("main")
    
    def test_checkout_branch_with_remote_fallback(self):
        """Test branch checkout with remote fallback."""
        mock_repo = MagicMock()
        mock_git = MagicMock()
        mock_repo.git = mock_git
        
        # First call fails, second succeeds
        mock_git.checkout.side_effect = [GitCommandError("checkout", "error"), None]
        
        self.agent._checkout_branch(mock_repo, "feature-branch")
        
        # Should try local first, then remote
        assert mock_git.checkout.call_count == 2
        mock_git.checkout.assert_any_call("feature-branch")
        mock_git.checkout.assert_any_call("origin/feature-branch")
    
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch.object(CodeFetcherAgent, '_clone_repository')
    @patch.object(CodeFetcherAgent, '_checkout_branch')
    def test_get_pr_diff_success(self, mock_checkout, mock_clone, mock_exists, mock_rmtree, mock_mkdtemp):
        """Test successful PR diff retrieval."""
        # Setup mocks
        mock_mkdtemp.return_value = "/tmp/test_dir"
        mock_exists.return_value = True
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        # Mock git diff output
        mock_repo.remotes.origin.fetch.return_value = None
        mock_repo.git.diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        
        # Test
        result = self.agent.get_pr_diff(
            repo_url="https://github.com/test/repo.git",
            pr_id=123,
            target_branch="main",
            source_branch="feature"
        )
        
        # Assertions
        assert "diff --git a/file.py b/file.py" in result
        assert "+new line" in result
        mock_clone.assert_called_once()
        mock_checkout.assert_called_once_with(mock_repo, "main")
        mock_rmtree.assert_called_once_with("/tmp/test_dir")
    
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch.object(CodeFetcherAgent, '_clone_repository')
    def test_get_pr_diff_no_source_branch(self, mock_clone, mock_exists, mock_rmtree, mock_mkdtemp):
        """Test PR diff retrieval without source branch."""
        mock_mkdtemp.return_value = "/tmp/test_dir"
        mock_exists.return_value = True
        
        with pytest.raises(Exception) as exc_info:
            self.agent.get_pr_diff(
                repo_url="https://github.com/test/repo.git",
                pr_id=123,
                target_branch="main",
                source_branch=None
            )
        
        assert "Source branch must be provided" in str(exc_info.value)
        mock_rmtree.assert_called_once_with("/tmp/test_dir")
    
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch('os.walk')
    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data="print('hello world')")
    @patch.object(CodeFetcherAgent, '_clone_repository')
    @patch.object(CodeFetcherAgent, '_checkout_branch')
    def test_get_project_files_success(self, mock_checkout, mock_clone, mock_open_file, 
                                     mock_getsize, mock_walk, mock_exists, mock_rmtree, mock_mkdtemp):
        """Test successful project files retrieval."""
        # Setup mocks
        mock_mkdtemp.return_value = "/tmp/test_dir"
        mock_exists.return_value = True
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        # Mock file system walk
        mock_walk.return_value = [
            ("/tmp/test_dir", ["src"], ["main.py", "README.md"]),
            ("/tmp/test_dir/src", [], ["utils.py", "config.json"])
        ]
        
        # Mock file size (small files)
        mock_getsize.return_value = 1024
        
        # Test
        result = self.agent.get_project_files(
            repo_url="https://github.com/test/repo.git",
            branch_or_commit="main"
        )
        
        # Assertions
        assert isinstance(result, dict)
        assert "main.py" in result
        assert "src/utils.py" in result
        assert "README.md" not in result  # Not a supported file
        assert "src/config.json" not in result  # Not a supported file
        
        # Check file content
        assert result["main.py"] == "print('hello world')"
        assert result["src/utils.py"] == "print('hello world')"
        
        mock_clone.assert_called_once()
        mock_checkout.assert_called_once_with(mock_repo, "main")
        mock_rmtree.assert_called_once_with("/tmp/test_dir")
    
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    @patch('os.walk')
    @patch('os.path.getsize')
    @patch.object(CodeFetcherAgent, '_clone_repository')
    @patch.object(CodeFetcherAgent, '_checkout_branch')
    def test_get_project_files_large_file_skip(self, mock_checkout, mock_clone, 
                                             mock_getsize, mock_walk, mock_rmtree, mock_mkdtemp):
        """Test skipping large files during project file retrieval."""
        # Setup mocks
        mock_mkdtemp.return_value = "/tmp/test_dir"
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        # Mock file system walk
        mock_walk.return_value = [
            ("/tmp/test_dir", [], ["small.py", "large.py"])
        ]
        
        # Mock file sizes - one small, one large
        def mock_size_func(path):
            if "large.py" in path:
                return 20 * 1024 * 1024  # 20MB - larger than default 10MB limit
            return 1024  # 1KB
        
        mock_getsize.side_effect = mock_size_func
        
        with patch('builtins.open', mock_open(read_data="print('hello')")):
            result = self.agent.get_project_files(
                repo_url="https://github.com/test/repo.git",
                branch_or_commit="main"
            )
        
        # Assertions
        assert "small.py" in result
        assert "large.py" not in result  # Should be skipped due to size
    
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch.object(CodeFetcherAgent, '_clone_repository')
    def test_get_project_files_clone_failure(self, mock_clone, mock_exists, mock_rmtree, mock_mkdtemp):
        """Test project files retrieval with clone failure."""
        mock_mkdtemp.return_value = "/tmp/test_dir"
        mock_exists.return_value = True
        mock_clone.side_effect = GitCommandError("clone", "error")
        
        with pytest.raises(Exception) as exc_info:
            self.agent.get_project_files(
                repo_url="https://github.com/invalid/repo.git",
                branch_or_commit="main"
            )
        
        assert "Failed to fetch project files" in str(exc_info.value)
        mock_rmtree.assert_called_once_with("/tmp/test_dir")
    
    def test_get_changed_files_from_diff(self):
        """Test extracting changed files from diff content."""
        diff_content = """
diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,4 @@
 import os
+import sys
 
 def main():
diff --git a/README.md b/README.md
index 2345678..bcdefgh 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 # Test Project
+This is a test.
diff --git a/src/utils.java b/src/utils.java
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/utils.java
@@ -0,0 +1,5 @@
+public class Utils {
+    // Utility class
+}
        """
        
        changed_files = self.agent.get_changed_files_from_diff(diff_content)
        
        # Should only include supported file types
        assert "src/main.py" in changed_files
        assert "src/utils.java" in changed_files
        assert "README.md" not in changed_files  # Not a supported file type
        
        # Should not have duplicates
        assert len(changed_files) == len(set(changed_files))
    
    def test_get_changed_files_from_diff_empty(self):
        """Test extracting changed files from empty diff."""
        diff_content = ""
        
        changed_files = self.agent.get_changed_files_from_diff(diff_content)
        
        assert changed_files == []
    
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="file content")
    @patch.object(CodeFetcherAgent, '_clone_repository')
    def test_get_file_content_at_commit_success(self, mock_clone, mock_open_file, 
                                              mock_exists, mock_rmtree, mock_mkdtemp):
        """Test successful file content retrieval at specific commit."""
        # Setup mocks
        mock_mkdtemp.return_value = "/tmp/test_dir"
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        mock_exists.return_value = True
        
        # Test
        result = self.agent.get_file_content_at_commit(
            repo_url="https://github.com/test/repo.git",
            file_path="src/main.py",
            commit_hash="abc123"
        )
        
        # Assertions
        assert result == "file content"
        mock_clone.assert_called_once()
        mock_repo.git.checkout.assert_called_once_with("abc123")
        mock_rmtree.assert_called_once_with("/tmp/test_dir")
    
    @patch('tempfile.mkdtemp')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch.object(CodeFetcherAgent, '_clone_repository')
    def test_get_file_content_at_commit_file_not_found(self, mock_clone, mock_exists, 
                                                     mock_rmtree, mock_mkdtemp):
        """Test file content retrieval when file doesn't exist."""
        # Setup mocks
        mock_mkdtemp.return_value = "/tmp/test_dir"
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        
        # Mock exists to return True for temp_dir but False for the specific file
        def mock_exists_func(path):
            if path == "/tmp/test_dir":
                return True
            return False  # File doesn't exist
        mock_exists.side_effect = mock_exists_func
        
        # Test
        result = self.agent.get_file_content_at_commit(
            repo_url="https://github.com/test/repo.git",
            file_path="nonexistent.py",
            commit_hash="abc123"
        )
        
        # Assertions
        assert result is None
        mock_rmtree.assert_called_once_with("/tmp/test_dir")


class TestCodeFetcherAgentIntegration:
    """Integration test scenarios for CodeFetcherAgent."""
    
    @pytest.mark.integration
    def test_agent_initialization_with_settings(self):
        """Test agent initialization with different settings."""
        with patch('src.core_engine.agents.code_fetcher_agent.settings') as mock_settings:
            mock_settings.supported_languages = ['python']
            mock_settings.max_file_size_mb = 5
            
            agent = CodeFetcherAgent()
            
            assert agent.supported_languages == ['python']
            extensions = agent._get_supported_file_extensions()
            assert '.py' in extensions
            assert '.java' not in extensions
    
    @pytest.mark.integration
    def test_error_handling_chain(self):
        """Test error handling across multiple methods."""
        agent = CodeFetcherAgent()
        
        # Test with invalid repository URL
        with pytest.raises(Exception):
            agent.get_project_files("invalid-url", "main")
        
        # Test with invalid diff content
        result = agent.get_changed_files_from_diff("invalid diff content")
        assert result == []


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"]) 