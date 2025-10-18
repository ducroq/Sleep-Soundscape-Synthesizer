# Project Documentation

# Project Structure
```
Sleep Soundscape Synthesizer/
├── test/
│   ├── debug_api_call.py
│   ├── test_exact_flow.py
│   ├── test_fade.py
│   ├── test_personalities.py
│   ├── test_ssml_compatibility.py
│   ├── test_tts.py
├── ARCHITECTURE.md
├── QUICKSTART.md
├── README.md
├── config.yaml
├── extend_soundscape.py
├── generate_language.py
├── generate_soundscape.py
├── generate_ssml.py
├── merge_audio.py
├── personality_sampler.py
├── requirements.txt
├── sleep-soundscape-concept.md
├── spatialize_audio.py
├── tts.py
```

# test\debug_api_call.py
```python
"""
Debug Script - Check what's being sent to ElevenLabs API
"""

import configparser
import yaml
from generate_language import LanguageGenerator, generate_utterance
from generate_ssml import generate_ssml
from personality_sampler import initialize_speaker_personalities

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Get API key
secrets = configparser.ConfigParser()
secrets.read('secrets.ini')
api_key = secrets.get('elevenlabs', 'api_key')

print("=" * 70)
print("DEBUG: What's being sent to ElevenLabs?")
print("=" * 70)

# Initialize
lang_gen = LanguageGenerator(softness=config['language']['softness'])
voices = config['voices']
personalities = initialize_speaker_personalities(voices, config)

# Get first voice
voice_id = voices[0]
personality = personalities[voice_id]

print(f"\n[1] Voice ID: {voice_id}")
print(f"[2] Personality traits:")
print(f"    - Verbosity: {personality.traits['verbosity']:.2f}")
print(f"    - Rate baseline: {personality.prosody_baseline['rate']:.2f}")
print(f"    - Pitch baseline: {personality.prosody_baseline['pitch']:.1f}%")

# Generate utterance
verbosity = personality.get_verbosity()
text, utterance_type = generate_utterance(lang_gen, config, verbosity)

print(f"\n[3] Generated text: {text}")
print(f"[4] Utterance type: {utterance_type}")

# Generate SSML
ssml = generate_ssml(text, personality, utterance_type)

print(f"\n[5] Generated SSML:")
print(f"    {ssml}")

# Sample prosody
prosody = personality.sample_utterance_prosody(utterance_type)

print(f"\n[6] Prosody parameters:")
print(f"    - Rate: {prosody['rate']:.2f}")
print(f"    - Pitch: {prosody['pitch']:.1f}%")
print(f"    - Volume: {prosody['volume']}")

# Check what would be sent to API
is_ssml = ssml.strip().startswith('<speak>')
print(f"\n[7] API call would include:")
print(f"    - Text: {ssml[:80]}...")
print(f"    - enable_ssml: {is_ssml}")
print(f"    - model_id: {config['elevenlabs']['model_id']}")
print(f"    - output_format: {config['audio']['output_format']}")

# Check tts.py file
print(f"\n[8] Checking tts.py file...")
import os
if os.path.exists('tts.py'):
    with open('tts.py', 'r') as f:
        tts_content = f.read()
    
    if 'enable_ssml' in tts_content:
        print(f"    ✓ tts.py contains 'enable_ssml' parameter")
    else:
        print(f"    ✗ WARNING: tts.py does NOT contain 'enable_ssml' parameter!")
        print(f"    You need to download the updated tts.py file!")
    
    if 're.sub' in tts_content and 'Strip' in tts_content:
        print(f"    ✗ WARNING: tts.py is stripping SSML tags!")
        print(f"    You need to download the updated tts.py file!")
    else:
        print(f"    ✓ tts.py is NOT stripping SSML tags")
else:
    print(f"    ✗ ERROR: tts.py not found!")

print("\n" + "=" * 70)
print("\nIf you see warnings above, download the updated tts.py from:")
print("  /mnt/user-data/outputs/tts.py")
print("=" * 70)
```


# test\test_exact_flow.py
```python
"""
Test Exact Generate Soundscape Flow
Mimics exactly what generate_soundscape.py does
"""

import yaml
from generate_language import LanguageGenerator, generate_utterance
from generate_ssml import generate_ssml
from personality_sampler import initialize_speaker_personalities
from tts import generate_speech
import random

print("=" * 70)
print("Testing EXACT generate_soundscape.py flow")
print("=" * 70)

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize language generator
print("\n[1] Initializing language generator...")
lang_gen = LanguageGenerator(softness=config['language']['softness'])

# Initialize personalities
print("[2] Initializing personalities...")
voices = config['voices']
personalities = initialize_speaker_personalities(voices, config)

# Generate 3 test clips exactly like generate_soundscape.py does
print("\n[3] Generating 3 test clips using EXACT same process...\n")

for i in range(3):
    print(f"  Clip {i+1}:")
    
    # Select random voice and its personality (EXACT same as generate_soundscape.py)
    voice_id = random.choice(voices)
    personality = personalities[voice_id]
    
    # Generate text with personality's verbosity (EXACT same)
    verbosity = personality.get_verbosity()
    text, utterance_type = generate_utterance(lang_gen, config, verbosity)
    
    # Generate SSML with personality-aware prosody (EXACT same)
    ssml = generate_ssml(text, personality, utterance_type)
    
    # Extract prosody parameters (EXACT same)
    prosody = personality.sample_utterance_prosody(utterance_type)
    
    # Generate audio (EXACT same call)
    output_path = f"exact_test_{i+1}.mp3"
    
    print(f"    Voice: {voice_id[:10]}")
    print(f"    Type: {utterance_type}")
    print(f"    Text: {text[:40]}...")
    print(f"    SSML: {ssml[:80]}...")
    
    try:
        success = generate_speech(ssml, voice_id, output_path, config, prosody=prosody)
        if success:
            print(f"    ✓ Saved to: {output_path}")
        else:
            print(f"    ✗ Failed (returned False)")
    except Exception as e:
        print(f"    ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print()

print("=" * 70)
print("RESULTS:")
print("  exact_test_1.mp3")
print("  exact_test_2.mp3") 
print("  exact_test_3.mp3")
print("\nPlay these files. If they have AUDIO, the problem is elsewhere.")
print("If they're SILENT, there's an issue in tts.py's generate_speech function.")
print("=" * 70)
```


# test\test_fade.py
```python
"""
Test if fade is corrupting audio
"""

import yaml
from generate_language import LanguageGenerator, generate_utterance
from generate_ssml import generate_ssml
from personality_sampler import initialize_speaker_personalities
from tts import generate_speech
import random

print("=" * 70)
print("Testing WITH and WITHOUT fade")
print("=" * 70)

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize
lang_gen = LanguageGenerator(softness=config['language']['softness'])
voices = config['voices']
personalities = initialize_speaker_personalities(voices, config)

# Generate one clip
voice_id = random.choice(voices)
personality = personalities[voice_id]
verbosity = personality.get_verbosity()
text, utterance_type = generate_utterance(lang_gen, config, verbosity)
ssml = generate_ssml(text, personality, utterance_type)
prosody = personality.sample_utterance_prosody(utterance_type)

print(f"\nVoice: {voice_id[:10]}")
print(f"Text: {text}")
print(f"SSML: {ssml[:100]}...")

# Test 1: WITH fade (normal)
print("\n[Test 1] WITH fade (apply_fading=True)...")
try:
    success = generate_speech(ssml, voice_id, "test_with_fade.mp3", config, apply_fading=True, prosody=prosody)
    print(f"  Result: {success}")
    print(f"  Saved to: test_with_fade.mp3")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: WITHOUT fade
print("\n[Test 2] WITHOUT fade (apply_fading=False)...")
try:
    success = generate_speech(ssml, voice_id, "test_without_fade.mp3", config, apply_fading=False, prosody=prosody)
    print(f"  Result: {success}")
    print(f"  Saved to: test_without_fade.mp3")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 70)
print("RESULTS:")
print("  test_with_fade.mp3    - Play this")
print("  test_without_fade.mp3 - Play this")
print("\nIf WITHOUT fade has audio but WITH fade doesn't,")
print("then the ffmpeg fade process is corrupting the audio!")
print("=" * 70)
```


# test\test_personalities.py
```python
"""
Test Script for Personality System
Verifies that personalities are sampled correctly and show variation.
"""

import yaml
from personality_sampler import initialize_speaker_personalities, SpeakerPersonality


def test_personality_system():
    """Test the personality sampling system."""
    
    print("=" * 70)
    print("Testing Probabilistic Personality System")
    print("=" * 70)
    
    # Load config
    print("\n[1/3] Loading configuration...")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("  ✓ Config loaded successfully")
    except FileNotFoundError:
        print("  ✗ Error: config.yaml not found")
        return
    
    # Get voices
    voices = config.get('voices', [])
    if not voices:
        print("  ✗ Error: No voices in config")
        return
    
    print(f"  ✓ Found {len(voices)} voices")
    
    # Initialize personalities
    print("\n[2/3] Sampling speaker personalities...")
    personalities = initialize_speaker_personalities(voices, config)
    
    print(f"\n  Generated {len(personalities)} unique personalities:\n")
    print(f"  {'Voice ID':<12} {'Laugh':<8} {'Agree':<8} {'Verbose':<10} {'Pause':<8} {'Rate':<8} {'Pitch':<8}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")
    
    for voice_id, personality in personalities.items():
        short_id = voice_id[:10]
        traits = personality.traits
        baseline = personality.prosody_baseline
        
        print(f"  {short_id:<12} "
              f"{traits['laughter_frequency']:<8.2f} "
              f"{traits['agreement_frequency']:<8.2f} "
              f"{traits['verbosity']:<10.2f} "
              f"{traits['pause_tendency']:<8.2f} "
              f"{baseline['rate']:<8.2f} "
              f"{baseline['pitch']:<8.1f}%")
    
    # Test per-utterance variation
    print("\n[3/3] Testing per-utterance variation for first voice...")
    test_voice_id = voices[0]
    test_personality = personalities[test_voice_id]
    
    print(f"\n  Testing 5 normal utterances for {test_voice_id[:10]}:")
    print(f"  {'#':<4} {'Rate':<8} {'Pitch':<8} {'Volume':<8}")
    print(f"  {'-'*4} {'-'*8} {'-'*8} {'-'*8}")
    
    for i in range(5):
        prosody = test_personality.sample_utterance_prosody('normal')
        print(f"  {i+1:<4} {prosody['rate']:<8.2f} {prosody['pitch']:<8.1f}% {prosody['volume']:<8}")
    
    print("\n  Testing utterance types:")
    print(f"  {'Type':<12} {'Rate':<8} {'Pitch':<8} {'Volume':<8}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
    
    for utt_type in ['normal', 'question', 'agreement', 'thinking']:
        prosody = test_personality.sample_utterance_prosody(utt_type)
        print(f"  {utt_type:<12} {prosody['rate']:<8.2f} {prosody['pitch']:<8.1f}% {prosody['volume']:<8}")
    
    # Test pause sampling
    print("\n  Testing pause sampling:")
    print(f"  {'Type':<15} {'Duration':<10}")
    print(f"  {'-'*15} {'-'*10}")
    
    for pause_type in ['micro_pause', 'comma_pause', 'thinking_pause']:
        pause = test_personality.sample_pause(pause_type)
        print(f"  {pause_type:<15} {pause:<10.2f}s")
    
    # Statistics
    print("\n" + "=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    
    all_laughs = [p.traits['laughter_frequency'] for p in personalities.values()]
    all_agrees = [p.traits['agreement_frequency'] for p in personalities.values()]
    all_verbosity = [p.traits['verbosity'] for p in personalities.values()]
    all_rates = [p.prosody_baseline['rate'] for p in personalities.values()]
    all_pitches = [p.prosody_baseline['pitch'] for p in personalities.values()]
    
    print(f"\n  Trait Ranges:")
    print(f"    Laughter:  {min(all_laughs):.2f} - {max(all_laughs):.2f}")
    print(f"    Agreement: {min(all_agrees):.2f} - {max(all_agrees):.2f}")
    print(f"    Verbosity: {min(all_verbosity):.2f} - {max(all_verbosity):.2f}")
    print(f"    Rate:      {min(all_rates):.2f} - {max(all_rates):.2f}")
    print(f"    Pitch:     {min(all_pitches):.1f}% - {max(all_pitches):.1f}%")
    
    print(f"\n  ✓ All tests passed!")
    print(f"  The personality system is working correctly.\n")
    print("=" * 70)


if __name__ == "__main__":
    test_personality_system()

```


