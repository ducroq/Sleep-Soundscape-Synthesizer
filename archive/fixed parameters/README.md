# Sleep Soundscape Generator

Simple, modular prototype for generating sleep soundscapes with invented language.

## Quick Start

### 1. Install

```bash
pip install requests pyyaml
```

**Note:** `merge_audio.py` and `spatialize_audio.py` require ffmpeg to be installed and in your PATH.

### 2. Configure

Edit `config.yaml`:
- Add your ElevenLabs voice IDs
- Adjust prosody (speech rate, pitch)
- Set language softness
- Configure pauses

### 3. Run

```bash
export ELEVENLABS_API_KEY="your_key"
python generate_soundscape.py
```

## Scripts

**generate_language.py** - Create invented language phrases
```bash
python generate_language.py
```

**generate_ssml.py** - Convert text to SSML
```bash
python generate_ssml.py "mila sora venita"
```

**tts.py** - Text to speech
```bash
python tts.py "your text here"
```

**generate_soundscape.py** - Full generation (uses all the above)
```bash
python generate_soundscape.py
```

**merge_audio.py** - Merge individual clips into one file
```bash
python merge_audio.py
```

**spatialize_audio.py** - Create overlapping spatial layers (NEW!)
```bash
python spatialize_audio.py
```

## Pipeline

**Simple (sequential conversation):**
1. Generate → `python generate_soundscape.py`
2. Merge → `python merge_audio.py`

**Spatial (overlapping conversations - more soothing):**
1. Generate → `python generate_soundscape.py`
2. Spatialize → `python spatialize_audio.py`

The spatialize script creates 3 overlapping conversation layers:
- Left speaker (quieter, background)
- Center speaker (medium volume)
- Right speaker (quieter, background)

This creates a café-like ambience that's harder to "follow" and more relaxing!

## Configuration (config.yaml)

```yaml
voices:
  - id: "YOUR_VOICE_ID"
    gender: female

prosody:
  speech_rate: 0.85  # 0.5-1.5
  pitch: "medium"    # low/medium/high

language:
  softness: 0.8      # 0.0-1.0
  laughter_prob: 0.15

conversation:
  min_pause: 0.5
  max_pause: 2.5

session:
  duration_minutes: 5
  output_dir: "output"
```

## Output

**Individual clips:**
Creates `output/soundscape_0001.mp3`, `output/soundscape_0002.mp3`, etc.

**Sequential (one conversation):**
```bash
python merge_audio.py
```
→ Creates `output/soundscape_complete.mp3`

**Spatial (overlapping conversations - recommended!):**
```bash
python spatialize_audio.py
```
→ Creates `output/soundscape_spatial.mp3`

The spatial version has 3 overlapping conversations positioned left/center/right with different volumes. Much more immersive and soothing! 🎧

## That's It!

Simple, modular, easy to extend.