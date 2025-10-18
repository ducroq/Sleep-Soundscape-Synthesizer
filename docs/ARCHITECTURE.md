# Sleep Soundscape Synthesizer - Architecture Documentation

## Table of Contents
1. [Current Architecture](#current-architecture)
2. [Proposed Architecture Goals](#proposed-architecture-goals)
3. [Hardcoded Parameters Analysis](#hardcoded-parameters-analysis)
4. [Proposed Config.yaml Extensions](#proposed-configyaml-extensions)
5. [Proposed main.py Pipeline](#proposed-mainpy-pipeline)
6. [Migration Path](#migration-path)

---

## Current Architecture

### System Overview

The Sleep Soundscape Synthesizer creates continuous background chatter in an invented language using the ElevenLabs TTS API. The system uses a **probabilistic personality model** where each speaker has consistent traits sampled from statistical distributions.

### Current Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Clip Generation (generate_soundscape.py)         │
├─────────────────────────────────────────────────────────────┤
│  1. Load config.yaml                                        │
│  2. Initialize LanguageGenerator (phonology system)         │
│  3. Initialize SpeakerPersonality for each voice            │
│     - Sample traits: laughter, agreement, verbosity, pauses │
│     - Sample prosody baseline: rate, pitch                  │
│  4. For each clip (default: 20):                            │
│     a. Select random voice + personality                    │
│     b. Generate text (generate_language.py)                 │
│        - Use personality's verbosity multiplier             │
│        - Decide utterance type (thinking/agreement/laugh/   │
│          question/normal) via hardcoded probabilities       │
│     c. Generate SSML (generate_ssml.py)                     │
│        - Apply personality-aware prosody                    │
│        - Add emphasis and pauses                            │
│     d. Call ElevenLabs API (tts.py)                         │
│        - Convert SSML → audio                               │
│     e. Save to output/clips/clip_NNN.mp3                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Sequential Merge (merge_audio.py)                │
├─────────────────────────────────────────────────────────────┤
│  1. Load all clips from output/clips/                       │
│  2. Sample pause durations between clips (from config)      │
│  3. Use ffmpeg concat demuxer to create single file         │
│  4. Output: output/conversation.mp3                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: 3D Spatialization (spatialize_audio.py)          │
├─────────────────────────────────────────────────────────────┤
│  1. Read merged conversation file                           │
│  2. Create N layers (default: 3) with:                      │
│     - Stereo panning (left/center/right)                    │
│     - Volume adjustments                                    │
│     - Time offsets for overlap                              │
│  3. Use ffmpeg filter_complex to mix layers                 │
│  4. Output: output/soundscape_3d.mp3 (FINAL)                │
└─────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

#### 1. **personality_sampler.py** - Core Personality System
- **`SpeakerPersonality` class**: Encapsulates all speaker traits
  - Samples traits from normal distributions at initialization
  - Provides methods: `sample_utterance_prosody()`, `should_laugh()`, `get_verbosity()`, etc.
- **`initialize_speaker_personalities()`**: Creates personalities for all voices at session start
- **Design Pattern**: Per-speaker consistency with per-utterance natural variation

#### 2. **generate_language.py** - Invented Language Phonology
- **`LanguageGenerator` class**: Romance-language-influenced phoneme system
- **Phoneme system**:
  - Soft consonants: `['l', 'm', 'n', 'r', 'v', 'j', 'w']`
  - Medium consonants: `['b', 'd', 'f', 's', 'z']`
  - Hard consonants: `['p', 't', 'k', 'g', 'ch', 'sh']`
  - Vowels: `['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ea', 'ia', 'io']`
- **Softness parameter**: Controls weighted selection from consonant pools
- **Syllable structure**: (C)V(C) with probabilistic onset/coda
- **Special sounds**: Agreement, laughter, thinking (hardcoded lists)

#### 3. **generate_ssml.py** - SSML Generation
- Wraps text in SSML `<speak>` tags with prosody attributes
- Adds `<emphasis>`, `<break>`, and `<prosody>` tags
- Consumes personality objects to generate natural variation

#### 4. **tts.py** - ElevenLabs API Interface
- **`call_elevenlabs_tts()`**: HTTP request to ElevenLabs
- **Hardcoded values**:
  - API URL: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
  - Voice settings: `stability=0.5, similarity_boost=0.75, style=0.0`
- **SSML auto-detection**: Checks for `<speak>` tag and sets `enable_ssml` flag
- **Fade functionality**: Disabled by default (causes corruption with some ffmpeg versions)

#### 5. **generate_soundscape.py** - Main Orchestrator
- Coordinates entire clip generation pipeline
- **Current workflow**: Load config → Initialize personalities → Generate clips → Done
- **User must manually run**: `merge_audio.py` then `spatialize_audio.py`

#### 6. **merge_audio.py** - Sequential Conversation Creation
- Uses ffmpeg concat demuxer with pause durations
- Reads pause distributions from config

#### 7. **spatialize_audio.py** - 3D Soundscape Creation
- Creates overlapping conversation layers
- Applies stereo panning, volume, time offsets (all from config)
- Uses ffmpeg `filter_complex` for mixing

### Current Configuration Structure

**config.yaml** currently handles:
- Voice IDs
- Language settings: `softness`, `min/max_phrase_length`, `min/max_word_length`
- Prosody distributions (rate, pitch)
- Speaker personality distributions
- Break/pause distributions
- Conversation settings
- Emphasis settings
- Utterance type prosody modifiers
- Agreement/laughter/thinking sound lists
- Audio processing settings
- Output paths
- Spatialization parameters

---

## Proposed Architecture Goals

### 1. **Complete Configuration Migration**
Move ALL hardcoded parameters to `config.yaml`:
- Phoneme lists (soft/medium/hard consonants, vowels)
- Syllable structure probabilities (onset, coda chances)
- Consonant weighting ratios
- Utterance type probabilities (thinking, agreement, laughter, question)
- Micro pause injection probability
- ElevenLabs voice settings (stability, similarity_boost, style)
- API URL

### 2. **Unified Pipeline with main.py**
Create a single entry point that runs all three stages:
```bash
python main.py  # Runs: clips → merge → spatialize
```

Benefits:
- Single command workflow
- Clear stage boundaries
- Easier for users
- Consistent error handling

### 3. **Multichannel WAV Output for Audacity**
Modify `spatialize_audio.py` to output multichannel WAV:
- Each conversation layer = separate audio channel
- Allows manual mixing/editing in Audacity
- Keeps existing stereo MP3 output as option

### 4. **Maintain Modular Design**
- Keep separation between language, SSML, TTS modules
- Continue using dependency injection for personalities
- Preserve backward compatibility where possible

---

## Hardcoded Parameters Analysis

### In generate_language.py (Lines 24-29)

**HARDCODED PHONEMES:**
```python
self.soft_consonants = ['l', 'm', 'n', 'r', 'v', 'j', 'w']
self.medium_consonants = ['b', 'd', 'f', 's', 'z']
self.hard_consonants = ['p', 't', 'k', 'g', 'ch', 'sh']
self.vowels = ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ea', 'ia', 'io']
```

**HARDCODED CONSONANT WEIGHTING (Lines 36-38):**
```python
soft_weight = self.softness
medium_weight = (1.0 - self.softness) * 0.6
hard_weight = (1.0 - self.softness) * 0.4
```
The `0.6` and `0.4` ratios are hardcoded.

**HARDCODED SYLLABLE STRUCTURE PROBABILITIES (Lines 69, 76):**
```python
if i == 0 or random.random() < 0.7:  # 70% chance of initial consonant
if random.random() < 0.3:            # 30% chance of final consonant
```

**HARDCODED AGREEMENT SOUNDS (Lines 124-127):**
```python
agreements = ["mm-hmm", "mhm", "yeah", "uh-huh", "right", "sure", "okay", "yes"]
```
(These ARE in config.yaml lines 120-128, but code doesn't use them)

**HARDCODED LAUGHTER SOUNDS (Lines 132-134):**
```python
laughs = ["ha ha", "he he", "hehe", "haha", "ah ha"]
```
(These ARE in config.yaml lines 131-136, but code doesn't use them)

**HARDCODED THINKING SOUNDS (Lines 139):**
```python
thinks = ["hmm", "uh", "um", "ah", "oh"]
```
(These ARE in config.yaml lines 139-144, but code doesn't use them)

**HARDCODED UTTERANCE TYPE PROBABILITIES (Lines 164-177):**
```python
if rand < 0.05:      # 5% thinking sounds
elif rand < 0.15:    # 10% agreement
elif rand < 0.20:    # 5% laughter
elif rand < 0.35:    # 15% questions
else:                # 65% normal statements
```

### In generate_ssml.py (Line 88)

**HARDCODED MICRO PAUSE PROBABILITY:**
```python
if i < len(words) - 1 and random.random() < 0.2:  # 20% chance of micro pause
```

### In tts.py (Lines 44, 175-177)

**HARDCODED API URL:**
```python
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
```

**HARDCODED VOICE SETTINGS:**
```python
stability = 0.5
similarity_boost = 0.75
style = 0.0
```

### In spatialize_audio.py

**No hardcoded parameters** - all spatialization parameters come from config.yaml.

---

## Proposed Config.yaml Extensions

Add the following sections to `config.yaml`:

```yaml
# Language Phonology System
language:
  softness: 0.7  # Existing
  min_phrase_length: 3  # Existing
  max_phrase_length: 12  # Existing
  min_word_length: 2  # Existing
  max_word_length: 5  # Existing

  # NEW: Phoneme definitions
  phonemes:
    soft_consonants: ['l', 'm', 'n', 'r', 'v', 'j', 'w']
    medium_consonants: ['b', 'd', 'f', 's', 'z']
    hard_consonants: ['p', 't', 'k', 'g', 'ch', 'sh']
    vowels: ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ea', 'ia', 'io']

  # NEW: Syllable structure probabilities
  syllable_structure:
    onset_probability: 0.7       # Chance of initial consonant
    onset_first_syllable: 1.0    # First syllable always has onset
    coda_probability: 0.3        # Chance of final consonant

  # NEW: Consonant weighting (how softness affects distribution)
  consonant_weighting:
    soft_ratio: 1.0      # Multiplier for soft consonants
    medium_ratio: 0.6    # Multiplier for medium consonants when softness=0
    hard_ratio: 0.4      # Multiplier for hard consonants when softness=0

# NEW: Utterance Type Probabilities
utterance_type_probabilities:
  thinking: 0.05      # 5% thinking sounds (hmm, uh)
  agreement: 0.10     # 10% agreement sounds (mm-hmm, yeah)
  laughter: 0.05      # 5% laughter sounds (haha, hehe)
  question: 0.15      # 15% questions (rising intonation)
  normal: 0.65        # 65% normal statements
  # Note: Must sum to 1.0

# Enhanced Breaks Configuration
breaks:
  micro_pause:  # Existing
    mean: 0.3
    std: 0.1
    min: 0.1
    max: 0.6
    probability: 0.2  # NEW: 20% chance between words

  comma_pause:  # Existing
    mean: 0.4
    std: 0.15
    min: 0.2
    max: 0.7

  thinking_pause:  # Existing
    mean: 0.8
    std: 0.3
    min: 0.4
    max: 1.5

# ElevenLabs API Configuration
elevenlabs:
  model_id: "eleven_multilingual_v2"  # Existing
  api_url: "https://api.elevenlabs.io/v1/text-to-speech"  # NEW

  # NEW: Voice settings (currently hardcoded in tts.py)
  voice_settings:
    stability: 0.5           # 0.0-1.0, higher = more consistent
    similarity_boost: 0.75   # 0.0-1.0, higher = closer to original voice
    style: 0.0               # 0.0-1.0, exaggeration level
    use_speaker_boost: true

# Audio Output Configuration
audio:
  fade_duration_ms: 20  # Existing (currently disabled)
  output_format: "mp3_22050_32"  # Existing
  sample_rate: 22050  # Existing

  # NEW: Multichannel output settings
  multichannel:
    enabled: false                  # Set to true for multichannel WAV
    format: "wav"                   # Output format when multichannel enabled
    channels_per_layer: 1           # Mono channels per conversation layer
    bit_depth: 16                   # 16 or 24 bit
```

---

## Proposed main.py Pipeline

Create a new `main.py` file that orchestrates all three stages:

```python
"""
Sleep Soundscape Synthesizer - Main Pipeline
Runs all stages: clip generation → merge → spatialize
"""

import os
import sys
import yaml
from generate_soundscape import generate_soundscape
from merge_audio import merge_audio_clips
from spatialize_audio import spatialize_audio


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_pipeline(config_path: str = "config.yaml", skip_stages: list = None):
    """
    Run complete soundscape generation pipeline.

    Args:
        config_path: Path to config.yaml
        skip_stages: List of stages to skip (e.g., ['clips', 'merge', 'spatialize'])

    Pipeline stages:
        1. clips - Generate individual audio clips with personalities
        2. merge - Merge clips into sequential conversation
        3. spatialize - Create 3D spatialized soundscape (or multichannel WAV)
    """
    skip_stages = skip_stages or []

    print("=" * 70)
    print("SLEEP SOUNDSCAPE SYNTHESIZER - FULL PIPELINE")
    print("=" * 70)
    print(f"\nConfig: {config_path}")

    config = load_config(config_path)

    # Stage 1: Generate Clips
    if 'clips' not in skip_stages:
        print("\n" + "=" * 70)
        print("STAGE 1/3: GENERATING CLIPS")
        print("=" * 70)
        try:
            generate_soundscape(config_path)
        except Exception as e:
            print(f"\nERROR in Stage 1: {e}")
            return False
    else:
        print("\n[Skipping Stage 1: Clips already generated]")

    # Stage 2: Merge Clips
    if 'merge' not in skip_stages:
        print("\n" + "=" * 70)
        print("STAGE 2/3: MERGING CLIPS INTO CONVERSATION")
        print("=" * 70)
        try:
            merge_audio_clips(config_path)
        except Exception as e:
            print(f"\nERROR in Stage 2: {e}")
            return False
    else:
        print("\n[Skipping Stage 2: Conversation already merged]")

    # Stage 3: Spatialize Audio
    if 'spatialize' not in skip_stages:
        print("\n" + "=" * 70)
        print("STAGE 3/3: CREATING 3D SOUNDSCAPE")
        print("=" * 70)
        try:
            # Check if multichannel output is enabled
            multichannel_config = config.get('audio', {}).get('multichannel', {})
            if multichannel_config.get('enabled', False):
                print("Multichannel mode enabled - outputting WAV with separate channels")
                spatialize_audio_multichannel(config_path)
            else:
                spatialize_audio(config_path)
        except Exception as e:
            print(f"\nERROR in Stage 3: {e}")
            return False
    else:
        print("\n[Skipping Stage 3: Soundscape already spatialized]")

    # Success
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)

    output_file = config['paths'].get('spatialized_file', 'output/soundscape_3d.mp3')
    print(f"\nFinal output: {output_file}")

    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"File size: {size_mb:.1f} MB")

    print("\nYour sleep soundscape is ready!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Sleep Soundscape Synthesizer - Generate AI conversation soundscapes"
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )
    parser.add_argument(
        '--skip-clips',
        action='store_true',
        help='Skip clip generation (use existing clips)'
    )
    parser.add_argument(
        '--skip-merge',
        action='store_true',
        help='Skip merging (use existing conversation.mp3)'
    )
    parser.add_argument(
        '--skip-spatialize',
        action='store_true',
        help='Skip spatialization (only generate clips and merge)'
    )

    args = parser.parse_args()

    # Build skip list
    skip_stages = []
    if args.skip_clips:
        skip_stages.append('clips')
    if args.skip_merge:
        skip_stages.append('merge')
    if args.skip_spatialize:
        skip_stages.append('spatialize')

    try:
        success = run_pipeline(args.config, skip_stages)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### Usage Examples

```bash
# Run full pipeline (all 3 stages)
python main.py

# Use custom config
python main.py --config my_config.yaml

# Skip clip generation (reuse existing clips)
python main.py --skip-clips

# Only generate and merge (no spatialization)
python main.py --skip-spatialize

# Only spatialize (clips and merge already done)
python main.py --skip-clips --skip-merge
```

---

## Migration Path

### Phase 1: Extend Config (No Breaking Changes)

**File: config.yaml**
1. Add new sections (phonemes, syllable_structure, utterance_type_probabilities, etc.)
2. Keep existing structure intact
3. All modules continue working with current code

**File: generate_language.py**
1. Modify `__init__()` to read phonemes from config (with fallback to hardcoded)
2. Modify `_build_consonant_pool()` to use `consonant_weighting` from config
3. Modify `generate_word()` to use `syllable_structure.onset_probability` and `coda_probability`
4. Modify special sound methods to read from config (with fallbacks)
5. Modify `generate_utterance()` to use `utterance_type_probabilities` from config

**File: generate_ssml.py**
1. Modify `add_pauses_to_text()` to use `breaks.micro_pause.probability` from config

**File: tts.py**
1. Modify `call_elevenlabs_tts()` to use `elevenlabs.api_url` from config
2. Modify `generate_speech()` to use `elevenlabs.voice_settings` from config

### Phase 2: Create main.py

**New file: main.py**
1. Implement pipeline orchestrator as shown above
2. Add argument parsing for skip options
3. Add multichannel output detection

**New file: spatialize_audio_multichannel.py** (or modify spatialize_audio.py)
1. Implement multichannel WAV export
2. Each layer outputs to separate channel
3. Use `audio.multichannel` config section

### Phase 3: Update Documentation

**File: CLAUDE.md**
1. Update Development Commands section to show `python main.py`
2. Add section on multichannel output
3. Document new config parameters

**File: README.md** (create if needed)
1. Add quick start guide
2. Document pipeline stages
3. Show configuration examples

### Phase 4: Testing

**Create test files:**
1. `test/test_config_migration.py` - Verify config loading with new parameters
2. `test/test_phoneme_generation.py` - Test configurable phoneme system
3. `test/test_pipeline.py` - Test main.py orchestration
4. `test/test_multichannel.py` - Test multichannel output

---

## Benefits of Proposed Architecture

### 1. **Full Configurability**
- Users can customize phonology without code changes
- Easy to create different language "flavors" (harsh Germanic vs. soft Romance)
- Adjust utterance type balance (more questions vs. statements)

### 2. **Simplified Workflow**
- Single command: `python main.py`
- Optional stage skipping for faster iteration
- Clear progress indicators

### 3. **Enhanced Output Flexibility**
- Stereo MP3 for immediate playback (existing)
- Multichannel WAV for Audacity editing (new)
- Each conversation layer editable independently

### 4. **Backward Compatibility**
- All existing scripts still work independently
- Config migration uses sensible defaults
- No breaking changes to existing workflows

### 5. **Better Maintainability**
- All "magic numbers" documented in config
- Easier to experiment with parameters
- Clear separation of concerns maintained

---

## Implementation Checklist

- [ ] Extend config.yaml with new sections
- [ ] Update generate_language.py to read phonemes from config
- [ ] Update generate_language.py to read syllable probabilities from config
- [ ] Update generate_language.py to read utterance type probabilities from config
- [ ] Update generate_language.py to use sound lists from config
- [ ] Update generate_ssml.py to read micro_pause.probability from config
- [ ] Update tts.py to read API URL from config
- [ ] Update tts.py to read voice_settings from config
- [ ] Create main.py pipeline orchestrator
- [ ] Add multichannel WAV output option to spatialize_audio.py
- [ ] Update CLAUDE.md with new workflow
- [ ] Create tests for config migration
- [ ] Create tests for main.py pipeline
- [ ] Verify backward compatibility

---

## Technical Notes

### Probability Distribution Patterns

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
- Parameter `enable_ssml` automatically set when `<speak>` detected
- Voice settings (stability, similarity_boost, style) apply to entire utterance
- Prosody (rate, pitch, volume) can vary per `<prosody>` tag

### Multichannel Audio Format

Proposed multichannel WAV structure:
```
Channel 1-2: Layer 1 (stereo pair)
Channel 3-4: Layer 2 (stereo pair)
Channel 5-6: Layer 3 (stereo pair)
...
```

Or if `channels_per_layer: 1`:
```
Channel 1: Layer 1 (mono)
Channel 2: Layer 2 (mono)
Channel 3: Layer 3 (mono)
...
```

Users can import into Audacity and adjust:
- Individual layer volumes
- Pan positions
- Time offsets
- Effects per layer
- Export custom mix

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

### Pure Functions
Most functions are pure (no side effects):
```python
def sample_utterance_prosody(utterance_type: str) -> Dict[str, Any]:
    # Returns new dict, doesn't modify state
```

---

## Performance Characteristics

- **Memory:** Low (streaming audio, no large buffers)
- **CPU:** Minimal (ffmpeg does heavy lifting)
- **Network:** Dominated by ElevenLabs API calls
- **Bottleneck:** ElevenLabs API rate limits and latency

**Typical Timeline:**
```
Generate 20 clips: ~60-120 seconds (API dependent)
Merge clips:       ~1 second
Spatialize:        ~5-10 seconds
Total:             ~70-130 seconds
```

---

This architecture provides:
- **Modularity**: Each component is independent
- **Extensibility**: Easy to add new features
- **Testability**: Each module can be tested separately
- **Configurability**: Everything controlled via YAML
- **Usability**: Simple one-command workflow with main.py
