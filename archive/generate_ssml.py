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
