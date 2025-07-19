#!/usr/bin/env python3
"""
Equity Research Assistant Setup Script
Run this script to set up the application locally
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required Python packages"""
    packages = [
        'beautifulsoup4',
        'email-validator', 
        'flask',
        'flask-sqlalchemy',
        'gunicorn',
        'jinja2',
        'openai',
        'openpyxl',
        'pandas',
        'psycopg2-binary',
        'pymupdf',
        'python-docx',
        'sqlalchemy',
        'weasyprint',
        'werkzeug'
    ]
    
    print("Installing Python dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    
    print("✓ All dependencies installed successfully!")
    return True

def create_directories():
    """Create required directories"""
    directories = ['uploads', 'downloads', 'instance']
    
    print("Creating required directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created {directory}/ directory")

def create_env_template():
    """Create environment template file"""
    env_content = """# Equity Research Assistant Environment Variables
# Copy this file to .env and fill in your actual values

# Required: OpenAI API key for AI analysis features
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Required: Flask session security key
# Generate a random secret key for production use
SESSION_SECRET=your_random_secret_key_here

# Optional: PostgreSQL database URL
# If not provided, SQLite will be used (recommended for development)
# DATABASE_URL=postgresql://username:password@localhost/database_name
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env.template file")
    print("  Please copy this to .env and add your actual API keys")

def initialize_database():
    """Initialize the database"""
    print("Initializing database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✓ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("Equity Research Assistant Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("✗ Python 3.11 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if not install_dependencies():
        print("Setup failed during dependency installation")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create environment template
    create_env_template()
    
    # Initialize database
    if not initialize_database():
        print("Setup failed during database initialization")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Copy .env.template to .env")
    print("2. Add your OpenAI API key to .env")
    print("3. Run: python main.py")
    print("4. Open http://localhost:5000 in your browser")
    print("\nFor production deployment, use:")
    print("gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app")

if __name__ == "__main__":
    main()