# Configuration Loader Usage Guide

**Module:** `src/utils/config_loader.py`
**Last Updated:** 2025-10-18

## Overview

The `config_loader` module provides centralized configuration loading with comprehensive validation and helpful error messages. It ensures that all required configuration sections exist before your code runs, preventing runtime errors.

## Features

✅ **Comprehensive Validation** - Checks all required sections and keys
✅ **Helpful Error Messages** - Clear guidance when configuration is missing or invalid
✅ **Backward Compatibility** - Provides default config for testing
✅ **Path Resolution** - Automatically resolves paths relative to project root
✅ **Secrets Management** - Secure API key loading from secrets.ini

## Installation

The module is already included in `src/utils/config_loader.py`. No installation required.

## Basic Usage

### 1. Load Configuration

```python
from src.utils.config_loader import load_config

# Load and validate config from config/config.yaml
config = load_config()

# Now use the config
voices = config['voices']
softness = config['language']['softness']
model_id = config['elevenlabs']['model_id']
```

### 2. Load API Key

```python
from src.utils.config_loader import get_elevenlabs_api_key

# Get API key from config/secrets.ini
api_key = get_elevenlabs_api_key()
```

### 3. Get Default Config (Testing)

```python
from src.utils.config_loader import get_default_config

# Get a working default config (for backward compatibility or testing)
config = get_default_config()
```

### 4. Resolve Output Paths

```python
from src.utils.config_loader import load_config, resolve_output_paths

config = load_config()
paths = resolve_output_paths(config)

# Access resolved absolute paths
clips_dir = paths['clips_dir']  # Path object
merged_file = paths['merged_file']  # Path object
```

### 5. Create Output Directories

```python
from src.utils.config_loader import load_config, ensure_output_dirs

config = load_config()

# Create all output directories if they don't exist
ensure_output_dirs(config)
```

## Function Reference

### `load_config(config_path=None, validate=True)`

Load configuration from YAML file with validation.

**Parameters:**
- `config_path` (Optional[str]): Path to config file. If None, uses `config/config.yaml`
- `validate` (bool): Whether to validate config structure. Default: True

**Returns:**
- `Dict[str, Any]`: Configuration dictionary

**Raises:**
- `FileNotFoundError`: Config file doesn't exist
- `yaml.YAMLError`: Config file has invalid YAML syntax
- `ValueError`: Required sections are missing

**Example:**
```python
# Load from default location with validation
config = load_config()

# Load from custom path
config = load_config("custom/path/config.yaml")

# Load without validation (not recommended)
config = load_config(validate=False)
```

### `get_default_config()`

Get default configuration for backward compatibility.

**Returns:**
- `Dict[str, Any]`: Default configuration dictionary with all required sections

**Example:**
```python
# Get default config for testing
config = get_default_config()

# Use it just like loaded config
voices = config['voices']
```

**Note:** Use `load_config()` in production. This is for backward compatibility and testing only.

### `get_elevenlabs_api_key(secrets=None)`

Get ElevenLabs API key from secrets.

**Parameters:**
- `secrets` (Optional[ConfigParser]): ConfigParser object. If None, loads from `config/secrets.ini`

**Returns:**
- `str`: API key string

**Example:**
```python
# Load API key from default location
api_key = get_elevenlabs_api_key()

# Or load from custom secrets
from src.utils.config_loader import load_secrets
secrets = load_secrets("custom/secrets.ini")
api_key = get_elevenlabs_api_key(secrets)
```

### `load_secrets(secrets_path=None)`

Load secrets from INI file.

**Parameters:**
- `secrets_path` (Optional[str]): Path to secrets file. If None, uses `config/secrets.ini`

**Returns:**
- `ConfigParser`: ConfigParser object with secrets

**Raises:**
- `FileNotFoundError`: Secrets file doesn't exist
- `ValueError`: Missing required sections or keys

**Example:**
```python
from src.utils.config_loader import load_secrets

secrets = load_secrets()
api_key = secrets.get('elevenlabs', 'api_key')
```

### `resolve_output_paths(config)`

