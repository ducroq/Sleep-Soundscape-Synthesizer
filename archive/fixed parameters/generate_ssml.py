#!/usr/bin/env python3
"""
Generate SSML markup from plain text with natural variations
"""

import yaml
import random


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def text_to_ssml(text, config, add_natural_breaks=True):
    """
    Convert plain text to SSML with prosody tags and natural variations
    
    Args:
        text: Plain text phrase
        config: Configuration dict
        add_natural_breaks: Add subtle pauses within speech
    
    Returns:
        SSML-formatted string
    """
    prosody = config['prosody']
    
    # Base speech rate
    rate = f"{int(prosody['speech_rate'] * 100)}%"
    pitch = prosody['pitch']
    
    # Detect special utterances
    text_lower = text.lower().strip()
    
    # Agreement sounds - softer, with breath-like pauses
    if text_lower in ['mm', 'ah', 'oh', 'si', 'na', 'eh', 'hmm']:
        ssml = f'''<speak>
  <prosody rate="{rate}" pitch="{pitch}" volume="soft">
    <break time="0.3s"/>{text}<break time="0.5s"/>
  </prosody>
</speak>'''
    
    # Laughter - lighter, slightly faster
    elif text_lower in ['hehe', 'hoho', 'haha', 'hihi']:
        ssml = f'''<speak>
  <prosody rate="110%" pitch="+5%" volume="soft">
    <break time="0.2s"/>{text}<break time="0.4s"/>
  </prosody>
</speak>'''
    
    # Regular phrase - add natural micro-breaks and slight variations
    else:
        words = text.split()
        
        # Add natural pauses after some words
        if add_natural_breaks and len(words) > 3:
            # Add a subtle pause after 2-4 words
            pause_position = random.randint(2, min(4, len(words) - 1))
            words[pause_position] = f'{words[pause_position]}<break time="0.3s"/>'
        
        # Occasionally emphasize a word slightly
        if len(words) > 2 and random.random() < 0.3:
            emphasis_pos = random.randint(0, len(words) - 1)
            words[emphasis_pos] = f'<emphasis level="moderate">{words[emphasis_pos]}</emphasis>'
        
        # Add comma pause if present
        enhanced_text = ' '.join(words)
        enhanced_text = enhanced_text.replace(',', ',<break time="0.4s"/>')
        
        # Slight volume variation for naturalness
        volume = random.choice(['medium', 'soft', 'medium'])
        
        ssml = f'''<speak>
  <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
    {enhanced_text}
  </prosody>
</speak>'''
    
    return ssml


def text_to_ssml_simple(text, config):
    """
    Simple SSML without variations (for testing/comparison)
    """
    prosody = config['prosody']
    rate = f"{int(prosody['speech_rate'] * 100)}%"
    pitch = prosody['pitch']
    
    ssml = f'''<speak>
  <prosody rate="{rate}" pitch="{pitch}">
    {text}
  </prosody>
</speak>'''
    
    return ssml


if __name__ == '__main__':
    import sys
    
    config = load_config()
    
    if len(sys.argv) > 1:
        # Use text from command line
        text = ' '.join(sys.argv[1:])
    else:
        # Use example
        text = "mila sora venita"
    
    # Generate both versions for comparison
    print("=== Enhanced SSML ===")
    ssml = text_to_ssml(text, config)
    print(ssml)
    
    print("\n=== Simple SSML ===")
    ssml_simple = text_to_ssml_simple(text, config)
    print(ssml_simple)