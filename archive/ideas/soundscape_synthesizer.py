#!/usr/bin/env python3
"""
Sleep Soundscape Synthesizer
Generates continuous background chatter in an invented language using ElevenLabs API
"""

import os
import random
import time
from typing import List, Dict
import requests
import json
from io import BytesIO
import simpleaudio as sa  # For audio playback


class InventedLanguageGenerator:
    """Generates phrases in a beautiful invented language"""
    
    def __init__(self, softness: float = 0.8):
        """
        Initialize the language generator
        
        Args:
            softness: 0.0-1.0, controls consonant hardness
        """
        self.softness = softness
        
        # Vowels - always available
        self.vowels = ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ei', 'ou', 'ia']
        
        # Consonants by softness level
        self.soft_consonants = ['l', 'r', 'm', 'n', 'v', 's', 'h', 'w', 'y']
        self.medium_consonants = ['f', 'z', 'sh', 'ch']
        self.hard_consonants = ['k', 't', 'p', 'g', 'd', 'b']
        
        # Agreement sounds
        self.agreement_sounds = ['mm', 'ah', 'oh', 'si', 'na', 'eh']
        
        # Laughter
        self.laughter = ['hehe', 'hoho', 'haha', 'hihi']
        
        self._update_consonants()
    
    def _update_consonants(self):
        """Update available consonants based on softness parameter"""
        self.consonants = self.soft_consonants.copy()
        
        if self.softness < 0.7:
            self.consonants.extend(self.medium_consonants)
        
        if self.softness < 0.4:
            self.consonants.extend(self.hard_consonants)
    
    def set_softness(self, softness: float):
        """Update softness parameter"""
        self.softness = softness
        self._update_consonants()
    
    def generate_syllable(self) -> str:
        """Generate a single syllable"""
        patterns = [
            ('V', 0.1),      # just vowel
            ('CV', 0.5),     # consonant + vowel
            ('CVC', 0.3),    # consonant + vowel + consonant
            ('VCV', 0.1),    # vowel + consonant + vowel
        ]
        
        pattern = random.choices(
            [p[0] for p in patterns],
            weights=[p[1] for p in patterns]
        )[0]
        
        syllable = ''
        for char in pattern:
            if char == 'C':
                syllable += random.choice(self.consonants)
            else:  # V
                syllable += random.choice(self.vowels)
        
        return syllable
    
    def generate_word(self, min_syllables: int = 1, max_syllables: int = 3) -> str:
        """Generate a word with multiple syllables"""
        num_syllables = random.randint(min_syllables, max_syllables)
        return ''.join(self.generate_syllable() for _ in range(num_syllables))
    
    def generate_phrase(self, min_words: int = 2, max_words: int = 6) -> str:
        """Generate a complete phrase"""
        num_words = random.randint(min_words, max_words)
        words = [self.generate_word() for _ in range(num_words)]
        return ' '.join(words)
    
    def generate_agreement(self) -> str:
        """Generate an agreement sound"""
        return random.choice(self.agreement_sounds)
    
    def generate_laughter(self) -> str:
        """Generate soft laughter"""
        return random.choice(self.laughter)
    
    def generate_utterance(self, laughter_prob: float = 0.15, agreement_prob: float = 0.25) -> str:
        """Generate a complete utterance (phrase, agreement, or laughter)"""
        rand = random.random()
        
        if rand < laughter_prob:
            return self.generate_laughter()
        elif rand < laughter_prob + agreement_prob:
            return self.generate_agreement()
        else:
            # Regular phrase, sometimes with agreement at end
            phrase = self.generate_phrase()
            if random.random() < 0.3:
                phrase += ', ' + self.generate_agreement()
            return phrase