Resolve all output paths relative to project root.

**Parameters:**
- `config` (Dict[str, Any]): Configuration dictionary

**Returns:**
- `Dict[str, Path]`: Dictionary mapping path names to absolute Path objects

**Example:**
```python
from src.utils.config_loader import load_config, resolve_output_paths

config = load_config()
paths = resolve_output_paths(config)

# Access paths
print(paths['clips_dir'])  # Path('C:/project/output/clips')
print(paths['merged_file'])  # Path('C:/project/output/conversation.mp3')
```

### `ensure_output_dirs(config)`

Create output directories if they don't exist.

**Parameters:**
- `config` (Dict[str, Any]): Configuration dictionary

**Example:**
```python
from src.utils.config_loader import load_config, ensure_output_dirs

config = load_config()
ensure_output_dirs(config)  # Creates output/, output/clips/, etc.
```

### `get_project_root()`

Get the project root directory (parent of src/).

**Returns:**
- `Path`: Project root directory as Path object

**Example:**
```python
from src.utils.config_loader import get_project_root

root = get_project_root()
config_path = root / "config" / "config.yaml"
```

## Validation

The `load_config()` function performs comprehensive validation by default:

### Required Top-Level Sections

- `elevenlabs` - ElevenLabs API settings
- `voices` - List of voice IDs
- `language` - Language generation settings
- `prosody_distributions` - Prosody variation settings
- `speaker_personality_distributions` - Speaker personality trait distributions
- `breaks` - Pause/break duration settings
- `conversation` - Conversation generation settings
- `emphasis` - Word emphasis settings
- `utterance_types` - Special prosody for utterance types
- `audio` - Audio processing settings
- `paths` - Output file paths

### Required Subsections

**elevenlabs:**
- `model_id` - ElevenLabs model ID
- `api_url` - ElevenLabs API URL
- `voice_settings` - Voice generation settings
  - `stability`
  - `similarity_boost`
  - `style`
  - `use_speaker_boost`

**language:**
- `softness` - Phoneme softness (must be 0.0-1.0)
- `phonemes` - Phoneme definitions
- `syllable_structure` - Syllable structure probabilities
- `consonant_weighting` - Consonant weight ratios

**paths:**
- `output_dir`
- `clips_dir`
- `merged_file`
- `spatialized_file`

## Error Messages

The config loader provides clear, actionable error messages:

### Missing Config File

```
FileNotFoundError: Configuration file not found: /path/to/config.yaml
Expected location: /project/config/config.yaml
Make sure config/config.yaml exists in the project root.
```

### Missing Sections

```
ValueError: Configuration file is missing required sections:
  - elevenlabs: ElevenLabs API settings
  - voices: List of voice IDs
  - language: Language generation settings

Config file: /path/to/config.yaml
Please ensure your config.yaml includes all required sections.
```

### Invalid YAML

```
yaml.YAMLError: Invalid YAML in config file: /path/to/config.yaml
Error: mapping values are not allowed here
```

### Missing Subsection Keys

```
ValueError: elevenlabs section is missing required keys:
  - model_id: ElevenLabs model ID
  - api_url: ElevenLabs API URL
```

### Invalid Values

```
ValueError: language.softness must be between 0.0 and 1.0, got 1.5
```

## Complete Example

Here's a complete example showing all common use cases:

