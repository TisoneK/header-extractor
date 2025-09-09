"""
Configuration management for Header Extractor.
"""
import json
from pathlib import Path

# Paths
PACKAGE_DIR = Path(__file__).parent
CONFIG_JSON = PACKAGE_DIR / "config.json"
USER_CONFIG_DIR = Path.home() / ".config" / "header_extractor"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"

# Load default config from package
try:
    with open(CONFIG_JSON, 'r') as f:
        CONFIG = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Fallback to default config if config.json is missing or invalid
    CONFIG = {
        "default_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
        "comprehensive_headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        },
        "default_timeout": 10,
        "output_dir": "output",
        "auto_create_output_dir": True
    }

# Load user config if exists
if USER_CONFIG_FILE.exists():
    try:
        with open(USER_CONFIG_FILE, 'r') as f:
            CONFIG.update(json.load(f))
    except json.JSONDecodeError:
        pass  # Keep using default config if user config is invalid

def get_config():
    """Get current configuration."""
    return CONFIG

def save_config():
    """Save current configuration to user config file."""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(USER_CONFIG_FILE, 'w') as f:
        json.dump(CONFIG, f, indent=2)

def update_config(updates):
    """Update configuration with new values and save."""
    CONFIG.update(updates)
    save_config()
    return CONFIG