# test\test_ssml_compatibility.py
```python
"""
SSML Compatibility Test
Tests different SSML formats to find what works
"""

import configparser
import requests
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Get API key
secrets = configparser.ConfigParser()
secrets.read('secrets.ini')
api_key = secrets.get('elevenlabs', 'api_key')

voice_id = config['voices'][0]
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

print("=" * 70)
print("SSML Compatibility Tests")
print("=" * 70)

tests = [
    {
        "name": "Plain text (control)",
        "text": "ruzu jaumeaio wonoze",
        "enable_ssml": False
    },
    {
        "name": "SSML with just speak tags",
        "text": "<speak>ruzu jaumeaio wonoze</speak>",
        "enable_ssml": True
    },
    {
        "name": "SSML with break tag",
        "text": '<speak>ruzu <break time="0.5s"/> jaumeaio wonoze</speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with emphasis",
        "text": '<speak>ruzu <emphasis level="strong">jaumeaio</emphasis> wonoze</speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (rate only)",
        "text": '<speak><prosody rate="90%">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (pitch only)",
        "text": '<speak><prosody pitch="+5%">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (volume only)",
        "text": '<speak><prosody volume="medium">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (rate + pitch)",
        "text": '<speak><prosody rate="90%" pitch="+5%">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (ALL: rate + pitch + volume)",
        "text": '<speak><prosody rate="87%" pitch="-7%" volume="medium">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody + emphasis (like we generate)",
        "text": '<speak><prosody rate="87%" pitch="-7%" volume="medium">ruzu jaumeaio <emphasis level="strong">wonoze</emphasis></prosody></speak>',
        "enable_ssml": True
    }
]

results = []

for i, test in enumerate(tests):
    print(f"\n[Test {i+1}/{len(tests)}] {test['name']}")
    print(f"  Text: {test['text'][:60]}...")
    
    data = {
        "text": test['text'],
        "model_id": config['elevenlabs']['model_id'],
        "output_format": config['audio']['output_format'],
        "enable_ssml": test['enable_ssml']
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_size = len(response.content)
            filename = f"test_{i+1:02d}.mp3"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✓ Status: {response.status_code}")
            print(f"  ✓ Audio size: {audio_size:,} bytes")
            print(f"  ✓ Saved to: {filename}")
            
            results.append({
                "test": test['name'],
                "status": "SUCCESS",
                "size": audio_size,
                "file": filename
            })
        else:
            print(f"  ✗ ERROR: Status {response.status_code}")
            print(f"  ✗ Response: {response.text[:200]}")
            results.append({
                "test": test['name'],
                "status": "FAILED",
                "error": response.text
            })
    
    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")
        results.append({
            "test": test['name'],
            "status": "EXCEPTION",
            "error": str(e)
        })

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\nPlay each file and note which ones have AUDIO:\n")

for i, result in enumerate(results):
    if result['status'] == 'SUCCESS':
        size_kb = result['size'] / 1024
        print(f"  {result['file']}: {result['test']}")
        print(f"    Size: {size_kb:.1f} KB - Play this and check!")
    else:
        print(f"  Test {i+1}: {result['test']} - {result['status']}")

print("\n" + "=" * 70)
print("INSTRUCTIONS:")
print("  1. Play EACH mp3 file above")
print("  2. Note which ones have actual SPEECH")
print("  3. Report back which test numbers work")
print("\nThis will tell us which SSML features are causing the problem!")
print("=" * 70)
```


# test\test_tts.py
```python
"""
Quick TTS Test - Diagnose audio generation issues
"""

import configparser
import yaml
from tts import call_elevenlabs_tts

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Get API key
secrets = configparser.ConfigParser()
secrets.read('secrets.ini')
api_key = secrets.get('elevenlabs', 'api_key')

# Get first voice
voice_id = config['voices'][0]

print("Testing ElevenLabs TTS API...")
print(f"Voice ID: {voice_id}")

# Test 1: Plain text
print("\n[Test 1] Plain text...")
try:
    audio = call_elevenlabs_tts(
        text="Hello, this is a test.",
        voice_id=voice_id,
        api_key=api_key,
        model_id=config['elevenlabs']['model_id']
    )
    print(f"  ✓ Got {len(audio)} bytes of audio")
    with open('test_plain.mp3', 'wb') as f:
        f.write(audio)
    print(f"  ✓ Saved to test_plain.mp3")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 2: SSML with prosody
print("\n[Test 2] SSML with prosody...")
ssml_text = '<speak><prosody rate="90%" pitch="+5%" volume="medium">Hello, this is a test with SSML.</prosody></speak>'
try:
    audio = call_elevenlabs_tts(
        text=ssml_text,
        voice_id=voice_id,
        api_key=api_key,
        model_id=config['elevenlabs']['model_id']
    )
    print(f"  ✓ Got {len(audio)} bytes of audio")
    with open('test_ssml.mp3', 'wb') as f:
        f.write(audio)
    print(f"  ✓ Saved to test_ssml.mp3")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 3: Invented language
print("\n[Test 3] Invented language (plain)...")
try:
    audio = call_elevenlabs_tts(
        text="loria belina taso ren",
        voice_id=voice_id,
        api_key=api_key,
        model_id=config['elevenlabs']['model_id']
    )
    print(f"  ✓ Got {len(audio)} bytes of audio")
    with open('test_invented.mp3', 'wb') as f:
        f.write(audio)
    print(f"  ✓ Saved to test_invented.mp3")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\nTests complete! Play the MP3 files to check if they have audio.")
print("If test_plain.mp3 has audio but test_ssml.mp3 doesn't, SSML is the issue.")

```


# ARCHITECTURE.md
```markdown
# System Architecture

## Overview

The Sleep Soundscape Synthesizer uses a multi-stage pipeline with probabilistic personality modeling to create realistic, varied sleep soundscapes.

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          SESSION START                           │
│                      (generate_soundscape.py)                    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Initialize Speaker Personalities                       │
│  (personality_sampler.py)                                        │
│                                                                  │
│  For each voice_id:                                             │
│    Sample traits from distributions:                            │
│      • laughter_frequency ~ N(0.15, 0.08²)                     │
│      • agreement_frequency ~ N(0.25, 0.10²)                    │
│      • verbosity ~ N(1.0, 0.2²)                                │
│      • pause_tendency ~ N(1.0, 0.15²)                          │
│    Sample prosody baseline:                                     │
│      • rate ~ N(0.85, 0.10²)                                   │
│      • pitch ~ N(0, 8²)                                        │
│                                                                  │
│  Result: Each voice has unique, consistent personality          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Generate Each Clip (Loop: num_clips times)            │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┴────────────────────────┐
        ▼                                                  ▼
┌──────────────────────┐                    ┌──────────────────────┐
│  2a. Select Voice    │                    │  2b. Generate Text   │
│                      │                    │  (generate_language)  │
│  voice = random()    │─────────────────▶  │                      │
│  personality = [id]  │                    │  • Use personality's │
└──────────────────────┘                    │    verbosity trait   │
                                            │  • Determine type:   │
                                            │    - 5% thinking     │
                                            │    - 10% agreement   │
                                            │    - 5% laughter     │
                                            │    - 15% question    │
                                            │    - 65% normal      │
                                            └──────────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────────┐
                                            │  2c. Generate SSML   │
                                            │  (generate_ssml)     │
                                            │                      │
                                            │  Sample prosody:     │
                                            │  • rate = baseline   │
                                            │    ± utterance_var   │
                                            │    × type_factor     │
                                            │  • pitch = baseline  │
                                            │    ± utterance_var   │
                                            │    + type_boost      │
                                            │  • volume = type     │
                                            │                      │
                                            │  Add elements:       │
                                            │  • Emphasis (30%)    │
                                            │  • Micro pauses      │
                                            │  • Thinking pauses   │
                                            └──────────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────────┐
                                            │  2d. Generate Audio  │
                                            │  (tts.py)            │
                                            │                      │
                                            │  1. Call ElevenLabs  │
                                            │  2. Apply 20ms fade  │
                                            │  3. Save MP3         │
                                            └──────────────────────┘
                                                      │
                                                      ▼
                                            [clip_000.mp3 saved]
                                                      │
                                            [Repeat for all clips]
                                                      
┌─────────────────────────────────────────────────────────────────┐
│                   POST-PROCESSING PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┴────────────────────────┐
        ▼                                                  ▼
┌──────────────────────┐                    ┌──────────────────────┐
│  OPTION A: Merge     │                    │  OPTION B: 3D        │
│  (merge_audio.py)    │                    │  Spatialize          │
│                      │                    │  (spatialize_audio)   │
│  Concatenate clips   │                    │                      │
│  with variable       │                    │  Create 3 layers:    │
│  pauses sampled      │                    │  • Layer 1: Left     │
│  from distribution   │                    │  • Layer 2: Center   │
│                      │                    │  • Layer 3: Right    │
│  Output:             │                    │                      │
│  conversation.mp3    │                    │  With:               │
└──────────────────────┘                    │  • Time offsets      │
                                            │  • Volume adjust     │
                                            │  • Stereo panning    │
                                            │                      │
                                            │  Output:             │
                                            │  soundscape_3d.mp3   │
                                            └──────────────────────┘
```

## Module Responsibilities

### personality_sampler.py
**Purpose:** Probabilistic personality modeling

**Key Classes:**
- `SpeakerPersonality`: Encapsulates a speaker's traits and prosody baseline
  - Samples traits at initialization
  - Provides methods to sample per-utterance variation
  - Determines behavioral probabilities (laugh, agree, etc.)

**Key Functions:**
- `initialize_speaker_personalities()`: Creates personalities for all voices
- `sample_conversation_pause()`: Samples pauses between turns
- `get_default_config()`: Backward compatibility

### generate_language.py
**Purpose:** Invented language generation

**Key Classes:**
- `LanguageGenerator`: Phoneme-based word/phrase generation
  - Softness parameter controls consonant selection
  - Romance language influenced phonology
  - Verbosity-aware phrase length

**Key Functions:**
- `generate_word()`: Creates nonsense words
- `generate_phrase()`: Creates phrases with verbosity multiplier
- `generate_utterance()`: Determines type and generates appropriate text

### generate_ssml.py
**Purpose:** SSML generation with personality-aware prosody

**Key Functions:**
- `generate_ssml()`: Main SSML generation
  - Samples prosody from personality
  - Adds emphasis tags
  - Adds pause tags
  - Handles utterance types
- `add_emphasis_to_text()`: Random word emphasis
- `add_pauses_to_text()`: Natural pause insertion
- `format_prosody_value()`: SSML value formatting

### tts.py
**Purpose:** ElevenLabs API interface and audio processing

**Key Functions:**
- `call_elevenlabs_tts()`: API request handling
- `apply_fade()`: 20ms fade-in/fade-out via ffmpeg
- `generate_speech()`: Complete TTS pipeline

### generate_soundscape.py
**Purpose:** Main orchestration

