# System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Interactive CLI │    │  Python Scripts  │              │
│  │                  │    │                  │              │
│  │  • Start/Stop    │    │  • Sessions      │              │
│  │  • Parameters    │    │  • Presets       │              │
│  │  • Presets       │    │  • Examples      │              │
│  └────────┬─────────┘    └────────┬─────────┘              │
│           │                       │                         │
└───────────┼───────────────────────┼─────────────────────────┘
            │                       │
            └───────────┬───────────┘
                        │
            ┌───────────▼────────────┐
            │  SoundscapeSynthesizer │
            │                        │
            │  Parameters:           │
            │  • speech_rate         │
            │  • conversation_density│
            │  • pitch_variation     │
            │  • softness            │
            │  • laughter_frequency  │
            │  • num_speakers        │
            └───────────┬────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Language    │ │ Voice/Speaker│ │     SSML     │
│  Generator   │ │   Selector   │ │   Builder    │
│              │ │              │ │              │
│ • Phonology  │ │ • Rotation   │ │ • Rate       │
│ • Syllables  │ │ • Variation  │ │ • Pitch      │
│ • Phrases    │ │ • Pool       │ │ • Pauses     │
│ • Laughter   │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                ┌───────▼────────┐
                │  ElevenLabs    │
                │     API        │
                │                │
                │  • TTS Engine  │
                │  • Voice Models│
                │  • SSML Parse  │
                └───────┬────────┘
                        │
                ┌───────▼────────┐
                │  Audio Output  │
                │                │
                │  • MP3 Files   │
                │  • Stream      │
                │  • Playback    │
                └────────────────┘
```

## Data Flow

### Generation Loop

```
1. User starts generation
   │
2. Loop until stopped:
   │
   ├─> Generate utterance text
   │   └─> InventedLanguageGenerator
   │       • Select phonemes based on softness
   │       • Construct syllables
   │       • Form words and phrases
   │       • Add agreement sounds/laughter
   │
   ├─> Select voice
   │   └─> Voice Selector
   │       • Rotate through speaker pool
   │       • Randomize to avoid patterns
   │
   ├─> Build SSML
   │   └─> SSML Builder
   │       • Wrap text in <speak> tags
   │       • Add <prosody> for rate/pitch
   │       • Apply parameter modulations
   │
   ├─> Call ElevenLabs API
   │   └─> HTTP POST to /text-to-speech
   │       • Send text + SSML
   │       • Send voice_id
   │       • Receive MP3 data
   │
   ├─> Save/Play audio
   │   └─> Output Handler
   │       • Save to file (optional)
   │       • Play through speakers (optional)
   │
   └─> Calculate pause
       └─> Pause Calculator
           • Based on conversation_density
           • Add randomization
           • Sleep/wait
```

## Component Details

### InventedLanguageGenerator

**Purpose:** Create phonetically pleasant, non-existent language phrases

**Inputs:**
- `softness` parameter (0.0-1.0)
- `laughter_frequency` parameter

**Process:**
1. Selects consonant pool based on softness
2. Randomly combines consonants + vowels into syllables
3. Combines syllables into words
4. Combines words into phrases
5. Occasionally adds agreement sounds or laughter

**Outputs:**
- Text strings like "mila sora venita"
- Agreement sounds like "mm", "ah"
- Laughter like "hehe", "hoho"

### Voice Selector

**Purpose:** Choose which speaker voice to use for each utterance

**Inputs:**
- `num_speakers` parameter (2-5)
- Pool of available voice IDs

**Process:**
1. Maintains current speaker index
2. Rotates through speakers with some randomness
3. 30% chance to repeat same speaker (natural)
4. 70% chance to switch to next speaker

**Outputs:**
- ElevenLabs voice_id string

### SSML Builder

**Purpose:** Wrap text in XML tags to control prosody

**Inputs:**
- Plain text utterance
- `speech_rate` parameter
- `pitch_variation` parameter

**Process:**
1. Wraps text in `<speak>` tags
2. Adds `<prosody rate="X%">` for speech speed
3. Adds `<prosody pitch="X">` for pitch modulation
4. Can add `<break>` tags for pauses

**Outputs:**
- SSML-formatted XML string

**Example:**
```xml
<speak>
  <prosody rate="85%" pitch="medium">
    mila sora venita
  </prosody>
