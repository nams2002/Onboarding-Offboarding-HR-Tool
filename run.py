#!/usr/bin/env python3
"""
Launcher script for Rapid Innovation Onboarding Automation System
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import jinja2
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def check_images():
    """Check if required images exist"""
    required_images = [
        "images/Rapid Innovation Header (1).png",
        "images/footer (1) copy (1) copy.png", 
        "images/Aarushi.sign.png"
    ]
    
    missing_images = []
    for img in required_images:
        if not os.path.exists(img):
            missing_images.append(img)
    
    if missing_images:
        print("⚠️  Warning: Missing image files:")
        for img in missing_images:
            print(f"   - {img}")
        print("The application will still work, but documents may not display properly.")
        return False
    else:
        print("✅ All required images found!")
        return True

def main():
    print("🚀 Starting Rapid Innovation Onboarding Automation System...")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies. Please install manually.")
        return
    
    # Check images
    check_images()
    
    # Create images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")
        print("📁 Created images directory")
    
    print("=" * 60)
    print("🌐 Launching Streamlit application...")
    print("📱 The application will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("=" * 60)
    
    # Launch Streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")

if __name__ == "__main__":
    main()
