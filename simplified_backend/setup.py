#!/usr/bin/env python3
"""
DevMind Simplified Backend Setup Script
Automates the setup process for hackathon demo
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, check=True):
    """Run a command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error output: {result.stderr}")
        return False
    return True

def main():
    print("🚀 Setting up DevMind Simplified Backend for Hackathon")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install dependencies")
        return False
    
    print("✅ Dependencies installed successfully")
    
    # Check if anthropic is properly installed
    try:
        import anthropic
        print("✅ Anthropic library is available")
    except ImportError:
        print("❌ Anthropic library not found, installing...")
        if not run_command("pip install anthropic"):
            return False
    
    # Verify FastAPI installation
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are available")
    except ImportError:
        print("❌ FastAPI or Uvicorn not found")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Set your Anthropic API key in the frontend")
    print("2. Run the backend: python main.py")
    print("3. Open simplified_frontend/index.html in your browser")
    print("\nThe backend will be available at: http://localhost:8000")
    print("API docs will be at: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
