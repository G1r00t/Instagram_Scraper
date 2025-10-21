#!/bin/bash

# Instagram Scraper Automation Script
# This script handles the complete workflow: install dependencies, run scraper, then download media

set -e  # Exit on any error

echo "=========================================="
echo "Instagram Scraper Automation Script"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✓ Python 3 and pip3 are available"

# Install requirements
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if users.txt exists
if [ ! -f "users.txt" ]; then
    echo "❌ users.txt file not found. Please create it with the target username."
    exit 1
fi

echo ""
echo "📋 Target username: $(cat users.txt)"

# Run the main scraper
echo ""
echo "🚀 Starting Instagram scraper..."
echo "This will take some time depending on the number of posts..."
echo ""

python3 main.py

# Check if captured_requests.json was created
if [ ! -f "captured_requests.json" ]; then
    echo "❌ captured_requests.json was not created. Scraping may have failed."
    exit 1
fi

echo ""
echo "✓ Scraping completed successfully!"
echo "📄 captured_requests.json created"

# Run the download script
echo ""
echo "📥 Starting media download..."
echo ""

python3 download.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ ALL TASKS COMPLETED SUCCESSFULLY!"
    echo "=========================================="
    echo "📊 Results:"
    echo "  - Scraped data: captured_requests.json"
    echo "  - Media info JSONs: instagram_media_ohneis652_jsons/"
    echo "  - Media files: instagram_media_ohneis652/"
    echo "  - Log file: scraper_log.txt"
    echo "=========================================="
else
    echo "❌ Download script failed"
    exit 1
fi
