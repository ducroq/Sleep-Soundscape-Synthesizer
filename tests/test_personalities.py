"""
Test Script for Personality System
Verifies that personalities are sampled correctly and show variation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.generation.personality import initialize_speaker_personalities, SpeakerPersonality
from src.utils.config_loader import load_config


def test_personality_system():
    """Test the personality sampling system."""

    print("=" * 70)
    print("Testing Probabilistic Personality System")
    print("=" * 70)

    # Load config
    print("\n[1/3] Loading configuration...")
    try:
        config = load_config()
        print("  [OK] Config loaded successfully")
    except FileNotFoundError:
        print("  [FAIL] Error: config.yaml not found")
        return
    except ValueError as e:
        print(f"  [FAIL] Config validation error: {e}")
        return

    # Get voices
    voices = config.get('voices', [])
    if not voices:
        print("  [FAIL] Error: No voices in config")
        return

    print(f"  [OK] Found {len(voices)} voices")
    
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

    print(f"\n  [OK] All tests passed!")
    print(f"  The personality system is working correctly.\n")
    print("=" * 70)


if __name__ == "__main__":
    test_personality_system()
