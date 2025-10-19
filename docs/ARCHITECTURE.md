# Sleep Soundscape Synthesizer - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Current Architecture (Phase 2 Complete)](#current-architecture-phase-2-complete)
3. [Module Responsibilities](#module-responsibilities)
4. [Configuration System](#configuration-system)
5. [Design Patterns](#design-patterns)
6. [Performance Characteristics](#performance-characteristics)
7. [Development History](#development-history)

---

## System Overview

The Sleep Soundscape Synthesizer creates continuous background chatter in an invented language using the ElevenLabs TTS API. The system uses a **probabilistic personality model** where each speaker has consistent traits sampled from statistical distributions.

---

## Current Architecture (Phase 2 Complete)

### Unified Pipeline Flow

**Phase 2** introduced a unified pipeline that consolidates all stages into a single command:

```bash
python -m src.pipeline.main
```

This replaces the previous 3-step manual workflow (generate → merge → spatialize).

```
┌─────────────────────────────────────────────────────────────┐
│  ENTRY POINT: src/pipeline/main.py                         │
│  Command: python -m src.pipeline.main                      │
│                                                             │
│  CLI Options:                                               │
│  - --clips N: Override number of clips                     │
│  - --skip-merge: Only generate clips                       │
│  - --skip-spatial: Skip 3D spatialization                  │
│  - --config PATH: Custom config file                       │
│  - --quiet: Suppress progress messages                     │
│  - --help: Show all options                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Clip Generation (src/pipeline/clip_generator.py) │
├─────────────────────────────────────────────────────────────┤
│  1. Load config/config.yaml                                 │
│  2. Initialize LanguageGenerator (phonology system)         │
│  3. Initialize SpeakerPersonality for each voice            │
│     - Sample traits: laughter, agreement, verbosity, pauses │
│     - Sample prosody baseline: rate, pitch                  │
│  4. For each clip (default: 50):                            │
│     a. Select random voice + personality                    │
│     b. Generate text (src/generation/language.py)           │
│        - Use personality's verbosity multiplier             │
│        - Decide utterance type from config probabilities    │
│     c. Generate SSML (src/generation/ssml.py)               │
│        - Apply personality-aware prosody                    │
│        - Add emphasis and pauses                            │
│     d. Call ElevenLabs API (src/audio/tts.py)               │
│        - Convert SSML → audio                               │
│     e. Save to output/clips/clip_NNN.mp3                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Sequential Merge (src/audio/merge.py)            │
├─────────────────────────────────────────────────────────────┤
│  Function: merge_clips(config, verbose=True)                │
│  1. Load all clips from output/clips/                       │
│  2. Sample pause durations between clips (from config)      │
│  3. Use ffmpeg concat demuxer to create single file         │
│  4. Output: output/conversation.mp3                         │
│  5. Returns: Path to merged file                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: 3D Spatialization (src/audio/spatialize.py)      │
├─────────────────────────────────────────────────────────────┤
│  Function: create_spatial_soundscape(config, verbose=True)  │
│  1. Read merged conversation file                           │
│  2. Create N layers (default: 7) with:                      │
│     - Stereo panning (from -0.8 to +0.8)                    │
│     - Volume adjustments per layer                          │
│     - Time offsets for overlap (0s, 3s, 5s, 8s, etc.)      │
│  3. Use ffmpeg filter_complex to mix layers                 │
│  4. Output: output/soundscape_3d.mp3 (FINAL)                │
│  5. Returns: Path to spatialized file                       │
└─────────────────────────────────────────────────────────────┘
```

### Legacy Archive Scripts

For backward compatibility, the original scripts remain in the `archive/` directory:
- `archive/generate_soundscape.py` - Original clip generator (frozen)
- `archive/merge_audio.py` - Original merger (frozen)
- `archive/spatialize_audio.py` - Original spatializer (frozen)

These are **frozen** and no longer actively developed. Use the unified pipeline instead.

---

## Module Responsibilities

### Generation Modules (src/generation/)

#### 1. **personality.py** - Core Personality System
- **`SpeakerPersonality` class**: Encapsulates all speaker traits
  - Samples traits from normal distributions at initialization
  - Provides methods: `sample_utterance_prosody()`, `should_laugh()`, `get_verbosity()`, etc.
- **`initialize_speaker_personalities()`**: Creates personalities for all voices at session start
- **Design Pattern**: Per-speaker consistency with per-utterance natural variation

#### 2. **language.py** - Invented Language Phonology
- **`LanguageGenerator` class**: Romance-language-influenced phoneme system
- **Phoneme system** (from config):
  - **Full Romance orthography** with accents and special characters
  - **French**: é, è, ê, à, ô, an, en, in, on, un, ch
  - **Portuguese**: ã, õ, ão, õe, lh, nh, rr, ç
  - **Spanish**: ll, ñ, á, í, ó, ú
  - **Italian**: gn, ia, ie, io
  - All configurable in `config/config.yaml`
- **Softness parameter**: Controls weighted selection from consonant pools
- **Syllable structure**: (C)V(C) with probabilistic onset/coda (configurable)
- **Special sounds**: Agreement, laughter, thinking (from config)

#### 3. **ssml.py** - SSML Generation
- Wraps text in SSML `<speak>` tags with prosody attributes
- Adds `<emphasis>`, `<break>`, and `<prosody>` tags
- Consumes personality objects to generate natural variation

### Audio Modules (src/audio/)

#### 4. **tts.py** - ElevenLabs API Interface
- **`generate_speech()`**: Complete TTS pipeline
- **`call_elevenlabs_tts()`**: HTTP request to ElevenLabs
- **Configuration** (from config/config.yaml):
  - API URL, model ID
  - Voice settings: stability, similarity_boost, style, use_speaker_boost
- **SSML auto-detection**: Checks for `<speak>` tag and sets `enable_ssml` flag
- **Fade functionality**: Disabled by default (causes corruption with some ffmpeg versions)

#### 5. **merge.py** - Sequential Conversation Creation
- **`merge_clips(config, verbose=True)`**: New wrapper function for pipeline
- **`merge_audio_clips(config_path)`**: Legacy function (backward compatible)
- Uses ffmpeg concat demuxer with pause durations
- Reads pause distributions from config
- Returns path to merged file

#### 6. **spatialize.py** - 3D Soundscape Creation
- **`create_spatial_soundscape(config, verbose=True)`**: New wrapper function
- **`spatialize_audio(config_path)`**: Legacy function (backward compatible)
- Creates overlapping conversation layers (default: 7)
- Applies stereo panning, volume adjustment, time offsets (all from config)
- Uses ffmpeg `filter_complex` for mixing
- Returns path to spatialized file

### Utility Modules (src/utils/)

#### 7. **config_loader.py** - Configuration Management
- **`load_config()`**: Loads and validates config/config.yaml
- **`get_elevenlabs_api_key()`**: Retrieves API key from config/secrets.ini
- **`ensure_output_dirs()`**: Creates output directories
- **`get_default_config()`**: Provides defaults for backward compatibility
- Comprehensive validation with helpful error messages

#### 8. **logger.py** - Centralized Logging
- Consistent logging across all modules
- Configurable log levels
- Formatted output for better readability

### Pipeline Modules (src/pipeline/)

#### 9. **main.py** - Unified Pipeline Orchestrator ✨ Phase 2
- **Entry point**: `python -m src.pipeline.main`
- **`run_pipeline()`**: Orchestrates all three stages
- **CLI interface** with argparse:
  - `--clips N`: Override number of clips
  - `--skip-merge`: Only generate clips
  - `--skip-spatial`: Skip 3D spatialization
  - `--config PATH`: Custom config file
  - `--quiet`: Suppress progress messages
  - `--help`: Show all options
- Progress tracking with verbose output
- Comprehensive error handling
- Returns result dictionary with file paths

#### 10. **clip_generator.py** - Clip Generation Orchestrator ✨ Phase 2
- **`generate_clips(config, num_clips, verbose=True)`**: Main function
- Coordinates entire clip generation process
- Initializes personalities once at start
- Loops through clip generation with random voice selection
- Progress bar for visual feedback
- Returns list of generated clip paths

---

## Configuration System

**config/config.yaml** handles all system configuration:

### Core Settings
- **`elevenlabs`**: API settings (model_id, api_url, voice_settings)
- **`voices`**: List of ElevenLabs voice IDs
- **`language`**: Generation settings
  - `softness`, `min/max_phrase_length`, `min/max_word_length`
  - **Phonemes**: Full Romance orthography with accents (é, ã, ñ, etc.)
  - `syllable_structure`: onset/coda probabilities
  - `consonant_weighting`: soft/medium/hard ratios

### Personality & Prosody
- **`prosody_distributions`**: Rate/pitch variation parameters
  - `base_mean`, `per_speaker_variation`, `per_utterance_variation`
  - `min`/`max` bounds
- **`speaker_personality_distributions`**: Trait distributions
  - `laughter_frequency`, `agreement_frequency`
  - `verbosity` (phrase length multiplier)
  - `pause_tendency` (pause length multiplier)

### Utterances & Timing
- **`breaks`**: Pause duration distributions (micro, comma, thinking)
  - Each has `mean`, `std`, `min`, `max`
  - `micro_pause` includes `probability` (20%)
- **`conversation`**: Number of clips, pause between speakers
- **`emphasis`**: Word emphasis probability and levels
- **`utterance_type_probabilities`**: Distribution of utterance types
  - `thinking`, `agreement`, `laughter`, `question`, `normal`
- **`utterance_types`**: Special prosody for each type
  - Questions: higher pitch, faster rate
  - Agreements: soft volume, slower rate
  - Thinking: slower rate, pause before

### Audio & Output
- **`audio`**: Output format (mp3_22050_32 optimized for sleep)
- **`spatialization`**: 3D soundscape parameters
  - `num_layers`: 7 (default)
  - `stereo_positions`: [-0.8, -0.6, -0.3, 0.0, 0.3, 0.6, 0.8]
  - `volume_adjustments`: Per-layer volume
  - `time_offsets`: Staggered start times [0s, 3s, 5s, 8s, 12s, 15s, 20s]
- **`paths`**: Output file paths

---

## Design Patterns

### Separation of Concerns
Each module has a single, clear responsibility:
- Language generation doesn't know about TTS
- SSML generation doesn't know about personalities (receives them as input)
- TTS doesn't know about language generation

### Dependency Injection
Personalities are created once and passed to functions:
```python
personality = personalities[voice_id]
ssml = generate_ssml(text, personality, utterance_type)
```

### Backward Compatibility
If distributions aren't in config, defaults are used:
```python
config = config or get_default_config()
```

The audio modules provide both new wrapper functions (for pipeline) and legacy functions:
- `merge_clips(config, verbose)` ← new
- `merge_audio_clips(config_path)` ← legacy

### Pure Functions
Most functions are pure (no side effects):
```python
def sample_utterance_prosody(utterance_type: str) -> Dict[str, Any]:
    # Returns new dict, doesn't modify state
```

### Probabilistic Modeling
Traits sampled from normal distributions at session start:
- **Global variation** between speakers via `per_speaker_variation`
- **Per-speaker consistency** via sampled baseline
- **Per-utterance naturalness** via `per_utterance_variation`
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

---

## Performance Characteristics

- **Memory:** Low (streaming audio, no large buffers)
- **CPU:** Minimal (ffmpeg does heavy lifting)
- **Network:** Dominated by ElevenLabs API calls
- **Bottleneck:** ElevenLabs API rate limits and latency

**Typical Timeline (50 clips):**
```
Generate 50 clips: ~2-5 minutes (API dependent)
Merge clips:       ~1 second
Spatialize:        ~5-10 seconds
Total:             ~3-6 minutes
```

---

## Development History

### Phase 1: Modular Architecture (Complete ✅)
**Goal**: Organize codebase with proper separation of concerns

**Achievements:**
- Moved all code to `src/` directory structure
- Created modular generation/audio/utils packages
- Centralized configuration loading (`src/utils/config_loader.py`)
- Comprehensive config validation with helpful error messages
- All hardcoded parameters moved to `config/config.yaml`
- Full Romance orthography with accents (é, ã, ñ, etc.)
- Updated test suite for new structure
- Complete documentation for all modules

**Files Changed:**
- Created `src/generation/` (personality.py, language.py, ssml.py)
- Created `src/audio/` (tts.py, merge.py, spatialize.py)
- Created `src/utils/` (config_loader.py, logger.py)
- Moved original scripts to `archive/` (frozen for backward compatibility)

### Phase 2: Unified Pipeline (Complete ✅)
**Goal**: Single-command workflow replacing 3-step manual process

**Achievements:**
- Created `src/pipeline/main.py` - unified CLI entry point
- Created `src/pipeline/clip_generator.py` - clip generation orchestrator
- Rich CLI interface with multiple options (--clips, --skip-merge, --skip-spatial, etc.)
- Progress tracking with verbose output
- Better error handling with clear exceptions
- Wrapper functions in audio modules for pipeline integration
- Complete documentation updates

**Command:**
```bash
python -m src.pipeline.main  # One command does everything!
```

**Before Phase 2:**
```bash
cd archive
python generate_soundscape.py  # Step 1
python merge_audio.py          # Step 2
python spatialize_audio.py     # Step 3
cd ..
```

**After Phase 2:**
```bash
python -m src.pipeline.main    # Done!
```

**Files Changed:**
- `src/pipeline/main.py` (new)
- `src/pipeline/clip_generator.py` (new)
- `src/audio/merge.py` (added merge_clips wrapper)
- `src/audio/spatialize.py` (added create_spatial_soundscape wrapper)
- Updated all documentation (README.md, QUICKSTART.md, CLAUDE.md, ARCHITECTURE.md)

### Future Enhancements
**High Priority:**
- **Offline Neural TTS** - Piper/Coqui TTS for free, local generation
  - See detailed plan: `docs/FUTURE_OFFLINE_TTS.md`
  - Benefits: Zero cost, offline operation, unlimited generation

**Medium Priority:**
- Voice cloning for custom voices
- Emotion distributions (happy, tired, excited)
- Background ambience mixing (café, rain)
- Real-time generation mode

**Low Priority:**
- Web interface for parameter tuning
- Dynamic pitch contours
- Conversation topic clustering
- Multichannel WAV output for Audacity editing

---

## Technical Notes

### ElevenLabs SSML Support
- API supports `<speak>`, `<prosody>`, `<break>`, and `<emphasis>` tags
- Parameter `enable_ssml` automatically set when `<speak>` detected
- Voice settings (stability, similarity_boost, style, use_speaker_boost) configurable in config.yaml
- Prosody (rate, pitch, volume) can vary per `<prosody>` tag

### Audio Processing
- Uses ffmpeg directly (Python 3.13 compatible)
- All relative paths with `cwd` parameter
- Format: MP3 22.05kHz @ 32kbps (optimized for sleep soundscapes)
  - Smaller files than CD quality
  - Clear for background speech
  - Faster API downloads
- Fades disabled due to corruption issues with certain ffmpeg versions

### File Structure
```
output/
├── clips/           # Individual audio clips (~5 sec each)
├── conversation.mp3 # Sequential conversation
└── soundscape_3d.mp3 # Final 3D soundscape (RECOMMENDED)
```

---

This architecture provides:
- **Modularity**: Each component is independent
- **Extensibility**: Easy to add new features
- **Testability**: Each module can be tested separately
- **Configurability**: Everything controlled via YAML
- **Usability**: Simple one-command workflow with unified pipeline
