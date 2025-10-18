#!/usr/bin/env python3
"""
Generate phrases in the invented language
"""

import random
import yaml


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def generate_language(softness=0.8):
    """
    Generate language phonemes based on softness level
    Returns: (vowels, consonants)
    """
    vowels = ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ei', 'ou']
    
    # Soft consonants (always available)
    consonants = ['l', 'r', 'm', 'n', 'v', 's', 'h', 'w', 'y']
    
    # Add harder consonants as softness decreases
    if softness < 0.7:
        consonants.extend(['f', 'z', 'sh', 'ch'])
    if softness < 0.4:
        consonants.extend(['k', 't', 'p', 'g', 'd', 'b'])
    
    return vowels, consonants


def generate_syllable(vowels, consonants):
    """Generate a single syllable"""
    patterns = ['V', 'CV', 'CVC', 'VCV']
    weights = [0.1, 0.5, 0.3, 0.1]
    
    pattern = random.choices(patterns, weights=weights)[0]
    
    syllable = ''
    for char in pattern:
        if char == 'C':
            syllable += random.choice(consonants)
        else:  # V
            syllable += random.choice(vowels)
    
    return syllable


def generate_word(vowels, consonants, min_syl=1, max_syl=3):
    """Generate a word with multiple syllables"""
    num_syllables = random.randint(min_syl, max_syl)
    return ''.join(generate_syllable(vowels, consonants) for _ in range(num_syllables))


def generate_phrase(config):
    """Generate a complete phrase based on config"""
    lang_config = config['language']
    vowels, consonants = generate_language(lang_config['softness'])
    
    # Decide what type of utterance
    rand = random.random()
    
    if rand < lang_config['laughter_prob']:
        return random.choice(['hehe', 'hoho', 'haha'])
    
    elif rand < lang_config['laughter_prob'] + lang_config['agreement_prob']:
        return random.choice(['mm', 'ah', 'oh', 'si', 'na', 'eh'])
    
    else:
        # Regular phrase
        num_words = random.randint(lang_config['min_words'], lang_config['max_words'])
        words = [generate_word(vowels, consonants) for _ in range(num_words)]
        phrase = ' '.join(words)
        
        # Sometimes add agreement at end
        if random.random() < 0.3:
            phrase += ', ' + random.choice(['mm', 'ah', 'si', 'na'])
        
        return phrase


if __name__ == '__main__':
    config = load_config()
    
    # Generate 10 example phrases
    for i in range(10):
        print(generate_phrase(config))