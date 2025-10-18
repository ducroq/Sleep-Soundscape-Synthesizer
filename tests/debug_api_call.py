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