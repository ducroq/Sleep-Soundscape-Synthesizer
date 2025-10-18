# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sleep Soundscape Synthesizer creates continuous background chatter in an invented language using ElevenLabs TTS API. The system uses probabilistic speaker personalities to create realistic, varied conversations that sound natural without cognitive engagement.

## Development Commands

### Generate Soundscape (Full Pipeline)

**Using Archive Scripts (Legacy - Still Working):**
```bash
# From project root
cd archive
python generate_soundscape.py  # Generate clips (1-2 min)
python merge_audio.py          # Merge into conversation (1 sec)
python spatialize_audio.py     # Create 3D soundscape (10 sec)
cd ..
```

**Using New Modular Structure:**
```bash
# Config loader tests all modules
python src/utils/config_loader.py

# Test personality system
python tests/test_personalities.py

# Test exact pipeline flow
python tests/test_exact_flow.py
```

### Run Tests
```bash
# Run pytest (official test suite)
python -m pytest tests/ -v

# Test individual modules
python src/utils/config_loader.py      # Config loading + validation
python src/generation/language.py       # Language generation
python src/generation/ssml.py          # SSML generation
python src/generation/personality.py    # Personality sampling
python src/audio/tts.py                # TTS integration

# Test scripts
python tests/test_personalities.py     # Personality system
python tests/test_tts.py              # TTS integration
python tests/test_ssml_compatibility.py  # SSML compatibility
python tests/test_exact_flow.py        # Full pipeline flow
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Required:** ffmpeg must be in PATH. Python 3.10+ (3.13 tested).

### API Key Setup
Create `config/secrets.ini` in project root:
```ini
[elevenlabs]
api_key = your_elevenlabs_api_key_here
```

## Architecture

### Pipeline Flow

The system uses a **probabilistic personality model** where each speaker has consistent traits sampled from distributions:

```
1. Session Start
   ↓
2. Initialize Speaker Personalities (src/generation/personality.py)
   - Sample traits for each voice: laughter_frequency, agreement_frequency, verbosity, pause_tendency
   - Sample prosody baseline: rate, pitch
   ↓
3. Generate Each Clip (Loop)
   a. Select random voice/personality
   b. Generate text (src/generation/language.py) - uses personality's verbosity
   c. Generate SSML (src/generation/ssml.py) - uses personality-aware prosody
   d. Generate audio (src/audio/tts.py) - calls ElevenLabs API
   ↓
4. Post-Processing
   - src/audio/merge.py: Concatenate clips with variable pauses
   - src/audio/spatialize.py: Create 3D layered soundscape (RECOMMENDED)
```

### Key Modules

**src/generation/personality.py** - Core personality system
- `SpeakerPersonality` class: Encapsulates speaker traits and prosody baseline
- `initialize_speaker_personalities()`: Creates personalities for all voices at session start
- Each speaker gets unique but consistent traits sampled from normal distributions

**src/generation/language.py** - Invented language generation
- `LanguageGenerator` class: Romance-language-influenced phonology
- Softness parameter (0.0-1.0) controls consonant selection
- Verbosity-aware phrase length controlled by speaker personality
- Reads phonemes, syllable structure, consonant weighting from config

**src/generation/ssml.py** - SSML generation with personality-aware prosody
- Wraps text in SSML with `<prosody>`, `<break>`, and `<emphasis>` tags
- Samples prosody from speaker's baseline with per-utterance variation
- Special handling for questions, agreements, thinking sounds, laughter
- Reads micro_pause.probability from config

**src/audio/tts.py** - ElevenLabs API interface
- `generate_speech()`: Complete TTS pipeline
- `call_elevenlabs_tts()`: API request handling
- Reads api_url and voice_settings from config
- `apply_fade()`: 20ms fade-in/fade-out via ffmpeg (currently disabled due to audio corruption)

**src/utils/config_loader.py** - Configuration management
- `load_config()`: Loads and validates config/config.yaml
- `get_elevenlabs_api_key()`: Retrieves API key from config/secrets.ini
- `ensure_output_dirs()`: Creates output directories
- `get_default_config()`: Provides defaults for backward compatibility
- Comprehensive validation with helpful error messages

**archive/generate_soundscape.py** - Main orchestrator (legacy)
- Coordinates entire pipeline
- Initializes personalities once at start
- Loops through clip generation with random voice selection

**src/audio/merge.py** - Audio merger
- Concatenates clips with variable pauses sampled from distribution
- Uses ffmpeg concat demuxer

**src/audio/spatialize.py** - 3D soundscape creator
- Creates overlapping conversation layers
- Applies stereo panning, volume adjustment, time offsets
- Output is `output/soundscape_3d.mp3` (recommended final product)

### Key Design Patterns

**Probabilistic Modeling**
- Traits sampled from normal distributions at session start
- Per-speaker consistency: Each voice has fixed baseline traits
- Per-utterance variation: Natural variation around baseline

**Separation of Concerns**
- Language generation doesn't know about TTS
- SSML generation receives personalities as input
- TTS doesn't know about language generation

**Dependency Injection**
- Personalities created once and passed to functions
- Config passed throughout pipeline

**Configuration-Driven Design**
- All "magic numbers" moved to config/config.yaml
- Centralized config loading with validation
- Backward-compatible defaults

### Configuration Structure

All configuration in `config/config.yaml`:
- `elevenlabs`: API settings (model_id, api_url, voice_settings)
- `voices`: List of ElevenLabs voice IDs
- `language`: Generation settings (softness, phonemes, syllable_structure, consonant_weighting)
- `prosody_distributions`: Rate/pitch variation parameters
- `speaker_personality_distributions`: Trait distributions (laughter, agreement, verbosity, pause_tendency)
- `breaks`: Pause duration distributions (micro, comma, thinking) with probabilities
- `conversation`: Number of clips, pause between speakers
- `emphasis`: Word emphasis probability and levels
- `utterance_type_probabilities`: Distribution of utterance types
- `utterance_types`: Special prosody for questions, agreements, thinking, laughter
- `spatialization`: Number of layers, stereo positions, volume adjustments, time offsets
- `audio`: Output format (mp3_22050_32 optimized for sleep soundscapes)
- `paths`: Output file paths

## Important Technical Details

### Probability Distributions
Most traits use **normal distributions N(μ, σ²)**:
- Global variation between speakers via `per_speaker_variation`
- Per-speaker consistency via sampled baseline
- Per-utterance naturalness via `per_utterance_variation`
- Values clipped to realistic ranges

Example: Rate calculation for an utterance
```python
# At session start: sample speaker's baseline
speaker_rate ~ N(0.85, 0.10²)  # mean=0.85, speaker_var=0.10

