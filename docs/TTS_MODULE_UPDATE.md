# TTS Module Update Summary

**Date:** 2025-10-18
**Module:** `src/audio/tts.py`
**Related Test:** `tests/test_tts.py`

## Changes Made

### 1. Updated `call_elevenlabs_tts()` Function

**Location:** `src/audio/tts.py` lines 13-52

**Changes:**
- Added `config: Optional[Dict[str, Any]] = None` parameter
- Reads `api_url` from `config['elevenlabs']['api_url']`
- Replaced hardcoded API URL

**Previous Implementation:**
```python
def call_elevenlabs_tts(
    text: str,
    voice_id: str,
    api_key: str,
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True
) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
```

**New Implementation:**
```python
def call_elevenlabs_tts(
    text: str,
    voice_id: str,
    api_key: str,
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> bytes:
    # Get API URL from config or use default
    if config:
        api_url = config.get('elevenlabs', {}).get('api_url', 'https://api.elevenlabs.io/v1/text-to-speech')
    else:
        api_url = 'https://api.elevenlabs.io/v1/text-to-speech'

    url = f"{api_url}/{voice_id}"
```

**Key Changes:**
- Added optional `config` parameter
- Reads API URL from config with fallback to hardcoded default
- Maintains backward compatibility - function works with or without config

### 2. Updated `generate_speech()` Function

**Location:** `src/audio/tts.py` lines 177-200

**Changes:**
- Reads `voice_settings` from `config['elevenlabs']['voice_settings']`
- Extracts `stability`, `similarity_boost`, `style`, `use_speaker_boost` from config
- Passes config to `call_elevenlabs_tts()`

**Previous Implementation:**
```python
# Get model settings
model_id = config['elevenlabs'].get('model_id', 'eleven_multilingual_v2')
output_format = config['audio'].get('output_format', 'mp3_44100_128')

# Use default voice settings - SSML handles prosody
stability = 0.5
similarity_boost = 0.75
style = 0.0

# Call API
audio_bytes = call_elevenlabs_tts(
    text=text,
    voice_id=voice_id,
    api_key=api_key,
    model_id=model_id,
    output_format=output_format,
    stability=stability,
    similarity_boost=similarity_boost,
    style=style
)
```

**New Implementation:**
```python
# Get model settings
model_id = config['elevenlabs'].get('model_id', 'eleven_multilingual_v2')
output_format = config['audio'].get('output_format', 'mp3_44100_128')

# Get voice settings from config or use defaults
voice_settings = config.get('elevenlabs', {}).get('voice_settings', {})
stability = voice_settings.get('stability', 0.5)
similarity_boost = voice_settings.get('similarity_boost', 0.75)
style = voice_settings.get('style', 0.0)
use_speaker_boost = voice_settings.get('use_speaker_boost', True)

# Call API
audio_bytes = call_elevenlabs_tts(
    text=text,
    voice_id=voice_id,
    api_key=api_key,
    model_id=model_id,
    output_format=output_format,
    stability=stability,
    similarity_boost=similarity_boost,
    style=style,
    use_speaker_boost=use_speaker_boost,
    config=config
)
```

**Key Changes:**
- Reads all voice settings from config with individual `.get()` fallbacks
- Passes `use_speaker_boost` parameter (was missing before)
- Passes `config` to `call_elevenlabs_tts()` for API URL resolution
- Maintains backward compatibility with default values

### 3. Updated Type Imports

**Location:** `src/audio/tts.py` line 10

**Changes:**
```python
# Previous
from typing import Optional

# New
from typing import Optional, Dict, Any
```

### 4. Updated Test File

**Location:** `tests/test_tts.py`

**Changes:**
- Added project root to `sys.path` for proper module imports
- Updated to use `src.audio.tts` and `src.utils.config_loader`
- Added `config=config` parameter to all `call_elevenlabs_tts()` calls
- Replaced Unicode characters (✓, ✗) with ASCII ([OK], [FAIL]) for Windows console compatibility

**Previous:**
```python
import configparser
import yaml
from tts import call_elevenlabs_tts

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

secrets = configparser.ConfigParser()
secrets.read('secrets.ini')
api_key = secrets.get('elevenlabs', 'api_key')

audio = call_elevenlabs_tts(
    text="Hello, this is a test.",
    voice_id=voice_id,
    api_key=api_key,
    model_id=config['elevenlabs']['model_id']
)
```

