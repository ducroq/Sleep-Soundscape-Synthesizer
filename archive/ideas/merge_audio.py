#!/usr/bin/env python3
"""
Merge Soundscape Files
Combines all generated soundscape_*.mp3 files into a single audio file
"""

import os
import glob
import re


def merge_with_pydub():
    """Merge using pydub library"""
    try:
        from pydub import AudioSegment
    except ImportError:
        print("❌ pydub not installed. Install with: pip install pydub")
        print("   You'll also need ffmpeg installed on your system")
        return False
    
    # Find all soundscape files
    files = sorted(glob.glob("soundscape_*.mp3"), key=lambda x: int(re.search(r'(\d+)', x).group()))
    
    if not files:
        print("❌ No soundscape_*.mp3 files found in current directory")
        return False
    
    print(f"📂 Found {len(files)} files to merge")
    print(f"   First: {files[0]}")
    print(f"   Last:  {files[-1]}")
    
    # Load and concatenate
    print("\n🔄 Merging files...")
    combined = AudioSegment.empty()
    
    for i, file in enumerate(files, 1):
        print(f"   [{i}/{len(files)}] Adding {file}...", end='\r')
        audio = AudioSegment.from_mp3(file)
        combined += audio
    
    print("\n✅ All files loaded")
    
    # Export
    output_file = "soundscape_complete.mp3"
    print(f"\n💾 Exporting to {output_file}...")
    combined.export(output_file, format="mp3", bitrate="192k")
    
    duration_min = len(combined) / 1000 / 60
    file_size_mb = os.path.getsize(output_file) / 1024 / 1024
    
    print(f"\n✅ Complete!")
    print(f"   Output: {output_file}")
    print(f"   Duration: {duration_min:.1f} minutes")
    print(f"   Size: {file_size_mb:.1f} MB")
    
    return True


def merge_with_ffmpeg():
    """Generate ffmpeg command for merging"""
    files = sorted(glob.glob("soundscape_*.mp3"), key=lambda x: int(re.search(r'(\d+)', x).group()))
    
    if not files:
        print("❌ No soundscape_*.mp3 files found in current directory")
        return False
    
    print(f"📂 Found {len(files)} files")
    
    # Create file list for ffmpeg
    with open('filelist.txt', 'w') as f:
        for file in files:
            f.write(f"file '{file}'\n")
    
    print("\n✅ Created filelist.txt")
    print("\nRun this ffmpeg command to merge:")
    print("  ffmpeg -f concat -safe 0 -i filelist.txt -c copy soundscape_complete.mp3")
    
    return True


def main():
    print("=" * 60)
    print("  🎵 Soundscape File Merger")
    print("=" * 60)
    
    print("\nSelect merge method:")
    print("1. Use pydub (Python library, recommended)")
    print("2. Generate ffmpeg command (manual)")
    
    choice = input("\nChoice (1-2, default 1): ").strip() or '1'
    
    if choice == '1':
        if not merge_with_pydub():
            print("\nFalling back to ffmpeg method...")
            merge_with_ffmpeg()
    else:
        merge_with_ffmpeg()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
