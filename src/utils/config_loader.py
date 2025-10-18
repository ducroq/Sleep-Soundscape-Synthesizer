"""
Configuration Loader
Centralized configuration loading for Sleep Soundscape Synthesizer.
Handles loading from config/ directory and provides validation.
"""

import os
import yaml
import configparser
from pathlib import Path
from typing import Dict, Any, Optional


def get_project_root() -> Path:
    """Get the project root directory (parent of src/)."""
    return Path(__file__).parent.parent.parent


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Optional path to config file. If None, uses config/config.yaml

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    if config_path is None:
        config_path = get_project_root() / "config" / "config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required sections
    required_sections = ['voices', 'language', 'prosody_distributions', 'paths']
    missing = [s for s in required_sections if s not in config]
    if missing:
        raise ValueError(f"Config missing required sections: {missing}")

    return config


def load_secrets(secrets_path: Optional[str] = None) -> configparser.ConfigParser:
    """
    Load secrets from INI file.

    Args:
        secrets_path: Optional path to secrets file. If None, uses config/secrets.ini

    Returns:
        ConfigParser object with secrets

    Raises:
        FileNotFoundError: If secrets file doesn't exist
    """
    if secrets_path is None:
        secrets_path = get_project_root() / "config" / "secrets.ini"
    else:
        secrets_path = Path(secrets_path)

    if not secrets_path.exists():
        raise FileNotFoundError(
            f"Secrets file not found: {secrets_path}\n"
            f"Create it from config/secrets.ini.example"
        )

    secrets = configparser.ConfigParser()
    secrets.read(secrets_path)

    # Validate ElevenLabs API key exists
    if not secrets.has_section('elevenlabs'):
        raise ValueError("secrets.ini missing [elevenlabs] section")
    if not secrets.has_option('elevenlabs', 'api_key'):
        raise ValueError("secrets.ini missing api_key in [elevenlabs] section")

    return secrets


def get_elevenlabs_api_key(secrets: Optional[configparser.ConfigParser] = None) -> str:
    """
    Get ElevenLabs API key from secrets.

    Args:
        secrets: Optional ConfigParser. If None, loads from config/secrets.ini

    Returns:
        API key string
    """
    if secrets is None:
        secrets = load_secrets()

    return secrets.get('elevenlabs', 'api_key')


def resolve_output_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    """
    Resolve all output paths relative to project root.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary mapping path names to absolute Path objects
    """
    root = get_project_root()
    paths_config = config.get('paths', {})

    resolved = {}
    for key, value in paths_config.items():
        resolved[key] = root / value

    return resolved


def ensure_output_dirs(config: Dict[str, Any]):
    """
    Create output directories if they don't exist.

    Args:
        config: Configuration dictionary
    """
    paths = resolve_output_paths(config)

    # Create directories for directory paths
    dirs_to_create = [
        paths.get('output_dir'),
        paths.get('clips_dir'),
    ]

    for dir_path in dirs_to_create:
        if dir_path:
            dir_path.mkdir(parents=True, exist_ok=True)

    # Create parent directories for file paths
    file_paths = [
        paths.get('merged_file'),
        paths.get('spatialized_file'),
    ]

    for file_path in file_paths:
        if file_path:
            file_path.parent.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Test configuration loading
    print("Testing configuration loader...")

    try:
        config = load_config()
        print(f"✓ Config loaded successfully")
        print(f"  Voices: {len(config.get('voices', []))}")
        print(f"  Language softness: {config.get('language', {}).get('softness')}")

        paths = resolve_output_paths(config)
        print(f"✓ Paths resolved:")
        for key, path in paths.items():
            print(f"    {key}: {path}")

        secrets = load_secrets()
        print(f"✓ Secrets loaded")

        api_key = get_elevenlabs_api_key(secrets)
        print(f"✓ API key found: {api_key[:8]}...")

    except Exception as e:
        print(f"✗ Error: {e}")
