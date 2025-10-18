"""
Audio Merger
Concatenates individual clips into a single sequential conversation.
Adds natural pauses between speakers using personality-aware sampling.
"""

import os
import subprocess
from src.generation.personality import sample_conversation_pause
from src.utils.config_loader import load_config


def merge_clips(config: dict, verbose: bool = True) -> str:
    """
    Merge all audio clips into a single conversation file.

    Args:
        config: Configuration dictionary from config_loader
        verbose: Whether to print progress messages

    Returns:
        Path to the merged output file
    """
    clips_dir = config['paths']['clips_dir']
    output_file = config['paths']['merged_file']

    if verbose:
        print(f"\n[Merge Clips]")
        print(f"  Input: {clips_dir}")
        print(f"  Output: {output_file}")

    # Get all clip files
    clip_files = sorted([
        os.path.join(clips_dir, f)
        for f in os.listdir(clips_dir)
        if f.startswith('clip_') and f.endswith('.mp3')
    ])

    if not clip_files:
        raise FileNotFoundError(f"No clips found in {clips_dir}")

    if verbose:
        print(f"  Found {len(clip_files)} clips")

    # Build ffmpeg concat list with pauses
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

    if verbose:
        print(f"  Built concat list with variable pauses")

    # Run ffmpeg to concatenate
    if verbose:
        print(f"  Running ffmpeg...")

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
        "-i", "concat_list.txt",
        "-c", "copy",
        "-y",
        output_relative
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=clips_dir
    )

    if result.returncode != 0:
        raise Exception(f"ffmpeg failed: {result.stderr.decode()}")

    # Clean up concat list
    try:
        os.remove(concat_file)
    except:
        pass

    return output_file


def merge_audio_clips(config_path: str = "config.yaml"):
    """
    Merge all audio clips into a single conversation file (legacy wrapper).
    Adds variable pauses between clips based on conversation pause distribution.
    """
    print("=" * 60)
    print("Audio Merger - Creating Sequential Conversation")
    print("=" * 60)

    # Load configuration
    print("\n[1/2] Loading configuration...")
    config = load_config(config_path)

    # Merge clips
    print("\n[2/2] Merging clips...")
    try:
        output_file = merge_clips(config, verbose=True)
        print(f"\n[OK] Success!")
        print(f"  Output: {output_file}")
        print("\nNext step:")
        print("  Run: python spatialize_audio.py (creates 3D layered soundscape)")
        print("\n" + "=" * 60)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


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
