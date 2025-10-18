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

## Generate Your Soundscape (3 Commands)

```bash
# Step 1: Generate clips with personalities (1-2 minutes)
python generate_soundscape.py

# Step 2: Merge clips into conversation (1 second)
python merge_audio.py

# Step 3: Create 3D soundscape (10 seconds)
python spatialize_audio.py
```

## Your Files

- **Main output:** `output/soundscape_3d.mp3` ← This is what you want!
- Individual clips: `output/clips/`
- Sequential version: `output/conversation.mp3`

## Test the System

```bash
# Verify personalities are working
python test_personalities.py

# Test language generation
python generate_language.py

# Test SSML generation
python generate_ssml.py
```

## Customize (Optional)

Edit `config.yaml`:

- **More clips:** Change `num_clips: 20` to `num_clips: 50`
- **More talkative:** Increase `verbosity.mean` to `1.2`
- **More pauses:** Increase `pause_distribution.mean` to `2.0`
- **More layers:** Increase `num_layers` to `5`

## Common Issues

**"API key not found"**
→ Make sure environment variable is set in current terminal session

**"ffmpeg: command not found"**
→ Install ffmpeg and add to PATH

**"No clips found"**
→ Run `generate_soundscape.py` first

**Clips sound too similar**
→ Increase `per_speaker_variation` values in config

## What's Different from Basic Version?

✨ **Probabilistic Personalities**: Each voice now has:
- Unique laughter frequency (some laugh more than others)
- Unique agreement frequency (some say "mm-hmm" more)
- Unique verbosity (some talk more/less)
- Unique pause tendency (some pause more/less)
- Unique baseline rate and pitch
- Natural per-utterance variation

Result: Each speaker sounds like a **consistent, distinct person** with natural variation!

---

That's it! You now have a sophisticated sleep soundscape with realistic speaker personalities. 😴✨
