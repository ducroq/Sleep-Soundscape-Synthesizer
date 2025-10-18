#!/usr/bin/env python3
"""
Generate sleep soundscape
"""

import os
import time
import random
import yaml
from pathlib import Path
from generate_language import generate_phrase
from generate_ssml import text_to_ssml
from tts import text_to_speech
import configparser


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def generate_soundscape(config, api_key):
    """Generate complete soundscape session"""
    
    # Create output directory
    output_dir = Path(config['session']['output_dir'])
    output_dir.mkdir(exist_ok=True)
    
    # Calculate duration
    duration_seconds = config['session']['duration_minutes'] * 60
    
    print(f"🎵 Generating {config['session']['duration_minutes']} minute soundscape")
    print(f"📁 Saving to {output_dir}/")
    print()
    
    start_time = time.time()
    utterance_count = 0
    
    while time.time() - start_time < duration_seconds:
        utterance_count += 1
        
        # 1. Generate phrase
        text = generate_phrase(config)
        print(f"[{utterance_count}] {text}")
        
        # 2. Convert to SSML
        ssml = text_to_ssml(text, config)
        
        # 3. Select voice
        voice = random.choice(config['voices'])
        voice_id = voice['id']
        
        # 4. Generate speech with fade-in/fade-out to prevent clicks
        output_file = output_dir / f"soundscape_{utterance_count:04d}.mp3"
        fade_duration = config.get('ssml', {}).get('fade_duration', 0.02)
        text_to_speech(ssml, voice_id, api_key, str(output_file), fade_duration)
        
        # 5. Pause
        pause = random.uniform(
            config['conversation']['min_pause'],
            config['conversation']['max_pause']
        )
        print(f"   Pausing {pause:.1f}s...\n")
        time.sleep(pause)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Generated {utterance_count} utterances in {elapsed:.1f} seconds")


if __name__ == '__main__':
    # Get API key
    secrets = configparser.ConfigParser()
    secrets.read('secrets.ini')
    api_key = secrets.get('elevenlabs', 'api_key')  

    # Load config
    config = load_config()
    
    # Generate
    generate_soundscape(config, api_key)