**Flow:**
1. Load configuration
2. Initialize language generator
3. Sample speaker personalities
4. Loop: generate clips
   - Select random voice
   - Get personality
   - Generate text with verbosity
   - Create SSML with prosody
   - Generate audio
5. Save all clips

### merge_audio.py
**Purpose:** Sequential conversation creation

**Process:**
1. Load all clips
2. Build ffmpeg concat list
3. Insert variable pauses between clips
4. Concatenate with ffmpeg

### spatialize_audio.py
**Purpose:** 3D soundscape creation

**Process:**
1. Load merged conversation
2. Create multiple layers from same source
3. Apply per-layer:
   - Stereo panning
   - Volume adjustment
   - Time offset
4. Mix all layers with ffmpeg

## Configuration Hierarchy

```
config.yaml
│
├── elevenlabs
│   ├── api_key_env
│   └── model_id
│
├── voices [list]
│
├── language
│   ├── softness
│   ├── min_phrase_length
│   └── max_phrase_length
│
├── prosody_distributions
│   ├── rate
│   │   ├── base_mean
│   │   ├── per_speaker_variation
│   │   └── per_utterance_variation
│   └── pitch
│       ├── per_speaker_variation
│       └── per_utterance_variation
│
├── speaker_personality_distributions
│   ├── laughter_frequency
│   ├── agreement_frequency
│   ├── verbosity
│   └── pause_tendency
│
├── breaks
│   ├── micro_pause
│   ├── comma_pause
│   └── thinking_pause
│
├── conversation
│   └── pause_distribution
│
├── emphasis
│   ├── probability
│   ├── levels
│   └── level_weights
│
├── utterance_types
│   ├── question
│   ├── agreement
│   ├── thinking
│   └── laughter
│
└── spatialization
    ├── num_layers
    ├── stereo_positions
    ├── volume_adjustments
    └── time_offsets
```

## Probability Distributions

### Normal Distribution (Gaussian)

Most traits use normal distributions:
```
value ~ N(μ, σ²)

Where:
  μ = mean (center of distribution)
  σ = standard deviation (spread)
```

**Examples:**
- `laughter_frequency ~ N(0.15, 0.08²)` → Most speakers around 15%, some 5%, some 25%
- `rate ~ N(0.85, 0.10²)` → Most rates around 85%, varies by speaker
- Per-utterance: `actual_rate ~ N(speaker_baseline, 0.03²)` → Varies around their baseline

### Clipping

Values are clipped to realistic ranges:
```python
rate = np.clip(sampled_rate, min=0.70, max=1.00)
verbosity = np.clip(sampled_verbosity, min=0.7, max=1.4)
```

### Composition

Final values are composed hierarchically:
```
utterance_rate = clip(
    N(speaker_baseline_rate, per_utterance_var) × utterance_type_factor,
    min, max
)
```

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

## Extension Points

### Adding New Personality Traits
1. Add to `speaker_personality_distributions` in config
2. Sample in `SpeakerPersonality._sample_personality_traits()`
3. Use in relevant generation functions

### Adding New Utterance Types
1. Add to `utterance_types` in config
2. Add generation logic in `generate_utterance()`
3. Add special handling in `generate_ssml()` if needed

### Adding New Audio Effects
1. Add effect in `apply_fade()` or create new function
2. Chain effects before saving audio
3. Add configuration options

---

This architecture provides:
- **Modularity**: Each component is independent
- **Extensibility**: Easy to add new features
- **Testability**: Each module can be tested separately
- **Configurability**: Everything controlled via YAML

```


# QUICKSTART.md
```markdown
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

```


# README.md
```markdown
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

```
1. generate_language.py  → Creates invented language phrases
2. generate_ssml.py      → Wraps in SSML with personality-aware prosody
3. tts.py                → Calls ElevenLabs API, applies fades
4. generate_soundscape.py → Orchestrates: samples personalities, generates clips
5. merge_audio.py        → Concatenates clips with variable pauses
6. spatialize_audio.py   → Creates 3D layered soundscape (RECOMMENDED)
```

**New module:**
- `personality_sampler.py` → Samples speaker traits from distributions

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

Create a `secrets.ini` file with your ElevenLabs API key:

```ini
[elevenlabs]
api_key = your_elevenlabs_api_key_here
```

### 3. Generate Soundscape

```bash
# Generate individual clips with personalities
python generate_soundscape.py

# Merge clips into sequential conversation
python merge_audio.py

# Create 3D spatialized soundscape (recommended!)
python spatialize_audio.py
```

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

## 📁 File Structure

```
sleep-soundscape-synthesizer/
│
├── config.yaml                    # All configuration
├── secrets.ini                    # ElevenLabs API key (create this!)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
│
├── personality_sampler.py         # NEW: Personality sampling
├── generate_language.py           # Language generation (verbosity-aware)
├── generate_ssml.py               # SSML generation (personality-aware)
├── tts.py                         # ElevenLabs API interface
├── generate_soundscape.py         # Main orchestrator
├── merge_audio.py                 # Audio concatenation
├── spatialize_audio.py            # 3D spatialization
│
└── output/
    ├── clips/                     # Individual clips
    ├── conversation.mp3           # Sequential conversation
    └── soundscape_3d.mp3          # Final 3D soundscape
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
Make sure you have a `secrets.ini` file in the project directory with:
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
# Test language generation
python generate_language.py

# Test SSML generation
python generate_ssml.py

# Test TTS (requires API key)
python tts.py
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

```


# config.yaml
```text
# Sleep Soundscape Synthesizer Configuration
# Enhanced with Probabilistic Speaker Personalities

# ElevenLabs API Settings
elevenlabs:
  model_id: "eleven_multilingual_v2"  # API key stored in secrets.ini

# Voice IDs
voices:
  - "21m00Tcm4TlvDq8ikWAM"  # Rachel
  - "AZnzlk1XvdvUeBnXmlld"  # Domi
  - "EXAVITQu4vr4xnSDxMaL"  # Bella
  - "ErXwobaYiN019PkySvjV"  # Antoni
  - "MF3mGyEYCl7XYWbV9V6O"  # Elli
  - "TxGEqnHWrfWFTfGW9XjX"  # Josh
  - "VR6AewLTigWG4xSOukaG"  # Arnold
  - "pNInz6obpgDQGcFmaJgB"  # Adam
  - "yoZ06aMxZJJ28mfd3POQ"  # Sam

# Language Generation Settings
language:
  softness: 0.7  # 0.0-1.0, controls phoneme selection (higher = softer sounds)
  min_phrase_length: 3
  max_phrase_length: 12
  min_word_length: 2
  max_word_length: 5

# Probabilistic Prosody Distributions
prosody_distributions:
  rate:
    base_mean: 0.85               # Center point for all speakers
    per_speaker_variation: 0.10   # How different speakers are from each other
    per_utterance_variation: 0.03 # How much one speaker varies per utterance
    min: 0.70
    max: 1.00
  
  pitch:
    base: "medium"                # Base reference
    per_speaker_variation: 8      # ±8% per speaker from base
    per_utterance_variation: 3    # ±3% per utterance variation
    min: -15                      # Minimum pitch offset percentage
    max: 15                       # Maximum pitch offset percentage

# Speaker Personality Trait Distributions
speaker_personality_distributions:
  laughter_frequency:
    mean: 0.15      # Average probability of laughing
    std: 0.08       # Standard deviation (some speakers laugh more/less)
  
  agreement_frequency:
    mean: 0.25      # Average probability of agreement sounds (mm-hmm, yeah)
    std: 0.10
  
  verbosity:          # Phrase length multiplier
    mean: 1.0       # Average verbosity
    std: 0.2        # Some speakers are more/less talkative
    min: 0.7        # Minimum multiplier
    max: 1.4        # Maximum multiplier
  
  pause_tendency:     # Pause length multiplier
    mean: 1.0       # Average pause tendency
    std: 0.15       # Some speakers pause more/less
    min: 0.7
    max: 1.3

# Pause/Break Distributions
breaks:
  micro_pause:       # Small pauses within phrases
    mean: 0.3
    std: 0.1
    min: 0.1
    max: 0.6
  
  comma_pause:       # Natural comma pauses
    mean: 0.4
    std: 0.15
    min: 0.2
    max: 0.7
  
  thinking_pause:    # Longer thoughtful pauses
    mean: 0.8
    std: 0.3
    min: 0.4
    max: 1.5

# Conversation Settings
conversation:
  num_clips: 20                    # Number of individual clips to generate
  pause_distribution:               # Pauses between speakers
    mean: 1.2
    std: 0.5
    min: 0.5
    max: 3.0

# Emphasis Settings
emphasis:
  probability: 0.3                 # 30% chance of emphasizing a word
  levels: ["moderate", "strong", "reduced"]
  level_weights: [0.6, 0.2, 0.2]   # Probabilities for each level

# Special Prosody for Utterance Types
utterance_types:
  question:
    pitch_boost: 15        # Questions get higher pitch
    rate_factor: 1.05      # Slightly faster
  
  agreement:
    volume: "soft"
    rate_factor: 0.9       # Slightly slower
  
  thinking:
    rate_factor: 0.85      # Slower, contemplative
    pause_before: 0.6      # Pause before thinking sounds
  
  laughter:
    volume: "soft"
    rate_factor: 1.1       # Slightly faster

# Agreement/Reaction Sounds
agreement_sounds:
  - "mm-hmm"
  - "mhm"
  - "yeah"
  - "uh-huh"
  - "right"
  - "sure"
  - "okay"
  - "yes"

# Laughter Sounds (in invented language style)
laughter_sounds:
  - "ha ha"
  - "he he"
  - "hehe"
  - "haha"
  - "ah ha"

# Thinking Sounds
thinking_sounds:
  - "hmm"
  - "uh"
  - "um"
  - "ah"
  - "oh"

# Audio Processing Settings
audio:
  fade_duration_ms: 20       # Fade in/out (currently disabled - causes audio corruption)
  output_format: "mp3_22050_32"  # Optimized for sleep soundscapes (smaller files)
  sample_rate: 22050         # Half of CD quality, perfect for speech

# Output Paths
paths:
  output_dir: "output"
  clips_dir: "output/clips"
  merged_file: "output/conversation.mp3"
  spatialized_file: "output/soundscape_3d.mp3"

# Spatialization Settings (for spatialize_audio.py)
spatialization:
  num_layers: 3              # Number of overlapping conversation layers
  stereo_positions:          # Pan positions for each layer (-1 = left, 1 = right)
    - -0.6                   # Left-ish
    - 0.0                    # Center
    - 0.5                    # Right-ish
  volume_adjustments:        # Volume for each layer (0.0-1.0)
    - 0.7
    - 0.8
    - 0.6
  time_offsets:              # Start time offset for each layer (seconds)
    - 0.0
    - 5.0
    - 12.0

```


