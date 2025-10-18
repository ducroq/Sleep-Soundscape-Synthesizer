#!/usr/bin/env python3
"""
Merge Soundscape Files
Combines all generated soundscape_*.mp3 files into a single audio file using ffmpeg
"""

import os
import glob
import re
import subprocess


def merge_soundscape_files(output_dir='output', output_name='soundscape_complete.mp3'):
    """
    Merge all soundscape_*.mp3 files in the output directory using ffmpeg
    
    Args:
        output_dir: Directory containing the MP3 files
        output_name: Name for the merged output file
    """
    
    # Find all soundscape files
    pattern = os.path.join(output_dir, 'soundscape_*.mp3')
    files = glob.glob(pattern)
    
    if not files:
        print(f"❌ No soundscape_*.mp3 files found in {output_dir}/")
        return False
    
    # Sort files numerically by the number in the filename
    def extract_number(filepath):
        match = re.search(r'soundscape_(\d+)\.mp3', os.path.basename(filepath))
        return int(match.group(1)) if match else 0
    
    files.sort(key=extract_number)
    
    print(f"📂 Found {len(files)} files to merge")
    print(f"   First: {os.path.basename(files[0])}")
    print(f"   Last:  {os.path.basename(files[-1])}")
    
    # Create filelist.txt for ffmpeg
    filelist_path = os.path.join(output_dir, 'filelist.txt')
    with open(filelist_path, 'w', encoding='utf-8') as f:
        for file in files:
            # Use relative path for the filelist
            relative_path = os.path.basename(file)
            f.write(f"file '{relative_path}'\n")
    
    print(f"\n✅ Created filelist.txt with {len(files)} files")
    
    # Merge using ffmpeg
    output_path = os.path.join(output_dir, output_name)
    
    print(f"\n🔄 Merging files with ffmpeg...")
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'filelist.txt',  # Just the filename, since we're running from output_dir
        '-c', 'copy',
        '-y',  # Overwrite output file without asking
        output_name  # Just the filename, not full path
    ]
    
    try:
        result = subprocess.run(
            ffmpeg_cmd,
            cwd=output_dir,  # Run from output directory
            capture_output=True,
            text=True,
            check=True
        )
        
        # Clean up filelist
        os.remove(filelist_path)
        
        # Get file stats (output_path is the full path)
        file_size_mb = os.path.getsize(output_path) / 1024 / 1024
        
        print(f"\n✅ Complete!")
        print(f"   Output: {output_path}")
        print(f"   Size: {file_size_mb:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ffmpeg error:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"\n❌ ffmpeg not found!")
        print("   Make sure ffmpeg is installed and in your PATH")
        print("   Download from: https://ffmpeg.org/download.html")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  🎵 Soundscape File Merger")
    print("=" * 60)
    
    success = merge_soundscape_files()
    
    print("\n" + "=" * 60)