class SoundscapeSynthesizer:
    """Main synthesizer that generates audio using ElevenLabs API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the synthesizer
        
        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Synthesizer parameters
        self.params = {
            'speech_rate': 0.85,          # 0.5-1.2
            'conversation_density': 0.6,   # 0.1-1.0 (affects pauses)
            'pitch_variation': 0.3,        # 0.0-1.0
            'softness': 0.8,               # 0.0-1.0
            'laughter_frequency': 0.15,    # 0.0-0.5
            'num_speakers': 3,             # 2-5
            'volume': 0.7,                 # 0.0-1.0
        }
        
        # Voice pool (using ElevenLabs voice IDs)
        # You'll need to replace these with actual voice IDs from your account
        self.voices = {
            'male1': '21m00Tcm4TlvDq8ikWAM',  # Rachel (placeholder - replace)
            'male2': 'AZnzlk1XvdvUeBnXmlld',  # Domi (placeholder - replace)
            'female1': 'EXAVITQu4vr4xnSDxMaL',  # Bella (placeholder - replace)
            'female2': 'ErXwobaYiN019PkySvjV',  # Antoni (placeholder - replace)
            'female3': 'MF3mGyEYCl7XYWbV9V6O',  # Elli (placeholder - replace)
        }
        
        self.language_generator = InventedLanguageGenerator(self.params['softness'])
        self.current_speaker_idx = 0
        self.speaker_keys = list(self.voices.keys())[:self.params['num_speakers']]
    
    def set_parameter(self, param_name: str, value: float):
        """Update a synthesizer parameter"""
        if param_name in self.params:
            self.params[param_name] = value
            
            # Update dependent systems
            if param_name == 'softness':
                self.language_generator.set_softness(value)
            elif param_name == 'num_speakers':
                self.speaker_keys = list(self.voices.keys())[:int(value)]
        else:
            raise ValueError(f"Unknown parameter: {param_name}")
    
    def get_next_speaker(self) -> str:
        """Get the next speaker voice ID"""
        # Rotate through speakers with some randomness
        if random.random() < 0.3:  # 30% chance to repeat same speaker
            voice_key = self.speaker_keys[self.current_speaker_idx]
        else:
            self.current_speaker_idx = (self.current_speaker_idx + 1) % len(self.speaker_keys)
            voice_key = self.speaker_keys[self.current_speaker_idx]
        
        return self.voices[voice_key]
    
    def calculate_pause_duration(self) -> float:
        """Calculate pause between utterances based on conversation density"""
        density = self.params['conversation_density']
        
        # Higher density = shorter pauses
        min_pause = 0.3
        max_pause = 3.0
        
        # Inverse relationship
        pause = max_pause - (density * (max_pause - min_pause))
        
        # Add some variation
        pause *= random.uniform(0.7, 1.3)
        
        return pause
    
    def build_ssml(self, text: str) -> str:
        """Build SSML with prosody tags based on parameters"""
        rate = self.params['speech_rate']
        pitch_var = self.params['pitch_variation']
        
        # Convert rate to percentage
        rate_percent = f"{int(rate * 100)}%"
        
        # Pitch variation: map 0-1 to specific pitch changes
        if pitch_var < 0.3:
            pitch = "low"
        elif pitch_var < 0.6:
            pitch = "medium"
        else:
            pitch = "+5%"
        
        ssml = f'''<speak>
    <prosody rate="{rate_percent}" pitch="{pitch}">
        {text}
    </prosody>
</speak>'''
        
        return ssml
    
    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: Text to convert (can include SSML)
            voice_id: ElevenLabs voice ID
            
        Returns:
            Audio data as bytes
        """
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
    
    def generate_utterance_audio(self) -> tuple[bytes, float]:
        """
        Generate a single utterance with audio
        
        Returns:
            Tuple of (audio_data, pause_duration)
        """
        # Generate utterance text
        utterance = self.language_generator.generate_utterance(
            laughter_prob=self.params['laughter_frequency'],
            agreement_prob=0.25
        )
        
        # Build SSML
        ssml = self.build_ssml(utterance)
        
        # Get speaker
        voice_id = self.get_next_speaker()
        
        # Generate audio
        print(f"Generating: '{utterance}' (voice: {voice_id})")
        audio_data = self.text_to_speech(ssml, voice_id)
        
        # Calculate pause
        pause_duration = self.calculate_pause_duration()
        
        return audio_data, pause_duration
    
    def play_audio(self, audio_data: bytes):
        """Play audio data"""
        # Note: This requires simpleaudio or similar library
        # You might want to use pygame or pydub instead
        try:
            wave_obj = sa.WaveObject.from_wave_file(BytesIO(audio_data))
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            print(f"Error playing audio: {e}")
            print("You may need to save to file and play manually")
    
    def save_audio(self, audio_data: bytes, filename: str):
        """Save audio data to file"""
        with open(filename, 'wb') as f:
            f.write(audio_data)
        print(f"Saved audio to {filename}")
    
    def generate_session(self, duration_seconds: int = 60, save_to_files: bool = False):
        """
        Generate a continuous soundscape session
        
        Args:
            duration_seconds: How long to generate for
            save_to_files: Whether to save individual utterances to files
        """
        print(f"Starting soundscape session for {duration_seconds} seconds...")
        print(f"Parameters: {json.dumps(self.params, indent=2)}")
        
        start_time = time.time()
        utterance_count = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                # Generate utterance
                audio_data, pause_duration = self.generate_utterance_audio()
                utterance_count += 1
                
                # Save if requested
                if save_to_files:
                    filename = f"soundscape_{utterance_count:04d}.mp3"
                    self.save_audio(audio_data, filename)
                
                # Play audio (comment out if you just want to save files)
                # self.play_audio(audio_data)
                
                # Pause between utterances
                print(f"Pausing for {pause_duration:.2f} seconds...")
                time.sleep(pause_duration)
                
            except KeyboardInterrupt:
                print("\nStopping session...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
        
        elapsed = time.time() - start_time
        print(f"\nSession complete!")
        print(f"Generated {utterance_count} utterances in {elapsed:.1f} seconds")


def main():
    """Main function with example usage"""
    
    # Get API key from environment or prompt
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        api_key = input("Enter your ElevenLabs API key: ")
    
    # Create synthesizer
    synth = SoundscapeSynthesizer(api_key)
    
    # Example: Adjust parameters
    synth.set_parameter('speech_rate', 0.75)  # Slower speech
    synth.set_parameter('softness', 0.9)       # Very soft consonants
    synth.set_parameter('conversation_density', 0.4)  # More spacious
    synth.set_parameter('laughter_frequency', 0.2)    # Occasional laughter
    
    # Generate a 60-second session, saving to files
    synth.generate_session(duration_seconds=60, save_to_files=True)
    
    # Example: Generate a single utterance
    # audio_data, pause = synth.generate_utterance_audio()
    # synth.save_audio(audio_data, "test_utterance.mp3")


if __name__ == "__main__":
    main()
