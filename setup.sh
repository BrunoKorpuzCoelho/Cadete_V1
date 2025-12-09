#!/bin/bash

# Cadete Application Setup Script
# ================================
# This script automates the initial setup process

set -e  # Exit on error

echo "=========================================="
echo "  Cadete Application Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Check if .env exists
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env

    # Generate SECRET_KEY
    echo "Generating SECRET_KEY..."
    secret_key=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    # Update .env with new SECRET_KEY (works on both Linux and macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$secret_key/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$secret_key/" .env
    fi

    echo "✓ .env file created with unique SECRET_KEY"
else
    echo "✓ .env file already exists"
fi

# Create instance directory if it doesn't exist
echo ""
if [ ! -d "instance" ]; then
    echo "Creating instance directory..."
    mkdir -p instance
    echo "✓ Instance directory created"
else
    echo "✓ Instance directory exists"
fi

# Check if database exists
echo ""
if [ ! -f "instance/test.db" ]; then
    echo "Database not found. It will be created on first run."
else
    echo "✓ Database file exists"

    # Ask about password migration
    echo ""
    echo "=========================================="
    echo "  Password Migration"
    echo "=========================================="
    echo ""
    echo "If you have existing users with plaintext passwords,"
    echo "you should run the password migration script."
    echo ""
    read -p "Do you want to migrate passwords now? (y/n): " migrate_choice

    if [[ $migrate_choice =~ ^[Yy]$ ]]; then
        echo ""
        echo "Starting password migration..."
        python3 migrate_passwords.py
    else
        echo "Skipping password migration."
        echo "You can run it later with: python migrate_passwords.py"
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Review your .env configuration:"
echo "   nano .env"
echo ""
echo "2. Start the application:"
echo ""
echo "   Development mode:"
echo "   - Update .env: FLASK_DEBUG=True"
echo "   - Run: python app.py"
echo ""
echo "   Production mode (recommended):"
echo "   - Ensure .env has: FLASK_DEBUG=False"
echo "   - Run: gunicorn -c gunicorn_config.py wsgi:app"
echo ""
echo "3. Default login credentials:"
echo "   Admin: username='cubix', password='cubix'"
echo "   User:  username='cadete', password='cadete'"
echo ""
echo "   ⚠️  CHANGE THESE PASSWORDS IMMEDIATELY!"
echo ""
echo "4. For production deployment, see:"
echo "   - SECURITY.md"
echo "   - DEPLOYMENT.md"
echo ""
echo "=========================================="
echo ""
