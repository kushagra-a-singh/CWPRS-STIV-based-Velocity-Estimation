import os
import numpy as np
import re
import shutil

# Folder containing your calibration and DISTO files
path = r"D:\STIV-based-Velocity-Estimation\DISTO_values"

# Files we expect for app_calibration / freehelper
expected_files = [
    "cross_section.txt",
    "GCPs.txt",
    "shoreline.txt",
    "cross_section_offset.txt",
    "profile_offset.txt",
    "watercolumn.txt"
]

def clean_line(line):
    """Remove brackets, commas, and non-numeric chars except minus/decimal."""
    # Replace commas with spaces
    line = line.replace(",", " ")
    # Remove brackets and other unwanted chars
    line = re.sub(r"[\[\]\(\)]", "", line)
    # Remove multiple spaces
    line = re.sub(r"\s+", " ", line).strip()
    return line

def process_file(filepath):
    """Clean and reformat a single file."""
    print(f"\n🧹 Cleaning {os.path.basename(filepath)}...")

    # Backup original
    backup_path = filepath + ".bak"
    shutil.copy(filepath, backup_path)

    cleaned_lines = []
    with open(filepath, "r") as f:
        for line in f:
            line = clean_line(line)
            if not line:
                continue
            parts = line.split()
            # Keep only first 3 numeric values (X Y Z)
            nums = [p for p in parts if re.match(r"^-?\d+(\.\d+)?$", p)]
            if len(nums) >= 3:
                cleaned_lines.append(" ".join(nums[:3]))
            elif len(nums) == 1:  # offset file
                cleaned_lines.append(nums[0])

    # Save cleaned data
    with open(filepath, "w") as f:
        for line in cleaned_lines:
            f.write(line + "\n")

    # Check final shape
    try:
        arr = np.loadtxt(filepath)
        print(f"✅ Cleaned OK — shape: {arr.shape}")
    except Exception as e:
        print(f"⚠️ Could not load after cleaning: {e}")

def main():
    for fname in expected_files:
        fpath = os.path.join(path, fname)
        if os.path.isfile(fpath):
            process_file(fpath)
        else:
            print(f"❌ Missing {fname}, skipping")

if __name__ == "__main__":
    main()
