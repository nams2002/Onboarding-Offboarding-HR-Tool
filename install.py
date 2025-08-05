#!/usr/bin/env python3
"""
Installation script for Rapid Innovation Onboarding Automation System
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["images"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists(".env"):
        print("✅ .env file found!")
        return True
    else:
        print("⚠️  .env file not found. Creating template...")
        create_env_template()
        return False

def create_env_template():
    """Create a template .env file"""
    template = """# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
DEFAULT_SENDER_EMAIL=your_email@gmail.com
DEFAULT_SENDER_NAME=Your Company HR
"""
    
    with open(".env.template", "w") as f:
        f.write(template)
    
    print("📝 Created .env.template file")
    print("📋 Please copy .env.template to .env and update with your email credentials")

def main():
    print("🚀 Rapid Innovation Onboarding Automation System - Installation")
    print("=" * 70)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Installation failed. Please check the error messages above.")
        return
    
    # Create directories
    create_directories()
    
    # Check environment file
    check_env_file()
    
    print("=" * 70)
    print("✅ Installation completed!")
    print("\n📋 Next steps:")
    print("1. Configure your .env file with email credentials")
    print("2. Add company images to the images/ folder:")
    print("   - Rapid Innovation Header (1).png")
    print("   - footer (1) copy (1) copy.png")
    print("   - Aarushi.sign.png")
    print("3. Run the application: python run.py")
    print("\n🎯 Ready to streamline your onboarding process!")

if __name__ == "__main__":
    main()
