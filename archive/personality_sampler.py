"""
Personality Sampler Module
Provides functions to sample speaker personalities and prosody parameters from distributions.
Creates per-speaker consistency with per-utterance variation.
"""

import random
import numpy as np
from typing import Dict, Any, List


class SpeakerPersonality:
    """Represents a speaker's personality traits sampled from distributions."""
    
    def __init__(self, voice_id: str, config: Dict[str, Any]):
        self.voice_id = voice_id
        self.config = config
        
        # Sample base personality traits for this speaker
        self.traits = self._sample_personality_traits()
        self.prosody_baseline = self._sample_prosody_baseline()
    
    def _sample_personality_traits(self) -> Dict[str, float]:
        """Sample personality traits from distributions."""
        traits = {}
        personality_dists = self.config.get('speaker_personality_distributions', {})
        
        # Laughter frequency
        laughter = personality_dists.get('laughter_frequency', {})
        traits['laughter_frequency'] = max(0, np.random.normal(
            laughter.get('mean', 0.15),
            laughter.get('std', 0.08)
        ))
        
        # Agreement frequency
        agreement = personality_dists.get('agreement_frequency', {})
        traits['agreement_frequency'] = max(0, np.random.normal(
            agreement.get('mean', 0.25),
            agreement.get('std', 0.10)
        ))
        
        # Verbosity (phrase length multiplier)
        verbosity = personality_dists.get('verbosity', {})
        traits['verbosity'] = np.clip(
            np.random.normal(verbosity.get('mean', 1.0), verbosity.get('std', 0.2)),
            verbosity.get('min', 0.7),
            verbosity.get('max', 1.4)
        )
        
        # Pause tendency (pause length multiplier)
        pause_tendency = personality_dists.get('pause_tendency', {})
        traits['pause_tendency'] = np.clip(
            np.random.normal(pause_tendency.get('mean', 1.0), pause_tendency.get('std', 0.15)),
            pause_tendency.get('min', 0.7),
            pause_tendency.get('max', 1.3)
        )
        
        return traits
    
    def _sample_prosody_baseline(self) -> Dict[str, Any]:
        """Sample this speaker's baseline prosody parameters."""
        prosody = {}
        prosody_dists = self.config.get('prosody_distributions', {})
        
        # Rate baseline
        rate_config = prosody_dists.get('rate', {})
        base_mean = rate_config.get('base_mean', 0.85)
        per_speaker_var = rate_config.get('per_speaker_variation', 0.10)
        prosody['rate'] = np.clip(
            np.random.normal(base_mean, per_speaker_var),
            rate_config.get('min', 0.70),
            rate_config.get('max', 1.00)
        )
        
        # Pitch baseline (in percentage offset)
        pitch_config = prosody_dists.get('pitch', {})
        per_speaker_var_pitch = pitch_config.get('per_speaker_variation', 8)
        prosody['pitch'] = np.clip(
            np.random.normal(0, per_speaker_var_pitch),
            pitch_config.get('min', -15),
            pitch_config.get('max', 15)
        )
        
        return prosody
    
    def sample_utterance_prosody(self, utterance_type: str = 'normal') -> Dict[str, Any]:
        """
        Sample prosody parameters for a specific utterance.
        Varies around this speaker's baseline.
        """
        prosody = {}
        prosody_dists = self.config.get('prosody_distributions', {})
        utterance_types = self.config.get('utterance_types', {})
        
        # Rate: baseline + per-utterance variation + type modifier
        rate_config = prosody_dists.get('rate', {})
        per_utterance_var = rate_config.get('per_utterance_variation', 0.03)
        rate = np.random.normal(self.prosody_baseline['rate'], per_utterance_var)
        
        # Apply utterance type modifier
        if utterance_type in utterance_types:
            rate_factor = utterance_types[utterance_type].get('rate_factor', 1.0)
            rate *= rate_factor
        
        prosody['rate'] = np.clip(rate, rate_config.get('min', 0.70), rate_config.get('max', 1.00))
        
        # Pitch: baseline + per-utterance variation + type modifier
        pitch_config = prosody_dists.get('pitch', {})
        per_utterance_var_pitch = pitch_config.get('per_utterance_variation', 3)
        pitch = np.random.normal(self.prosody_baseline['pitch'], per_utterance_var_pitch)
        
        # Apply utterance type modifier (e.g., questions get pitch boost)
        if utterance_type in utterance_types:
            pitch_boost = utterance_types[utterance_type].get('pitch_boost', 0)
            pitch += pitch_boost
        
        prosody['pitch'] = np.clip(pitch, pitch_config.get('min', -15), pitch_config.get('max', 15))
        
        # Volume
        volume_options = ['soft', 'medium']
        if utterance_type in utterance_types and 'volume' in utterance_types[utterance_type]:
            prosody['volume'] = utterance_types[utterance_type]['volume']
        else:
            prosody['volume'] = random.choice(volume_options)
        
        return prosody
    
    def should_laugh(self) -> bool:
        """Determine if this speaker should laugh based on their personality."""
        return random.random() < self.traits['laughter_frequency']
    
    def should_agree(self) -> bool:
        """Determine if this speaker should make agreement sounds."""
        return random.random() < self.traits['agreement_frequency']
    
    def get_verbosity(self) -> float:
        """Get this speaker's verbosity multiplier for phrase length."""
        return self.traits['verbosity']
    
    def sample_pause(self, pause_type: str) -> float:
        """Sample a pause duration for this speaker."""
        breaks_config = self.config.get('breaks', {})
        pause_config = breaks_config.get(pause_type, {})
        
        # Sample from distribution
        pause_duration = max(
            pause_config.get('min', 0.1),
            np.random.normal(
                pause_config.get('mean', 0.5),
                pause_config.get('std', 0.15)
            )
        )
        
        # Apply speaker's pause tendency
        pause_duration *= self.traits['pause_tendency']
        
        # Apply max if specified
        if 'max' in pause_config:
            pause_duration = min(pause_duration, pause_config['max'])
        
        return pause_duration
    
    def should_emphasize(self) -> tuple[bool, str]:
        """Determine if a word should be emphasized and what level."""
        emphasis_config = self.config.get('emphasis', {})
        probability = emphasis_config.get('probability', 0.3)
        
        if random.random() < probability:
            levels = emphasis_config.get('levels', ['moderate', 'strong', 'reduced'])
            weights = emphasis_config.get('level_weights', [0.6, 0.2, 0.2])
            level = random.choices(levels, weights=weights)[0]
            return True, level
        
        return False, 'none'


