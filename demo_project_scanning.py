#!/usr/bin/env python3
"""
Demo script for ProjectScanningAgent functionality.

This script demonstrates the complete project scanning workflow including:
- Project-level analysis with hierarchical summarization
- Integration with LLM and RAG components
- Risk assessment and architectural analysis
- Report generation with recommendations

Usage:
    python demo_project_scanning.py
"""

import logging
import sys
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_project() -> Dict[str, str]:
    """
    Create a sample Python project for demonstration.
    
    Returns:
        Dict[str, str]: Sample project files
    """
    return {
        "main.py": '''
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime

# Security issue: Hardcoded credentials
API_KEY = "hardcoded-api-key-123"
DATABASE_URL = "postgresql://admin:password@localhost/db"

def main():
    """Main application entry point."""
    logger = setup_logging()
    
    try:
        # Security issue: SQL injection vulnerability
        user_input = input("Enter user ID: ")
        users = get_users_by_id(user_input)
        
        for user in users:
            process_user_data(user)
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

def setup_logging():
    """Setup application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def get_users_by_id(user_id: str) -> List[Dict]:
    """Get users from database - vulnerable to SQL injection."""
    import sqlite3
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Security issue: Direct string interpolation in SQL
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"id": row[0], "name": row[1], "email": row[2]} for row in results]

def process_user_data(user_data: Dict) -> None:
    """Process individual user data."""
    # Code quality issue: Long function that should be split
    user_id = user_data.get("id")
    user_name = user_data.get("name")
    user_email = user_data.get("email")
    
    # Validate user data
    if not user_id:
        raise ValueError("User ID is required")
    if not user_name or len(user_name.strip()) == 0:
        raise ValueError("User name is required")
    if not user_email or "@" not in user_email:
        raise ValueError("Valid email is required")
    
    # Process user preferences
    preferences = get_user_preferences(user_id)
    updated_preferences = update_user_preferences(user_id, preferences)
    
    # Send notifications
    if preferences.get("email_notifications", False):
        send_email_notification(user_email, "Profile updated")
    
    # Log activity
    log_user_activity(user_id, "profile_update", datetime.now())
    
    # Update user metrics
    update_user_metrics(user_id, updated_preferences)
    
    print(f"Processed user: {user_name}")

if __name__ == "__main__":
    main()
''',

        "utils/database.py": '''
import sqlite3
import os
import subprocess
from typing import Any, List, Dict, Optional

class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Execute database query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
        finally:
            conn.close()
    
    def backup_database(self, backup_path: str) -> bool:
        """Backup database using system command."""
        # Security issue: Command injection vulnerability
        command = f"cp {self.db_path} {backup_path}"
        result = subprocess.run(command, shell=True, capture_output=True)
        return result.returncode == 0
    
    def read_config_file(self, filename: str) -> str:
        """Read configuration file."""
        # Security issue: Path traversal vulnerability
        with open(filename, 'r') as f:
            return f.read()

def get_user_preferences(user_id: str) -> Dict:
    """Get user preferences from database."""
    db = DatabaseManager("users.db")
    
    # Potential issue: No input validation
    query = "SELECT preferences FROM user_preferences WHERE user_id = ?"
    results = db.execute_query(query, (user_id,))
    
    if results:
        return eval(results[0]["preferences"])  # Security issue: eval() usage
    return {}

def update_user_preferences(user_id: str, preferences: Dict) -> Dict:
    """Update user preferences in database."""
    # Code quality issue: Function too long, no error handling
    db = DatabaseManager("users.db")
    
    # Validate preferences
    if not isinstance(preferences, dict):
        preferences = {}
    
    # Add default preferences
    default_prefs = {
        "theme": "light",
        "notifications": True,
        "email_notifications": False,
        "language": "en"
    }
    
    for key, value in default_prefs.items():
        if key not in preferences:
            preferences[key] = value
    
    # Update in database
    query = "UPDATE user_preferences SET preferences = ? WHERE user_id = ?"
    db.execute_query(query, (str(preferences), user_id))
    
    return preferences
''',

        "utils/notifications.py": '''
import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

# Security issue: Hardcoded credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "admin@company.com"
EMAIL_PASSWORD = "hardcoded-password-123"

def send_email_notification(to_email: str, message: str) -> bool:
    """Send email notification."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = "Notification"
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_slack_notification(webhook_url: str, message: str) -> bool:
    """Send Slack notification."""
    try:
        payload = {"text": message}
        
        # Security issue: No SSL verification
        response = requests.post(webhook_url, json=payload, verify=False)
        
        if response.status_code == 200:
            logger.info("Slack notification sent successfully")
            return True
        else:
            logger.error(f"Slack notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {str(e)}")
        return False

class NotificationManager:
    """Manage different types of notifications."""
    
    def __init__(self):
        self.email_enabled = True
        self.slack_enabled = True
        
    def send_notification(self, notification_type: str, recipient: str, message: str) -> bool:
        """Send notification based on type."""
        # Code quality issue: No input validation, too many responsibilities
        if notification_type == "email":
            return send_email_notification(recipient, message)
        elif notification_type == "slack":
            return send_slack_notification(recipient, message)
        else:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False
''',

        "config/settings.py": '''
import os
from typing import Dict, Any

# Security issues: Multiple hardcoded secrets and poor practices
class Config:
    """Application configuration."""
    
    # Database configuration
    DATABASE_URL = "postgresql://admin:password123@localhost:5432/myapp"
    DATABASE_POOL_SIZE = 10
    DATABASE_TIMEOUT = 30
    
    # API Keys (should be in environment variables)
    OPENAI_API_KEY = "sk-abcd1234567890abcd1234567890"
    STRIPE_SECRET_KEY = "sk_test_1234567890abcdef"
    AWS_ACCESS_KEY_ID = "AKIAI234567890ABCDEF"
    AWS_SECRET_ACCESS_KEY = "abcd1234567890abcd1234567890abcd12345678"
    
    # Security settings
    SECRET_KEY = "super-secret-key-123"  # Should be random and from env
    DEBUG = True  # Should be False in production
    ALLOWED_HOSTS = ["*"]  # Too permissive
    
    # Feature flags
    ENABLE_LOGGING = True
    ENABLE_METRICS = True
    ENABLE_CACHE = True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL."""
        return cls.DATABASE_URL
    
    @classmethod
    def get_api_keys(cls) -> Dict[str, str]:
        """Get API keys."""
        return {
            "openai": cls.OPENAI_API_KEY,
            "stripe": cls.STRIPE_SECRET_KEY,
            "aws_access": cls.AWS_ACCESS_KEY_ID,
            "aws_secret": cls.AWS_SECRET_ACCESS_KEY
        }

# Performance issue: Loading config on import
config = Config()
''',

        "tests/test_main.py": '''
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import process_user_data, get_users_by_id

class TestMain(unittest.TestCase):
    """Test cases for main module."""
    
    def test_process_user_data_valid(self):
        """Test processing valid user data."""
        user_data = {
            "id": "123",
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        # This test doesn't properly mock dependencies
        with patch('main.get_user_preferences') as mock_prefs:
            mock_prefs.return_value = {"notifications": True}
            
            # This will fail because other functions aren't mocked
            try:
                process_user_data(user_data)
            except Exception:
                pass  # Expected to fail due to missing mocks
    
    def test_get_users_by_id(self):
        """Test getting users by ID."""
        # Code quality issue: No proper database mocking
        try:
            result = get_users_by_id("1")
            self.assertIsInstance(result, list)
        except Exception:
            pass  # Expected to fail without proper database setup

if __name__ == "__main__":
    unittest.main()
''',

        "requirements.txt": '''
requests==2.28.1
sqlite3
smtplib
logging
datetime
typing
''',

        "README.md": '''
# Sample Python Application

This is a sample Python application for demonstrating code analysis capabilities.

## Features
- User management
- Database operations
- Email notifications
- Configuration management

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python main.py`

## Known Issues
This application contains several intentional security vulnerabilities and code quality issues for demonstration purposes:
- SQL injection vulnerabilities
- Hardcoded credentials
- Command injection risks
- Path traversal vulnerabilities
- Poor error handling
- Code quality issues

**Do not use this code in production!**
'''
    }