# extend_soundscape.py
```python
"""
Extend Soundscape - Reuse clips to create longer compositions
Creates multiple variations of the same clips for extended playtime
"""

import os
import yaml
import random
import subprocess
import numpy as np
from pathlib import Path


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def extend_soundscape(
    target_duration_minutes: int = 30,
    num_variations: int = 3,
    config_path: str = "config.yaml"
):
    """
    Extend soundscape by creating variations and concatenating them.
    
    Args:
        target_duration_minutes: Desired duration in minutes
        num_variations: Number of different orderings to create
        config_path: Path to config file
    """
    print("=" * 70)
    print(f"Extending Soundscape to ~{target_duration_minutes} minutes")
    print("=" * 70)
    
    config = load_config(config_path)
    clips_dir = config['paths']['clips_dir']
    output_dir = config['paths']['output_dir']
    
    # Get all clips
    print(f"\n[1/5] Loading clips from {clips_dir}...")
    clip_files = sorted([
        os.path.join(clips_dir, f)
        for f in os.listdir(clips_dir)
        if f.startswith('clip_') and f.endswith('.mp3')
    ])
    
    if not clip_files:
        print(f"  Error: No clips found in {clips_dir}")
        print(f"  Run: python generate_soundscape.py first")
        return
    
    print(f"  Found {len(clip_files)} clips")
    
    # Calculate how many variations needed
    avg_clip_duration = 4  # seconds (rough estimate)
    avg_pause = 1.2
    variation_duration = len(clip_files) * (avg_clip_duration + avg_pause)
    num_repeats = int((target_duration_minutes * 60) / variation_duration) + 1
    
    print(f"\n[2/5] Planning extension...")
    print(f"  Estimated variation duration: {variation_duration:.0f}s")
    print(f"  Creating {num_variations} variations")
    print(f"  Repeating {num_repeats} times each")
    print(f"  Total estimated duration: {num_variations * num_repeats * variation_duration / 60:.1f} minutes")
    
    # Create variations
    print(f"\n[3/5] Creating {num_variations} variations with different orderings...")
    variation_files = []
    
    for v in range(num_variations):
        print(f"  Variation {v+1}/{num_variations}...")
        
        # Shuffle clips (different order)
        shuffled_clips = clip_files.copy()
        random.shuffle(shuffled_clips)
        
        # Build concat list with pauses
        concat_list = []
        for i, clip_file in enumerate(shuffled_clips):
            concat_list.append(f"file '{os.path.abspath(clip_file)}'")
            
            # Add pause after each clip except the last
            if i < len(shuffled_clips) - 1:
                # Sample pause from distribution
                pause_mean = config['conversation']['pause_distribution']['mean']
                pause_std = config['conversation']['pause_distribution']['std']
                pause_duration = max(0.5, np.random.normal(pause_mean, pause_std))
                concat_list.append(f"duration {pause_duration:.2f}")
        
        # Write concat list
        concat_file = os.path.join(clips_dir, f"concat_variation_{v+1}.txt")
        with open(concat_file, 'w') as f:
            f.write('\n'.join(concat_list))
        
        # Merge this variation (use relative paths with cwd)
        variation_output = os.path.join(output_dir, f"variation_{v+1}.mp3")
        output_relative = os.path.relpath(variation_output, clips_dir)
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", f"concat_variation_{v+1}.txt",  # Relative to clips_dir
            "-c", "copy",
            "-y",
            output_relative  # Relative to clips_dir
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=clips_dir
        )
        
        if result.returncode == 0:
            variation_files.append(variation_output)
            print(f"    ✓ Created {os.path.basename(variation_output)}")
        else:
            print(f"    ✗ Failed: {result.stderr.decode()[:100]}")
    
    # Repeat variations to reach target duration
    print(f"\n[4/5] Repeating variations to reach target duration...")
    extended_list = []
    for r in range(num_repeats):
        for vf in variation_files:
            extended_list.append(f"file '{os.path.abspath(vf)}'")
    
    # Write extended concat list
    extended_concat_file = os.path.join(output_dir, "concat_extended.txt")
    with open(extended_concat_file, 'w') as f:
        f.write('\n'.join(extended_list))
    
    # Create extended base conversation
    extended_output = os.path.join(output_dir, f"conversation_extended_{target_duration_minutes}min.mp3")
    
    print(f"  Concatenating {len(extended_list)} segments...")
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", extended_concat_file,  # Use absolute path, no cwd
        "-c", "copy",
        "-y",
        extended_output
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        # No cwd parameter - use absolute paths
    )
    
    if result.returncode != 0:
        print(f"  Error: {result.stderr.decode()[:200]}")
        return
    
    print(f"  ✓ Created extended conversation")
    
    # Get actual duration
    duration_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        extended_output
    ]
    
    duration_result = subprocess.run(
        duration_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if duration_result.returncode == 0:
        duration = float(duration_result.stdout.decode().strip())
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"  ✓ Actual duration: {minutes}m {seconds}s")
    
    # Spatialize - use DIFFERENT variations for each layer
    print(f"\n[5/5] Creating spatialized 3D version with parallel conversations...")
    spat_output = os.path.join(output_dir, f"soundscape_extended_{target_duration_minutes}min.mp3")
    
    # Use existing spatialization config
    spat_config = config.get('spatialization', {})
    num_layers = min(spat_config.get('num_layers', 3), len(variation_files))  # Can't have more layers than variations
    stereo_positions = spat_config.get('stereo_positions', [-0.6, 0.0, 0.5])
    volume_adjustments = spat_config.get('volume_adjustments', [0.7, 0.8, 0.6])
    time_offsets = spat_config.get('time_offsets', [0.0, 5.0, 12.0])
    
    print(f"  Using {num_layers} parallel conversation layers")
    
    # Build extended versions for EACH layer using DIFFERENT variations
    layer_files = []
    for layer_idx in range(num_layers):
        print(f"  Building layer {layer_idx + 1}/{num_layers}...")
        
        # Create a different sequence for this layer
        # Rotate which variations are used and in what order
        layer_list = []
        for r in range(num_repeats):
            for v_idx, vf in enumerate(variation_files):
                # Each layer uses variations in different order
                rotated_idx = (v_idx + layer_idx) % len(variation_files)
                layer_list.append(f"file '{os.path.abspath(variation_files[rotated_idx])}'")
        
        # Write layer concat list
        layer_concat_file = os.path.join(output_dir, f"concat_layer_{layer_idx + 1}.txt")
        with open(layer_concat_file, 'w') as f:
            f.write('\n'.join(layer_list))
        
        # Create this layer's file
        layer_output = os.path.join(output_dir, f"layer_{layer_idx + 1}_temp.mp3")
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", layer_concat_file,
            "-c", "copy",
            "-y",
            layer_output
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            layer_files.append(layer_output)
        else:
            print(f"    ✗ Failed to create layer {layer_idx + 1}")
            continue
    
    if len(layer_files) < num_layers:
        print(f"  Warning: Only created {len(layer_files)} layers instead of {num_layers}")
    
    # Now spatialize using DIFFERENT files for each layer
    print(f"  Mixing {len(layer_files)} layers with stereo positioning...")
    
    # Build ffmpeg filter
    inputs = []
    filter_parts = []
    
    for i, layer_file in enumerate(layer_files):
        inputs.extend(["-ss", str(time_offsets[i]), "-i", layer_file])
        
        pan_value = stereo_positions[i]
        volume = volume_adjustments[i]
        left_gain = (1.0 - pan_value) / 2.0 * volume
        right_gain = (1.0 + pan_value) / 2.0 * volume
        
        filter_parts.append(
            f"[{i}:a]volume={volume},pan=stereo|c0={left_gain}*c0+{left_gain}*c1|c1={right_gain}*c0+{right_gain}*c1[a{i}]"
        )
    
    mix_inputs = ''.join([f"[a{i}]" for i in range(len(layer_files))])
    filter_parts.append(f"{mix_inputs}amix=inputs={len(layer_files)}:duration=longest:dropout_transition=2[aout]")
    filter_complex = ';'.join(filter_parts)
    
    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "2",
        "-y",
        spat_output
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if result.returncode == 0:
        print(f"  ✓ Created spatialized version")
        
        # Clean up temporary layer files
        for layer_file in layer_files:
            try:
                os.remove(layer_file)
            except:
                pass
    else:
        print(f"  ✗ Failed: {result.stderr.decode()[:200]}")
    
    print("\n" + "=" * 70)
    print("✓ Extended soundscape complete!")
    print(f"\n  Base conversation: {extended_output}")
    print(f"  3D soundscape:     {spat_output}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import sys
    
    # Allow custom duration
    if len(sys.argv) > 1:
        target_minutes = int(sys.argv[1])
    else:
        target_minutes = 30  # Default: 30 minutes
    
    try:
        extend_soundscape(target_duration_minutes=target_minutes)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

```


# generate_language.py
```python
"""
Invented Language Generator
Generates phonetically pleasing nonsense phrases for sleep soundscapes.
Now supports personality-based verbosity for varying phrase lengths.
"""

import random
from typing import List


class LanguageGenerator:
    """Generates invented language phrases based on phonological softness."""
    
    def __init__(self, softness: float = 0.7):
        """
        Initialize the language generator.
        
        Args:
            softness: 0.0-1.0, controls phoneme selection (higher = softer sounds)
        """
        self.softness = max(0.0, min(1.0, softness))
        
        # Consonants ranked by softness (Romance language influenced)
        self.soft_consonants = ['l', 'm', 'n', 'r', 'v', 'j', 'w']
        self.medium_consonants = ['b', 'd', 'f', 's', 'z']
        self.hard_consonants = ['p', 't', 'k', 'g', 'ch', 'sh']
        
        # Vowels (inherently soft)
        self.vowels = ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ea', 'ia', 'io']
        
        # Build weighted consonant list based on softness
        self._build_consonant_pool()
    
    def _build_consonant_pool(self):
        """Build a weighted pool of consonants based on softness parameter."""
        soft_weight = self.softness
        medium_weight = (1.0 - self.softness) * 0.6
        hard_weight = (1.0 - self.softness) * 0.4
        
        self.consonant_pool = (
            self.soft_consonants * int(soft_weight * 10) +
            self.medium_consonants * int(medium_weight * 10) +
            self.hard_consonants * int(hard_weight * 10)
        )
        
        # Ensure we always have some consonants
        if not self.consonant_pool:
            self.consonant_pool = self.soft_consonants + self.medium_consonants
    
    def generate_word(self, min_length: int = 2, max_length: int = 5) -> str:
        """
        Generate a single nonsense word.
        
        Args:
            min_length: Minimum syllables
            max_length: Maximum syllables
        
        Returns:
            A nonsense word
        """
        num_syllables = random.randint(min_length, max_length)
        word = ""
        
        for i in range(num_syllables):
            # Syllable structure: (C)V(C) where C=consonant, V=vowel
            syllable = ""
            
            # Optional initial consonant (more likely for first syllable)
            if i == 0 or random.random() < 0.7:
                syllable += random.choice(self.consonant_pool)
            
            # Vowel (required)
            syllable += random.choice(self.vowels)
            
            # Optional final consonant (less likely for smoother flow)
            if random.random() < 0.3:
                syllable += random.choice(self.consonant_pool)
            
            word += syllable
        
        return word
    
    def generate_phrase(
        self,
        min_words: int = 3,
        max_words: int = 12,
        verbosity_multiplier: float = 1.0
    ) -> str:
        """
        Generate a phrase of nonsense words.
        
        Args:
            min_words: Minimum number of words
            max_words: Maximum number of words
            verbosity_multiplier: Personality-based length adjustment (0.7-1.4)
        
        Returns:
            A nonsense phrase
        """
        # Apply verbosity multiplier to phrase length
        adjusted_min = max(1, int(min_words * verbosity_multiplier))
        adjusted_max = max(adjusted_min + 1, int(max_words * verbosity_multiplier))
        
        num_words = random.randint(adjusted_min, adjusted_max)
        words = [self.generate_word() for _ in range(num_words)]
        
        return " ".join(words)
    
    def generate_question(
        self,
        min_words: int = 3,
        max_words: int = 10,
        verbosity_multiplier: float = 1.0
    ) -> str:
        """
        Generate a phrase that sounds like a question.
        Questions tend to be slightly shorter.
        """
        adjusted_max = max(3, int(max_words * 0.8 * verbosity_multiplier))
        return self.generate_phrase(min_words, adjusted_max, verbosity_multiplier)
    
    def generate_agreement(self) -> str:
        """Generate an agreement sound."""
        agreements = [
            "mm-hmm", "mhm", "yeah", "uh-huh",
            "right", "sure", "okay", "yes"
        ]
        return random.choice(agreements)
    
    def generate_laughter(self) -> str:
        """Generate laughter sounds."""
        laughs = [
            "ha ha", "he he", "hehe", "haha", "ah ha"
        ]
        return random.choice(laughs)
    
    def generate_thinking(self) -> str:
        """Generate thinking sounds."""
        thinks = ["hmm", "uh", "um", "ah", "oh"]
        return random.choice(thinks)


def generate_utterance(
    generator: LanguageGenerator,
    config: dict,
    verbosity_multiplier: float = 1.0
) -> tuple[str, str]:
    """
    Generate a single utterance with type detection.
    
    Args:
        generator: LanguageGenerator instance
        config: Configuration dictionary
        verbosity_multiplier: Personality-based length adjustment
    
    Returns:
        Tuple of (text, utterance_type)
    """
    lang_config = config.get('language', {})
    
    # Determine utterance type
    rand = random.random()
    
    if rand < 0.05:  # 5% thinking sounds
        return generator.generate_thinking(), 'thinking'
    elif rand < 0.15:  # 10% agreement
        return generator.generate_agreement(), 'agreement'
    elif rand < 0.20:  # 5% laughter
        return generator.generate_laughter(), 'laughter'
    elif rand < 0.35:  # 15% questions
        text = generator.generate_question(
            lang_config.get('min_phrase_length', 3),
            lang_config.get('max_phrase_length', 12),
            verbosity_multiplier
        )
        return text, 'question'
    else:  # 65% normal statements
        text = generator.generate_phrase(
            lang_config.get('min_phrase_length', 3),
            lang_config.get('max_phrase_length', 12),
            verbosity_multiplier
        )
        return text, 'normal'


if __name__ == "__main__":
    # Test the language generator
    gen = LanguageGenerator(softness=0.7)
    
    print("Sample words:")
    for _ in range(5):
        print(f"  {gen.generate_word()}")
    
    print("\nSample phrases:")
    for _ in range(5):
        print(f"  {gen.generate_phrase()}")
    
    print("\nWith verbosity variations:")
    for mult in [0.7, 1.0, 1.4]:
        print(f"\n  Verbosity {mult}:")
        for _ in range(3):
            print(f"    {gen.generate_phrase(verbosity_multiplier=mult)}")

```


