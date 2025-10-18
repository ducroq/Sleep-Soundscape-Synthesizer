"""
Invented Language Generator
Generates phonetically pleasing nonsense phrases for sleep soundscapes.
Now supports personality-based verbosity for varying phrase lengths.
"""

import random
from typing import List


class LanguageGenerator:
    """Generates invented language phrases based on phonological softness."""
    
    def __init__(self, softness: float = 0.7):
        """
        Initialize the language generator.
        
        Args:
            softness: 0.0-1.0, controls phoneme selection (higher = softer sounds)
        """
        self.softness = max(0.0, min(1.0, softness))
        
        # Consonants ranked by softness (Romance language influenced)
        self.soft_consonants = ['l', 'm', 'n', 'r', 'v', 'j', 'w']
        self.medium_consonants = ['b', 'd', 'f', 's', 'z']
        self.hard_consonants = ['p', 't', 'k', 'g', 'ch', 'sh']
        
        # Vowels (inherently soft)
        self.vowels = ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ea', 'ia', 'io']
        
        # Build weighted consonant list based on softness
        self._build_consonant_pool()
    
    def _build_consonant_pool(self):
        """Build a weighted pool of consonants based on softness parameter."""
        soft_weight = self.softness
        medium_weight = (1.0 - self.softness) * 0.6
        hard_weight = (1.0 - self.softness) * 0.4
        
        self.consonant_pool = (
            self.soft_consonants * int(soft_weight * 10) +
            self.medium_consonants * int(medium_weight * 10) +
            self.hard_consonants * int(hard_weight * 10)
        )
        
        # Ensure we always have some consonants
        if not self.consonant_pool:
            self.consonant_pool = self.soft_consonants + self.medium_consonants
    
    def generate_word(self, min_length: int = 2, max_length: int = 5) -> str:
        """
        Generate a single nonsense word.
        
        Args:
            min_length: Minimum syllables
            max_length: Maximum syllables
        
        Returns:
            A nonsense word
        """
        num_syllables = random.randint(min_length, max_length)
        word = ""
        
        for i in range(num_syllables):
            # Syllable structure: (C)V(C) where C=consonant, V=vowel
            syllable = ""
            
            # Optional initial consonant (more likely for first syllable)
            if i == 0 or random.random() < 0.7:
                syllable += random.choice(self.consonant_pool)
            
            # Vowel (required)
            syllable += random.choice(self.vowels)
            
            # Optional final consonant (less likely for smoother flow)
            if random.random() < 0.3:
                syllable += random.choice(self.consonant_pool)
            
            word += syllable
        
        return word
    
    def generate_phrase(
        self,
        min_words: int = 3,
        max_words: int = 12,
        verbosity_multiplier: float = 1.0
    ) -> str:
        """
        Generate a phrase of nonsense words.
        
        Args:
            min_words: Minimum number of words
            max_words: Maximum number of words
            verbosity_multiplier: Personality-based length adjustment (0.7-1.4)
        
        Returns:
            A nonsense phrase
        """
        # Apply verbosity multiplier to phrase length
        adjusted_min = max(1, int(min_words * verbosity_multiplier))
        adjusted_max = max(adjusted_min + 1, int(max_words * verbosity_multiplier))
        
        num_words = random.randint(adjusted_min, adjusted_max)
        words = [self.generate_word() for _ in range(num_words)]
        
        return " ".join(words)
    
    def generate_question(
        self,
        min_words: int = 3,
        max_words: int = 10,
        verbosity_multiplier: float = 1.0
    ) -> str:
        """
        Generate a phrase that sounds like a question.
        Questions tend to be slightly shorter.
        """
        adjusted_max = max(3, int(max_words * 0.8 * verbosity_multiplier))
        return self.generate_phrase(min_words, adjusted_max, verbosity_multiplier)
    
    def generate_agreement(self) -> str:
        """Generate an agreement sound."""
        agreements = [
            "mm-hmm", "mhm", "yeah", "uh-huh",
            "right", "sure", "okay", "yes"
        ]
        return random.choice(agreements)
    
    def generate_laughter(self) -> str:
        """Generate laughter sounds."""
        laughs = [
            "ha ha", "he he", "hehe", "haha", "ah ha"
        ]
        return random.choice(laughs)
    
    def generate_thinking(self) -> str:
        """Generate thinking sounds."""
        thinks = ["hmm", "uh", "um", "ah", "oh"]
        return random.choice(thinks)


def generate_utterance(
    generator: LanguageGenerator,
    config: dict,
    verbosity_multiplier: float = 1.0
) -> tuple[str, str]:
    """
    Generate a single utterance with type detection.
    
    Args:
        generator: LanguageGenerator instance
        config: Configuration dictionary
        verbosity_multiplier: Personality-based length adjustment
    
    Returns:
        Tuple of (text, utterance_type)
    """
    lang_config = config.get('language', {})
    
    # Determine utterance type
    rand = random.random()
    
    if rand < 0.05:  # 5% thinking sounds
        return generator.generate_thinking(), 'thinking'
    elif rand < 0.15:  # 10% agreement
        return generator.generate_agreement(), 'agreement'
    elif rand < 0.20:  # 5% laughter
        return generator.generate_laughter(), 'laughter'
    elif rand < 0.35:  # 15% questions
        text = generator.generate_question(
            lang_config.get('min_phrase_length', 3),
            lang_config.get('max_phrase_length', 12),
            verbosity_multiplier
        )
        return text, 'question'
    else:  # 65% normal statements
        text = generator.generate_phrase(
            lang_config.get('min_phrase_length', 3),
            lang_config.get('max_phrase_length', 12),
            verbosity_multiplier
        )
        return text, 'normal'


if __name__ == "__main__":
    # Test the language generator
    gen = LanguageGenerator(softness=0.7)
    
    print("Sample words:")
    for _ in range(5):
        print(f"  {gen.generate_word()}")
    
    print("\nSample phrases:")
    for _ in range(5):
        print(f"  {gen.generate_phrase()}")
    
    print("\nWith verbosity variations:")
    for mult in [0.7, 1.0, 1.4]:
        print(f"\n  Verbosity {mult}:")
        for _ in range(3):
            print(f"    {gen.generate_phrase(verbosity_multiplier=mult)}")
