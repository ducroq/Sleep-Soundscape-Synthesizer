# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sleep Soundscape Synthesizer creates continuous background chatter in an invented language using ElevenLabs TTS API. The system uses probabilistic speaker personalities to create realistic, varied conversations that sound natural without cognitive engagement.

## Development Commands

### Generate Soundscape (Full Pipeline)
```bash
# Generate individual clips with personalities (1-2 minutes)
python generate_soundscape.py

# Merge clips into sequential conversation (1 second)
python merge_audio.py

# Create 3D spatialized soundscape - recommended final output (10 seconds)
python spatialize_audio.py
```

### Run Tests
```bash
# Test personality system
python test/test_personalities.py

# Test TTS integration
python test/test_tts.py

# Test SSML compatibility
python test/test_ssml_compatibility.py

# Test exact flow
python test/test_exact_flow.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Required:** ffmpeg must be in PATH. Python 3.10+ (3.13 tested).

### API Key Setup
Create `secrets.ini` in project root:
```ini
[elevenlabs]
api_key = your_elevenlabs_api_key_here
```

## Architecture

### Pipeline Flow

The system uses a **probabilistic personality model** where each speaker has consistent traits sampled from distributions:

```
1. Session Start (generate_soundscape.py)
   ↓
2. Initialize Speaker Personalities (personality_sampler.py)
   - Sample traits for each voice: laughter_frequency, agreement_frequency, verbosity, pause_tendency
   - Sample prosody baseline: rate, pitch
   ↓
3. Generate Each Clip (Loop)
   a. Select random voice/personality
   b. Generate text (generate_language.py) - uses personality's verbosity
   c. Generate SSML (generate_ssml.py) - uses personality-aware prosody
   d. Generate audio (tts.py) - calls ElevenLabs API
   ↓
4. Post-Processing
   - merge_audio.py: Concatenate clips with variable pauses
   - spatialize_audio.py: Create 3D layered soundscape (RECOMMENDED)
```

### Key Modules

**personality_sampler.py** - Core personality system
- `SpeakerPersonality` class: Encapsulates speaker traits and prosody baseline
- `initialize_speaker_personalities()`: Creates personalities for all voices at session start
- Each speaker gets unique but consistent traits sampled from normal distributions

**generate_language.py** - Invented language generation
- `LanguageGenerator` class: Romance-language-influenced phonology
- Softness parameter (0.0-1.0) controls consonant selection
- Verbosity-aware phrase length controlled by speaker personality

**generate_ssml.py** - SSML generation with personality-aware prosody
- Wraps text in SSML with `<prosody>`, `<break>`, and `<emphasis>` tags
- Samples prosody from speaker's baseline with per-utterance variation
- Special handling for questions, agreements, thinking sounds, laughter

**tts.py** - ElevenLabs API interface
- `generate_speech()`: Complete TTS pipeline
- `call_elevenlabs_tts()`: API request handling
- `apply_fade()`: 20ms fade-in/fade-out via ffmpeg (currently disabled due to audio corruption)

**generate_soundscape.py** - Main orchestrator
- Coordinates entire pipeline
- Initializes personalities once at start
- Loops through clip generation with random voice selection

**merge_audio.py** - Sequential conversation creation
- Concatenates clips with variable pauses sampled from distribution
- Uses ffmpeg concat demuxer

**spatialize_audio.py** - 3D soundscape creation
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

### Configuration Structure

All configuration in `config.yaml`:
- `voices`: List of ElevenLabs voice IDs
- `prosody_distributions`: Rate/pitch variation parameters
- `speaker_personality_distributions`: Trait distributions (laughter, agreement, verbosity, pause_tendency)
- `breaks`: Pause duration distributions (micro, comma, thinking)
- `conversation`: Number of clips, pause between speakers
- `emphasis`: Word emphasis probability and levels
- `utterance_types`: Special prosody for questions, agreements, thinking, laughter
- `spatialization`: Number of layers, stereo positions, volume adjustments, time offsets
- `audio`: Output format (mp3_22050_32 optimized for sleep soundscapes)

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
- Voice settings (stability, similarity_boost) used for fine-tuning

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
Edit `prosody_distributions` in `config.yaml`:
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

**API errors:** Check `secrets.ini` exists with valid ElevenLabs API key

**FFmpeg errors:** Ensure ffmpeg is installed and in PATH. On Windows, download from ffmpeg.org and add to PATH environment variable.