def create_sample_static_findings() -> List[Dict[str, Any]]:
    """
    Create sample static analysis findings.
    
    Returns:
        List[Dict[str, Any]]: Sample findings
    """
    return [
        {
            "rule_id": "HARDCODED_CREDENTIALS",
            "severity": "High",
            "category": "Security",
            "message": "Hardcoded API key detected",
            "file_path": "main.py",
            "line_number": 9,
            "code_snippet": 'API_KEY = "hardcoded-api-key-123"'
        },
        {
            "rule_id": "SQL_INJECTION",
            "severity": "High", 
            "category": "Security",
            "message": "Potential SQL injection vulnerability",
            "file_path": "main.py",
            "line_number": 40,
            "code_snippet": 'query = f"SELECT * FROM users WHERE id = \'{user_id}\'"'
        },
        {
            "rule_id": "COMMAND_INJECTION",
            "severity": "High",
            "category": "Security", 
            "message": "Command injection vulnerability in subprocess call",
            "file_path": "utils/database.py",
            "line_number": 34,
            "code_snippet": "subprocess.run(command, shell=True, capture_output=True)"
        },
        {
            "rule_id": "PATH_TRAVERSAL",
            "severity": "Medium",
            "category": "Security",
            "message": "Potential path traversal vulnerability",
            "file_path": "utils/database.py", 
            "line_number": 39,
            "code_snippet": "with open(filename, 'r') as f:"
        },
        {
            "rule_id": "EVAL_USAGE",
            "severity": "High",
            "category": "Security",
            "message": "Use of eval() poses security risk",
            "file_path": "utils/database.py",
            "line_number": 49,
            "code_snippet": "return eval(results[0][\"preferences\"])"
        },
        {
            "rule_id": "FUNCTION_TOO_LONG",
            "severity": "Medium",
            "category": "Code Quality",
            "message": "Function is too long and should be split",
            "file_path": "main.py",
            "line_number": 46,
            "code_snippet": "def process_user_data(user_data: Dict) -> None:"
        }
    ]

