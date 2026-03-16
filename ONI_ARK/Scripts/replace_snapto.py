import os
import re
import shutil

base_dir = r'kanimal-SE'
target_dir = r'kanimal-SE\sample_anim'
scml_path = os.path.join(target_dir, 'achievement_fixed.scml')

with open(scml_path, 'r', encoding='utf-8') as f:
    scml_lines = f.readlines()

# Find all files with width="20" height="20"
target_names = []
for line in scml_lines:
    if '<file ' in line and 'width="20"' in line and 'height="20"' in line:
        match = re.search(r'<file .*? name="([^"]+)"', line)
        if match:
            target_names.append(match.group(1))

print(f'Found {len(target_names)} files to replace.')

low_res_dirs = [d for d in os.listdir(base_dir) if d.endswith('_low_res')]
component_data = {}

for d in low_res_dirs:
    dir_path = os.path.join(base_dir, d)
    scml_file = None
    for f in os.listdir(dir_path):
        if f.endswith('.scml'):
            scml_file = os.path.join(dir_path, f)
            break
    
    if scml_file:
        with open(scml_file, 'r', encoding='utf-8') as sf:
            for line in sf:
                match = re.search(r'<file .*? name="([^"]+)" width="([^"]+)" height="([^"]+)" pivot_x="([^"]+)" pivot_y="([^"]+)"', line)
                if match:
                    name = match.group(1)
                    width = match.group(2)
                    height = match.group(3)
                    pivot_x = match.group(4)
                    pivot_y = match.group(5)
                    
                    component_data[name] = {
                        'origin_file': os.path.join(dir_path, name),
                        'width': width,
                        'height': height,
                        'pivot_x': pivot_x,
                        'pivot_y': pivot_y,
                        'dir': dir_path
                    }

print(f'Found {len(component_data)} component definitions in low_res folders.')

def find_match(target_name):
    base = target_name.replace('.png', '')
    if base.endswith('_0'):
        base = base[:-2]
        
    # Check if it starts with snapto_ and we want to strip it
    if base.startswith('snapto_'):
        base_snapto = base[7:] # remove 'snapto_'
        for comp_name, data in component_data.items():
            if comp_name.startswith(base_snapto):
                return comp_name, data
                
    # Normal match
    for comp_name, data in component_data.items():
        if comp_name.startswith(base):
            return comp_name, data
            
    return None, None

replacements = 0
for target_name in target_names:
    comp_name, data = find_match(target_name)
    if comp_name:
        dir_path = data['dir']
        base_match = '_'.join(comp_name.split('_')[:-1])
        if not base_match:
            base_match = comp_name.split('.')[0]
        
        actual_file = None
        # Find the actual PNG file that corresponds to the SCML entry
        for f in os.listdir(dir_path):
            if (f.startswith(base_match) or f.startswith(comp_name.replace('.png', ''))) and f.endswith('.png'):
                actual_file = os.path.join(dir_path, f)
                break
        
        if actual_file:
            dest_file = os.path.join(target_dir, target_name)
            shutil.copy2(actual_file, dest_file)
            print(f'Copied {actual_file} to {dest_file}')
            
            for i, line in enumerate(scml_lines):
                if f'name="{target_name}"' in line:
                    scml_lines[i] = re.sub(
                        r'width="[^"]*" height="[^"]*" pivot_x="[^"]*" pivot_y="[^"]*"',
                        f'width="{data["width"]}" height="{data["height"]}" pivot_x="{data["pivot_x"]}" pivot_y="{data["pivot_y"]}"',
                        line
                    )
            replacements += 1
        else:
            print(f'Could not find actual png file for {comp_name} in {dir_path}')
    else:
        print(f'No match found for {target_name}')

with open(scml_path, 'w', encoding='utf-8') as f:
    f.writelines(scml_lines)

print(f'Replaced {replacements} files.')