```python
#!/usr/bin/env python
"""
Example: Using config_loader in your module
"""

import sys
from pathlib import Path

# Add project root to path (if running as standalone script)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config_loader import (
    load_config,
    get_elevenlabs_api_key,
    resolve_output_paths,
    ensure_output_dirs,
    get_default_config
)

def main():
    # Load configuration with validation
    try:
        config = load_config()
        print("✓ Configuration loaded successfully")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Using default config instead...")
        config = get_default_config()
    except ValueError as e:
        print(f"Configuration validation error: {e}")
        return

    # Get API key
    try:
        api_key = get_elevenlabs_api_key()
        print(f"✓ API key loaded: {api_key[:8]}...")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Ensure output directories exist
    ensure_output_dirs(config)
    print("✓ Output directories created")

    # Resolve paths for file operations
    paths = resolve_output_paths(config)
    clips_dir = paths['clips_dir']
    merged_file = paths['merged_file']

    # Use configuration values
    voices = config['voices']
    softness = config['language']['softness']
    model_id = config['elevenlabs']['model_id']
    api_url = config['elevenlabs']['api_url']

    print(f"\nConfiguration:")
    print(f"  Voices: {len(voices)}")
    print(f"  Language softness: {softness}")
    print(f"  Model: {model_id}")
    print(f"  API URL: {api_url}")
    print(f"  Clips directory: {clips_dir}")
    print(f"  Merged file: {merged_file}")

if __name__ == "__main__":
    main()
```

## Testing

Run the built-in tests:

```bash
python src/utils/config_loader.py
```

Output:
```
======================================================================
Testing Configuration Loader
======================================================================

[Test 1] Loading config from config/config.yaml with validation...
  [OK] Config loaded and validated successfully
       Voices: 9
       Language softness: 0.7
       Model ID: eleven_multilingual_v2
       API URL: https://api.elevenlabs.io/v1/text-to-speech

[Test 2] Getting default config (backward compatibility)...
  [OK] Default config generated
       Voices: 2
       Language softness: 0.7
       Has all required sections: True

[Test 3] Resolving output paths...
  [OK] Paths resolved:
       output_dir: C:\project\output
       clips_dir: C:\project\output\clips
       merged_file: C:\project\output\conversation.mp3
       spatialized_file: C:\project\output\soundscape_3d.mp3

[Test 4] Loading secrets from secrets.ini...
  [OK] Secrets loaded
  [OK] API key found: sk_a7626...

[Test 5] Testing validation error messages...
  [OK] Validation correctly detected missing sections

======================================================================
Configuration loader tests complete!
======================================================================
```

## Migration from Old Code

### Before (Old Way)

```python
import yaml
import configparser

# Load config manually
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Load secrets manually
secrets = configparser.ConfigParser()
secrets.read('secrets.ini')
api_key = secrets.get('elevenlabs', 'api_key')

# No validation - errors happen at runtime
voices = config['voices']  # KeyError if missing!
```

### After (New Way)

```python
from src.utils.config_loader import load_config, get_elevenlabs_api_key

# Load config with automatic validation
config = load_config()  # ValueError with helpful message if invalid

# Load API key
api_key = get_elevenlabs_api_key()

# Safe to access - validation ensures it exists
voices = config['voices']
```

## Best Practices

1. **Always validate in production:**
   ```python
   config = load_config()  # validate=True by default
   ```

2. **Use get_default_config() only for testing:**
   ```python
   # In tests
   config = get_default_config()

   # In production
   config = load_config()
   ```

3. **Handle errors gracefully:**
   ```python
   try:
       config = load_config()
   except FileNotFoundError:
       print("Config file not found. Please create config/config.yaml")
       exit(1)
   except ValueError as e:
       print(f"Invalid configuration: {e}")
       exit(1)
   ```

4. **Use resolve_output_paths() for file operations:**
   ```python
   paths = resolve_output_paths(config)
   with open(paths['merged_file'], 'wb') as f:
       f.write(audio_data)
   ```

5. **Create directories before writing files:**
   ```python
   ensure_output_dirs(config)
   # Now safe to write to output/clips/
   ```

## Related Documentation

- `docs/CONFIG_MIGRATION_SUMMARY.md` - Overall config migration details
- `docs/LANGUAGE_MODULE_UPDATE.md` - Language module config usage
- `docs/SSML_MODULE_UPDATE.md` - SSML module config usage
- `docs/TTS_MODULE_UPDATE.md` - TTS module config usage
- `config/config.yaml` - Main configuration file

## Support

For issues or questions:
1. Check that `config/config.yaml` exists and is valid YAML
2. Ensure all required sections are present (see Validation section)
3. Run `python src/utils/config_loader.py` to test
4. Check error messages for specific guidance
