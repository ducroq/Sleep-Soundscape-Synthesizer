"""
Quick TTS Test - Diagnose audio generation issues
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.audio.tts import call_elevenlabs_tts
from src.utils.config_loader import load_config, get_elevenlabs_api_key

# Load config
config = load_config()

# Get API key
api_key = get_elevenlabs_api_key()

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
        model_id=config['elevenlabs']['model_id'],
        config=config
    )
    print(f"  [OK] Got {len(audio)} bytes of audio")
    with open('test_plain.mp3', 'wb') as f:
        f.write(audio)
    print(f"  [OK] Saved to test_plain.mp3")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

# Test 2: SSML with prosody
print("\n[Test 2] SSML with prosody...")
ssml_text = '<speak><prosody rate="90%" pitch="+5%" volume="medium">Hello, this is a test with SSML.</prosody></speak>'
try:
    audio = call_elevenlabs_tts(
        text=ssml_text,
        voice_id=voice_id,
        api_key=api_key,
        model_id=config['elevenlabs']['model_id'],
        config=config
    )
    print(f"  [OK] Got {len(audio)} bytes of audio")
    with open('test_ssml.mp3', 'wb') as f:
        f.write(audio)
    print(f"  [OK] Saved to test_ssml.mp3")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

# Test 3: Invented language
print("\n[Test 3] Invented language (plain)...")
try:
    audio = call_elevenlabs_tts(
        text="loria belina taso ren",
        voice_id=voice_id,
        api_key=api_key,
        model_id=config['elevenlabs']['model_id'],
        config=config
    )
    print(f"  [OK] Got {len(audio)} bytes of audio")
    with open('test_invented.mp3', 'wb') as f:
        f.write(audio)
    print(f"  [OK] Saved to test_invented.mp3")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

print("\nTests complete! Play the MP3 files to check if they have audio.")
print("If test_plain.mp3 has audio but test_ssml.mp3 doesn't, SSML is the issue.")
