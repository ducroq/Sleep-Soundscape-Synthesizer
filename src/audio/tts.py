"""
Text-to-Speech Module
Interfaces with ElevenLabs API and applies fade-in/fade-out to prevent clicks.
"""

import os
import configparser
import requests
import subprocess
from typing import Optional, Dict, Any


def call_elevenlabs_tts(
    text: str,
    voice_id: str,
    api_key: str,
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True,
    config: Dict[str, Any] = None
) -> bytes:
    """
    Call ElevenLabs TTS API to generate speech.

    Args:
        text: Text or SSML to synthesize
        voice_id: ElevenLabs voice ID
        api_key: ElevenLabs API key
        model_id: Model to use
        output_format: Audio format
        stability: Voice stability (0.0-1.0)
        similarity_boost: Similarity boost (0.0-1.0)
        style: Style exaggeration (0.0-1.0)
        use_speaker_boost: Enable speaker boost
        config: Configuration dictionary from config_loader

    Returns:
        Raw audio bytes (MP3)

    Raises:
        Exception: If API call fails
    """
    # Get API URL from config (validated by config_loader)
    api_url = config['elevenlabs']['api_url']

    url = f"{api_url}/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    # Check if text contains SSML
    is_ssml = text.strip().startswith('<speak>')
    
    data = {
        "text": text,
        "model_id": model_id,
        "output_format": output_format,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        },
        "enable_ssml": is_ssml
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
    
    return response.content


def apply_fade(
    input_audio: bytes,
    fade_duration_ms: int = 20,
    temp_dir: str = "."
) -> bytes:
    """
    Apply fade-in and fade-out to audio to prevent clicks.
    Uses ffmpeg directly via subprocess.
    
    Args:
        input_audio: Raw audio bytes
        fade_duration_ms: Duration of fade in milliseconds
        temp_dir: Directory for temporary files
    
    Returns:
        Processed audio bytes
    """
    # Write input to temp file
    input_path = os.path.join(temp_dir, "temp_input.mp3")
    output_path = os.path.join(temp_dir, "temp_output.mp3")
    
    try:
        # Write input audio
        with open(input_path, "wb") as f:
            f.write(input_audio)
        
        # Calculate fade duration in seconds
        fade_duration_sec = fade_duration_ms / 1000.0
        
        # Build ffmpeg command
        # Use just filenames since we're setting cwd to temp_dir
        cmd = [
            "ffmpeg",
            "-i", "temp_input.mp3",
            "-af", f"afade=t=in:st=0:d={fade_duration_sec},afade=t=out:d={fade_duration_sec}",
            "-c:a", "libmp3lame",
            "-y",  # Overwrite output
            "temp_output.mp3"
        ]
        
        # Run ffmpeg with cwd set to temp_dir
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=temp_dir
        )
        
        if result.returncode != 0:
            raise Exception(f"ffmpeg fade failed: {result.stderr.decode()}")
        
        # Read processed audio
        with open(output_path, "rb") as f:
            processed_audio = f.read()
        
        return processed_audio
    
    finally:
        # Clean up temp files
        for path in [input_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass


def generate_speech(
    text: str,
    voice_id: str,
    output_path: str,
    config: dict,
    apply_fading: bool = False,  # Changed to False by default
    prosody: dict = None
) -> bool:
    """
    Generate speech and save to file.
    
    Args:
        text: Text or SSML to synthesize (SSML will be auto-detected)
        voice_id: ElevenLabs voice ID
        output_path: Where to save the audio file
        config: Configuration dictionary
        apply_fading: Whether to apply fade-in/fade-out (disabled by default - use separate post-processing)
        prosody: Optional prosody parameters (unused - kept for compatibility)
    
    Returns:
        True if successful
    """
    # Get API key from secrets.ini
    from src.utils.config_loader import load_secrets, get_elevenlabs_api_key
    api_key = get_elevenlabs_api_key()
    
    # Get model settings from config (validated by config_loader)
    model_id = config['elevenlabs']['model_id']
    output_format = config['audio']['output_format']

    # Get voice settings from config (validated by config_loader)
    voice_settings = config['elevenlabs']['voice_settings']
    stability = voice_settings['stability']
    similarity_boost = voice_settings['similarity_boost']
    style = voice_settings['style']
    use_speaker_boost = voice_settings['use_speaker_boost']

    # Call API
    audio_bytes = call_elevenlabs_tts(
        text=text,
        voice_id=voice_id,
        api_key=api_key,
        model_id=model_id,
        output_format=output_format,
        stability=stability,
        similarity_boost=similarity_boost,
        style=style,
        use_speaker_boost=use_speaker_boost,
        config=config
    )
    
    # Apply fading if requested (disabled by default - causes audio corruption)
    if apply_fading:
        fade_duration_ms = config['audio']['fade_duration_ms']
        temp_dir = os.path.dirname(output_path) or "."
        audio_bytes = apply_fade(audio_bytes, fade_duration_ms, temp_dir)
    
    # Save to file
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    return True


if __name__ == "__main__":
    # Test TTS functionality
    from src.utils.config_loader import load_config

    print("Testing ElevenLabs TTS...")

    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        print("Error: config/config.yaml not found")
        exit(1)
    
    # Simple test
    test_text = '<speak><prosody rate="85%" pitch="+5%" volume="medium">Hello, this is a test.</prosody></speak>'
    test_voice = config['voices'][0]  # Use first voice
    test_output = "test_output.mp3"
    
    try:
        success = generate_speech(test_text, test_voice, test_output, config)
        if success:
            print(f"Success! Audio saved to {test_output}")
        else:
            print("Failed to generate speech")
    except Exception as e:
        print(f"Error: {e}")