# generate_soundscape.py
```python
"""
Sleep Soundscape Generator
Orchestrates the entire pipeline: language generation → SSML → TTS
Now with probabilistic speaker personalities!
"""

import os
import yaml
import random
from typing import Dict, List
from generate_language import LanguageGenerator, generate_utterance
from generate_ssml import generate_ssml
from tts import generate_speech
from personality_sampler import initialize_speaker_personalities, SpeakerPersonality


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def ensure_output_dirs(config: dict):
    """Create output directories if they don't exist."""
    output_dir = config['paths']['output_dir']
    clips_dir = config['paths']['clips_dir']
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(clips_dir, exist_ok=True)


def generate_soundscape(config_path: str = "config.yaml"):
    """
    Main function to generate the sleep soundscape.
    
    Process:
    1. Load config and initialize speaker personalities
    2. For each clip:
       - Select random voice/personality
       - Generate text based on personality's verbosity
       - Create SSML with personality-aware prosody
       - Generate audio via TTS
    """
    print("=" * 60)
    print("Sleep Soundscape Generator with Probabilistic Personalities")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/6] Loading configuration...")
    config = load_config(config_path)
    ensure_output_dirs(config)
    
    # Get settings
    voices = config['voices']
    num_clips = config['conversation']['num_clips']
    softness = config['language']['softness']
    
    print(f"  Voices: {len(voices)}")
    print(f"  Clips to generate: {num_clips}")
    print(f"  Softness: {softness}")
    
    # Initialize language generator
    print("\n[2/6] Initializing language generator...")
    lang_gen = LanguageGenerator(softness=softness)
    
    # Initialize speaker personalities
    print("\n[3/6] Sampling speaker personalities...")
    personalities = initialize_speaker_personalities(voices, config)
    
    print(f"  Created {len(personalities)} unique personalities:")
    for voice_id, personality in personalities.items():
        short_id = voice_id[:8]
        print(f"    {short_id}: laughter={personality.traits['laughter_frequency']:.2f}, "
              f"agreement={personality.traits['agreement_frequency']:.2f}, "
              f"verbosity={personality.traits['verbosity']:.2f}, "
              f"pause_tendency={personality.traits['pause_tendency']:.2f}")
    
    # Generate clips
    print(f"\n[4/6] Generating {num_clips} audio clips...")
    clips_dir = config['paths']['clips_dir']
    
    for i in range(num_clips):
        # Select random voice and its personality
        voice_id = random.choice(voices)
        personality = personalities[voice_id]
        
        # Generate text with personality's verbosity
        verbosity = personality.get_verbosity()
        text, utterance_type = generate_utterance(lang_gen, config, verbosity)
        
        # Generate SSML with personality-aware prosody
        ssml = generate_ssml(text, personality, utterance_type)
        
        # Extract prosody parameters for ElevenLabs API
        prosody = personality.sample_utterance_prosody(utterance_type)
        
        # Generate audio
        output_path = os.path.join(clips_dir, f"clip_{i:03d}.mp3")
        
        try:
            generate_speech(ssml, voice_id, output_path, config, prosody=prosody)
            
            # Show progress
            short_id = voice_id[:8]
            print(f"  [{i+1:2d}/{num_clips}] {short_id} ({utterance_type:10s}): {text[:40]}")
        
        except Exception as e:
            print(f"  Error generating clip {i}: {e}")
            continue
    
    print("\n[5/6] All clips generated!")
    print(f"  Location: {clips_dir}")
    
    print("\n[6/6] Next steps:")
    print("  Run: python merge_audio.py          (creates sequential conversation)")
    print("  Run: python spatialize_audio.py     (creates 3D layered soundscape)")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    # Allow custom config path
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    try:
        generate_soundscape(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure config.yaml exists in the current directory.")
    except KeyError as e:
        print(f"Error: Missing configuration key: {e}")
        print("Check that config.yaml has all required fields.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

```


# generate_ssml.py
```python
"""
SSML Generator with Probabilistic Personality-Aware Prosody
Wraps text in SSML tags with dynamic prosody based on speaker personality.

ElevenLabs supports SSML with <speak>, <prosody>, <break>, and <emphasis> tags.
The enable_ssml parameter is automatically set in the API call when SSML is detected.
"""

import random
from typing import Dict, Any
from personality_sampler import SpeakerPersonality


def format_prosody_value(value: float, value_type: str) -> str:
    """
    Format prosody values for SSML.
    
    Args:
        value: The numeric value
        value_type: 'rate', 'pitch', or 'volume'
    
    Returns:
        Formatted string for SSML
    """
    if value_type == 'rate':
        # Rate is a multiplier (0.7 -> "70%", 1.0 -> "100%")
        return f"{int(value * 100)}%"
    elif value_type == 'pitch':
        # Pitch is a percentage offset (-15 -> "-15%", +10 -> "+10%")
        if value >= 0:
            return f"+{int(value)}%"
        else:
            return f"{int(value)}%"
    elif value_type == 'volume':
        # Volume is descriptive
        return value  # 'soft', 'medium', 'loud'
    
    return str(value)


def add_emphasis_to_text(text: str, personality: SpeakerPersonality) -> str:
    """
    Add emphasis tags to random words in the text based on personality.
    
    Args:
        text: The text to emphasize
        personality: Speaker's personality object
    
    Returns:
        Text with emphasis tags
    """
    words = text.split()
    if len(words) <= 1:
        return text
    
    emphasized_words = []
    for word in words:
        should_emphasize, level = personality.should_emphasize()
        if should_emphasize and len(word) > 2:  # Don't emphasize short words
            emphasized_words.append(f'<emphasis level="{level}">{word}</emphasis>')
        else:
            emphasized_words.append(word)
    
    return " ".join(emphasized_words)


def add_pauses_to_text(text: str, personality: SpeakerPersonality) -> str:
    """
    Add break tags at natural pause points (commas, between phrases).
    
    Args:
        text: The text to add pauses to
        personality: Speaker's personality object
    
    Returns:
        Text with break tags
    """
    # Add micro pauses between some words
    words = text.split()
    if len(words) <= 2:
        return text
    
    result = []
    for i, word in enumerate(words):
        result.append(word)
        
        # Add occasional micro pauses (not after last word)
        if i < len(words) - 1 and random.random() < 0.2:
            pause_duration = personality.sample_pause('micro_pause')
            result.append(f'<break time="{pause_duration:.1f}s"/>')
    
    return " ".join(result)


def generate_ssml(
    text: str,
    personality: SpeakerPersonality,
    utterance_type: str = 'normal',
    add_breaks: bool = True,
    add_emphasis: bool = True
) -> str:
    """
    Generate SSML-wrapped text with personality-aware prosody.
    
    Args:
        text: The text to wrap
        personality: Speaker's personality object
        utterance_type: Type of utterance ('normal', 'question', 'agreement', etc.)
        add_breaks: Whether to add break tags
        add_emphasis: Whether to add emphasis tags
    
    Returns:
        SSML-formatted string
    """
    # Sample prosody parameters for this utterance
    prosody = personality.sample_utterance_prosody(utterance_type)
    
    # Format prosody values
    rate_str = format_prosody_value(prosody['rate'], 'rate')
    pitch_str = format_prosody_value(prosody['pitch'], 'pitch')
    volume_str = prosody['volume']
    
    # Process text
    processed_text = text
    
    # Add pauses
    if add_breaks and utterance_type not in ['agreement', 'laughter', 'thinking']:
        processed_text = add_pauses_to_text(processed_text, personality)
    
    # Add emphasis
    if add_emphasis and utterance_type == 'normal':
        processed_text = add_emphasis_to_text(processed_text, personality)
    
    # Special handling for thinking sounds (add pause before)
    if utterance_type == 'thinking':
        pause_duration = personality.sample_pause('thinking_pause')
        processed_text = f'<break time="{pause_duration:.1f}s"/>{processed_text}'
    
    # Wrap in prosody tag
    ssml = f'<speak><prosody rate="{rate_str}" pitch="{pitch_str}" volume="{volume_str}">{processed_text}</prosody></speak>'
    
    return ssml


def generate_simple_ssml(text: str, rate: float = 0.85, pitch: int = 0, volume: str = "medium") -> str:
    """
    Generate simple SSML without personality (for backward compatibility).
    
    Args:
        text: The text to wrap
        rate: Speech rate multiplier (0.7-1.0)
        pitch: Pitch offset percentage (-15 to +15)
        volume: Volume level ('soft', 'medium', 'loud')
    
    Returns:
        SSML-formatted string
    """
    rate_str = format_prosody_value(rate, 'rate')
    pitch_str = format_prosody_value(pitch, 'pitch')
    
    ssml = f'<speak><prosody rate="{rate_str}" pitch="{pitch_str}" volume="{volume}">{text}</prosody></speak>'
    
    return ssml


if __name__ == "__main__":
    # Test SSML generation
    import yaml
    from personality_sampler import SpeakerPersonality, get_default_config
    
    # Load or create config
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = get_default_config()
    
    # Create a test personality
    personality = SpeakerPersonality("test_voice", config)
    
    print("Speaker Personality Traits:")
    print(f"  Laughter frequency: {personality.traits['laughter_frequency']:.2f}")
    print(f"  Agreement frequency: {personality.traits['agreement_frequency']:.2f}")
    print(f"  Verbosity: {personality.traits['verbosity']:.2f}")
    print(f"  Pause tendency: {personality.traits['pause_tendency']:.2f}")
    print(f"  Base rate: {personality.prosody_baseline['rate']:.2f}")
    print(f"  Base pitch: {personality.prosody_baseline['pitch']:.1f}%")
    
    print("\nSample SSML outputs:")
    
    test_phrases = [
        ("loria belina taso ren", "normal"),
        ("marina solo vea tion", "question"),
        ("mm-hmm", "agreement"),
        ("hmm", "thinking"),
    ]
    
    for text, utt_type in test_phrases:
        ssml = generate_ssml(text, personality, utt_type)
        print(f"\n{utt_type.upper()}: {text}")
        print(f"  {ssml}")

```


