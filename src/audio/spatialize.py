"""
Audio Spatialization Module
Creates 3D spatial soundscapes from audio clips.

Supports two output modes:
- Stereo MP3: Ready-to-listen spatial mix with panning
- Multichannel WAV: Individual layers for manual mixing in Audacity
"""

import subprocess
import os
import sys
import random
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))
print(f"Added to sys.path: {project_root}")

from src.utils.config_loader import load_config
from src.utils.logger import setup_logger
   
logger = setup_logger(__name__)

def get_audio_duration(file_path):
    """Get duration of an audio file using ffprobe"""
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.getcwd()
        )
        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting duration for {file_path}: {e}")
        return 0.0


def create_stereo_spatial_mix(clips_dir='output/clips', output_file='output/final/soundscape_spatial.mp3', config=None, shuffle=None, reuse_clips=None):
    """
    Create the traditional stereo spatial mix (existing functionality)
    
    Args:
        clips_dir: Directory containing audio clips
        output_file: Output MP3 file path
        config: Configuration dict (loaded if None)
        shuffle: If True, randomize clip order for each layer (None = use config)
        reuse_clips: If True, reuse all clips for each layer (None = use config)
    """
    if config is None:
        config = load_config()
    
    # Get spatialization config
    spatial_config = config.get('spatialization', {})
    num_layers = spatial_config.get('num_layers', 3)
    stereo_positions = spatial_config.get('stereo_positions', [-0.7, 0.0, 0.7])
    volume_adjustments = spatial_config.get('volume_adjustments', [0.6, 0.8, 0.6])
    time_offsets = spatial_config.get('time_offsets', [0.0, 5.0, 10.0])
    
    # Get shuffle/reuse settings from config (can be overridden by function args)
    config_shuffle = spatial_config.get('shuffle_clips', True)
    config_reuse = spatial_config.get('reuse_clips', True)
    config_target_duration = spatial_config.get('target_duration_minutes', None)
    
    # Use provided args or fall back to config
    if shuffle is None:
        shuffle = config_shuffle
    if reuse_clips is None:
        reuse_clips = config_reuse
    
    logger.info(f"Creating stereo spatial mix with {num_layers} layers...")
    logger.info(f"Settings: shuffle={shuffle}, reuse_clips={reuse_clips}")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Get all clips
    all_clips = sorted([f for f in os.listdir(clips_dir) if f.endswith('.mp3')])
    
    if not all_clips:
        logger.error(f"No audio clips found in {clips_dir}")
        return False
    
    logger.info(f"Found {len(all_clips)} clips")
    
    # Calculate total available duration
    total_clip_duration = 0.0
    for clip in all_clips[:min(5, len(all_clips))]:  # Sample first 5 clips
        clip_path = os.path.join(clips_dir, clip)
        total_clip_duration += get_audio_duration(clip_path)
    
    if total_clip_duration > 0:
        avg_clip_duration = total_clip_duration / min(5, len(all_clips))
        estimated_total_duration = avg_clip_duration * len(all_clips)
        logger.info(f"Estimated total clip duration: {estimated_total_duration:.1f}s (~{estimated_total_duration/60:.1f} min)")
    else:
        avg_clip_duration = 10.0  # Fallback estimate
        estimated_total_duration = avg_clip_duration * len(all_clips)
    
    # Handle target duration
    if config_target_duration and config_target_duration > 0:
        target_seconds = config_target_duration * 60
        logger.info(f"Target duration: {config_target_duration:.1f} minutes ({target_seconds:.0f}s)")
        
        if reuse_clips:
            # Calculate how many times we need to repeat clips to reach target
            repeat_factor = max(1, int(target_seconds / estimated_total_duration))
            if repeat_factor > 1:
                logger.info(f"Will repeat clip set {repeat_factor}x to reach target duration")
                # Extend all_clips by repeating
                all_clips = all_clips * repeat_factor
                logger.info(f"Extended to {len(all_clips)} total clips")
        else:
            logger.warning(f"Target duration set but reuse_clips=False - cannot extend duration")
            logger.warning(f"Enable reuse_clips or increase num_clips to reach target duration")
    
    # Determine clips per layer based on reuse setting
    if reuse_clips:
        clips_per_layer = len(all_clips)
        logger.info(f"Each layer will use all {clips_per_layer} clips (shuffled differently)")
    else:
        clips_per_layer = len(all_clips) // num_layers
        logger.info(f"Dividing {len(all_clips)} clips across {num_layers} layers ({clips_per_layer} per layer)")
    
    # Build filter complex for each layer
