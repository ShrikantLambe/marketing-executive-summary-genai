"""
config.py

Centralized configuration for metric thresholds, benchmarks, baselines, and prompt tone.
Loads from .env or YAML for enterprise configurability.
"""
import os
from typing import Dict, Any
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Default config values
DEFAULT_CONFIG = {
    "metric_thresholds": {
        "CTR": 2.0,  # %
        "ROAS": 3.0,
        "Conversion Rate": 5.0,
        "CAC": 150.0,
    },
    "strategic_benchmarks": {
        "CTR": 2.5,
        "ROAS": 4.0,
        "Conversion Rate": 7.0,
        "CAC": 120.0,
    },
    "industry_baselines": {
        "CTR": 1.8,
        "ROAS": 2.5,
        "Conversion Rate": 4.0,
        "CAC": 200.0,
    },
    "prompt_tone": os.getenv("PROMPT_TONE", "executive"),  # e.g., 'executive', 'analyst', 'casual'
}

CONFIG_PATH = os.getenv("CONFIG_YAML", "config.yaml")


def load_config() -> Dict[str, Any]:
    """
    Load config from YAML if present, else use defaults and .env overrides.
    """
    config = DEFAULT_CONFIG.copy()
    yaml_path = Path(CONFIG_PATH)
    if yaml_path.exists():
        with open(yaml_path, "r") as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                config.update(yaml_config)
    # Allow .env to override prompt_tone
    config["prompt_tone"] = os.getenv("PROMPT_TONE", config["prompt_tone"])
    return config

# Example usage:
# config = load_config()
# print(config["metric_thresholds"])