</speak>
```

### ElevenLabs API Interface

**Purpose:** Convert text to speech using neural TTS

**Inputs:**
- SSML text
- voice_id
- API key
- Model settings

**Process:**
1. Makes HTTP POST to ElevenLabs endpoint
2. Sends JSON with text, model_id, voice_settings
3. Receives response with audio data

**Outputs:**
- MP3 audio data (bytes)

### Pause Calculator

**Purpose:** Determine silence duration between utterances

**Inputs:**
- `conversation_density` parameter (0.1-1.0)

**Process:**
1. Maps density to pause range
   - High density (0.8-1.0) → 0.3-1.0 second pauses
   - Low density (0.1-0.3) → 2.0-3.0 second pauses
2. Adds 30% randomization for naturalness

**Outputs:**
- Float value in seconds

## File Organization

```
outputs/
├── soundscape_synthesizer.py      # Core engine
├── interactive_controller.py      # CLI interface
├── example_generate_session.py    # Example usage
├── merge_audio.py                 # Utility for combining files
├── requirements.txt               # Dependencies
├── README.md                      # Full documentation
├── QUICKSTART.md                  # Quick setup guide
└── ARCHITECTURE.md                # This file
```

## Extension Points

### 1. Biometric Integration

Add a `BiometricAdapter` component:
```
┌─────────────────┐
│ Heart Rate      │───┐
│ Monitor         │   │
└─────────────────┘   │
                      ├──> ┌──────────────────┐
┌─────────────────┐   │    │ BiometricAdapter │
│ Movement        │───┤    │                  │
│ Sensor          │   │    │ Maps sensor data │
└─────────────────┘   │    │ to parameters    │
                      └──> └─────────┬────────┘
                                     │
                              Updates parameters
                                     │
                                     ▼
                          SoundscapeSynthesizer
```

### 2. Audio Effects

Add post-processing:
```
ElevenLabs API
      │
      ▼
┌──────────────┐
│ Raw MP3 Data │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Audio FX     │
│              │
│ • Reverb     │
│ • EQ         │
│ • Compression│
│ • Spatial    │
└──────┬───────┘
       │
       ▼
  Final Output
```

### 3. Web Interface

Replace CLI with web app:
```
┌──────────────────────────────┐
│       Web Browser            │
│                              │
│  ┌────────────────────────┐ │
│  │  React/Vue Frontend    │ │
│  │                        │ │
│  │  • Sliders             │ │
│  │  • Real-time preview   │ │
│  │  • Waveform viz        │ │
│  └───────────┬────────────┘ │
└──────────────┼───────────────┘
               │
         WebSocket/HTTP
               │
┌──────────────▼───────────────┐
│    Flask/FastAPI Backend     │
│                              │
│  • REST API                  │
│  • WebSocket for streaming   │
│  • Session management        │
└──────────────┬───────────────┘
               │
               ▼
    SoundscapeSynthesizer
```

## Performance Considerations

### API Rate Limiting
- ElevenLabs has rate limits
- Pre-generate phrases in batches
- Cache audio segments
- Implement request queuing

### Audio Continuity
- Generate next utterance while playing current one
- Use threading/async for parallel generation
- Buffer multiple utterances ahead

### Memory Management
- Don't keep all MP3s in memory
- Stream to disk immediately
- Delete old utterances in continuous mode

### Cost Optimization
- Track character usage
- Set session limits
- Implement caching for repeated phrases
- Consider local TTS alternatives for development