**New:**
```python
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.audio.tts import call_elevenlabs_tts
from src.utils.config_loader import load_config, get_elevenlabs_api_key

config = load_config()
api_key = get_elevenlabs_api_key()

audio = call_elevenlabs_tts(
    text="Hello, this is a test.",
    voice_id=voice_id,
    api_key=api_key,
    model_id=config['elevenlabs']['model_id'],
    config=config
)
```

## Testing Results

**Command:** `python tests/test_tts.py`

**Results:** ✅ All 3 tests passed successfully

| Test # | Test Name | Status | Audio Size |
|--------|-----------|--------|------------|
| 1 | Plain text | SUCCESS | 23,868 bytes |
| 2 | SSML with prosody | SUCCESS | 34,735 bytes |
| 3 | Invented language (plain) | SUCCESS | 26,794 bytes |

**Verification:**
- All API calls returned 200 status
- All generated valid MP3 files
- API URL successfully read from config
- Voice settings successfully read from config
- SSML prosody working correctly
- Invented language processing working

## Configuration Reference

The TTS module now reads the following from config:

```yaml
# config/config.yaml
elevenlabs:
  model_id: "eleven_multilingual_v2"
  api_url: "https://api.elevenlabs.io/v1/text-to-speech"  # <-- NEW

  # Voice settings (NEW)
  voice_settings:
    stability: 0.5           # 0.0-1.0, higher = more consistent
    similarity_boost: 0.75   # 0.0-1.0, higher = closer to original voice
    style: 0.0               # 0.0-1.0, exaggeration level
    use_speaker_boost: true  # Enable speaker boost
```

**Customization Examples:**

1. **More consistent voices:**
```yaml
voice_settings:
  stability: 0.7  # Higher stability for more consistent output
```

2. **Closer to original voice:**
```yaml
voice_settings:
  similarity_boost: 0.85  # Closer match to original voice
```

3. **More expressive voices:**
```yaml
voice_settings:
  style: 0.3  # More exaggeration and expressiveness
```

4. **Use different API endpoint (for testing):**
```yaml
elevenlabs:
  api_url: "https://api-dev.elevenlabs.io/v1/text-to-speech"
```

## Backward Compatibility

The module maintains full backward compatibility:

1. **`call_elevenlabs_tts()` config parameter is optional:**
   - If not provided, uses hardcoded default API URL
   - Existing code calling without config continues to work

2. **Voice settings have fallback defaults:**
   - If `voice_settings` not in config, uses defaults (0.5, 0.75, 0.0, true)
   - If individual settings missing, uses individual defaults
   - Nested `.get()` pattern prevents KeyError exceptions

3. **Signature-compatible with previous version:**
   - New `config` parameter is optional and last in parameter list
   - Existing positional/keyword argument calls work unchanged

## Related Files

- `src/audio/tts.py` - Updated TTS module
- `tests/test_tts.py` - Updated test file
- `config/config.yaml` - Configuration file with elevenlabs.api_url and voice_settings
- `src/utils/config_loader.py` - Config loading utility
- `docs/CONFIG_MIGRATION_SUMMARY.md` - Overall config migration documentation
- `docs/LANGUAGE_MODULE_UPDATE.md` - Language module config migration
- `docs/SSML_MODULE_UPDATE.md` - SSML module config migration

## Phase 1 Completion Status

**PHASE 1 COMPLETE!** 🎉

All hardcoded parameters have been moved to `config/config.yaml`:

1. ✅ **config/config.yaml** - Extended with all hardcoded parameters
2. ✅ **src/generation/language.py** - Reads phonemes, syllable structure, utterance probabilities
3. ✅ **src/generation/ssml.py** - Reads micro_pause.probability
4. ✅ **src/audio/tts.py** - Reads api_url and voice_settings

Per ARCHITECTURE.md, all modules now read from config with backward-compatible defaults.

## Next Steps (Phase 2)

According to ARCHITECTURE.md, Phase 2 is:

**Create `main.py` unified pipeline orchestrator:**
- Single entry point for the entire soundscape generation pipeline
- Coordinates: language generation → SSML generation → TTS → audio merging → spatialization
- Replaces multiple standalone scripts with one cohesive workflow
- Improved logging and error handling

This will consolidate:
- `generate_soundscape.py`
- `merge_audio.py`
- `spatialize_audio.py`

Into a single unified pipeline with better modularity and control flow.
