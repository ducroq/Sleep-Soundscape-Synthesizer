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
