# Quick Start Guide

## What You Have

This prototype includes:

1. **soundscape_synthesizer.py** - Core synthesizer engine
2. **interactive_controller.py** - Real-time parameter control
3. **example_generate_session.py** - Generate long sessions with presets
4. **merge_audio.py** - Combine individual files into one
5. **README.md** - Full documentation
6. **requirements.txt** - Python dependencies

## 5-Minute Setup

### 1. Install

```bash
pip install requests simpleaudio
# Optional for merging:
pip install pydub
```

### 2. Get Your ElevenLabs Voices

Visit your ElevenLabs account and note down voice IDs:
https://elevenlabs.io/app/voice-library

### 3. Update Voice IDs

Edit `soundscape_synthesizer.py` line ~130 and add your voice IDs:
```python
self.voices = {
    'male1': 'YOUR_VOICE_ID_HERE',
    'male2': 'YOUR_VOICE_ID_HERE',
    # ... etc
}
```

### 4. Set API Key

```bash
export ELEVENLABS_API_KEY="your_key_here"
```

## Three Ways to Use

### Option A: Interactive Controller (Recommended)

```bash
python interactive_controller.py
```

Then try:
```
> preset meditative
> start
> set softness 0.95
> stop
```

### Option B: Generate a Session

```bash
python example_generate_session.py
```

Follow the prompts to choose a preset and duration.

### Option C: Python Script

```python
from soundscape_synthesizer import SoundscapeSynthesizer

synth = SoundscapeSynthesizer("your_api_key")
synth.set_parameter('softness', 0.95)
synth.set_parameter('speech_rate', 0.7)
synth.generate_session(duration_seconds=300, save_to_files=True)
```

## Merge Your Audio

After generating files:

```bash
python merge_audio.py
```

Creates `soundscape_complete.mp3` from all the individual files.

## Tips

- **Start with presets** - Try 'meditative' or 'gentle' first
- **Save files** - Use `start --save` in interactive mode
- **Short tests** - Generate 30-60 seconds first to test voices
- **API costs** - Monitor your ElevenLabs usage
- **Experiment** - The parameters are designed for exploration!

## Common Issues

**"Voice ID not found"**
→ Update voice IDs in soundscape_synthesizer.py

**"API key invalid"**
→ Check your ELEVENLABS_API_KEY environment variable

**"simpleaudio won't install"**
→ It's optional, just ignore or comment out play_audio() calls

**"Audio files are separate"**
→ Use merge_audio.py to combine them

## Next: Extend It

Ideas to enhance the prototype:
- Add reverb/ambience using audio libraries
- Create a web UI with Flask/FastAPI
- Integrate with home automation (trigger on sleep schedule)
- Add biometric sensor support (heart rate API)
- Create an "endless" mode that generates continuously

Enjoy your sleep soundscape! 🌙
