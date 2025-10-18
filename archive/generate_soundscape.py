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
