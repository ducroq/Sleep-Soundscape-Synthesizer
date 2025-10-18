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


def load_config(config_path: Optional[str] = None, validate: bool = True) -> Dict[str, Any]:
    """
    Load configuration from YAML file with comprehensive validation.

    Args:
        config_path: Optional path to config file. If None, uses config/config.yaml
        validate: Whether to validate config structure (default: True)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
        ValueError: If required sections are missing
    """
    if config_path is None:
        config_path = get_project_root() / "config" / "config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Expected location: {get_project_root() / 'config' / 'config.yaml'}\n"
            f"Make sure config/config.yaml exists in the project root."
        )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Invalid YAML in config file: {config_path}\n"
            f"Error: {e}"
        )

    if not isinstance(config, dict):
        raise ValueError(
            f"Config file must contain a YAML dictionary, got {type(config).__name__}"
        )

    if validate:
        _validate_config(config, config_path)

    return config


def _validate_config(config: Dict[str, Any], config_path: Path):
    """
    Validate configuration structure and provide helpful error messages.

    Args:
        config: Configuration dictionary to validate
        config_path: Path to config file (for error messages)

    Raises:
        ValueError: If validation fails with detailed error message
    """
    # Define required top-level sections
    required_sections = {
        'elevenlabs': 'ElevenLabs API settings',
        'voices': 'List of voice IDs',
        'language': 'Language generation settings',
        'prosody_distributions': 'Prosody variation settings',
        'speaker_personality_distributions': 'Speaker personality trait distributions',
        'breaks': 'Pause/break duration settings',
        'conversation': 'Conversation generation settings',
        'emphasis': 'Word emphasis settings',
        'utterance_types': 'Special prosody for utterance types',
        'audio': 'Audio processing settings',
        'paths': 'Output file paths'
    }

    # Check for missing top-level sections
    missing_sections = [name for name in required_sections if name not in config]
    if missing_sections:
        error_msg = f"Configuration file is missing required sections:\n"
        for section in missing_sections:
            error_msg += f"  - {section}: {required_sections[section]}\n"
        error_msg += f"\nConfig file: {config_path}\n"
        error_msg += f"Please ensure your config.yaml includes all required sections."
        raise ValueError(error_msg)

    # Validate elevenlabs section
    if 'elevenlabs' in config:
        elevenlabs = config['elevenlabs']
        required_elevenlabs = {
            'model_id': 'ElevenLabs model ID',
            'api_url': 'ElevenLabs API URL',
            'voice_settings': 'Voice generation settings'
        }
        missing = [k for k in required_elevenlabs if k not in elevenlabs]
        if missing:
            error_msg = "elevenlabs section is missing required keys:\n"
            for key in missing:
                error_msg += f"  - {key}: {required_elevenlabs[key]}\n"
            raise ValueError(error_msg)

        # Validate voice_settings subsection
        if 'voice_settings' in elevenlabs:
            voice_settings = elevenlabs['voice_settings']
            required_voice = ['stability', 'similarity_boost', 'style', 'use_speaker_boost']
            missing = [k for k in required_voice if k not in voice_settings]
            if missing:
                raise ValueError(
                    f"elevenlabs.voice_settings missing required keys: {missing}\n"
                    f"Required: {required_voice}"
                )

    # Validate voices list
    if 'voices' in config:
        if not isinstance(config['voices'], list):
            raise ValueError("'voices' must be a list of voice IDs")
        if len(config['voices']) == 0:
            raise ValueError("'voices' list is empty. Add at least one ElevenLabs voice ID.")

    # Validate language section
    if 'language' in config:
        language = config['language']
        required_language = {
            'softness': 'Phoneme softness (0.0-1.0)',
            'phonemes': 'Phoneme definitions',
            'syllable_structure': 'Syllable structure probabilities',
            'consonant_weighting': 'Consonant weight ratios'
        }
        missing = [k for k in required_language if k not in language]
        if missing:
            error_msg = "language section is missing required keys:\n"
            for key in missing:
                error_msg += f"  - {key}: {required_language[key]}\n"
            raise ValueError(error_msg)

    # Validate paths section
    if 'paths' in config:
        paths = config['paths']
        required_paths = ['output_dir', 'clips_dir', 'merged_file', 'spatialized_file']
        missing = [k for k in required_paths if k not in paths]
        if missing:
            raise ValueError(
                f"paths section is missing required keys: {missing}\n"
                f"Required: {required_paths}"
            )

    # Validate numeric ranges for critical settings
    if 'language' in config and 'softness' in config['language']:
        softness = config['language']['softness']
        if not (0.0 <= softness <= 1.0):
            raise ValueError(
                f"language.softness must be between 0.0 and 1.0, got {softness}"
            )


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration for backward compatibility.

    This function provides a minimal working configuration when config.yaml
    is not available or for testing purposes.

    Returns:
        Default configuration dictionary

    Note:
        This is a fallback for backward compatibility. In production,
        use load_config() to load from config/config.yaml.
    """
    return {
        'elevenlabs': {
            'model_id': 'eleven_multilingual_v2',
            'api_url': 'https://api.elevenlabs.io/v1/text-to-speech',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75,
                'style': 0.0,
                'use_speaker_boost': True
            }
        },
        'voices': [
            '21m00Tcm4TlvDq8ikWAM',  # Rachel
            'AZnzlk1XvdvUeBnXmlld',  # Domi
        ],
        'language': {
            'softness': 0.7,
            'min_phrase_length': 3,
            'max_phrase_length': 12,
            'min_word_length': 2,
            'max_word_length': 5,
            'phonemes': {
                'soft_consonants': ['l', 'm', 'n', 'r', 'v', 'j', 'w'],
                'medium_consonants': ['b', 'd', 'f', 's', 'z'],
                'hard_consonants': ['p', 't', 'k', 'g', 'ch', 'sh'],
                'vowels': ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ea', 'ia', 'io']
            },
            'syllable_structure': {
                'onset_probability': 0.7,
                'onset_first_syllable': 1.0,
                'coda_probability': 0.3
            },
            'consonant_weighting': {
                'soft_ratio': 1.0,
                'medium_ratio': 0.6,
                'hard_ratio': 0.4
            }
        },
        'prosody_distributions': {
            'rate': {
                'base_mean': 0.85,
                'per_speaker_variation': 0.10,
                'per_utterance_variation': 0.03,
                'min': 0.70,
                'max': 1.00
            },
            'pitch': {
                'base': 'medium',
                'per_speaker_variation': 8,
                'per_utterance_variation': 3,
                'min': -15,
                'max': 15
            }
        },
        'speaker_personality_distributions': {
            'laughter_frequency': {'mean': 0.15, 'std': 0.08},
            'agreement_frequency': {'mean': 0.25, 'std': 0.10},
            'verbosity': {'mean': 1.0, 'std': 0.2, 'min': 0.7, 'max': 1.4},
            'pause_tendency': {'mean': 1.0, 'std': 0.15, 'min': 0.7, 'max': 1.3}
        },
        'breaks': {
            'micro_pause': {
                'mean': 0.3,
                'std': 0.1,
                'min': 0.1,
                'max': 0.6,
                'probability': 0.2
            },
            'comma_pause': {'mean': 0.4, 'std': 0.15, 'min': 0.2, 'max': 0.7},
            'thinking_pause': {'mean': 0.8, 'std': 0.3, 'min': 0.4, 'max': 1.5}
        },
        'conversation': {
            'num_clips': 20,
            'pause_distribution': {'mean': 1.2, 'std': 0.5, 'min': 0.5, 'max': 3.0}
        },
        'emphasis': {
            'probability': 0.3,
            'levels': ['moderate', 'strong', 'reduced'],
            'level_weights': [0.6, 0.2, 0.2]
        },
        'utterance_type_probabilities': {
            'thinking': 0.05,
            'agreement': 0.10,
            'laughter': 0.05,
            'question': 0.15,
            'normal': 0.65
        },
        'utterance_types': {
            'question': {'pitch_boost': 15, 'rate_factor': 1.05},
            'agreement': {'volume': 'soft', 'rate_factor': 0.9},
            'thinking': {'rate_factor': 0.85, 'pause_before': 0.6},
            'laughter': {'volume': 'soft', 'rate_factor': 1.1}
        },
        'agreement_sounds': ['mm-hmm', 'mhm', 'yeah', 'uh-huh', 'right', 'sure', 'okay', 'yes'],
        'laughter_sounds': ['ha ha', 'he he', 'hehe', 'haha', 'ah ha'],
        'thinking_sounds': ['hmm', 'uh', 'um', 'ah', 'oh'],
        'audio': {
            'fade_duration_ms': 20,
            'output_format': 'mp3_22050_32',
            'sample_rate': 22050
        },
        'paths': {
            'output_dir': 'output',
            'clips_dir': 'output/clips',
            'merged_file': 'output/conversation.mp3',
            'spatialized_file': 'output/soundscape_3d.mp3'
        },
        'spatialization': {
            'num_layers': 3,
            'stereo_positions': [-0.6, 0.0, 0.5],
            'volume_adjustments': [0.7, 0.8, 0.6],
            'time_offsets': [0.0, 5.0, 12.0]
        }
    }


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
    # Test configuration loader
    print("=" * 70)
    print("Testing Configuration Loader")
    print("=" * 70)

    # Test 1: Load config from file with validation
    print("\n[Test 1] Loading config from config/config.yaml with validation...")
    try:
        config = load_config()
        print("  [OK] Config loaded and validated successfully")
        print(f"       Voices: {len(config.get('voices', []))}")
        print(f"       Language softness: {config.get('language', {}).get('softness')}")
        print(f"       Model ID: {config.get('elevenlabs', {}).get('model_id')}")
        print(f"       API URL: {config.get('elevenlabs', {}).get('api_url')}")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")

    # Test 2: Get default config (backward compatibility)
    print("\n[Test 2] Getting default config (backward compatibility)...")
    try:
        default_config = get_default_config()
        print("  [OK] Default config generated")
        print(f"       Voices: {len(default_config.get('voices', []))}")
        print(f"       Language softness: {default_config.get('language', {}).get('softness')}")
        print(f"       Has all required sections: {all(k in default_config for k in ['elevenlabs', 'voices', 'language', 'paths'])}")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")

    # Test 3: Resolve output paths
    print("\n[Test 3] Resolving output paths...")
    try:
        config = load_config()
        paths = resolve_output_paths(config)
        print("  [OK] Paths resolved:")
        for key, path in paths.items():
            print(f"       {key}: {path}")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")

    # Test 4: Load secrets
    print("\n[Test 4] Loading secrets from secrets.ini...")
    try:
        secrets = load_secrets()
        print("  [OK] Secrets loaded")

        api_key = get_elevenlabs_api_key(secrets)
        print(f"  [OK] API key found: {api_key[:8]}...")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")

    # Test 5: Test validation with missing section
    print("\n[Test 5] Testing validation error messages...")
    try:
        # Create a minimal invalid config
        invalid_config = {'voices': ['test']}
        _validate_config(invalid_config, Path("test.yaml"))
        print("  [FAIL] Should have raised ValueError")
    except ValueError as e:
        print("  [OK] Validation correctly detected missing sections")
        print(f"       Error preview: {str(e)[:100]}...")

    print("\n" + "=" * 70)
    print("Configuration loader tests complete!")
    print("=" * 70)
