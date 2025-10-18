"""
Audio Merger
Concatenates individual clips into a single sequential conversation.
Adds natural pauses between speakers using personality-aware sampling.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import subprocess
from personality_sampler import sample_conversation_pause
from src.utils.config_loader import load_config


def merge_audio_clips(config_path: str = "config.yaml"):
    """
    Merge all audio clips into a single conversation file.
    Adds variable pauses between clips based on conversation pause distribution.
    """
    print("=" * 60)
    print("Audio Merger - Creating Sequential Conversation")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/4] Loading configuration...")
    config = load_config(config_path)
    
    clips_dir = config['paths']['clips_dir']
    output_file = config['paths']['merged_file']
    
    # Get all clip files
    print("\n[2/4] Scanning for audio clips...")
    clip_files = sorted([
        os.path.join(clips_dir, f)
        for f in os.listdir(clips_dir)
        if f.startswith('clip_') and f.endswith('.mp3')
    ])
    
    if not clip_files:
        print("  Error: No clips found in", clips_dir)
        return
    
    print(f"  Found {len(clip_files)} clips")
    
    # Build ffmpeg concat list with pauses
    print("\n[3/4] Building concatenation list with pauses...")
    
    concat_list = []
    for i, clip_file in enumerate(clip_files):
        concat_list.append(f"file '{os.path.abspath(clip_file)}'")
        
        # Add pause after each clip except the last
        if i < len(clip_files) - 1:
            # Sample pause duration from distribution
            pause_duration = sample_conversation_pause(config)
            concat_list.append(f"duration {pause_duration:.2f}")
    
    # Write concat list to temp file
    concat_file = os.path.join(clips_dir, "concat_list.txt")
    with open(concat_file, 'w') as f:
        f.write('\n'.join(concat_list))
    
    print(f"  Created concat list with variable pauses")
    
    # Run ffmpeg to concatenate
    print("\n[4/4] Merging clips with ffmpeg...")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Calculate relative path from clips_dir to output_file
    output_relative = os.path.relpath(output_file, clips_dir)
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",  # Relative to clips_dir
        "-c", "copy",
        "-y",  # Overwrite output
        output_relative  # Relative to clips_dir
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=clips_dir
    )
    
    if result.returncode != 0:
        print(f"  Error: ffmpeg failed")
        print(result.stderr.decode())
        return
    
    # Clean up concat list
    try:
        os.remove(concat_file)
    except:
        pass
    
    print(f"\n✓ Success!")
    print(f"  Output: {output_file}")
    print("\nNext step:")
    print("  Run: python spatialize_audio.py (creates 3D layered soundscape)")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    # Allow custom config path
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    try:
        merge_audio_clips(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