# First, create concatenated tracks for each layer (same as multichannel approach)
    temp_layer_files = []
    
    for layer_idx in range(num_layers):
        # Get clips for this layer based on settings
        if reuse_clips:
            # Each layer gets all clips in a different random order
            layer_clips = all_clips.copy()
            if shuffle:
                random.seed(layer_idx * 12345)  # Deterministic but different per layer
                random.shuffle(layer_clips)
        else:
            # Divide clips across layers (old behavior)
            start_idx = layer_idx * clips_per_layer
            end_idx = start_idx + clips_per_layer if layer_idx < num_layers - 1 else len(all_clips)
            layer_clips = all_clips[start_idx:end_idx]
            if shuffle:
                random.seed(layer_idx * 12345)
                random.shuffle(layer_clips)
        
        position = stereo_positions[layer_idx]
        volume = volume_adjustments[layer_idx]
        time_offset = time_offsets[layer_idx]
        
        logger.info(f"Layer {layer_idx + 1}: {len(layer_clips)} clips, position={position:.1f}, volume={volume:.1f}, offset={time_offset:.1f}s")
        
        # Create temp concatenated file for this layer
        temp_file = f"output/final/temp_stereo_layer_{layer_idx}.mp3"
        temp_layer_files.append(temp_file)
        
        # Write concat list to temp file
        concat_list_file = f"output/final/temp_stereo_concat_{layer_idx}.txt"
        with open(concat_list_file, 'w') as f:
            for clip in layer_clips:
                clip_path = os.path.join(clips_dir, clip)
                f.write(f"file '{os.path.abspath(clip_path)}'\n")
        
        # Concatenate clips for this layer
        cmd_concat = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list_file,
            '-c:a', 'copy',  # Just copy, don't re-encode
            temp_file
        ]
        
        try:
            subprocess.run(cmd_concat, check=True, capture_output=True, cwd=os.getcwd())
            logger.info(f"  ✓ Layer {layer_idx + 1} concatenated")
            
            # Clean up concat list
            os.remove(concat_list_file)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error concatenating layer {layer_idx}: {e}")
            logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
            # Clean up any temp files
            for temp_file in temp_layer_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return False
    
    # Now build filter complex using the temp layer files (much shorter command!)
    filter_parts = []
    
    for layer_idx in range(num_layers):
        position = stereo_positions[layer_idx]
        volume = volume_adjustments[layer_idx]
        time_offset = time_offsets[layer_idx]
        
        # Apply delay if needed
        if time_offset > 0:
            delay_ms = int(time_offset * 1000)
            filter_parts.append(f"[{layer_idx}:a]adelay={delay_ms}|{delay_ms}[layer{layer_idx}_delayed]")
            current_stream = f"layer{layer_idx}_delayed"
        else:
            current_stream = f"{layer_idx}:a"
        
        # Apply stereo panning and volume
        filter_parts.append(
            f"[{current_stream}]"
            f"volume={volume},"
            f"stereotools=mlev=1:mpan={position}"
            f"[layer{layer_idx}_final]"
        )
    
    # Mix all layers together
    mix_inputs = ''.join([f"[layer{i}_final]" for i in range(num_layers)])
    filter_parts.append(f"{mix_inputs}amix=inputs={num_layers}:duration=longest[out]")
    
    # Join all filter parts
    filter_complex = ';'.join(filter_parts)
    
    # Build ffmpeg command (now with only 7 input files instead of 1470!)
    cmd = ['ffmpeg', '-y']
    
    # Add temp layer files as inputs
    for temp_file in temp_layer_files:
        cmd.extend(['-i', temp_file])
    
    # Add filter complex
    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[out]',
        '-c:a', 'libmp3lame',
        '-b:a', '32k',
        '-ar', '22050',
        output_file
    ])
    
    logger.info("Running ffmpeg for stereo spatial mix...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, cwd=os.getcwd())
        logger.info(f"✓ Stereo spatial mix created: {output_file}")
        
        # Clean up temp layer files
        for temp_file in temp_layer_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating stereo spatial mix: {e}")
        logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
        
        # Clean up temp layer files
        for temp_file in temp_layer_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return False


def create_spatial_soundscape(config: dict, verbose: bool = True) -> str:
    """
    Create 3D spatialized soundscape (wrapper for pipeline integration).

    This is the main entry point called by the unified pipeline.
    Creates a stereo MP3 spatial mix from the merged conversation file.

    Args:
        config: Configuration dictionary from config_loader
        verbose: Whether to print progress messages

    Returns:
        Path to the spatialized output file
    """
    clips_dir = config['paths']['clips_dir']
    output_file = config['paths']['spatialized_file']

    if verbose:
        print(f"\n[Spatial Soundscape]")
        print(f"  Input: {clips_dir}")
        print(f"  Output: {output_file}")

    # Use the stereo spatial mix function
    success = create_stereo_spatial_mix(
        clips_dir=clips_dir,
        output_file=output_file,
        config=config,
        shuffle=None,  # Use config defaults
        reuse_clips=None  # Use config defaults
    )

    if not success:
        raise Exception("Spatialization failed")

    return output_file


def spatialize_audio(config_path: str = "config.yaml"):
    """
    Create 3D spatialized soundscape (legacy wrapper for archive scripts).

    This maintains backward compatibility with archive/spatialize_audio.py
    """
    print("=" * 60)
    print("Audio Spatialization - Creating 3D Soundscape")
    print("=" * 60)

    # Load configuration
    print("\n[1/2] Loading configuration...")
    config = load_config(config_path)

    # Create spatial soundscape
    print("\n[2/2] Creating spatial soundscape...")
    try:
        output_file = create_spatial_soundscape(config, verbose=True)
        print(f"\n[OK] Success!")
        print(f"  Output: {output_file}")
        print("\nYour 3D soundscape is ready!")
        print("  Listen with headphones for best spatial effect 🎧")
        print("\n" + "=" * 60)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


def create_multichannel_wav(clips_dir='output/clips', output_file='output/final/soundscape_multichannel.wav', config=None, shuffle=None, reuse_clips=None):
    """
    Create multichannel WAV with each conversation layer as a separate channel
    Perfect for manual mixing/editing in Audacity
    
    Args:
        clips_dir: Directory containing audio clips
        output_file: Output WAV file path
        config: Configuration dict (loaded if None)
        shuffle: If True, randomize clip order for each layer (None = use config)
        reuse_clips: If True, reuse all clips for each layer (None = use config)
    
    Output format:
        - WAV file with N channels (one per conversation layer)
        - Each channel contains a complete conversation layer
        - Can be opened in Audacity for manual mixing/panning
        - Sample rate: 44.1kHz (CD quality for editing)
        - Bit depth: 16-bit PCM
    """
    if config is None:
        config = load_config()
    
    # Get spatialization config
    spatial_config = config.get('spatialization', {})
    num_layers = spatial_config.get('num_layers', 3)
    time_offsets = spatial_config.get('time_offsets', [0.0, 5.0, 10.0])
    
    # Get shuffle/reuse settings from config (can be overridden by function args)
    config_shuffle = spatial_config.get('shuffle_clips', True)
    config_reuse = spatial_config.get('reuse_clips', True)
    config_target_duration = spatial_config.get('target_duration_minutes', None)
    
    # Use provided args or fall back to config
    if shuffle is None:
        shuffle = config_shuffle
    if reuse_clips is None:
        reuse_clips = config_reuse
    
    logger.info(f"Creating multichannel WAV with {num_layers} channels...")
    logger.info(f"Settings: shuffle={shuffle}, reuse_clips={reuse_clips}")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Get all clips
    all_clips = sorted([f for f in os.listdir(clips_dir) if f.endswith('.mp3')])
    
    if not all_clips:
        logger.error(f"No audio clips found in {clips_dir}")
        return False
    
    logger.info(f"Found {len(all_clips)} clips")
    
    # Calculate total available duration
    total_clip_duration = 0.0
    for clip in all_clips[:min(5, len(all_clips))]:  # Sample first 5 clips
        clip_path = os.path.join(clips_dir, clip)
        total_clip_duration += get_audio_duration(clip_path)
    
    if total_clip_duration > 0:
        avg_clip_duration = total_clip_duration / min(5, len(all_clips))
        estimated_total_duration = avg_clip_duration * len(all_clips)
        logger.info(f"Estimated total clip duration: {estimated_total_duration:.1f}s (~{estimated_total_duration/60:.1f} min)")
    else:
        avg_clip_duration = 10.0  # Fallback estimate
        estimated_total_duration = avg_clip_duration * len(all_clips)
    
    # Handle target duration
    if config_target_duration and config_target_duration > 0:
        target_seconds = config_target_duration * 60
        logger.info(f"Target duration: {config_target_duration:.1f} minutes ({target_seconds:.0f}s)")
        
        if reuse_clips:
            # Calculate how many times we need to repeat clips to reach target
            repeat_factor = max(1, int(target_seconds / estimated_total_duration))
            if repeat_factor > 1:
                logger.info(f"Will repeat clip set {repeat_factor}x to reach target duration")
                # Extend all_clips by repeating
                all_clips = all_clips * repeat_factor
                logger.info(f"Extended to {len(all_clips)} total clips")
        else:
            logger.warning(f"Target duration set but reuse_clips=False - cannot extend duration")
            logger.warning(f"Enable reuse_clips or increase num_clips to reach target duration")
    
    # Determine clips per layer based on reuse setting
    if reuse_clips:
        # Each layer gets ALL clips (in different random orders)
        clips_per_layer = len(all_clips)
        logger.info(f"Each layer will use all {clips_per_layer} clips (shuffled differently)")
    else:
        # Divide clips across layers (old behavior)
        clips_per_layer = len(all_clips) // num_layers
        logger.info(f"Dividing {len(all_clips)} clips across {num_layers} layers ({clips_per_layer} per layer)")
    
    # First, create concatenated tracks for each layer
    temp_layer_files = []
    max_duration = 0.0
    
    for layer_idx in range(num_layers):
        # Get clips for this layer based on settings
        if reuse_clips:
            # Each layer gets all clips in a different random order
            layer_clips = all_clips.copy()
            if shuffle:
                random.seed(layer_idx * 12345)  # Deterministic but different per layer
                random.shuffle(layer_clips)
        else:
            # Divide clips across layers (old behavior)
            start_idx = layer_idx * clips_per_layer
            end_idx = start_idx + clips_per_layer if layer_idx < num_layers - 1 else len(all_clips)
            layer_clips = all_clips[start_idx:end_idx]
            if shuffle:
                random.seed(layer_idx * 12345)
                random.shuffle(layer_clips)
        
        time_offset = time_offsets[layer_idx]
        
        logger.info(f"Channel {layer_idx + 1}: {len(layer_clips)} clips, offset={time_offset:.1f}s")
        
        # Create temp file for this layer
        temp_file = f"output/final/temp_layer_{layer_idx}.wav"
        temp_layer_files.append(temp_file)
        
        # Build concat command
        concat_inputs = []
        for clip in layer_clips:
            clip_path = os.path.join(clips_dir, clip)
            concat_inputs.append(f"file '{os.path.abspath(clip_path)}'")
        
        # Write concat list to temp file
        concat_list_file = f"output/final/temp_concat_{layer_idx}.txt"
        with open(concat_list_file, 'w') as f:
            f.write('\n'.join(concat_inputs))
        
        # Concatenate clips for this layer
        cmd_concat = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list_file,
            '-ar', '44100',  # CD quality for editing
            '-ac', '1',  # Mono for each layer
            '-c:a', 'pcm_s16le',  # 16-bit PCM
            temp_file
        ]
        
        try:
            subprocess.run(cmd_concat, check=True, capture_output=True, cwd=os.getcwd())
            
            # Get duration
            duration = get_audio_duration(temp_file)
            adjusted_duration = duration + time_offset
            max_duration = max(max_duration, adjusted_duration)
            
            logger.info(f"  ✓ Layer {layer_idx + 1} concatenated: {duration:.1f}s (+ {time_offset:.1f}s offset)")
            
            # Clean up concat list
            os.remove(concat_list_file)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error concatenating layer {layer_idx}: {e}")
            logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
            # Clean up any temp files
            for temp_file in temp_layer_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return False
    
    logger.info(f"Max duration: {max_duration:.1f}s")
    
    # Now create filter complex to combine all layers into multichannel output
    filter_parts = []
    
    # Apply time delays to each layer and pad to max duration
    for layer_idx in range(num_layers):
        time_offset = time_offsets[layer_idx]
        
        if time_offset > 0:
            delay_ms = int(time_offset * 1000)
            filter_parts.append(f"[{layer_idx}:a]adelay={delay_ms}[delayed{layer_idx}]")
            current_stream = f"delayed{layer_idx}"
        else:
            current_stream = f"{layer_idx}:a"
        
        # Pad to max duration
        filter_parts.append(f"[{current_stream}]apad=whole_dur={max_duration}[padded{layer_idx}]")
    
    # Join all padded streams into multichannel output
    join_inputs = ''.join([f"[padded{i}]" for i in range(num_layers)])
    filter_parts.append(f"{join_inputs}join=inputs={num_layers}:channel_layout={num_layers}c[out]")
    
    filter_complex = ';'.join(filter_parts)
    
    # Build final ffmpeg command
    cmd_final = ['ffmpeg', '-y']
    
    # Add all layer files as inputs
    for temp_file in temp_layer_files:
        cmd_final.extend(['-i', temp_file])
    
    # Add filter complex and output
    cmd_final.extend([
        '-filter_complex', filter_complex,
        '-map', '[out]',
        '-ar', '44100',
        '-c:a', 'pcm_s16le',
        output_file
    ])
    
    logger.info("Running ffmpeg for multichannel merge...")
    try:
        subprocess.run(cmd_final, check=True, capture_output=True, cwd=os.getcwd())
        logger.info(f"✓ Multichannel WAV created: {output_file}")
        logger.info(f"  Format: {num_layers}-channel WAV, 44.1kHz, 16-bit PCM")
        logger.info(f"  Duration: {max_duration:.1f}s")
        logger.info(f"  Ready for Audacity import!")
        
        # Clean up temp files
        for temp_file in temp_layer_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating multichannel WAV: {e}")
        logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
        
        # Clean up temp files
        for temp_file in temp_layer_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return False


