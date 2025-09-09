"""
Configuration module for Header Extractor.

This module provides access to the configuration system. The configuration is loaded from:
1. Package's config.json (default values)
2. User's ~/.config/header_extractor/config.json (user overrides)

Usage:
    from header_extractor.config import get_config, update_config

    # Get current config
    config = get_config()

    # Update config
    update_config({"default_timeout": 15})
"""
from .config import get_config, save_config, update_config

# Expose the current config as CONFIG for backward compatibility
CONFIG = get_config()

__all__ = [
    'CONFIG',
    'get_config',
    'save_config',
    'update_config'
]
