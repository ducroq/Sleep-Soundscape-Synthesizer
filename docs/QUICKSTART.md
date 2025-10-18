# Quick Start Guide

## Setup (One Time)

1. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify ffmpeg is installed:**
   ```bash
   ffmpeg -version
   ```
   If not installed, download from: https://ffmpeg.org/download.html

3. **Create API key file:**
   ```bash
   # Create config/secrets.ini with your ElevenLabs API key
   # (copy from config/secrets.ini.example and fill in your key)
   ```

## Generate Your Soundscape (Option A: Archive Scripts - Easiest)

```bash
# From project root
cd archive

# Step 1: Generate clips with personalities (1-2 minutes)
python generate_soundscape.py

# Step 2: Merge clips into conversation (1 second)
python merge_audio.py

# Step 3: Create 3D soundscape (10 seconds)
python spatialize_audio.py

cd ..
```

## Generate Your Soundscape (Option B: New Modular Structure)

```bash
# From project root

# Test the system first
python src/utils/config_loader.py      # Verify config loads
python tests/test_personalities.py     # Test personality system
python tests/test_exact_flow.py        # Test full pipeline

# Then use archive scripts (Option A above) to generate actual soundscape
# (Unified pipeline coming in Phase 2!)
```

## Your Files

- **Main output:** `output/soundscape_3d.mp3` ← This is what you want!
- Individual clips: `output/clips/`
- Sequential version: `output/conversation.mp3`

## Test the System

```bash
# Run pytest test suite
python -m pytest tests/ -v

# Test individual modules
python src/utils/config_loader.py      # Config loading + validation
python src/generation/language.py      # Language generation
python src/generation/ssml.py          # SSML generation
python src/generation/personality.py   # Personality sampling
python src/audio/tts.py                # TTS integration

# Test scripts
python tests/test_personalities.py     # Personality system
python tests/test_tts.py              # TTS integration
python tests/test_ssml_compatibility.py  # SSML features
python tests/test_exact_flow.py        # Full pipeline
```

## Customize (Optional)

Edit `config/config.yaml`:

```yaml
# Make speakers more varied
prosody_distributions:
  rate:
    per_speaker_variation: 0.15  # (was 0.10)

# Make speakers more talkative
speaker_personality_distributions:
  verbosity:
    mean: 1.2  # (was 1.0)
    max: 1.6   # (was 1.4)

# Longer pauses between speakers
conversation:
  pause_distribution:
    mean: 2.0  # (was 1.2)

# More conversation layers
spatialization:
  num_layers: 5  # (was 3)
```

## Troubleshooting

**"ElevenLabs API key not found"**
- Make sure `config/secrets.ini` exists with your API key
- Copy from `config/secrets.ini.example` if needed

**"ffmpeg: command not found"**
- Install ffmpeg and add to PATH
- Windows: Download from ffmpeg.org, add to PATH
- Mac: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

**"Configuration file is missing required sections"**
- Run `python src/utils/config_loader.py` to see detailed validation errors
- Make sure `config/config.yaml` has all required sections

**Import errors**
- Run tests from project root directory
- Make sure you have Python 3.10+ installed
- Reinstall dependencies: `pip install -r requirements.txt`

## What's New (Phase 1 Complete)

✅ **Modular Structure** - All code organized in `src/` directory
✅ **Config Validation** - Comprehensive validation with helpful error messages
✅ **Centralized Config** - All settings in `config/config.yaml`
✅ **Better Testing** - Run `python -m pytest tests/ -v`
✅ **Documentation** - Complete guides for all modules

## Next: Phase 2 (Coming Soon)

**Unified Pipeline** - Single command to run everything:
```bash
python -m src.pipeline.main  # One command for the full pipeline!
```

For now, use the archive scripts (Option A above) to generate soundscapes.
