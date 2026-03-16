import xml.etree.ElementTree as ET

def test():
    tree = ET.parse('achievement_fixed.scml')
    root = tree.getroot()
    
    mismatch_count = 0
    mismatch_18_count = 0
    for anim in root.findall('.//animation'):
        t_dict = {t.get('name'): t for t in anim.findall('.//timeline')}
        for t_name, t1 in t_dict.items():
            if t_name.endswith('_1'):
                t0_name = t_name[:-2] + '_0'
                if t0_name in t_dict:
                    t0 = t_dict[t0_name]
                    obj0 = t0.find('.//object')
                    obj1 = t1.find('.//object')
                    if obj0 is not None and obj1 is not None:
                        if obj0.get('file') != obj1.get('file'):
                            mismatch_count += 1
                            if obj1.get('file') == '18':
                                mismatch_18_count += 1

    print(f"Total mismatches: {mismatch_count}")
    print(f"Mismatches where _1 has file='18': {mismatch_18_count}")

if __name__ == '__main__':
    test()
