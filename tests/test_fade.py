"""
Test if fade is corrupting audio
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import random
from src.generation.language import LanguageGenerator, generate_utterance
from src.generation.ssml import generate_ssml
from src.generation.personality import initialize_speaker_personalities
from src.audio.tts import generate_speech
from src.utils.config_loader import load_config

print("=" * 70)
print("Testing WITH and WITHOUT fade")
print("=" * 70)

# Load config
config = load_config()

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