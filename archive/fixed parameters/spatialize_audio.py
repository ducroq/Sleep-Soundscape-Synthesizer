#!/usr/bin/env python3
"""
Spatialize Soundscape
Creates multiple overlapping conversation layers with stereo positioning
"""

import os
import random
import subprocess
import glob
import re
import json


def load_audio_info(file_path):
    """Get audio duration using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        file_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def spatialize_soundscape(
    input_dir='output',
    output_name='soundscape_spatial.mp3',
    num_layers=3,
    layer_volumes=[0.7, 0.5, 0.4],  # Closer to further
    layer_pans=[-0.6, 0.0, 0.6],    # Left, center, right (-1.0 to 1.0)
    overlap_offset=0.5               # Seconds between layer starts
):
    """
    Create spatially positioned overlapping conversations
    
    Args:
        input_dir: Directory with soundscape_*.mp3 files
        output_name: Output filename
        num_layers: Number of simultaneous conversation layers
        layer_volumes: Volume for each layer (0.0-1.0)
        layer_pans: Stereo pan for each layer (-1.0=left, 1.0=right)
        overlap_offset: Time offset between layers starting (seconds)
    """
    
    # Find all soundscape files
    pattern = os.path.join(input_dir, 'soundscape_*.mp3')
    all_files = glob.glob(pattern)
    
    if not all_files:
        print(f"❌ No soundscape_*.mp3 files found in {input_dir}/")
        return False
    
    # Sort numerically
    def extract_number(filepath):
        match = re.search(r'soundscape_(\d+)\.mp3', os.path.basename(filepath))
        return int(match.group(1)) if match else 0
    
    all_files.sort(key=extract_number)
    
    print(f"📂 Found {len(all_files)} audio clips")
    print(f"🎚️  Creating {num_layers} spatial layers")
    
    # Distribute files across layers
    random.shuffle(all_files)  # Randomize to avoid patterns
    layer_files = [[] for _ in range(num_layers)]
    
    for i, file in enumerate(all_files):
        layer_idx = i % num_layers
        layer_files[layer_idx].append(file)
    
    for i, files in enumerate(layer_files):
        print(f"   Layer {i+1}: {len(files)} clips (pan: {layer_pans[i]:+.1f}, volume: {layer_volumes[i]:.1f})")
    
    # Create concat files for each layer
    layer_concat_files = []
    for i in range(num_layers):
        concat_filename = f'layer_{i}_concat.txt'
        concat_path = os.path.join(input_dir, concat_filename)
        with open(concat_path, 'w', encoding='utf-8') as f:
            for file in layer_files[i]:
                f.write(f"file '{os.path.basename(file)}'\n")
        layer_concat_files.append(concat_path)  # Store full path for cleanup
    
    # Build ffmpeg command to merge layers with spatial effects
    print("\n🔄 Mixing layers with spatial positioning...")
    
    # Generate temporary layer files
    layer_temp_files = []
    for i in range(num_layers):
        temp_filename = f'layer_{i}_temp.mp3'
        concat_filename = f'layer_{i}_concat.txt'
        layer_temp_files.append(temp_filename)
        
        # Concatenate each layer (use relative paths since cwd=input_dir)
        concat_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_filename,
            '-c', 'copy',
            '-y',
            temp_filename
        ]
        
        subprocess.run(concat_cmd, cwd=input_dir, capture_output=True, check=True)
        print(f"   ✓ Created layer {i+1}")
    
    # Now mix all layers with volume and pan adjustments
    output_path = os.path.join(input_dir, output_name)  # Full path for later use
    
    # Build filter complex for mixing
    # For each layer: apply volume, pan, and delay
    filter_parts = []
    for i in range(num_layers):
        delay_ms = int(overlap_offset * 1000 * i)
        volume = layer_volumes[i]
        pan = layer_pans[i]  # -1.0 (left) to 1.0 (right)
        
        # Convert pan to stereo coefficients
        # pan=-1: left=1.0, right=0.0
        # pan=0:  left=0.5, right=0.5
        # pan=1:  left=0.0, right=1.0
        left_gain = (1.0 - pan) / 2.0
        right_gain = (1.0 + pan) / 2.0
        
        filter_parts.append(
            f"[{i}:a]volume={volume},adelay={delay_ms}|{delay_ms},"
            f"pan=stereo|c0={left_gain}*c0+{left_gain}*c1|c1={right_gain}*c0+{right_gain}*c1[a{i}]"
        )
    
    # Combine all processed layers
    filter_complex = ";".join(filter_parts)
    amix_inputs = "".join([f"[a{i}]" for i in range(num_layers)])
    filter_complex += f";{amix_inputs}amix=inputs={num_layers}:duration=longest[aout]"
    
    # Build full ffmpeg command
    input_args = []
    for temp_file in layer_temp_files:
        input_args.extend(['-i', temp_file])
    
    mix_cmd = [
        'ffmpeg',
        *input_args,
        '-filter_complex', filter_complex,
        '-map', '[aout]',
        '-c:a', 'libmp3lame',
        '-b:a', '192k',
        '-y',
        output_name  # Just filename, we're running from input_dir
    ]
    
    print("\n🎛️  Applying spatial effects...")
    try:
        subprocess.run(mix_cmd, cwd=input_dir, capture_output=True, text=True, check=True)
        
        # Clean up temporary files
        print("\n🗑️  Cleaning up temporary files...")
        for concat_file in layer_concat_files:
            os.remove(concat_file)
        for temp_filename in layer_temp_files:
            temp_path = os.path.join(input_dir, temp_filename)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # Get file stats
        file_size_mb = os.path.getsize(output_path) / 1024 / 1024
        
        print(f"\n✅ Complete!")
        print(f"   Output: {output_path}")
        print(f"   Size: {file_size_mb:.1f} MB")
        print(f"   Layers: {num_layers} overlapping conversations")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ffmpeg error:")
        print(e.stderr)
        return False


def main():
    print("=" * 60)
    print("  🌊 Soundscape Spatializer")
    print("=" * 60)
    
    print("\nConfiguration:")
    print("  Layers: 3 (left, center, right)")
    print("  Volumes: Foreground (0.7), Mid (0.5), Background (0.4)")
    print("  Overlap: 0.5 second offset between layers")
    
    confirm = input("\nProceed with these settings? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\nCustomize settings in the script if needed.")
        return
    
    success = spatialize_soundscape(
        num_layers=3,
        layer_volumes=[0.7, 0.5, 0.4],
        layer_pans=[-0.6, 0.0, 0.6],
        overlap_offset=0.5
    )
    
    if success:
        print("\n💡 Tip: Listen with headphones to experience the spatial effect!")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()