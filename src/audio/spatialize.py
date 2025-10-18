"""
Audio Spatializer
Creates a 3D soundscape by layering multiple conversations with stereo positioning.
Generates the final immersive sleep soundscape.
"""

import os
import subprocess
from typing import List, Tuple
from src.utils.config_loader import load_config


def create_spatial_soundscape(config: dict, verbose: bool = True) -> str:
    """
    Create 3D soundscape by layering conversations with stereo positioning.

    Args:
        config: Configuration dictionary from config_loader
        verbose: Whether to print progress messages

    Returns:
        Path to the spatialized output file
    """
    merged_file = config['paths']['merged_file']
    output_file = config['paths']['spatialized_file']

    spat_config = config['spatialization']
    num_layers = spat_config['num_layers']
    stereo_positions = spat_config['stereo_positions']
    volume_adjustments = spat_config['volume_adjustments']
    time_offsets = spat_config['time_offsets']

    # Verify merged file exists
    if not os.path.exists(merged_file):
        raise FileNotFoundError(f"Merged conversation file not found: {merged_file}")

    if verbose:
        print(f"\n[3D Spatializer]")
        print(f"  Input: {merged_file}")
        print(f"  Layers: {num_layers}")

    # Build ffmpeg filter complex
    inputs = []
    filter_parts = []

    for i in range(num_layers):
        # Each layer reads from the same merged file with a time delay
        inputs.extend(["-ss", str(time_offsets[i]), "-i", merged_file])

        # Build filter for this layer
        pan_value = stereo_positions[i]
        volume = volume_adjustments[i]

        # Convert pan value to stereo balance
        left_gain = (1.0 - pan_value) / 2.0 * volume
        right_gain = (1.0 + pan_value) / 2.0 * volume

        filter_parts.append(
            f"[{i}:a]volume={volume},pan=stereo|c0={left_gain}*c0+{left_gain}*c1|c1={right_gain}*c0+{right_gain}*c1[a{i}]"
        )

    # Mix all processed layers together
    mix_inputs = ''.join([f"[a{i}]" for i in range(num_layers)])
    filter_parts.append(f"{mix_inputs}amix=inputs={num_layers}:duration=longest:dropout_transition=2[aout]")

    filter_complex = ';'.join(filter_parts)

    if verbose:
        print("  Spatial configuration:")
        for i in range(num_layers):
            position = "LEFT" if stereo_positions[i] < -0.3 else "RIGHT" if stereo_positions[i] > 0.3 else "CENTER"
            print(f"    Layer {i+1}: {position:6s} | Vol: {volume_adjustments[i]:.1f} | Offset: {time_offsets[i]:.1f}s")

    # Run ffmpeg
    if verbose:
        print(f"  Running ffmpeg...")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "2",
        "-y",
        output_file
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        raise Exception(f"ffmpeg failed: {result.stderr.decode()}")

    # Get file info
    if verbose and os.path.exists(output_file):
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"  File created: {file_size_mb:.1f} MB")

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
            print(f"  Duration: {minutes}m {seconds}s")

    return output_file


def spatialize_audio(config_path: str = "config.yaml"):
    """
    Create 3D soundscape by layering conversations with stereo positioning (legacy wrapper).
    """
    print("=" * 60)
    print("Audio Spatializer - Creating 3D Soundscape")
    print("=" * 60)

    # Load configuration
    print("\n[1/2] Loading configuration...")
    config = load_config(config_path)

    # Create spatial soundscape
    print("\n[2/2] Creating spatial soundscape...")
    try:
        output_file = create_spatial_soundscape(config, verbose=True)
        print(f"\n[OK] Success!")
        print(f"\nYour sleep soundscape is ready!")
        print(f"  Final soundscape: {output_file}")
        print("\nThe file contains multiple overlapping conversations")
        print("with natural stereo positioning for an immersive experience.")
        print("\n" + "=" * 60)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


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