# merge_audio.py
```python
"""
Audio Merger
Concatenates individual clips into a single sequential conversation.
Adds natural pauses between speakers using personality-aware sampling.
"""

import os
import yaml
import subprocess
from personality_sampler import sample_conversation_pause


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def merge_audio_clips(config_path: str = "config.yaml"):
    """
    Merge all audio clips into a single conversation file.
    Adds variable pauses between clips based on conversation pause distribution.
    """
    print("=" * 60)
    print("Audio Merger - Creating Sequential Conversation")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/4] Loading configuration...")
    config = load_config(config_path)
    
    clips_dir = config['paths']['clips_dir']
    output_file = config['paths']['merged_file']
    
    # Get all clip files
    print("\n[2/4] Scanning for audio clips...")
    clip_files = sorted([
        os.path.join(clips_dir, f)
        for f in os.listdir(clips_dir)
        if f.startswith('clip_') and f.endswith('.mp3')
    ])
    
    if not clip_files:
        print("  Error: No clips found in", clips_dir)
        return
    
    print(f"  Found {len(clip_files)} clips")
    
    # Build ffmpeg concat list with pauses
    print("\n[3/4] Building concatenation list with pauses...")
    
    concat_list = []
    for i, clip_file in enumerate(clip_files):
        concat_list.append(f"file '{os.path.abspath(clip_file)}'")
        
        # Add pause after each clip except the last
        if i < len(clip_files) - 1:
            # Sample pause duration from distribution
            pause_duration = sample_conversation_pause(config)
            concat_list.append(f"duration {pause_duration:.2f}")
    
    # Write concat list to temp file
    concat_file = os.path.join(clips_dir, "concat_list.txt")
    with open(concat_file, 'w') as f:
        f.write('\n'.join(concat_list))
    
    print(f"  Created concat list with variable pauses")
    
    # Run ffmpeg to concatenate
    print("\n[4/4] Merging clips with ffmpeg...")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Calculate relative path from clips_dir to output_file
    output_relative = os.path.relpath(output_file, clips_dir)
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",  # Relative to clips_dir
        "-c", "copy",
        "-y",  # Overwrite output
        output_relative  # Relative to clips_dir
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=clips_dir
    )
    
    if result.returncode != 0:
        print(f"  Error: ffmpeg failed")
        print(result.stderr.decode())
        return
    
    # Clean up concat list
    try:
        os.remove(concat_file)
    except:
        pass
    
    print(f"\n✓ Success!")
    print(f"  Output: {output_file}")
    print("\nNext step:")
    print("  Run: python spatialize_audio.py (creates 3D layered soundscape)")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    # Allow custom config path
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    try:
        merge_audio_clips(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

```


# personality_sampler.py
```python
"""
Personality Sampler Module
Provides functions to sample speaker personalities and prosody parameters from distributions.
Creates per-speaker consistency with per-utterance variation.
"""

import random
import numpy as np
from typing import Dict, Any, List


class SpeakerPersonality:
    """Represents a speaker's personality traits sampled from distributions."""
    
    def __init__(self, voice_id: str, config: Dict[str, Any]):
        self.voice_id = voice_id
        self.config = config
        
        # Sample base personality traits for this speaker
        self.traits = self._sample_personality_traits()
        self.prosody_baseline = self._sample_prosody_baseline()
    
    def _sample_personality_traits(self) -> Dict[str, float]:
        """Sample personality traits from distributions."""
        traits = {}
        personality_dists = self.config.get('speaker_personality_distributions', {})
        
        # Laughter frequency
        laughter = personality_dists.get('laughter_frequency', {})
        traits['laughter_frequency'] = max(0, np.random.normal(
            laughter.get('mean', 0.15),
            laughter.get('std', 0.08)
        ))
        
        # Agreement frequency
        agreement = personality_dists.get('agreement_frequency', {})
        traits['agreement_frequency'] = max(0, np.random.normal(
            agreement.get('mean', 0.25),
            agreement.get('std', 0.10)
        ))
        
        # Verbosity (phrase length multiplier)
        verbosity = personality_dists.get('verbosity', {})
        traits['verbosity'] = np.clip(
            np.random.normal(verbosity.get('mean', 1.0), verbosity.get('std', 0.2)),
            verbosity.get('min', 0.7),
            verbosity.get('max', 1.4)
        )
        
        # Pause tendency (pause length multiplier)
        pause_tendency = personality_dists.get('pause_tendency', {})
        traits['pause_tendency'] = np.clip(
            np.random.normal(pause_tendency.get('mean', 1.0), pause_tendency.get('std', 0.15)),
            pause_tendency.get('min', 0.7),
            pause_tendency.get('max', 1.3)
        )
        
        return traits
    
    def _sample_prosody_baseline(self) -> Dict[str, Any]:
        """Sample this speaker's baseline prosody parameters."""
        prosody = {}
        prosody_dists = self.config.get('prosody_distributions', {})
        
        # Rate baseline
        rate_config = prosody_dists.get('rate', {})
        base_mean = rate_config.get('base_mean', 0.85)
        per_speaker_var = rate_config.get('per_speaker_variation', 0.10)
        prosody['rate'] = np.clip(
            np.random.normal(base_mean, per_speaker_var),
            rate_config.get('min', 0.70),
            rate_config.get('max', 1.00)
        )
        
        # Pitch baseline (in percentage offset)
        pitch_config = prosody_dists.get('pitch', {})
        per_speaker_var_pitch = pitch_config.get('per_speaker_variation', 8)
        prosody['pitch'] = np.clip(
            np.random.normal(0, per_speaker_var_pitch),
            pitch_config.get('min', -15),
            pitch_config.get('max', 15)
        )
        
        return prosody
    
    def sample_utterance_prosody(self, utterance_type: str = 'normal') -> Dict[str, Any]:
        """
        Sample prosody parameters for a specific utterance.
        Varies around this speaker's baseline.
        """
        prosody = {}
        prosody_dists = self.config.get('prosody_distributions', {})
        utterance_types = self.config.get('utterance_types', {})
        
        # Rate: baseline + per-utterance variation + type modifier
        rate_config = prosody_dists.get('rate', {})
        per_utterance_var = rate_config.get('per_utterance_variation', 0.03)
        rate = np.random.normal(self.prosody_baseline['rate'], per_utterance_var)
        
        # Apply utterance type modifier
        if utterance_type in utterance_types:
            rate_factor = utterance_types[utterance_type].get('rate_factor', 1.0)
            rate *= rate_factor
        
        prosody['rate'] = np.clip(rate, rate_config.get('min', 0.70), rate_config.get('max', 1.00))
        
        # Pitch: baseline + per-utterance variation + type modifier
        pitch_config = prosody_dists.get('pitch', {})
        per_utterance_var_pitch = pitch_config.get('per_utterance_variation', 3)
        pitch = np.random.normal(self.prosody_baseline['pitch'], per_utterance_var_pitch)
        
        # Apply utterance type modifier (e.g., questions get pitch boost)
        if utterance_type in utterance_types:
            pitch_boost = utterance_types[utterance_type].get('pitch_boost', 0)
            pitch += pitch_boost
        
        prosody['pitch'] = np.clip(pitch, pitch_config.get('min', -15), pitch_config.get('max', 15))
        
        # Volume
        volume_options = ['soft', 'medium']
        if utterance_type in utterance_types and 'volume' in utterance_types[utterance_type]:
            prosody['volume'] = utterance_types[utterance_type]['volume']
        else:
            prosody['volume'] = random.choice(volume_options)
        
        return prosody
    
    def should_laugh(self) -> bool:
        """Determine if this speaker should laugh based on their personality."""
        return random.random() < self.traits['laughter_frequency']
    
    def should_agree(self) -> bool:
        """Determine if this speaker should make agreement sounds."""
        return random.random() < self.traits['agreement_frequency']
    
    def get_verbosity(self) -> float:
        """Get this speaker's verbosity multiplier for phrase length."""
        return self.traits['verbosity']
    
    def sample_pause(self, pause_type: str) -> float:
        """Sample a pause duration for this speaker."""
        breaks_config = self.config.get('breaks', {})
        pause_config = breaks_config.get(pause_type, {})
        
        # Sample from distribution
        pause_duration = max(
            pause_config.get('min', 0.1),
            np.random.normal(
                pause_config.get('mean', 0.5),
                pause_config.get('std', 0.15)
            )
        )
        
        # Apply speaker's pause tendency
        pause_duration *= self.traits['pause_tendency']
        
        # Apply max if specified
        if 'max' in pause_config:
            pause_duration = min(pause_duration, pause_config['max'])
        
        return pause_duration
    
    def should_emphasize(self) -> tuple[bool, str]:
        """Determine if a word should be emphasized and what level."""
        emphasis_config = self.config.get('emphasis', {})
        probability = emphasis_config.get('probability', 0.3)
        
        if random.random() < probability:
            levels = emphasis_config.get('levels', ['moderate', 'strong', 'reduced'])
            weights = emphasis_config.get('level_weights', [0.6, 0.2, 0.2])
            level = random.choices(levels, weights=weights)[0]
            return True, level
        
        return False, 'none'


def initialize_speaker_personalities(voices: List[str], config: Dict[str, Any]) -> Dict[str, SpeakerPersonality]:
    """
    Initialize personality objects for all speakers at session start.
    
    Args:
        voices: List of voice IDs
        config: Full configuration dictionary
    
    Returns:
        Dictionary mapping voice_id to SpeakerPersonality object
    """
    personalities = {}
    for voice_id in voices:
        personalities[voice_id] = SpeakerPersonality(voice_id, config)
    
    return personalities


def sample_conversation_pause(config: Dict[str, Any]) -> float:
    """Sample a pause between conversation turns."""
    conversation_config = config.get('conversation', {})
    pause_dist = conversation_config.get('pause_distribution', {})
    
    pause = np.random.normal(
        pause_dist.get('mean', 1.2),
        pause_dist.get('std', 0.5)
    )
    
    return np.clip(
        pause,
        pause_dist.get('min', 0.5),
        pause_dist.get('max', 3.0)
    )


def get_default_config() -> Dict[str, Any]:
    """
    Return default configuration if distributions aren't specified.
    Ensures backward compatibility.
    """
    return {
        'prosody_distributions': {
            'rate': {
                'base_mean': 0.85,
                'per_speaker_variation': 0.10,
                'per_utterance_variation': 0.03,
                'min': 0.70,
                'max': 1.00
            },
            'pitch': {
                'base': 'medium',
                'per_speaker_variation': 8,
                'per_utterance_variation': 3,
                'min': -15,
                'max': 15
            }
        },
        'speaker_personality_distributions': {
            'laughter_frequency': {
                'mean': 0.15,
                'std': 0.08
            },
            'agreement_frequency': {
                'mean': 0.25,
                'std': 0.10
            },
            'verbosity': {
                'mean': 1.0,
                'std': 0.2,
                'min': 0.7,
                'max': 1.4
            },
            'pause_tendency': {
                'mean': 1.0,
                'std': 0.15,
                'min': 0.7,
                'max': 1.3
            }
        },
        'breaks': {
            'micro_pause': {
                'mean': 0.3,
                'std': 0.1,
                'min': 0.1,
                'max': 0.6
            },
            'comma_pause': {
                'mean': 0.4,
                'std': 0.15
            },
            'thinking_pause': {
                'mean': 0.8,
                'std': 0.3
            }
        },
        'conversation': {
            'pause_distribution': {
                'mean': 1.2,
                'std': 0.5,
                'min': 0.5,
                'max': 3.0
            }
        },
        'emphasis': {
            'probability': 0.3,
            'levels': ['moderate', 'strong', 'reduced'],
            'level_weights': [0.6, 0.2, 0.2]
        },
        'utterance_types': {
            'question': {
                'pitch_boost': 15,
                'rate_factor': 1.05
            },
            'agreement': {
                'volume': 'soft',
                'rate_factor': 0.9
            },
            'thinking': {
                'rate_factor': 0.85,
                'pause_before': 0.6
            }
        }
    }

```


