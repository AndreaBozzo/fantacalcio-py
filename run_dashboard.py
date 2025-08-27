#!/usr/bin/env python3
"""
Script to run the Fantacalcio Dashboard
Usage: poetry run python run_dashboard.py
"""
import os
import sys
from loguru import logger

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from dashboard.app import app

if __name__ == "__main__":
    logger.info("🚀 Starting Fantacalcio Dashboard...")
    logger.info("📊 Dashboard will be available at: http://127.0.0.1:8050")
    logger.info("💡 Make sure you have run the main analysis first to generate data files")
    
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050
    )