"""
Test Exact Generate Soundscape Flow
Mimics exactly what generate_soundscape.py does
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
print("Testing EXACT generate_soundscape.py flow")
print("=" * 70)

# Load config
config = load_config()

# Initialize language generator
print("\n[1] Initializing language generator...")
lang_gen = LanguageGenerator(softness=config['language']['softness'], config=config)

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