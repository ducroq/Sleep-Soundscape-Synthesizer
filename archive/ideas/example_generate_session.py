#!/usr/bin/env python3
"""
Example: Generate a long soundscape session
"""

import os
from soundscape_synthesizer import SoundscapeSynthesizer


def main():
    # Get API key
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        api_key = input("Enter your ElevenLabs API key: ")
    
    # Create synthesizer
    synth = SoundscapeSynthesizer(api_key)
    
    print("Select a preset:")
    print("1. Gentle (soft, slow, intimate)")
    print("2. Meditative (very slow, spacious)")
    print("3. Lively (animated with laughter)")
    print("4. Intimate (warm couple conversation)")
    print("5. Cafe (moderate ambience)")
    print("6. Custom")
    
    choice = input("\nChoice (1-6): ").strip()
    
    if choice == '1':
        synth.set_parameter('speech_rate', 0.75)
        synth.set_parameter('conversation_density', 0.4)
        synth.set_parameter('softness', 0.9)
        synth.set_parameter('laughter_frequency', 0.1)
        synth.set_parameter('num_speakers', 2)
        print("✅ Loaded: Gentle")
    
    elif choice == '2':
        synth.set_parameter('speech_rate', 0.6)
        synth.set_parameter('conversation_density', 0.2)
        synth.set_parameter('softness', 0.95)
        synth.set_parameter('laughter_frequency', 0.05)
        synth.set_parameter('num_speakers', 2)
        print("✅ Loaded: Meditative")
    
    elif choice == '3':
        synth.set_parameter('speech_rate', 1.0)
        synth.set_parameter('conversation_density', 0.8)
        synth.set_parameter('softness', 0.6)
        synth.set_parameter('laughter_frequency', 0.3)
        synth.set_parameter('num_speakers', 4)
        print("✅ Loaded: Lively")
    
    elif choice == '4':
        synth.set_parameter('speech_rate', 0.8)
        synth.set_parameter('conversation_density', 0.5)
        synth.set_parameter('softness', 0.85)
        synth.set_parameter('laughter_frequency', 0.2)
        synth.set_parameter('num_speakers', 2)
        print("✅ Loaded: Intimate")
    
    elif choice == '5':
        synth.set_parameter('speech_rate', 0.9)
        synth.set_parameter('conversation_density', 0.7)
        synth.set_parameter('softness', 0.7)
        synth.set_parameter('laughter_frequency', 0.25)
        synth.set_parameter('num_speakers', 3)
        print("✅ Loaded: Cafe")
    
    else:
        print("Using default parameters")
    
    # Get duration
    duration_str = input("\nDuration in minutes (default 5): ").strip()
    duration_minutes = int(duration_str) if duration_str else 5
    duration_seconds = duration_minutes * 60
    
    print(f"\n🎵 Generating {duration_minutes} minute soundscape...")
    print("Files will be saved as soundscape_XXXX.mp3")
    print("\nPress Ctrl+C to stop early\n")
    
    # Generate
    synth.generate_session(
        duration_seconds=duration_seconds,
        save_to_files=True
    )
    
    print("\n✅ Generation complete!")
    print("\nTo merge all files into one:")
    print("  Using ffmpeg:")
    print("    ffmpeg -i 'concat:soundscape_0001.mp3|soundscape_0002.mp3|...' -acodec copy output.mp3")
    print("  Or use the provided merge script (if available)")


if __name__ == "__main__":
    main()