# For each utterance: vary around baseline
utterance_rate ~ N(speaker_rate, 0.03²)  # utterance_var=0.03
utterance_rate *= utterance_type_factor  # e.g., 1.05 for questions
utterance_rate = clip(utterance_rate, 0.70, 1.00)
```

### ElevenLabs SSML Support
- API supports `<speak>`, `<prosody>`, `<break>`, and `<emphasis>` tags
- Parameter `enable_ssml` automatically set when SSML detected
- Voice settings (stability, similarity_boost, style, use_speaker_boost) configurable in config.yaml

### Audio Processing
- Uses ffmpeg directly (Python 3.13 compatible)
- All relative paths with `cwd` parameter
- Format: MP3 22.05kHz @ 32kbps (optimized for sleep soundscapes)
- Fades disabled due to corruption issues with certain ffmpeg versions

### File Structure
```
output/
├── clips/           # Individual audio clips
├── conversation.mp3 # Sequential conversation
└── soundscape_3d.mp3 # Final 3D soundscape (RECOMMENDED)
```

## Common Customizations

### Increase speaker variation
Edit `prosody_distributions` in `config/config.yaml`:
```yaml
rate:
  per_speaker_variation: 0.15  # was 0.10
```

### More talkative speakers
```yaml
verbosity:
  mean: 1.2  # was 1.0
  max: 1.6   # was 1.4
```

### Longer pauses between speakers
```yaml
conversation:
  pause_distribution:
    mean: 2.0  # was 1.2
```

### More layers in 3D soundscape
```yaml
spatialization:
  num_layers: 5  # was 3
  stereo_positions: [-0.8, -0.4, 0.0, 0.4, 0.8]
  volume_adjustments: [0.6, 0.7, 0.8, 0.7, 0.6]
  time_offsets: [0.0, 3.0, 7.0, 12.0, 18.0]
```

## Troubleshooting

**Clips sound too similar:** Increase `per_speaker_variation` in prosody distributions

**Speakers sound robotic:** Increase `per_utterance_variation` for more natural variation

**API errors:** Check `config/secrets.ini` exists with valid ElevenLabs API key

**FFmpeg errors:** Ensure ffmpeg is installed and in PATH. On Windows, download from ffmpeg.org and add to PATH environment variable.

**Config validation errors:** Run `python src/utils/config_loader.py` to see detailed error messages about missing or invalid config sections

**Import errors:** Ensure you're running from project root and that `src/` is in Python path (test scripts add this automatically)

## Recent Changes (Phase 1 Complete)

✅ **Modular Structure**: All code moved to `src/` with proper module organization
✅ **Config Migration**: All hardcoded parameters moved to `config/config.yaml`
✅ **Config Validation**: Comprehensive validation with helpful error messages
✅ **Centralized Config Loading**: `src/utils/config_loader.py` used throughout
✅ **Updated Tests**: All test files use new module structure and config_loader
✅ **Documentation**: Complete usage guides for all modules

See these docs for details:
- `docs/CONFIG_LOADER_USAGE.md` - Complete config_loader guide
- `docs/CONFIG_LOADER_MIGRATION.md` - Migration summary
- `docs/LANGUAGE_MODULE_UPDATE.md` - Language module details
- `docs/SSML_MODULE_UPDATE.md` - SSML module details
- `docs/TTS_MODULE_UPDATE.md` - TTS module details

## Next Steps (Phase 2 - Planned)

**Create `src/pipeline/main.py`** - Unified pipeline orchestrator:
- Single entry point for entire workflow
- Replace archive scripts with modular pipeline
- Improved logging and error handling
- Command: `python -m src.pipeline.main`

This will consolidate:
- `archive/generate_soundscape.py`
- `archive/merge_audio.py`
- `archive/spatialize_audio.py`

Into a single unified pipeline with better modularity and control flow.
