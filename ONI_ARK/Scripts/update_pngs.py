import os
import re
import random
import subprocess
import sys

try:
    from PIL import Image
except ImportError:
    print("Pillow not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

work_dir = r"\kanimal-SE\sample_anim"
scml_path = os.path.join(work_dir, "achievement_fixed.scml")

with open(scml_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
modified_count = 0
for line in lines:
    if '<file ' in line and 'width="1"' in line and 'height="1"' in line:
        match = re.search(r'name="([^"]+)"', line)
        if match:
            filename = match.group(1)
            file_path = os.path.join(work_dir, filename)
            
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
            img = Image.new("RGBA", (20, 20), color)
            try:
                img.save(file_path)
                print(f"Created 20x20 random block for {filename} with color {color}")
            except Exception as e:
                print(f"Failed to create {filename}: {e}")
            
            line = line.replace('width="1"', 'width="20"')
            line = line.replace('height="1"', 'height="20"')
            modified_count += 1
    
    new_lines.append(line)

with open(scml_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Updated {modified_count} file definitions in achievement_fixed.scml.")
