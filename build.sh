#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Initialize the database
echo "Initializing database..."
python init_db.py

echo "Build completed successfully!" 