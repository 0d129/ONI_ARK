import xml.etree.ElementTree as ET

def fix_scml(scml_path='achievement_fixed.scml'):
    print(f"Loading {scml_path}...")
    tree = ET.parse(scml_path)
    root = tree.getroot()
    
    count = 0
    for anim in root.findall('.//animation'):
        # Map timeline names to timeline elements within this animation
        t_dict = {t.get('name'): t for t in anim.findall('.//timeline')}
        
        for t_name, t1 in t_dict.items():
            if t_name.endswith('_1'):
                # Find matching _0 timeline
                t0_name = t_name[:-2] + '_0'
                if t0_name in t_dict:
                    t0 = t_dict[t0_name]
                    
                    # Assume _0 uses a consistent folder and file we can learn from its first object
                    obj0 = t0.find('.//object')
                    if obj0 is not None:
                        folder0 = obj0.get('folder')
                        file0 = obj0.get('file')
                        
                        # Apply this folder and file to all objects in _1 that erroneously point to file "18"
                        for obj1 in t1.findall('.//object'):
                            if obj1.get('file') == '18':
                                if folder0 is not None:
                                    obj1.set('folder', folder0)
                                if file0 is not None:
                                    obj1.set('file', file0)
                                count += 1
                                
    print(f"Fixed {count} object references in {scml_path}")
    
    # Write the modified SCML back
    # The original file does not have an XML declaration at top
    print(f"Saving changes to {scml_path}...")
    tree.write(scml_path, encoding='utf-8', xml_declaration=False)
    print("Done!")

if __name__ == '__main__':
    fix_scml()
