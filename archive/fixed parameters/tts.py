#!/usr/bin/env python3
"""
Simple text-to-speech using ElevenLabs API
"""

import os
import requests
import yaml
import subprocess


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def text_to_speech(text, voice_id, api_key, output_file='output.mp3', fade_duration=0.02):
    """
    Convert text to speech using ElevenLabs, with fade-in/fade-out
    
    Args:
        text: Text or SSML to convert
        voice_id: ElevenLabs voice ID
        api_key: Your API key
        output_file: Where to save the MP3
        fade_duration: Fade duration in seconds (default 0.02 = 20ms)
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
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
        # Save to temporary file first
        temp_file = output_file + '.temp.mp3'
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Apply fade-in and fade-out using ffmpeg to prevent clicks
        fade_cmd = [
            'ffmpeg',
            '-i', temp_file,
            '-af', f'afade=t=in:d={fade_duration},afade=t=out:d={fade_duration}',
            '-y',
            output_file
        ]
        
        try:
            subprocess.run(fade_cmd, capture_output=True, check=True)
            os.remove(temp_file)  # Clean up temp file
            print(f"✅ Saved to {output_file}")
            return True
        except subprocess.CalledProcessError:
            # If fade fails, just use the original
            os.rename(temp_file, output_file)
            print(f"✅ Saved to {output_file} (no fade applied)")
            return True
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return False


if __name__ == '__main__':
    import sys
    
    # Get API key
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("Error: Set ELEVENLABS_API_KEY environment variable")
        sys.exit(1)
    
    # Load config
    config = load_config()
    
    # Get text from command line or use example
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    else:
        text = "<speak><prosody rate='85%' pitch='medium'>mila sora venita</prosody></speak>"
    
    # Use first voice from config
    voice_id = config['voices'][0]['id']
    
    # Generate
    print(f"Generating speech with voice {voice_id}...")
    text_to_speech(text, voice_id, api_key)