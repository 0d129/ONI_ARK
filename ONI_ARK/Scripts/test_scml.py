import xml.etree.ElementTree as ET

def test():
    tree = ET.parse('achievement_fixed.scml')
    root = tree.getroot()
    
    count = 0
    for anim in root.findall('.//animation'):
        t_dict = {t.get('name'): t for t in anim.findall('.//timeline')}
        for t_name, t1 in t_dict.items():
            if t_name.endswith('_1'):
                t0_name = t_name[:-1] + '0'
                if t0_name in t_dict:
                    t0 = t_dict[t0_name]
                    # Check keys and objects
                    for k1 in t1.findall('.//key'):
                        obj1 = k1.find('.//object')
                        if obj1 is not None and obj1.get('file') == '18':
                            # Find corresponding key in t0, or just use first key
                            obj0 = t0.find('.//object')
                            if obj0 is not None:
                                print(f"{anim.get('name')} | {t_name} | {obj1.get('file')} -> {obj0.get('file')}")
                                count += 1
    print(f"Total found: {count}")

if __name__ == '__main__':
    test()
