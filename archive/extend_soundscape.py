"""
Extend Soundscape - Reuse clips to create longer compositions
Creates multiple variations of the same clips for extended playtime
"""

import os
import yaml
import random
import subprocess
import numpy as np
from pathlib import Path


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def extend_soundscape(
    target_duration_minutes: int = 30,
    num_variations: int = 3,
    config_path: str = "config.yaml"
):
    """
    Extend soundscape by creating variations and concatenating them.
    
    Args:
        target_duration_minutes: Desired duration in minutes
        num_variations: Number of different orderings to create
        config_path: Path to config file
    """
    print("=" * 70)
    print(f"Extending Soundscape to ~{target_duration_minutes} minutes")
    print("=" * 70)
    
    config = load_config(config_path)
    clips_dir = config['paths']['clips_dir']
    output_dir = config['paths']['output_dir']
    
    # Get all clips
    print(f"\n[1/5] Loading clips from {clips_dir}...")
    clip_files = sorted([
        os.path.join(clips_dir, f)
        for f in os.listdir(clips_dir)
        if f.startswith('clip_') and f.endswith('.mp3')
    ])
    
    if not clip_files:
        print(f"  Error: No clips found in {clips_dir}")
        print(f"  Run: python generate_soundscape.py first")
        return
    
    print(f"  Found {len(clip_files)} clips")
    
    # Calculate how many variations needed
    avg_clip_duration = 4  # seconds (rough estimate)
    avg_pause = 1.2
    variation_duration = len(clip_files) * (avg_clip_duration + avg_pause)
    num_repeats = int((target_duration_minutes * 60) / variation_duration) + 1
    
    print(f"\n[2/5] Planning extension...")
    print(f"  Estimated variation duration: {variation_duration:.0f}s")
    print(f"  Creating {num_variations} variations")
    print(f"  Repeating {num_repeats} times each")
    print(f"  Total estimated duration: {num_variations * num_repeats * variation_duration / 60:.1f} minutes")
    
    # Create variations
    print(f"\n[3/5] Creating {num_variations} variations with different orderings...")
    variation_files = []
    
    for v in range(num_variations):
        print(f"  Variation {v+1}/{num_variations}...")
        
        # Shuffle clips (different order)
        shuffled_clips = clip_files.copy()
        random.shuffle(shuffled_clips)
        
        # Build concat list with pauses
        concat_list = []
        for i, clip_file in enumerate(shuffled_clips):
            concat_list.append(f"file '{os.path.abspath(clip_file)}'")
            
            # Add pause after each clip except the last
            if i < len(shuffled_clips) - 1:
                # Sample pause from distribution
                pause_mean = config['conversation']['pause_distribution']['mean']
                pause_std = config['conversation']['pause_distribution']['std']
                pause_duration = max(0.5, np.random.normal(pause_mean, pause_std))
                concat_list.append(f"duration {pause_duration:.2f}")
        
        # Write concat list
        concat_file = os.path.join(clips_dir, f"concat_variation_{v+1}.txt")
        with open(concat_file, 'w') as f:
            f.write('\n'.join(concat_list))
        
        # Merge this variation (use relative paths with cwd)
        variation_output = os.path.join(output_dir, f"variation_{v+1}.mp3")
        output_relative = os.path.relpath(variation_output, clips_dir)
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", f"concat_variation_{v+1}.txt",  # Relative to clips_dir
            "-c", "copy",
            "-y",
            output_relative  # Relative to clips_dir
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=clips_dir
        )
        
        if result.returncode == 0:
            variation_files.append(variation_output)
            print(f"    ✓ Created {os.path.basename(variation_output)}")
        else:
            print(f"    ✗ Failed: {result.stderr.decode()[:100]}")
    
    # Repeat variations to reach target duration
    print(f"\n[4/5] Repeating variations to reach target duration...")
    extended_list = []
    for r in range(num_repeats):
        for vf in variation_files:
            extended_list.append(f"file '{os.path.abspath(vf)}'")
    
    # Write extended concat list
    extended_concat_file = os.path.join(output_dir, "concat_extended.txt")
    with open(extended_concat_file, 'w') as f:
        f.write('\n'.join(extended_list))
    
    # Create extended base conversation
    extended_output = os.path.join(output_dir, f"conversation_extended_{target_duration_minutes}min.mp3")
    
    print(f"  Concatenating {len(extended_list)} segments...")
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", extended_concat_file,  # Use absolute path, no cwd
        "-c", "copy",
        "-y",
        extended_output
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        # No cwd parameter - use absolute paths
    )
    
    if result.returncode != 0:
        print(f"  Error: {result.stderr.decode()[:200]}")
        return
    
    print(f"  ✓ Created extended conversation")
    
    # Get actual duration
    duration_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        extended_output
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
        print(f"  ✓ Actual duration: {minutes}m {seconds}s")
    
    # Spatialize - use DIFFERENT variations for each layer
    print(f"\n[5/5] Creating spatialized 3D version with parallel conversations...")
    spat_output = os.path.join(output_dir, f"soundscape_extended_{target_duration_minutes}min.mp3")
    
    # Use existing spatialization config
    spat_config = config.get('spatialization', {})
    num_layers = min(spat_config.get('num_layers', 3), len(variation_files))  # Can't have more layers than variations
    stereo_positions = spat_config.get('stereo_positions', [-0.6, 0.0, 0.5])
    volume_adjustments = spat_config.get('volume_adjustments', [0.7, 0.8, 0.6])
    time_offsets = spat_config.get('time_offsets', [0.0, 5.0, 12.0])
    
    print(f"  Using {num_layers} parallel conversation layers")
    
    # Build extended versions for EACH layer using DIFFERENT variations
    layer_files = []
    for layer_idx in range(num_layers):
        print(f"  Building layer {layer_idx + 1}/{num_layers}...")
        
        # Create a different sequence for this layer
        # Rotate which variations are used and in what order
        layer_list = []
        for r in range(num_repeats):
            for v_idx, vf in enumerate(variation_files):
                # Each layer uses variations in different order
                rotated_idx = (v_idx + layer_idx) % len(variation_files)
                layer_list.append(f"file '{os.path.abspath(variation_files[rotated_idx])}'")
        
        # Write layer concat list
        layer_concat_file = os.path.join(output_dir, f"concat_layer_{layer_idx + 1}.txt")
        with open(layer_concat_file, 'w') as f:
            f.write('\n'.join(layer_list))
        
        # Create this layer's file
        layer_output = os.path.join(output_dir, f"layer_{layer_idx + 1}_temp.mp3")
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", layer_concat_file,
            "-c", "copy",
            "-y",
            layer_output
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            layer_files.append(layer_output)
        else:
            print(f"    ✗ Failed to create layer {layer_idx + 1}")
            continue
    
    if len(layer_files) < num_layers:
        print(f"  Warning: Only created {len(layer_files)} layers instead of {num_layers}")
    
    # Now spatialize using DIFFERENT files for each layer
    print(f"  Mixing {len(layer_files)} layers with stereo positioning...")
    
    # Build ffmpeg filter
    inputs = []
    filter_parts = []
    
    for i, layer_file in enumerate(layer_files):
        inputs.extend(["-ss", str(time_offsets[i]), "-i", layer_file])
        
        pan_value = stereo_positions[i]
        volume = volume_adjustments[i]
        left_gain = (1.0 - pan_value) / 2.0 * volume
        right_gain = (1.0 + pan_value) / 2.0 * volume
        
        filter_parts.append(
            f"[{i}:a]volume={volume},pan=stereo|c0={left_gain}*c0+{left_gain}*c1|c1={right_gain}*c0+{right_gain}*c1[a{i}]"
        )
    
    mix_inputs = ''.join([f"[a{i}]" for i in range(len(layer_files))])
    filter_parts.append(f"{mix_inputs}amix=inputs={len(layer_files)}:duration=longest:dropout_transition=2[aout]")
    filter_complex = ';'.join(filter_parts)
    
    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "2",
        "-y",
        spat_output
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if result.returncode == 0:
        print(f"  ✓ Created spatialized version")
        
        # Clean up temporary layer files
        for layer_file in layer_files:
            try:
                os.remove(layer_file)
            except:
                pass
    else:
        print(f"  ✗ Failed: {result.stderr.decode()[:200]}")
    
    print("\n" + "=" * 70)
    print("✓ Extended soundscape complete!")
    print(f"\n  Base conversation: {extended_output}")
    print(f"  3D soundscape:     {spat_output}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import sys
    
    # Allow custom duration
    if len(sys.argv) > 1:
        target_minutes = int(sys.argv[1])
    else:
        target_minutes = 30  # Default: 30 minutes
    
    try:
        extend_soundscape(target_duration_minutes=target_minutes)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
