"""
UnitAPI Logging Module

This module provides logging configuration and management functionality.
"""

import os
import logging
from typing import Dict, Any, Optional

class LoggingManager:
    """Manages logging configuration for UnitAPI."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the logging manager.
        
        Args:
            config: The configuration dictionary
        """
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging based on the configuration."""
        # Get logging configuration from config
        log_config = self.config.get("logging", {})
        log_level = log_config.get("level", "INFO").upper()
        log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_file = log_config.get("file")
        
        # Set up root logger
        root_logger = logging.getLogger()
        
        # Set log level
        level = getattr(logging, log_level, logging.INFO)
        root_logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Set up console handler
        if not root_logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Set up file handler if specified
        if log_file:
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Create unitapi logger
        self.logger = logging.getLogger("unitapi")
        self.logger.debug("Logging initialized")