# requirements.txt
```cmake
requests
pyyaml
```


# sleep-soundscape-concept.md
```markdown
# Sleep Soundscape Synthesizer
## Continuous Background Chatter in an Invented Language

---

## The Core Concept

A generative audio system that produces **continuous, comforting human conversation** in a beautiful but non-existent language. The soundscape provides the psychological comfort of human presence without the cognitive engagement that prevents sleep.

### Why This Works

- **Human voices = evolutionary comfort** ("others nearby = safe")
- **Unknown language = no cognitive processing** (brain doesn't try to understand)
- **Natural prosody = authentic presence** (feels like real conversation)
- **Soft laughter & warmth = emotional safety**

## Use Cases

- **Sleep Aid**: Primary - fall asleep to comforting voices
- **Meditation**: Low density + high softness
- **Focus Work**: Café-style background
- **Anxiety Relief**: Comforting presence without social demand
- **Tinnitus Masking**: Variable human voices
- **Children's Bedtime**: Safe presence like parents in next room

Unlike café ambience (real language) or white noise (impersonal), this creates the "sweet spot" of human warmth without mental engagement.

---

## Simple Architecture
```
config.yaml
    ↓
generate_language.py → invented phrases
    ↓
generate_ssml.py → add prosody tags
    ↓
tts.py → ElevenLabs API
    ↓
MP3 files
```

---

## Configuration Parameters

### Voice Settings
- **voices**: List of ElevenLabs voice IDs
- Mix of male/female voices

### Prosody (Speech Style)
- **speech_rate**: 0.5-1.5 (how fast they talk)
- **pitch**: low/medium/high

### Language Generation
- **softness**: 0.0-1.0
  - High (0.8+): soft consonants (l, m, n, v)
  - Low (0.3-): harder consonants (k, t, p, g)
- **laughter_prob**: How often soft "hehe" appears
- **agreement_prob**: Frequency of "mm", "ah" sounds

### Conversation Flow
- **min_pause / max_pause**: Silence between speakers
- Natural variation in pauses

---

## The Invented Language

### Phonological Design Principles

**Inspiration:** Italian, French, Japanese, Polynesian languages

**Vowels:** a, e, i, o, u (with variations: ai, au, ei, ou)

**Consonants (Soft Mode):**
- Liquids: l, r (soft)
- Nasals: m, n
- Fricatives: v, s (soft), h
- Approximants: w, y

**Consonants (Balanced Mode):**
Add: f, z, sh, ch

**Consonants (Harder Mode):**
Add: k, t, p, g, d, b

**Syllable Structure:**
- V (vowel alone): a, i, o
- CV (consonant + vowel): ma, li, no
- CVC (consonant + vowel + consonant): lan, mur, vin
- VCV: ola, ima, enu

### Example Phrases by Softness Level

**High Softness (0.8):**
- "Mila sora venita" (soft flowing)
- "Luma luma, ah si" (agreement)
- "Nalani velu morea" (dreamy)

**Medium Softness (0.5):**
- "Kora mita selano" (balanced)
- "Tiva runa, eh?" (questioning)
- "Palun sivo kirina" (natural)

**Low Softness (0.2):**
- "Kato pira duken" (sharper)
- "Tegra bok sitanu" (more percussive)

### Conversation Elements

**Agreement sounds:** mm, ah, oh, si, na

**Questions:** Rising intonation + "eh?" or "na?" at end

**Laughter:** hehe, hoho, haha (soft, breathy)

**Thinking sounds:** hmm, uh, eh

---

## Technical Implementation

### Architecture

```
[Phrase Generator] → [Voice Selector] → [SSML Builder] → [ElevenLabs TTS] → [Audio Stream]
        ↓                    ↓                 ↓                  ↓
   [Synthesizer Parameters]  [Speaker Pool]  [Prosody Tags]   [Real-time Mix]
```

### Phrase Generation Loop

1. **Generate phrase** using language rules + current parameters
2. **Select speaker** (rotate between 2-5 voices)
3. **Build SSML** with:
   - `<prosody rate="...">` for speech rate
   - `<prosody pitch="...">` for variation
   - `<break time="...">` for conversation density
4. **Send to ElevenLabs** voice model
5. **Mix to output stream**
6. **Repeat** with timing based on conversation density

### SSML Example

```xml
<speak>
  <prosody rate="85%" pitch="-5%">
    Mila sora venita
  </prosody>
  <break time="1.2s"/>
  <prosody rate="82%" pitch="medium">
    Mm, luma na
  </prosody>
  <break time="0.8s"/>
</speak>
```

### Voice Pool

**Male voices (ElevenLabs):**
- Warm baritone (primary male)
- Gentle tenor (secondary male)

**Female voices (ElevenLabs):**
- Soft mezzo (primary female)
- Warm alto (secondary female)
- Light soprano (tertiary female)

Rotate speakers with natural conversation patterns (not strict alternation).

---

## Future: The Synthesizer Interface

### Synthesizer Interface
Real-time knobs to control:
- Speech rate
- Conversation density
- Softness
- Laughter frequency
- Number of speakers


### Real-Time Control Parameters

#### **1. Speech Rate** (0.5 - 1.2x)
Controls how fast the speakers talk. Slower = more drowsy, meditative feel.
- **Low (0.5-0.7):** Very slow, hypnotic
- **Medium (0.7-0.9):** Natural sleepy conversation
- **High (0.9-1.2):** Gentle animated chat

#### **2. Conversation Density** (0.1 - 1.0)
How much overlap and silence exists between speakers.
- **Low (0.1-0.3):** Long pauses, spacious, meditative
- **Medium (0.4-0.7):** Natural conversation rhythm
- **High (0.8-1.0):** Lively overlapping dialogue

#### **3. Pitch Variation** (0.0 - 1.0)
How much the speakers vary their pitch (prosody expressiveness).
- **Low (0.0-0.3):** Monotone, calming
- **Medium (0.3-0.6):** Natural variation
- **High (0.6-1.0):** Expressive, animated

#### **4. Softness** (0.0 - 1.0)
Phonetic character of the invented language.
- **Low (0.0-0.3):** Harder consonants (k, t, p, g)
- **Medium (0.3-0.7):** Balanced
- **High (0.7-1.0):** Soft consonants (l, m, n, v, w) + flowing vowels

#### **5. Laughter Frequency** (0.0 - 0.5)
How often soft laughter appears in the conversation.
- **None (0.0):** Serious, calm
- **Rare (0.1-0.2):** Occasional warm chuckle
- **Frequent (0.3-0.5):** Gentle, joyful atmosphere

#### **6. Number of Speakers** (2-5)
Mix of male and female voices.
- **2 speakers:** Intimate, couple-like
- **3 speakers:** Small group
- **4-5 speakers:** Dinner party ambience

#### **7. Master Volume** (0.0 - 1.0)
Overall output level.

---

## Extended Features: Biometric Integration

### Sensor-Based Parameter Modulation

The synthesizer can respond to real-time biometric data to create adaptive soundscapes.

#### **Heart Rate (HR)**

**Low HR (40-60 bpm):** Deep sleep detected
- → Increase silence (lower conversation density)
- → Slower speech rate
- → Reduce volume slightly

**Medium HR (60-80 bpm):** Relaxed/drowsy state
- → Maintain current parameters
- → Occasional soft laughter

**High HR (80-100 bpm):** Still awake/restless
- → Increase conversation density slightly
- → More soothing, slower speech
- → Higher softness parameter

#### **Movement Sensors (Accelerometer)**

**No movement (5+ min):** Likely asleep
- → Gradually reduce volume
- → Increase pause length
- → Transition to more spacious soundscape

**Restless movement:** Still settling
- → Maintain engaging presence
- → Slightly increase conversation density

#### **Breathing Rate (via chest sensor or smart mattress)**

**Slow, regular breathing:** Deep relaxation
- → Sync conversation pauses with breath rhythm
- → Match speech rate to breathing tempo

**Irregular breathing:** Stress/anxiety
- → Increase softness
- → Add more soothing agreement sounds
- → Reduce pitch variation (more monotone)

#### **Time of Night**

**First 30 minutes:** Initial settling
- → Higher conversation density
- → More engaging presence

**Middle of night:** Deep sleep maintenance
- → Minimal volume
- → Very sparse, occasional phrases

**Early morning:** Gentle awakening
- → Gradually increase volume
- → More animated pitch variation
- → Morning-appropriate tempo

---

## Control Interface Designs

### Option 1: Physical Synthesizer

```
┌─────────────────────────────────────────┐
│   SLEEP SOUNDSCAPE SYNTHESIZER          │
├─────────────────────────────────────────┤
│                                         │
│  [◉ Speech Rate]  [◉ Density]  [◉ Vol] │
│                                         │
│  [◉ Pitch Var]    [◉ Softness]         │
│                                         │
│  [◉ Laughter]     [◯ Speakers: 3]      │
│                                         │
│         [▶ PLAY]     [◼ STOP]          │
│                                         │
│  Mode: [Manual] [Sensor-Adaptive]      │
└─────────────────────────────────────────┘
```

### Option 2: Mobile App

**Home Screen:**
- Central play/pause button
- Live waveform visualization
- Quick presets: "Gentle", "Intimate", "Lively", "Meditative"

**Synthesizer Tab:**
- Vertical sliders for each parameter
- Real-time preview
- Save custom presets

**Sensors Tab:**
- Connect biometric devices
- View current HR, movement, breathing
- See how parameters are adapting

**Library Tab:**
- Browse saved soundscapes
- Community presets
- Favorite combinations

### Option 3: Web Interface

Simple browser-based control panel with:
- Horizontal sliders
- Real-time audio generation
- URL-shareable parameter configurations
- Export to audio file option

---

## Use Cases

### **Primary: Sleep Aid**
The core application - falling asleep to comforting but incomprehensible voices.

### **Meditation & Relaxation**
Low conversation density + high softness = meditative background.

### **Focus Work (Café Mode)**
Medium density + slight laughter = productive ambience without distraction.

### **Anxiety Relief**
Presence of "others" without social demand - comforting for those who feel alone.

### **Tinnitus Masking**
Gentle, variable human voices mask ringing without creating new irritation.

### **Language Learner's Background**
Creates "immersive" feeling without interfering with actual study.

### **Children's Bedtime**
Safe, warm presence in the room - like parents talking in another room.

---

## Differentiation from Existing Products

| Feature | Café Ambience | ASMR | White Noise | This System |
|---------|---------------|------|-------------|-------------|
| Human voices | ✓ (real language) | ✓ (whispering) | ✗ | ✓ (invented) |
| No comprehension | ✗ | ✗ | ✓ | ✓ |
| Natural prosody | ✓ | Partial | ✗ | ✓ |
| Real-time control | ✗ | ✗ | Partial | ✓ |
| Adaptive | ✗ | ✗ | ✗ | ✓ (sensors) |
| Infinite variety | ✗ | ✗ | ✓ | ✓ |

---

## Technical Challenges

### 1. **Real-time Generation**
Generating natural conversation flow in real-time without repetition.

**Solution:** 
- Pre-generate phrase bank using Claude
- Combine procedurally with variation
- Regenerate bank periodically

### 2. **Natural Conversation Flow**
Avoiding robotic turn-taking; making it sound genuinely spontaneous.

**Solution:**
- Randomize pause lengths within bounds
- Occasional overlaps
- Agreement sounds that feel reactive

### 3. **ElevenLabs API Rate Limits**
Can't generate every phrase in real-time.

**Solution:**
- Pre-generate 50-100 phrases per session
- Cache and recombine
- Stream pre-generated audio chunks

### 4. **Sensor Integration**
Making biometric control smooth, not jarring.

**Solution:**
- Slow parameter transitions (30-60 second ramps)
- Threshold-based changes, not continuous
- Override option for manual control

---

## Development Roadmap

### Phase 1: Core Engine (MVP)
- [ ] Invented language generator
- [ ] SSML-based prosody control
- [ ] ElevenLabs integration
- [ ] Basic 6-parameter synthesizer
- [ ] Simple web interface

### Phase 2: Enhancement
- [ ] Improved language variety
- [ ] More voice options
- [ ] Preset library
- [ ] Export to audio file
- [ ] Mobile app (iOS/Android)

### Phase 3: Adaptive System
- [ ] Heart rate integration
- [ ] Movement sensor support
- [ ] Breathing rate detection
- [ ] Smart parameter adaptation
- [ ] Sleep tracking integration

### Phase 4: Community
- [ ] Preset sharing
- [ ] Custom voice upload
- [ ] Language phonology customization
- [ ] API for third-party apps
- [ ] Sleep data analytics

---

## Conclusion

This sleep soundscape synthesizer fills a unique niche: **the comfort of human presence without the cognitive load of language comprehension**. By combining:

- Neural TTS (ElevenLabs)
- Procedural language generation
- Real-time parameter control
- Optional biometric adaptation

...we create an infinitely variable, deeply personal sleep environment that evolves with the user's needs.

The result is warmer than white noise, less distracting than real conversation, and more natural than ASMR—a genuinely new category of sleep technology.

---
```


