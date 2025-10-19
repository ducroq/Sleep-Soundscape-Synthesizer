import os
import time
import glob
import random

def rename_mp3_files(folder_path):
    """
    Reads all MP3 files in a folder and renames them to clip_XXXXX.mp3,
    where XXXXX is a number derived from the current Unix timestamp.
    """
    # Use glob to find all files ending with .mp3 (case-insensitive)
    # The ** allows for recursive search (if needed), but we focus on one folder here.
    # The os.path.join is used for cross-platform compatibility.
    search_pattern = os.path.join(folder_path, "*.mp3")
    mp3_files = glob.glob(search_pattern)

    if not mp3_files:
        print(f"No MP3 files found in: {folder_path}")
        return

    print(f"Found {len(mp3_files)} MP3 files. Renaming...")

    # Get the current Unix timestamp
    current_time_str = str(int(time.time() * 1000))  # Get milliseconds for more entropy

    # Use a counter to ensure uniqueness even if multiple files are processed
    # within the same millisecond or if the timestamp derivation is the same.
    counter = 0

    for old_path in mp3_files:
        try:
            # 1. Generate the number part (XXXXX)
            # Use the last 6 digits of the current time, plus a unique counter
            # to make it highly unlikely to collide within the script run.
            # We also add a small random element for extra safety.
            
            # Use a slice of the timestamp and the counter for a unique ID
            unique_id = f"{current_time_str[-6:]}_{counter:02d}_{random.randint(0, 99):02d}"
            
            # 2. Construct the new file name
            new_filename = f"clip_{unique_id}.mp3"
            
            # 3. Construct the full new path
            new_path = os.path.join(folder_path, new_filename)

            # 4. Rename the file
            os.rename(old_path, new_path)

            print(f"Renamed: '{os.path.basename(old_path)}' -> '{new_filename}'")
            counter += 1

        except Exception as e:
            print(f"Error renaming file {os.path.basename(old_path)}: {e}")
    
    print("\nFile renaming complete.")

# ====================================================================
# ⚠️ IMPORTANT: Set the path to the folder containing your MP3 files.
# For example, to use a subfolder named 'audio' in the script's directory:
# FOLDER_TO_PROCESS = os.path.join(os.getcwd(), 'audio')
# ====================================================================

# Replace the string below with the actual path to your MP3 folder
FOLDER_TO_PROCESS = r"C:\local_dev\Sleep Soundscape Synthesizer\output\clips" 

# Run the function
rename_mp3_files(FOLDER_TO_PROCESS)