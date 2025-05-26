"""
CodeFetcherAgent for AI Code Review System.

This module implements the CodeFetcherAgent responsible for retrieving code
from Git repositories, including PR diffs and full project files.
"""

import os
import tempfile
import shutil
from typing import Dict, Optional
from pathlib import Path
import logging

import git
from git import Repo, GitCommandError

from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class CodeFetcherAgent:
    """
    Agent responsible for fetching code from Git repositories.
    
    This agent handles:
    - Cloning repositories
    - Fetching PR diffs between branches
    - Retrieving project files for analysis
    - Managing temporary directories for Git operations
    """
    
    def __init__(self):
        """
        Initialize the CodeFetcherAgent.
        
        Sets up configuration and prepares for Git operations.
        """
        self.supported_extensions = {
            'python': ['.py', '.pyx', '.pyi'],
            'java': ['.java'],
            'kotlin': ['.kt', '.kts']
        }
        
        # Get supported languages from settings
        self.supported_languages = getattr(settings, 'supported_languages', ['python', 'java', 'kotlin'])
        
        logger.info(f"CodeFetcherAgent initialized with languages: {self.supported_languages}")
    
    def _get_supported_file_extensions(self) -> list:
        """
        Get list of supported file extensions based on configured languages.
        
        Returns:
            list: List of file extensions to process
        """
        extensions = []
        for lang in self.supported_languages:
            if lang in self.supported_extensions:
                extensions.extend(self.supported_extensions[lang])
        return extensions
    
    def _is_supported_file(self, file_path: str) -> bool:
        """
        Check if a file should be processed based on its extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file should be processed
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self._get_supported_file_extensions()
    
    def _clone_repository(self, repo_url: str, target_dir: str) -> Repo:
        """
        Clone a Git repository to a temporary directory.
        
        Args:
            repo_url (str): URL of the Git repository
            target_dir (str): Directory to clone into
            
        Returns:
            Repo: GitPython Repo object
            
        Raises:
            GitCommandError: If cloning fails
            Exception: For other Git-related errors
        """
        try:
            logger.info(f"Cloning repository {repo_url} to {target_dir}")
            
            # Clone with depth=1 for faster cloning, but fetch all branches
            repo = Repo.clone_from(
                repo_url, 
                target_dir,
                # Don't use depth=1 as we need to access different branches
                multi_options=['--no-single-branch']
            )
            
            logger.info(f"Successfully cloned repository to {target_dir}")
            return repo
            
        except GitCommandError as e:
            logger.error(f"Git command error while cloning {repo_url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while cloning {repo_url}: {str(e)}")
            raise
    
    def _checkout_branch(self, repo: Repo, branch_name: str) -> None:
        """
        Checkout a specific branch in the repository.
        
        Args:
            repo (Repo): GitPython Repo object
            branch_name (str): Name of the branch to checkout
            
        Raises:
            GitCommandError: If checkout fails
        """
        try:
            logger.info(f"Checking out branch: {branch_name}")
            
            # First, try to checkout if it's a local branch
            try:
                repo.git.checkout(branch_name)
            except GitCommandError:
                # If local checkout fails, try to checkout remote branch
                try:
                    repo.git.checkout(f"origin/{branch_name}")
                except GitCommandError:
                    # If that fails, try to create and checkout from remote
                    repo.git.checkout('-b', branch_name, f"origin/{branch_name}")
            
            logger.info(f"Successfully checked out branch: {branch_name}")
            
        except GitCommandError as e:
            logger.error(f"Failed to checkout branch {branch_name}: {str(e)}")
            raise
    
    def get_pr_diff(
        self, 
        repo_url: str, 
        pr_id: int, 
        target_branch: str = "main", 
        source_branch: str = None
    ) -> str:
        """
        Get the diff for a Pull Request between two branches.
        
        Args:
            repo_url (str): URL of the Git repository
            pr_id (int): Pull request ID (for logging/tracking)
            target_branch (str): Target branch (usually main/master)
            source_branch (str): Source branch (PR branch)
            
        Returns:
            str: Git diff content between the branches
            
        Raises:
            Exception: If unable to fetch PR diff
        """
        temp_dir = None
        
        try:
            logger.info(f"Fetching PR #{pr_id} diff from {repo_url}")
            logger.info(f"Target branch: {target_branch}, Source branch: {source_branch}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f"aicode_pr_{pr_id}_")
            
            # Clone repository
            repo = self._clone_repository(repo_url, temp_dir)
            
            # If source_branch is not provided, try to infer from PR
            # For now, we'll require it to be provided
            if not source_branch:
                raise ValueError(f"Source branch must be provided for PR #{pr_id}")
            
            # Fetch all remote branches to ensure we have both branches
            repo.remotes.origin.fetch()
            
            # Checkout target branch first
            self._checkout_branch(repo, target_branch)
            
            # Get diff between target and source branch
            try:
                # Use git diff to compare branches
                diff_output = repo.git.diff(f"origin/{target_branch}...origin/{source_branch}")
                
                if not diff_output:
                    logger.warning(f"No differences found between {target_branch} and {source_branch}")
                    return f"# No differences found between {target_branch} and {source_branch}\n"
                
                logger.info(f"Successfully generated diff for PR #{pr_id}")
                return diff_output
                
            except GitCommandError as e:
                logger.error(f"Failed to generate diff: {str(e)}")
                # Fallback: try different diff approach
                try:
                    diff_output = repo.git.diff(f"{target_branch}..{source_branch}")
                    return diff_output
                except GitCommandError as e2:
                    logger.error(f"Fallback diff also failed: {str(e2)}")
                    raise Exception(f"Unable to generate diff for PR #{pr_id}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_id} diff: {str(e)}")
            raise Exception(f"Failed to fetch PR diff: {str(e)}")
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")
    
    def get_project_files(
        self, 
        repo_url: str, 
        branch_or_commit: str = "main"
    ) -> Dict[str, str]:
        """
        Get all supported project files from a repository.
        
        Args:
            repo_url (str): URL of the Git repository
            branch_or_commit (str): Branch name or commit hash to checkout
            
        Returns:
            Dict[str, str]: Dictionary mapping file paths to their content
            
        Raises:
            Exception: If unable to fetch project files
        """
        temp_dir = None
        
        try:
            logger.info(f"Fetching project files from {repo_url} at {branch_or_commit}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="aicode_project_")
            
            # Clone repository
            repo = self._clone_repository(repo_url, temp_dir)
            
            # Checkout specified branch or commit
            self._checkout_branch(repo, branch_or_commit)
            
            # Collect all supported files
            project_files = {}
            supported_extensions = self._get_supported_file_extensions()
            
            logger.info(f"Scanning for files with extensions: {supported_extensions}")
            
            # Walk through all files in the repository
            for root, dirs, files in os.walk(temp_dir):
                # Skip .git directory and other hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Get relative path from repo root
                    rel_path = os.path.relpath(file_path, temp_dir)
                    
                    # Skip if not a supported file type
                    if not self._is_supported_file(rel_path):
                        continue
                    
                    # Skip files that are too large
                    try:
                        file_size = os.path.getsize(file_path)
                        max_size = getattr(settings, 'max_file_size_mb', 10) * 1024 * 1024
                        
                        if file_size > max_size:
                            logger.warning(f"Skipping large file {rel_path} ({file_size} bytes)")
                            continue
                        
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            project_files[rel_path] = content
                            
                        logger.debug(f"Added file: {rel_path} ({len(content)} characters)")
                        
                    except Exception as e:
                        logger.warning(f"Failed to read file {rel_path}: {str(e)}")
                        continue
            
            logger.info(f"Successfully collected {len(project_files)} project files")
            
            if not project_files:
                logger.warning("No supported files found in the repository")
            
            return project_files
            
        except Exception as e:
            logger.error(f"Error fetching project files: {str(e)}")
            raise Exception(f"Failed to fetch project files: {str(e)}")
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")
    
    def get_changed_files_from_diff(self, diff_content: str) -> list:
        """
        Extract list of changed files from a git diff.
        
        Args:
            diff_content (str): Git diff content
            
        Returns:
            list: List of file paths that were changed
        """
        changed_files = []
        
        try:
            lines = diff_content.split('\n')
            
            for line in lines:
                # Look for diff headers that indicate file changes
                if line.startswith('diff --git'):
                    # Extract file path from "diff --git a/path b/path"
                    parts = line.split()
                    if len(parts) >= 4:
                        file_path = parts[3][2:]  # Remove "b/" prefix
                        if self._is_supported_file(file_path):
                            changed_files.append(file_path)
                            
        except Exception as e:
            logger.warning(f"Failed to parse changed files from diff: {str(e)}")
        
        return list(set(changed_files))  # Remove duplicates
    
    def get_file_content_at_commit(
        self, 
        repo_url: str, 
        file_path: str, 
        commit_hash: str
    ) -> Optional[str]:
        """
        Get content of a specific file at a specific commit.
        
        Args:
            repo_url (str): URL of the Git repository
            file_path (str): Path to the file
            commit_hash (str): Commit hash or branch name
            
        Returns:
            Optional[str]: File content or None if not found
        """
        temp_dir = None
        
        try:
            logger.info(f"Fetching {file_path} at commit {commit_hash}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="aicode_file_")
            
            # Clone repository
            repo = self._clone_repository(repo_url, temp_dir)
            
            # Checkout specific commit
            repo.git.checkout(commit_hash)
            
            # Read file content
            full_path = os.path.join(temp_dir, file_path)
            
            if not os.path.exists(full_path):
                logger.warning(f"File {file_path} not found at commit {commit_hash}")
                return None
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            logger.info(f"Successfully retrieved {file_path} ({len(content)} characters)")
            return content
            
        except Exception as e:
            logger.error(f"Error fetching file {file_path} at commit {commit_hash}: {str(e)}")
            return None
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create agent instance
    agent = CodeFetcherAgent()
    
    # Example: Test with a public repository
    test_repo_url = "https://github.com/octocat/Hello-World.git"
    
    try:
        # Test getting project files
        print("Testing get_project_files...")
        files = agent.get_project_files(test_repo_url, "master")
        print(f"Found {len(files)} files")
        
        for file_path, content in files.items():
            print(f"- {file_path}: {len(content)} characters")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
    
    print("CodeFetcherAgent testing completed!") 