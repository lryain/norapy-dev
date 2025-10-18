#!/usr/bin/env python3
"""
Clean up requirements files by removing -e prefixes
These local paths are handled by install-dev.py instead
"""
import re
from pathlib import Path

def clean_requirements_file(filepath):
    """Remove -e prefixes from requirements file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Remove -e prefix from lines
    # Pattern: -e ../../../path or -e ../../path or -e ../path etc
    lines = content.split('\n')
    cleaned_lines = []
    removed_count = 0
    
    for line in lines:
        if line.strip().startswith('-e '):
            # Extract just the path after -e
            path = line.strip()[3:].strip()
            # Comment it out instead of removing completely
            cleaned_lines.append(f"# {path}  # Local package, installed by install-dev.py")
            removed_count += 1
        else:
            cleaned_lines.append(line)
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    if cleaned_content != original:
        with open(filepath, 'w') as f:
            f.write(cleaned_content)
        return removed_count
    return 0

# Find all requirements files
req_files = list(Path('/home/pi/dev/norapy-dev/engine').glob('**/requirements/*.txt'))

total_removed = 0
modified_files = 0

for req_file in sorted(req_files):
    removed = clean_requirements_file(req_file)
    if removed > 0:
        modified_files += 1
        total_removed += removed
        rel_path = req_file.relative_to('/home/pi/dev/norapy-dev/engine')
        print(f"✓ {rel_path}: removed {removed} -e paths")

print(f"\n{'='*60}")
print(f"Modified {modified_files} files, removed {total_removed} -e paths total")
print(f"Local packages will be installed by install-dev.py instead")