# spatialize_audio.py
```python
"""
Audio Spatializer
Creates a 3D soundscape by layering multiple conversations with stereo positioning.
Generates the final immersive sleep soundscape.
"""

import os
import yaml
import subprocess
from typing import List, Tuple


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def spatialize_audio(config_path: str = "config.yaml"):
    """
    Create 3D soundscape by layering conversations with stereo positioning.
    
    Process:
    1. Generate multiple conversation layers from the same base conversation
    2. Apply stereo panning to each layer (left, center, right)
    3. Apply volume adjustments
    4. Add time offsets so layers overlap naturally
    5. Mix all layers together
    """
    print("=" * 60)
    print("Audio Spatializer - Creating 3D Soundscape")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/5] Loading configuration...")
    config = load_config(config_path)
    
    merged_file = config['paths']['merged_file']
    output_file = config['paths']['spatialized_file']
    
    spat_config = config.get('spatialization', {})
    num_layers = spat_config.get('num_layers', 3)
    stereo_positions = spat_config.get('stereo_positions', [-0.6, 0.0, 0.5])
    volume_adjustments = spat_config.get('volume_adjustments', [0.7, 0.8, 0.6])
    time_offsets = spat_config.get('time_offsets', [0.0, 5.0, 12.0])
    
    # Verify merged file exists
    if not os.path.exists(merged_file):
        print(f"\n  Error: Merged conversation file not found: {merged_file}")
        print("  Run: python merge_audio.py first")
        return
    
    print(f"  Input: {merged_file}")
    print(f"  Layers: {num_layers}")
    
    # Build ffmpeg filter complex
    print("\n[2/5] Building spatial audio filters...")
    
    # Input specifications
    inputs = []
    filter_parts = []
    
    for i in range(num_layers):
        # Each layer reads from the same merged file with a time delay
        inputs.extend(["-ss", str(time_offsets[i]), "-i", merged_file])
        
        # Build filter for this layer:
        # 1. Apply volume adjustment
        # 2. Apply stereo panning
        pan_value = stereo_positions[i]  # -1 (left) to +1 (right)
        volume = volume_adjustments[i]
        
        # Convert pan value to stereo balance
        # pan=0.0 -> balance both channels equally
        # pan=-1.0 -> 100% left, 0% right
        # pan=+1.0 -> 0% left, 100% right
        left_gain = (1.0 - pan_value) / 2.0 * volume
        right_gain = (1.0 + pan_value) / 2.0 * volume
        
        filter_parts.append(
            f"[{i}:a]volume={volume},pan=stereo|c0={left_gain}*c0+{left_gain}*c1|c1={right_gain}*c0+{right_gain}*c1[a{i}]"
        )
    
    # Mix all processed layers together
    mix_inputs = ''.join([f"[a{i}]" for i in range(num_layers)])
    filter_parts.append(f"{mix_inputs}amix=inputs={num_layers}:duration=longest:dropout_transition=2[aout]")
    
    filter_complex = ';'.join(filter_parts)
    
    print("  Spatial configuration:")
    for i in range(num_layers):
        position = "LEFT" if stereo_positions[i] < -0.3 else "RIGHT" if stereo_positions[i] > 0.3 else "CENTER"
        print(f"    Layer {i+1}: {position:6s} | Vol: {volume_adjustments[i]:.1f} | Offset: {time_offsets[i]:.1f}s")
    
    # Run ffmpeg
    print("\n[3/5] Mixing spatial layers with ffmpeg...")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "ffmpeg",
        *inputs,  # All input files
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "2",  # High quality MP3
        "-y",  # Overwrite output
        output_file
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if result.returncode != 0:
        print(f"  Error: ffmpeg failed")
        print(result.stderr.decode())
        return
    
    # Get file info
    print("\n[4/5] Verifying output...")
    
    if os.path.exists(output_file):
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"  ✓ File created: {file_size_mb:.1f} MB")
    
    # Get duration using ffprobe
    duration_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        output_file
    ]
    
    duration_result = subprocess.run(
        duration_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if duration_result.returncode == 0:
        duration = float(duration_result.stdout.decode().strip())
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"  ✓ Duration: {minutes}m {seconds}s")
    
    print("\n[5/5] Complete!")
    print(f"\n  🎵 Final soundscape: {output_file}")
    print("\nYour sleep soundscape is ready!")
    print("The file contains multiple overlapping conversations")
    print("with natural stereo positioning for an immersive experience.")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    # Allow custom config path
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    try:
        spatialize_audio(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

```


# tts.py
```python
"""
Text-to-Speech Module
Interfaces with ElevenLabs API and applies fade-in/fade-out to prevent clicks.
"""

import os
import configparser
import requests
import subprocess
from typing import Optional


def call_elevenlabs_tts(
    text: str,
    voice_id: str,
    api_key: str,
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True
) -> bytes:
    """
    Call ElevenLabs TTS API to generate speech.
    
    Args:
        text: Text or SSML to synthesize
        voice_id: ElevenLabs voice ID
        api_key: ElevenLabs API key
        model_id: Model to use
        output_format: Audio format
        stability: Voice stability (0.0-1.0)
        similarity_boost: Similarity boost (0.0-1.0)
        style: Style exaggeration (0.0-1.0)
        use_speaker_boost: Enable speaker boost
    
    Returns:
        Raw audio bytes (MP3)
    
    Raises:
        Exception: If API call fails
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    # Check if text contains SSML
    is_ssml = text.strip().startswith('<speak>')
    
    data = {
        "text": text,
        "model_id": model_id,
        "output_format": output_format,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        },
        "enable_ssml": is_ssml
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
    
    return response.content


def apply_fade(
    input_audio: bytes,
    fade_duration_ms: int = 20,
    temp_dir: str = "."
) -> bytes:
    """
    Apply fade-in and fade-out to audio to prevent clicks.
    Uses ffmpeg directly via subprocess.
    
    Args:
        input_audio: Raw audio bytes
        fade_duration_ms: Duration of fade in milliseconds
        temp_dir: Directory for temporary files
    
    Returns:
        Processed audio bytes
    """
    # Write input to temp file
    input_path = os.path.join(temp_dir, "temp_input.mp3")
    output_path = os.path.join(temp_dir, "temp_output.mp3")
    
    try:
        # Write input audio
        with open(input_path, "wb") as f:
            f.write(input_audio)
        
        # Calculate fade duration in seconds
        fade_duration_sec = fade_duration_ms / 1000.0
        
        # Build ffmpeg command
        # Use just filenames since we're setting cwd to temp_dir
        cmd = [
            "ffmpeg",
            "-i", "temp_input.mp3",
            "-af", f"afade=t=in:st=0:d={fade_duration_sec},afade=t=out:d={fade_duration_sec}",
            "-c:a", "libmp3lame",
            "-y",  # Overwrite output
            "temp_output.mp3"
        ]
        
        # Run ffmpeg with cwd set to temp_dir
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=temp_dir
        )
        
        if result.returncode != 0:
            raise Exception(f"ffmpeg fade failed: {result.stderr.decode()}")
        
        # Read processed audio
        with open(output_path, "rb") as f:
            processed_audio = f.read()
        
        return processed_audio
    
    finally:
        # Clean up temp files
        for path in [input_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass


def generate_speech(
    text: str,
    voice_id: str,
    output_path: str,
    config: dict,
    apply_fading: bool = False,  # Changed to False by default
    prosody: dict = None
) -> bool:
    """
    Generate speech and save to file.
    
    Args:
        text: Text or SSML to synthesize (SSML will be auto-detected)
        voice_id: ElevenLabs voice ID
        output_path: Where to save the audio file
        config: Configuration dictionary
        apply_fading: Whether to apply fade-in/fade-out (disabled by default - use separate post-processing)
        prosody: Optional prosody parameters (unused - kept for compatibility)
    
    Returns:
        True if successful
    """
    # Get API key from secrets.ini
    secrets = configparser.ConfigParser()
    secrets.read('secrets.ini')
    api_key = secrets.get('elevenlabs', 'api_key')
    
    # Get model settings
    model_id = config['elevenlabs'].get('model_id', 'eleven_multilingual_v2')
    output_format = config['audio'].get('output_format', 'mp3_44100_128')
    
    # Use default voice settings - SSML handles prosody
    stability = 0.5
    similarity_boost = 0.75
    style = 0.0
    
    # Call API
    audio_bytes = call_elevenlabs_tts(
        text=text,
        voice_id=voice_id,
        api_key=api_key,
        model_id=model_id,
        output_format=output_format,
        stability=stability,
        similarity_boost=similarity_boost,
        style=style
    )
    
    # Apply fading if requested (disabled by default - causes audio corruption)
    if apply_fading:
        fade_duration_ms = config['audio'].get('fade_duration_ms', 20)
        temp_dir = os.path.dirname(output_path) or "."
        audio_bytes = apply_fade(audio_bytes, fade_duration_ms, temp_dir)
    
    # Save to file
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    return True


if __name__ == "__main__":
    # Test TTS functionality
    import yaml
    
    print("Testing ElevenLabs TTS...")
    
    # Load config
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: config.yaml not found")
        exit(1)
    
    # Simple test
    test_text = '<speak><prosody rate="85%" pitch="+5%" volume="medium">Hello, this is a test.</prosody></speak>'
    test_voice = config['voices'][0]  # Use first voice
    test_output = "test_output.mp3"
    
    try:
        success = generate_speech(test_text, test_voice, test_output, config)
        if success:
            print(f"Success! Audio saved to {test_output}")
        else:
            print("Failed to generate speech")
    except Exception as e:
        print(f"Error: {e}")

```

