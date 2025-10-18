"""
Invented Language Generator
Generates phonetically pleasing nonsense phrases for sleep soundscapes.
Now supports personality-based verbosity for varying phrase lengths.
Updated to read phonemes and syllable structure from config.
"""

import random
from typing import List, Dict, Any, Optional


class LanguageGenerator:
    """Generates invented language phrases based on phonological softness."""

    def __init__(self, softness: float = 0.7, config: Dict[str, Any] = None):
        """
        Initialize the language generator.

        Args:
            softness: 0.0-1.0, controls phoneme selection (higher = softer sounds)
            config: Configuration dictionary from config_loader.
        """
        self.softness = max(0.0, min(1.0, softness))
        self.config = config

        # Get phonemes from config (validated by config_loader)
        phonemes = self.config['language']['phonemes']

        # Consonants ranked by softness (Romance language influenced)
        self.soft_consonants = phonemes['soft_consonants']
        self.medium_consonants = phonemes['medium_consonants']
        self.hard_consonants = phonemes['hard_consonants']

        # Vowels (inherently soft)
        self.vowels = phonemes['vowels']

        # Build weighted consonant list based on softness
        self._build_consonant_pool()
    
    def _build_consonant_pool(self):
        """Build a weighted pool of consonants based on softness parameter."""
        # Get consonant weighting ratios from config (validated by config_loader)
        weighting = self.config['language']['consonant_weighting']
        medium_ratio = weighting['medium_ratio']
        hard_ratio = weighting['hard_ratio']

        soft_weight = self.softness
        medium_weight = (1.0 - self.softness) * medium_ratio
        hard_weight = (1.0 - self.softness) * hard_ratio

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
        # Get syllable structure probabilities from config (validated by config_loader)
        syllable_structure = self.config['language']['syllable_structure']
        onset_probability = syllable_structure['onset_probability']
        onset_first_syllable = syllable_structure['onset_first_syllable']
        coda_probability = syllable_structure['coda_probability']

        num_syllables = random.randint(min_length, max_length)
        word = ""

        for i in range(num_syllables):
            # Syllable structure: (C)V(C) where C=consonant, V=vowel
            syllable = ""

            # Optional initial consonant (onset)
            # First syllable has higher probability (or 100% if onset_first_syllable=1.0)
            if i == 0:
                if random.random() < onset_first_syllable:
                    syllable += random.choice(self.consonant_pool)
            else:
                if random.random() < onset_probability:
                    syllable += random.choice(self.consonant_pool)

            # Vowel (required)
            syllable += random.choice(self.vowels)

            # Optional final consonant (coda)
            if random.random() < coda_probability:
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
        agreements = self.config.get('agreement_sounds', [
            "mm-hmm", "mhm", "yeah", "uh-huh",
            "right", "sure", "okay", "yes"
        ])
        return random.choice(agreements)

    def generate_laughter(self) -> str:
        """Generate laughter sounds."""
        laughs = self.config.get('laughter_sounds', [
            "ha ha", "he he", "hehe", "haha", "ah ha"
        ])
        return random.choice(laughs)

    def generate_thinking(self) -> str:
        """Generate thinking sounds."""
        thinks = self.config.get('thinking_sounds', [
            "hmm", "uh", "um", "ah", "oh"
        ])
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
    lang_config = config['language']

    # Get utterance type probabilities from config (validated by config_loader)
    type_probs = config['utterance_type_probabilities']
    thinking_prob = type_probs['thinking']
    agreement_prob = type_probs['agreement']
    laughter_prob = type_probs['laughter']
    question_prob = type_probs['question']
    # normal_prob = type_probs['normal']  # Remainder

    # Calculate cumulative probabilities
    thinking_threshold = thinking_prob
    agreement_threshold = thinking_threshold + agreement_prob
    laughter_threshold = agreement_threshold + laughter_prob
    question_threshold = laughter_threshold + question_prob
    # Everything else is normal

    # Determine utterance type
    rand = random.random()

    if rand < thinking_threshold:
        return generator.generate_thinking(), 'thinking'
    elif rand < agreement_threshold:
        return generator.generate_agreement(), 'agreement'
    elif rand < laughter_threshold:
        return generator.generate_laughter(), 'laughter'
    elif rand < question_threshold:
        text = generator.generate_question(
            lang_config['min_phrase_length'],
            lang_config['max_phrase_length'],
            verbosity_multiplier
        )
        return text, 'question'
    else:  # Normal statements (remainder)
        text = generator.generate_phrase(
            lang_config['min_phrase_length'],
            lang_config['max_phrase_length'],
            verbosity_multiplier
        )
        return text, 'normal'


if __name__ == "__main__":
    # Test the language generator
    import sys
    from pathlib import Path

    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from src.utils.config_loader import load_config

    # Load config (required)
    config = load_config()
    print("Testing with config from config/config.yaml")
    gen = LanguageGenerator(softness=0.7, config=config)

    print("\nSample words:")
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

    print("\nSpecial sounds:")
    print(f"  Agreement: {gen.generate_agreement()}")
    print(f"  Laughter: {gen.generate_laughter()}")
    print(f"  Thinking: {gen.generate_thinking()}")
