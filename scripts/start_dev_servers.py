#!/usr/bin/env python3
"""
Development server startup script for AI Code Reviewer.

This script starts both backend (FastAPI) and frontend (Vite) development servers
in parallel and provides monitoring and management capabilities.
"""

import subprocess
import time
import os
import signal
import sys
import threading
from pathlib import Path


class DevServerManager:
    """Manages development servers for backend and frontend."""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent.parent
        
    def start_backend(self):
        """Start FastAPI backend server."""
        print("🚀 Starting backend server...")
        try:
            self.backend_process = subprocess.Popen(
                [
                    "python", "-m", "uvicorn", 
                    "src.webapp.backend.api.main:app", 
                    "--reload", "--port", "8000"
                ],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor backend startup
            def monitor_backend():
                for line in iter(self.backend_process.stdout.readline, ''):
                    if line.strip():
                        print(f"[Backend] {line.strip()}")
                        if "Uvicorn running on" in line:
                            print("✅ Backend server started successfully!")
            
            backend_thread = threading.Thread(target=monitor_backend, daemon=True)
            backend_thread.start()
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
        
        return True
    
    def start_frontend(self):
        """Start Vite frontend development server."""
        print("🚀 Starting frontend server...")
        frontend_dir = self.project_root / "src" / "webapp" / "frontend"
        
        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor frontend startup
            def monitor_frontend():
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if line.strip():
                        print(f"[Frontend] {line.strip()}")
                        if "Local:" in line and "http://localhost:5173" in line:
                            print("✅ Frontend server started successfully!")
            
            frontend_thread = threading.Thread(target=monitor_frontend, daemon=True)
            frontend_thread.start()
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
        
        return True
    
    def check_dependencies(self):
        """Check if required dependencies are available."""
        print("🔍 Checking dependencies...")
        
        # Check Python and uvicorn
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except:
            print("❌ Python not found")
            return False
        
        # Check Node.js and npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            print(f"✅ npm: v{result.stdout.strip()}")
        except:
            print("❌ npm not found")
            return False
        
        # Check if frontend dependencies are installed
        frontend_dir = self.project_root / "src" / "webapp" / "frontend"
        if not (frontend_dir / "node_modules").exists():
            print("⚠️  Frontend dependencies not installed. Running npm install...")
            try:
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
                print("✅ Frontend dependencies installed")
            except:
                print("❌ Failed to install frontend dependencies")
                return False
        else:
            print("✅ Frontend dependencies found")
        
        return True
    
    def wait_for_servers(self):
        """Wait for both servers to be ready."""
        print("\n⏳ Waiting for servers to start...")
        
        # Wait for backend
        for i in range(30):
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("⚠️  Backend not responding after 30 seconds")
        
        # Wait for frontend
        for i in range(30):
            try:
                import requests
                response = requests.get("http://localhost:5173/", timeout=1)
                if response.status_code == 200:
                    print("✅ Frontend is ready!")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("⚠️  Frontend not responding after 30 seconds")
    
    def show_access_info(self):
        """Show access information for the user."""
        print("\n🎉 Development servers are running!")
        print("=" * 50)
        print("🌐 Access Points:")
        print("   Frontend:  http://localhost:5173")
        print("   Backend:   http://localhost:8000") 
        print("   API Docs:  http://localhost:8000/docs")
        print("   ReDoc:     http://localhost:8000/redoc")
        print("\n📚 Commands:")
        print("   Test Setup: python scripts/test_full_setup.py")
        print("   Stop:       Press Ctrl+C")
        print("=" * 50)
    
    def cleanup(self):
        """Clean up server processes."""
        print("\n🛑 Shutting down servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("✅ Backend server stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("🔸 Backend server force killed")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend server stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("🔸 Frontend server force killed")
    
    def start_all(self):
        """Start all development servers."""
        print("🚀 AI Code Reviewer Development Server Startup")
        print("=" * 50)
        
        if not self.check_dependencies():
            print("❌ Dependency check failed. Please install required dependencies.")
            return 1
        
        # Start servers
        if not self.start_backend():
            print("❌ Failed to start backend server")
            return 1
        
        time.sleep(2)  # Give backend time to start
        
        if not self.start_frontend():
            print("❌ Failed to start frontend server")
            self.cleanup()
            return 1
        
        # Wait for servers to be ready
        self.wait_for_servers()
        
        # Show access information
        self.show_access_info()
        
        # Wait for interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()
            print("\n👋 Servers stopped. Goodbye!")
            return 0


def main():
    """Main entry point."""
    manager = DevServerManager()
    
    def signal_handler(sig, frame):
        """Handle interrupt signals."""
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return manager.start_all()


if __name__ == "__main__":
    sys.exit(main()) 