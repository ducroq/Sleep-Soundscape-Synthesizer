"""
Audio Spatializer
Creates a 3D soundscape by layering multiple conversations with stereo positioning.
Generates the final immersive sleep soundscape.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import subprocess
from typing import List, Tuple
from src.utils.config_loader import load_config


def spatialize_audio(config_path: str = "config.yaml"):
    """
    Create 3D soundscape by layering conversations with stereo positioning.
    
    Process:
    1. Generate multiple conversation layers from the same base conversation
    2. Apply stereo panning to each layer (left, center, right)
    3. Apply volume adjustments
    4. Add time offsets so layers overlap naturally
    5. Mix all layers together
    """
    print("=" * 60)
    print("Audio Spatializer - Creating 3D Soundscape")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/5] Loading configuration...")
    config = load_config(config_path)
    
    merged_file = config['paths']['merged_file']
    output_file = config['paths']['spatialized_file']
    
    spat_config = config.get('spatialization', {})
    num_layers = spat_config.get('num_layers', 3)
    stereo_positions = spat_config.get('stereo_positions', [-0.6, 0.0, 0.5])
    volume_adjustments = spat_config.get('volume_adjustments', [0.7, 0.8, 0.6])
    time_offsets = spat_config.get('time_offsets', [0.0, 5.0, 12.0])
    
    # Verify merged file exists
    if not os.path.exists(merged_file):
        print(f"\n  Error: Merged conversation file not found: {merged_file}")
        print("  Run: python merge_audio.py first")
        return
    
    print(f"  Input: {merged_file}")
    print(f"  Layers: {num_layers}")
    
    # Build ffmpeg filter complex
    print("\n[2/5] Building spatial audio filters...")
    
    # Input specifications
    inputs = []
    filter_parts = []
    
    for i in range(num_layers):
        # Each layer reads from the same merged file with a time delay
        inputs.extend(["-ss", str(time_offsets[i]), "-i", merged_file])
        
        # Build filter for this layer:
        # 1. Apply volume adjustment
        # 2. Apply stereo panning
        pan_value = stereo_positions[i]  # -1 (left) to +1 (right)
        volume = volume_adjustments[i]
        
        # Convert pan value to stereo balance
        # pan=0.0 -> balance both channels equally
        # pan=-1.0 -> 100% left, 0% right
        # pan=+1.0 -> 0% left, 100% right
        left_gain = (1.0 - pan_value) / 2.0 * volume
        right_gain = (1.0 + pan_value) / 2.0 * volume
        
        filter_parts.append(
            f"[{i}:a]volume={volume},pan=stereo|c0={left_gain}*c0+{left_gain}*c1|c1={right_gain}*c0+{right_gain}*c1[a{i}]"
        )
    
    # Mix all processed layers together
    mix_inputs = ''.join([f"[a{i}]" for i in range(num_layers)])
    filter_parts.append(f"{mix_inputs}amix=inputs={num_layers}:duration=longest:dropout_transition=2[aout]")
    
    filter_complex = ';'.join(filter_parts)
    
    print("  Spatial configuration:")
    for i in range(num_layers):
        position = "LEFT" if stereo_positions[i] < -0.3 else "RIGHT" if stereo_positions[i] > 0.3 else "CENTER"
        print(f"    Layer {i+1}: {position:6s} | Vol: {volume_adjustments[i]:.1f} | Offset: {time_offsets[i]:.1f}s")
    
    # Run ffmpeg
    print("\n[3/5] Mixing spatial layers with ffmpeg...")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "ffmpeg",
        *inputs,  # All input files
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "2",  # High quality MP3
        "-y",  # Overwrite output
        output_file
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if result.returncode != 0:
        print(f"  Error: ffmpeg failed")
        print(result.stderr.decode())
        return
    
    # Get file info
    print("\n[4/5] Verifying output...")
    
    if os.path.exists(output_file):
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"  ✓ File created: {file_size_mb:.1f} MB")
    
    # Get duration using ffprobe
    duration_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        output_file
    ]
    
    duration_result = subprocess.run(
        duration_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if duration_result.returncode == 0:
        duration = float(duration_result.stdout.decode().strip())
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"  ✓ Duration: {minutes}m {seconds}s")
    
    print("\n[5/5] Complete!")
    print(f"\n  🎵 Final soundscape: {output_file}")
    print("\nYour sleep soundscape is ready!")
    print("The file contains multiple overlapping conversations")
    print("with natural stereo positioning for an immersive experience.")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    # Allow custom config path
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    try:
        spatialize_audio(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
