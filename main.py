#!/usr/bin/env python3
"""
Text Image Comparison Tool
A comprehensive Windows application that compares text extracted from images
with provided text to detect all types of changes with 100% accuracy.

Author: Abhishek Kumar Rawat
Version: 1.0.0
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import TextComparisonApp
from utils import constants


def setup_logging():
    """Setup application logging"""
    log_dir = os.path.dirname(constants.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, constants.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(constants.LOG_FILE),
            logging.StreamHandler() if constants.ENABLE_CONSOLE_LOGGING else logging.NullHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"Starting {constants.APP_NAME} v{constants.APP_VERSION}")
    logger.info("=" * 80)
    
    return logger


def main():
    """Main application entry point"""
    logger = setup_logging()
    
    try:
        # Import here to ensure logging is setup first
        from PyQt6.QtWidgets import QApplication
        
        logger.info("Initializing PyQt6 application...")
        app = QApplication(sys.argv)
        
        logger.info("Creating main window...")
        window = TextComparisonApp()
        window.show()
        
        logger.info("Application started successfully")
        sys.exit(app.exec())
    
    except ImportError as e:
        logger.critical(f"Missing required dependencies: {str(e)}")
        logger.critical("Please install required packages: pip install -r requirements.txt")
        print(f"Error: Missing required dependencies: {str(e)}")
        print("Please install required packages: pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        logger.critical(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
