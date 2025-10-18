# Sleep Soundscape Synthesizer

A sophisticated sleep soundscape generator that creates continuous background chatter in an invented language using ElevenLabs TTS API. The system now features **probabilistic speaker personalities** for realistic, varied conversations.

## 🎯 Goal

Create soothing, comforting human presence without cognitive engagement—like café ambience—using invented language that sounds natural but doesn't form recognizable words.

## ✨ New Feature: Probabilistic Speaker Personalities

Each speaker now has a unique, consistent personality sampled from probability distributions:

- **Laughter frequency**: How often they laugh
- **Agreement frequency**: How often they make "mm-hmm" sounds
- **Verbosity**: How long their phrases tend to be
- **Pause tendency**: How much they pause
- **Prosody baseline**: Their natural rate and pitch

Each utterance varies naturally around their personality baseline, creating:
- **Global variation** between speakers
- **Per-speaker consistency** (each voice sounds like the same person)
- **Per-utterance naturalness** (speech isn't robotic)

## 🏗️ Architecture

The project follows a modular architecture with clear separation of concerns:

```
Generation modules (src/generation/):
1. language.py     → Creates invented language phrases
2. ssml.py         → Wraps in SSML with personality-aware prosody
3. personality.py  → Samples speaker traits from distributions

Audio modules (src/audio/):
4. tts.py          → Calls ElevenLabs API
5. merge.py        → Concatenates clips with variable pauses
6. spatialize.py   → Creates 3D layered soundscape (RECOMMENDED)

Utilities (src/utils/):
- config_loader.py → Centralized configuration loading
- logger.py        → Consistent logging across modules
```

**Pipeline** (Phase 2 - coming soon):
- `src/pipeline/main.py` → Single command to run entire pipeline

See **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** for detailed documentation.

## 📋 Requirements

- **Python 3.13** (or 3.10+)
- **ffmpeg** (must be in PATH)
- **ElevenLabs API key** (set as environment variable)
- **Dependencies**: `requests`, `pyyaml`, `numpy`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

Create a `config/secrets.ini` file with your ElevenLabs API key:

```bash
# Copy the example file
cp config/secrets.ini.example config/secrets.ini

# Then edit config/secrets.ini and add your key:
[elevenlabs]
api_key = your_elevenlabs_api_key_here
```

### 3. Generate Soundscape

**Option A: Using Archive Scripts (Legacy)**

**Note:** These scripts are frozen for backward compatibility. For new development, use the modular src/ structure.

```bash
# From project root
cd archive
python generate_soundscape.py  # Generate clips (1-2 min)
python merge_audio.py          # Merge into conversation (1 sec)
python spatialize_audio.py     # Create 3D soundscape (10 sec)
cd ..
```

See [archive/README.md](archive/README.md) for more details.

**Option B: Using New Modular Structure (Recommended)**

```bash
# From project root - using new src/ modules
python -c "from src.generation import language, ssml, personality; from src.audio import tts"

# Or run individual module tests:
python src/utils/config_loader.py      # Test config loading
python tests/test_personalities.py     # Test personality system
python tests/test_exact_flow.py        # Test full pipeline flow
```

**Coming in Phase 2:** `python -m src.pipeline.main` to run all stages automatically!

### Output Files

- `output/clips/` - Individual audio clips
- `output/conversation.mp3` - Sequential conversation
- `output/soundscape_3d.mp3` - **Final 3D soundscape** (this is what you want!)

## ⚙️ Configuration

### config.yaml Structure

```yaml
# Simple voice list (no gender needed)
voices:
  - "voice_id_1"
  - "voice_id_2"
  - "voice_id_3"

# Prosody distributions
prosody_distributions:
  rate:
    base_mean: 0.85                # Average rate for all speakers
    per_speaker_variation: 0.10    # How different speakers are
    per_utterance_variation: 0.03  # Per-utterance naturalness
    min: 0.70
    max: 1.00
  
  pitch:
    per_speaker_variation: 8       # ±8% per speaker
    per_utterance_variation: 3     # ±3% per utterance
    min: -15
    max: 15

# Speaker personality traits
speaker_personality_distributions:
  laughter_frequency:
    mean: 0.15
    std: 0.08
  agreement_frequency:
    mean: 0.25
    std: 0.10
  verbosity:           # Phrase length multiplier
    mean: 1.0
    std: 0.2
    min: 0.7
    max: 1.4
  pause_tendency:      # Pause length multiplier
    mean: 1.0
    std: 0.15
    min: 0.7
    max: 1.3

# Pause distributions
breaks:
  micro_pause:
    mean: 0.3
    std: 0.1
  comma_pause:
    mean: 0.4
    std: 0.15
  thinking_pause:
    mean: 0.8
    std: 0.3

conversation:
  pause_distribution:
    mean: 1.2
    std: 0.5
    min: 0.5
    max: 3.0

# Emphasis
emphasis:
  probability: 0.3
  levels: ["moderate", "strong", "reduced"]
  level_weights: [0.6, 0.2, 0.2]

# Special utterance types
utterance_types:
  question:
    pitch_boost: 15
    rate_factor: 1.05
  agreement:
    volume: "soft"
    rate_factor: 0.9
  thinking:
    rate_factor: 0.85
    pause_before: 0.6
```

## 🎭 How Personalities Work

### At Session Start

When you run `generate_soundscape.py`, the system:

1. **Samples base traits** for each voice from distributions
   - Example: Voice A might get `verbosity=1.3` (talkative), Voice B gets `verbosity=0.8` (concise)

2. **Samples prosody baselines** for each voice
   - Example: Voice A gets `rate=0.90`, Voice B gets `rate=0.78`

### For Each Utterance

1. **Personality determines**:
   - Should this speaker laugh? (based on their `laughter_frequency`)
   - Should they agree? (based on their `agreement_frequency`)
   - How long should the phrase be? (based on their `verbosity`)

2. **Prosody varies naturally** around their baseline:
   - Rate: `baseline ± per_utterance_variation`
   - Pitch: `baseline ± per_utterance_variation`
   - Modified by utterance type (questions get higher pitch, etc.)

### Result

Each speaker sounds like a distinct, consistent person, but with natural per-utterance variation!

## 📁 Project Structure

```
sleep-soundscape-synthesizer/
│
├── README.md                      # This file
├── requirements.txt               # Python dependencies
│
├── config/                        # Configuration
│   ├── config.yaml               # All settings
│   ├── secrets.ini               # API key (create from example)
│   └── secrets.ini.example       # Template
│
├── src/                           # Source code
│   ├── generation/               # Language & personality modules
│   │   ├── language.py
│   │   ├── ssml.py
│   │   └── personality.py
│   ├── audio/                    # Audio processing modules
│   │   ├── tts.py
│   │   ├── merge.py
│   │   └── spatialize.py
│   ├── utils/                    # Utilities
│   │   ├── config_loader.py
│   │   └── logger.py
│   └── pipeline/                 # Main pipeline (Phase 2)
│       └── (main.py - coming soon)
│
├── tests/                         # Test files
│   ├── test_personalities.py
│   ├── test_tts.py
│   └── ...
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md           # Detailed architecture
│   ├── CLAUDE.md                 # Claude Code instructions
│   └── QUICKSTART.md
│
├── archive/                       # Original modules (preserved)
│   └── (old scripts for backward compatibility)
│
└── output/                        # Generated audio
    ├── clips/
    ├── conversations/
    └── final/
```

## 🎨 Customization Tips

### More Variation Between Speakers
Increase `per_speaker_variation` values:
```yaml
rate:
  per_speaker_variation: 0.15  # (was 0.10)
```

### More Natural Per-Utterance Variation
Increase `per_utterance_variation` values:
```yaml
rate:
  per_utterance_variation: 0.05  # (was 0.03)
```

### More Talkative Speakers
Increase verbosity:
```yaml
verbosity:
  mean: 1.2  # (was 1.0)
  max: 1.6   # (was 1.4)
```

### Longer Pauses Between Speakers
```yaml
conversation:
  pause_distribution:
    mean: 2.0  # (was 1.2)
```

### More Layers in Soundscape
```yaml
spatialization:
  num_layers: 5  # (was 3)
  stereo_positions: [-0.8, -0.4, 0.0, 0.4, 0.8]
  volume_adjustments: [0.6, 0.7, 0.8, 0.7, 0.6]
  time_offsets: [0.0, 3.0, 7.0, 12.0, 18.0]
```

### Higher Audio Quality
If you want CD-quality audio (larger files):
```yaml
audio:
  output_format: "mp3_44100_128"  # CD quality
  sample_rate: 44100
```

Or even higher (requires Creator tier+):
```yaml
audio:
  output_format: "mp3_44100_192"  # Highest quality
```

## 🔧 Technical Details

### Phonology
- Romance language influenced (French, Italian, Spanish accents)
- Soft consonants (l, m, n, r, v) prioritized
- Open vowels for melodic flow
- Configurable softness parameter (0.0-1.0)

### SSML Features
- Dynamic rate, pitch, volume per utterance via `<prosody>` tags
- Break tags `<break time="Xs"/>` for natural pauses (up to 3 seconds)
- Emphasis tags `<emphasis level="...">` for word stress
- Special handling for questions, agreements, thinking sounds

**ElevenLabs SSML Support:**
- Fully supported with `<speak>`, `<prosody>`, `<break>`, and `<emphasis>` tags
- API parameter `enable_ssml` is automatically set when SSML is detected
- Voice settings (stability, similarity_boost) used for additional fine-tuning

### Audio Processing
- ~~20ms fade-in/fade-out~~ (disabled - was corrupting audio)
- Uses ffmpeg directly (Python 3.13 compatible)
- All relative paths with `cwd` parameter
- **Format: MP3 22.05kHz @ 32kbps** (optimized for sleep soundscapes)
  - Much smaller files than CD quality
  - Perfectly clear for background speech
  - Faster API downloads
  - Same cost (ElevenLabs charges per character, not quality)

### Spatialization
- 3 overlapping conversation layers (configurable)
- Stereo panning (-1 = full left, +1 = full right)
- Volume adjustments per layer
- Time offsets for natural overlap

## 🐛 Troubleshooting

### "ElevenLabs API key not found"
Make sure you have a `config/secrets.ini` file with:
```ini
[elevenlabs]
api_key = your_actual_api_key
```

### "ffmpeg: command not found"
Install ffmpeg and add to PATH:
- Windows: Download from ffmpeg.org, add to PATH
- Mac: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

### "No clips found"
Run `generate_soundscape.py` first before merging or spatializing.

### Clips sound too similar
Increase `per_speaker_variation` in the prosody distributions.

### Speakers sound too robotic
Increase `per_utterance_variation` for more natural variation.

## 🎵 Advanced Usage

### Custom Personality Distributions

Edit `config.yaml` to change how personalities are sampled:

```yaml
speaker_personality_distributions:
  laughter_frequency:
    mean: 0.20    # More laughter overall
    std: 0.12     # More variation between speakers
```

### Testing Individual Modules

```bash
# Test config loader with validation
python src/utils/config_loader.py

# Test language generation
python src/generation/language.py

# Test SSML generation
python src/generation/ssml.py

# Test TTS (requires API key)
python src/audio/tts.py

# Run pytest tests
python -m pytest tests/ -v
```

### Generating Multiple Variants

```bash
# Generate 3 different soundscapes
for i in {1..3}; do
    python generate_soundscape.py
    python spatialize_audio.py
    mv output/soundscape_3d.mp3 output/soundscape_${i}.mp3
done
```

## 📊 Performance

- **Generation time**: ~2-5 seconds per clip (depends on API)
- **20 clips**: ~1-2 minutes total
- **Merging**: ~1 second
- **Spatialization**: ~5-10 seconds
- **Total**: ~2-3 minutes for complete soundscape

## 🔮 Future Enhancements

- [ ] Emotion distributions (happy, tired, excited speakers)
- [ ] Conversation topic clustering (speakers discuss related topics)
- [ ] Dynamic pitch contours (rising/falling intonation patterns)
- [ ] Background ambience mixing (café sounds, rain, etc.)
- [ ] Real-time generation mode
- [ ] Web interface

## 📄 License

This project is for personal use with the ElevenLabs API.

## 🙏 Credits

- ElevenLabs for the amazing TTS API
- ffmpeg for audio processing
- Romance languages for phonological inspiration

---

**Enjoy your personalized sleep soundscape!** 😴✨
