"""Configuration management for Chorus."""

import os
from typing import Any, Dict

import click
import yaml

DEFAULT_CONFIG = {
    "backing_directory": os.path.expanduser("~/.chorus"),
    "agents": [],
}


def get_config_path() -> str:
    """Get the path to the configuration file."""
    return os.path.expanduser("~/.config/chorus.yaml")


def load_config() -> Dict[str, Any]:
    """Load configuration from file, merging with defaults."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        click.echo(f"Error loading config file: {e}")
        config = {}
    
    # Merge with defaults
    return {**DEFAULT_CONFIG, **(config or {})}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    
    # Ensure config directory exists
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    with open(config_path, "w") as f:
        yaml.dump(config, f)


def get_chorus_directory(config: Dict[str, Any]) -> str:
    """Get the chorus backing directory path."""
    return os.path.expanduser(config["backing_directory"])


def add_agent(agent_name: str) -> bool:
    """Add an agent to the configuration. Returns True if added, False if already exists."""
    config = load_config()
    
    if "agents" not in config or not config["agents"]:
        config["agents"] = []
    
    if agent_name in config["agents"]:
        return False
    
    config["agents"].append(agent_name)
    save_config(config)
    return True