def main():
    """Main function - creates both stereo MP3 and multichannel WAV"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Spatialize audio clips into overlapping layers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create both formats with shuffled, reused clips (recommended)
  %(prog)s --format both
  
  # Create multichannel only without shuffling (old behavior)
  %(prog)s --format multichannel --no-shuffle --no-reuse
  
  # Create stereo with shuffling but no reuse (divide clips across layers)
  %(prog)s --format stereo --shuffle --no-reuse
        """
    )
    parser.add_argument('--clips-dir', default='output/clips', help='Directory containing audio clips')
    parser.add_argument('--output-dir', default='output/final', help='Output directory')
    parser.add_argument('--format', choices=['stereo', 'multichannel', 'both'], default='both',
                        help='Output format: stereo MP3, multichannel WAV, or both (default: both)')
    parser.add_argument('--shuffle', dest='shuffle', action='store_true',
                        help='Shuffle clips for each layer (overrides config)')
    parser.add_argument('--no-shuffle', dest='shuffle', action='store_false',
                        help='Use sequential clip order (overrides config)')
    parser.add_argument('--reuse', dest='reuse_clips', action='store_true',
                        help='Reuse all clips for each layer (overrides config)')
    parser.add_argument('--no-reuse', dest='reuse_clips', action='store_false',
                        help='Divide clips across layers (overrides config)')
    parser.set_defaults(shuffle=None, reuse_clips=None)  # None = use config values
    
    args = parser.parse_args()
    
    # Load config
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Determine final values (CLI overrides config)
    spatial_config = config.get('spatialization', {})
    final_shuffle = args.shuffle if args.shuffle is not None else spatial_config.get('shuffle_clips', True)
    final_reuse = args.reuse_clips if args.reuse_clips is not None else spatial_config.get('reuse_clips', True)
    final_target = spatial_config.get('target_duration_minutes', None)
    
    # Log settings
    logger.info("=" * 60)
    logger.info("SPATIALIZATION SETTINGS")
    logger.info("=" * 60)
    logger.info(f"Shuffle clips: {final_shuffle}" + 
                (" (from CLI)" if args.shuffle is not None else " (from config)"))
    logger.info(f"Reuse clips across layers: {final_reuse}" +
                (" (from CLI)" if args.reuse_clips is not None else " (from config)"))
    if final_target:
        logger.info(f"Target duration: {final_target} minutes (from config)")
    logger.info(f"Format: {args.format}")
    logger.info("")
    
    success = True
    
    # Create stereo spatial mix
    if args.format in ['stereo', 'both']:
        logger.info("=" * 60)
        logger.info("Creating stereo spatial MP3...")
        logger.info("=" * 60)
        stereo_output = os.path.join(args.output_dir, 'soundscape_spatial.mp3')
        if not create_stereo_spatial_mix(args.clips_dir, stereo_output, config, args.shuffle, args.reuse_clips):
            success = False
        logger.info("")
    
    # Create multichannel WAV
    if args.format in ['multichannel', 'both']:
        logger.info("=" * 60)
        logger.info("Creating multichannel WAV for Audacity...")
        logger.info("=" * 60)
        multichannel_output = os.path.join(args.output_dir, 'soundscape_multichannel.wav')
        if not create_multichannel_wav(args.clips_dir, multichannel_output, config, args.shuffle, args.reuse_clips):
            success = False
        logger.info("")
    
    if success:
        logger.info("=" * 60)
        logger.info("✓ Audio spatialization complete!")
        logger.info("=" * 60)
        
        if args.format in ['stereo', 'both']:
            logger.info(f"Stereo MP3: {os.path.join(args.output_dir, 'soundscape_spatial.mp3')}")
            logger.info("  → Ready to listen! 🎧")
        
        if args.format in ['multichannel', 'both']:
            logger.info(f"Multichannel WAV: {os.path.join(args.output_dir, 'soundscape_multichannel.wav')}")
            logger.info("  → Open in Audacity to mix individual conversation layers! 🎛️")
        
        logger.info("")
        if final_reuse:
            logger.info("💡 Clips were reused across all layers (longer conversations)")
        else:
            logger.info("💡 Clips were divided across layers (shorter, non-overlapping)")
        
        if final_shuffle:
            logger.info("💡 Clips were shuffled for each layer (varied conversations)")
        else:
            logger.info("💡 Clips used sequential order")
    else:
        logger.error("Some operations failed. Please check the logs above.")


if __name__ == '__main__':
    main()
