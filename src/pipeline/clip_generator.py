"""
Clip Generator Module
Generates individual audio clips with probabilistic speaker personalities.
"""

import os
import random
from typing import Dict
from pathlib import Path

from src.generation.language import LanguageGenerator, generate_utterance
from src.generation.ssml import generate_ssml
from src.generation.personality import initialize_speaker_personalities, SpeakerPersonality
from src.audio.tts import generate_speech


def generate_clips(config: dict, verbose: bool = True) -> int:
    """
    Generate audio clips with probabilistic speaker personalities.

    Args:
        config: Configuration dictionary from config_loader
        verbose: Whether to print progress messages

    Returns:
        Number of clips successfully generated
    """
    # Get settings
    voices = config['voices']
    num_clips = config['conversation']['num_clips']
    softness = config['language']['softness']
    clips_dir = config['paths']['clips_dir']

    if verbose:
        print(f"\n[Clip Generator]")
        print(f"  Voices: {len(voices)}")
        print(f"  Clips to generate: {num_clips}")
        print(f"  Softness: {softness}")
        print(f"  Output: {clips_dir}")

    # Initialize language generator
    if verbose:
        print(f"\n  Initializing language generator...")
    lang_gen = LanguageGenerator(softness=softness, config=config)

    # Initialize speaker personalities
    if verbose:
        print(f"  Sampling speaker personalities...")
    personalities = initialize_speaker_personalities(voices, config)

    if verbose:
        print(f"  Created {len(personalities)} unique personalities:")
        for voice_id, personality in personalities.items():
            short_id = voice_id[:8]
            print(f"    {short_id}: laughter={personality.traits['laughter_frequency']:.2f}, "
                  f"agreement={personality.traits['agreement_frequency']:.2f}, "
                  f"verbosity={personality.traits['verbosity']:.2f}")

    # Generate clips
    if verbose:
        print(f"\n  Generating {num_clips} audio clips...")

    successful_clips = 0

    for i in range(num_clips):
        # Select random voice and its personality
        voice_id = random.choice(voices)
        personality = personalities[voice_id]

        # Generate text with personality's verbosity
        verbosity = personality.get_verbosity()
        text, utterance_type = generate_utterance(lang_gen, config, verbosity)

        # Generate SSML with personality-aware prosody
        ssml = generate_ssml(text, personality, utterance_type)

        # Extract prosody parameters
        prosody = personality.sample_utterance_prosody(utterance_type)

        # Generate audio
        output_path = os.path.join(clips_dir, f"clip_{i:03d}.mp3")

        try:
            generate_speech(ssml, voice_id, output_path, config, prosody=prosody)
            successful_clips += 1

            # Show progress
            if verbose:
                short_id = voice_id[:8]
                print(f"    [{i+1:2d}/{num_clips}] {short_id} ({utterance_type:10s}): {text[:40]}")

        except Exception as e:
            if verbose:
                print(f"    [ERROR] Clip {i}: {e}")
            continue

    if verbose:
        print(f"\n  [OK] Generated {successful_clips}/{num_clips} clips successfully")
        print(f"  Location: {clips_dir}")

    return successful_clips