def initialize_speaker_personalities(voices: List[str], config: Dict[str, Any]) -> Dict[str, SpeakerPersonality]:
    """
    Initialize personality objects for all speakers at session start.
    
    Args:
        voices: List of voice IDs
        config: Full configuration dictionary
    
    Returns:
        Dictionary mapping voice_id to SpeakerPersonality object
    """
    personalities = {}
    for voice_id in voices:
        personalities[voice_id] = SpeakerPersonality(voice_id, config)
    
    return personalities


def sample_conversation_pause(config: Dict[str, Any]) -> float:
    """Sample a pause between conversation turns."""
    conversation_config = config.get('conversation', {})
    pause_dist = conversation_config.get('pause_distribution', {})
    
    pause = np.random.normal(
        pause_dist.get('mean', 1.2),
        pause_dist.get('std', 0.5)
    )
    
    return np.clip(
        pause,
        pause_dist.get('min', 0.5),
        pause_dist.get('max', 3.0)
    )


def get_default_config() -> Dict[str, Any]:
    """
    Return default configuration if distributions aren't specified.
    Ensures backward compatibility.
    """
    return {
        'prosody_distributions': {
            'rate': {
                'base_mean': 0.85,
                'per_speaker_variation': 0.10,
                'per_utterance_variation': 0.03,
                'min': 0.70,
                'max': 1.00
            },
            'pitch': {
                'base': 'medium',
                'per_speaker_variation': 8,
                'per_utterance_variation': 3,
                'min': -15,
                'max': 15
            }
        },
        'speaker_personality_distributions': {
            'laughter_frequency': {
                'mean': 0.15,
                'std': 0.08
            },
            'agreement_frequency': {
                'mean': 0.25,
                'std': 0.10
            },
            'verbosity': {
                'mean': 1.0,
                'std': 0.2,
                'min': 0.7,
                'max': 1.4
            },
            'pause_tendency': {
                'mean': 1.0,
                'std': 0.15,
                'min': 0.7,
                'max': 1.3
            }
        },
        'breaks': {
            'micro_pause': {
                'mean': 0.3,
                'std': 0.1,
                'min': 0.1,
                'max': 0.6
            },
            'comma_pause': {
                'mean': 0.4,
                'std': 0.15
            },
            'thinking_pause': {
                'mean': 0.8,
                'std': 0.3
            }
        },
        'conversation': {
            'pause_distribution': {
                'mean': 1.2,
                'std': 0.5,
                'min': 0.5,
                'max': 3.0
            }
        },
        'emphasis': {
            'probability': 0.3,
            'levels': ['moderate', 'strong', 'reduced'],
            'level_weights': [0.6, 0.2, 0.2]
        },
        'utterance_types': {
            'question': {
                'pitch_boost': 15,
                'rate_factor': 1.05
            },
            'agreement': {
                'volume': 'soft',
                'rate_factor': 0.9
            },
            'thinking': {
                'rate_factor': 0.85,
                'pause_before': 0.6
            }
        }
    }
