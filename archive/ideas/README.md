# Sleep Soundscape Synthesizer - Prototype

A Python prototype that generates continuous background chatter in an invented language using ElevenLabs API.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Your ElevenLabs API Key

Option A: Environment variable (recommended)
```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

Option B: The script will prompt you for it

### 3. Configure Voice IDs

Open `soundscape_synthesizer.py` and update the voice IDs in the `__init__` method around line 130:

```python
self.voices = {
    'male1': 'YOUR_MALE_VOICE_ID_1',
    'male2': 'YOUR_MALE_VOICE_ID_2', 
    'female1': 'YOUR_FEMALE_VOICE_ID_1',
    'female2': 'YOUR_FEMALE_VOICE_ID_2',
    'female3': 'YOUR_FEMALE_VOICE_ID_3',
}
```

To find your available voices, visit: https://api.elevenlabs.io/v1/voices

Or run this command:
```bash
curl -H "xi-api-key: YOUR_API_KEY" https://api.elevenlabs.io/v1/voices
```

### 4. Run the Prototype

```bash
python soundscape_synthesizer.py
```

This will generate a 60-second soundscape and save each utterance as an MP3 file.

## Usage Examples

### Basic Usage

```python
from soundscape_synthesizer import SoundscapeSynthesizer

# Create synthesizer
synth = SoundscapeSynthesizer(api_key="your_key_here")

# Generate 60-second session
synth.generate_session(duration_seconds=60, save_to_files=True)
```

### Adjust Parameters

```python
# Slow, meditative soundscape
synth.set_parameter('speech_rate', 0.6)
synth.set_parameter('conversation_density', 0.3)
synth.set_parameter('softness', 0.95)
synth.set_parameter('laughter_frequency', 0.05)

# Generate
synth.generate_session(duration_seconds=120)
```

### Generate Individual Utterances

```python
# Generate one utterance
audio_data, pause_duration = synth.generate_utterance_audio()

# Save it
synth.save_audio(audio_data, "my_utterance.mp3")
```

### Test the Language Generator

```python
from soundscape_synthesizer import InventedLanguageGenerator

# Create generator
lang = InventedLanguageGenerator(softness=0.8)

# Generate phrases
for i in range(10):
    print(lang.generate_phrase())

# Generate with different softness
lang.set_softness(0.3)
for i in range(10):
    print(lang.generate_phrase())
```

## Synthesizer Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `speech_rate` | 0.5 - 1.2 | Speed of speech (lower = slower) |
| `conversation_density` | 0.1 - 1.0 | How much silence between speakers (higher = less silence) |
| `pitch_variation` | 0.0 - 1.0 | Amount of pitch expressiveness (lower = more monotone) |
| `softness` | 0.0 - 1.0 | Phonetic softness of language (higher = softer consonants) |
| `laughter_frequency` | 0.0 - 0.5 | How often soft laughter appears |
| `num_speakers` | 2 - 5 | Number of different voices |
| `volume` | 0.0 - 1.0 | Master volume (not yet implemented in ElevenLabs call) |

## Language Examples

**High Softness (0.9):**
```
mila sora venita
luma luma, ah si
nalani velu morea
```

**Medium Softness (0.5):**
```
kora mita selano
tiva runa, eh?
palun sivo kirina
```

**Low Softness (0.2):**
```
kato pira duken
tegra bok sitanu
```

## SSML in ElevenLabs

The synthesizer uses SSML to control prosody:

```xml
<speak>
    <prosody rate="85%" pitch="medium">
        mila sora venita
    </prosody>
</speak>
```

Note: ElevenLabs SSML support may be limited. If you encounter issues, check their documentation for current SSML tag support.

## Output Files

By default, the script saves each utterance as:
- `soundscape_0001.mp3`
- `soundscape_0002.mp3`
- etc.

You can concatenate these later or modify the script to create a continuous audio stream.

## Troubleshooting

### "simpleaudio not working"
The audio playback is optional. If you have issues, just comment out the `play_audio()` calls and rely on the saved MP3 files.

### "API rate limit exceeded"
Add delays between API calls or reduce the `duration_seconds` parameter.

### "Voice ID not found"
Make sure you're using valid voice IDs from your ElevenLabs account. The default IDs are placeholders.

### "SSML not working"
Some ElevenLabs models have better SSML support than others. Try different models or adjust the SSML tags.

## Interactive Controller

For real-time parameter adjustment while the soundscape is running:

```bash
python interactive_controller.py
```

This launches an interactive CLI where you can:
- Start/stop generation
- Adjust parameters on the fly
- Load presets (gentle, meditative, lively, intimate, cafe)
- See current parameter values

### Interactive Commands

```
> start              # Start generating soundscape
> set softness 0.95  # Change a parameter
> preset meditative  # Load a preset
> params             # Show current settings
> stop               # Stop generation
> help               # Show all commands
> quit               # Exit
```

### Available Presets

- **gentle** - Soft, slow, intimate (2 speakers)
- **meditative** - Very slow, spacious, minimal (2 speakers)
- **lively** - Animated, frequent chatter with laughter (4 speakers)
- **intimate** - Warm couple-like conversation (2 speakers)
- **cafe** - Moderate café ambience (3 speakers)

## Next Steps

1. **Create continuous audio stream** - Modify to generate and play audio continuously without saving individual files
2. **Implement sensor integration** - Add heart rate or movement sensor support
3. **Better audio mixing** - Add background ambience, reverb, or spatial audio effects
4. **Web interface** - Create a browser-based control panel
5. **Export full sessions** - Combine individual MP3s into one long file

## API Costs

Keep in mind that ElevenLabs charges per character generated. A 60-second session might generate ~500-1000 characters depending on your parameters.

## License

This is a prototype for personal experimentation. Check ElevenLabs terms of service for commercial use restrictions.