def run_demo():
    """Run the ProjectScanningAgent demo."""
    logger.info("=== ProjectScanningAgent Demo ===")
    
    try:
        # Import ProjectScanningAgent
        from src.core_engine.agents.project_scanning_agent import ProjectScanningAgent
        
        # Create sample project and findings
        logger.info("Creating sample project with security vulnerabilities...")
        project_code = create_sample_project()
        static_findings = create_sample_static_findings()
        
        logger.info(f"Sample project contains {len(project_code)} files")
        logger.info(f"Sample static findings: {len(static_findings)} issues")
        
        # Initialize ProjectScanningAgent
        logger.info("Initializing ProjectScanningAgent...")
        scanner = ProjectScanningAgent()
        
        # Run project scan
        logger.info("Running comprehensive project scan...")
        scan_result = scanner.scan_entire_project(
            project_code=project_code,
            static_findings=static_findings
        )
        
        # Display results
        logger.info("=== SCAN RESULTS ===")
        logger.info(f"Scan Type: {scan_result.get('scan_type', 'unknown')}")
        
        # Complexity metrics
        complexity = scan_result.get('complexity_metrics', {})
        logger.info(f"Total Files: {complexity.get('total_files', 0)}")
        logger.info(f"Total Lines: {complexity.get('total_lines', 0)}")
        logger.info(f"Languages: {list(complexity.get('languages', {}).keys())}")
        
        # Risk assessment
        risk_assessment = scan_result.get('risk_assessment', {})
        logger.info(f"Overall Risk Level: {risk_assessment.get('overall_risk_level', 'unknown')}")
        
        # Recommendations
        recommendations = scan_result.get('recommendations', [])
        logger.info(f"Recommendations Generated: {len(recommendations)}")
        
        if recommendations:
            logger.info("Top 3 Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                logger.info(f"  {i}. {rec.get('title', 'N/A')}")
        
        # Architectural analysis (truncated)
        arch_analysis = scan_result.get('architectural_analysis', '')
        if arch_analysis:
            preview = arch_analysis[:200] + "..." if len(arch_analysis) > 200 else arch_analysis
            logger.info(f"Architectural Analysis Preview: {preview}")
        
        logger.info("=== Demo completed successfully! ===")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import ProjectScanningAgent: {str(e)}")
        logger.error("Make sure you're running from the project root directory")
        return False
    except Exception as e:
        logger.error(f"Demo failed with error: {str(e)}")
        logger.error("Check the logs above for more details")
        return False

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1) 