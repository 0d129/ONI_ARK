import xml.etree.ElementTree as ET

def test():
    tree = ET.parse('achievement_fixed.scml')
    root = tree.getroot()
    
    multiple_files_in_timeline = False
    for anim in root.findall('.//animation'):
        t_dict = {t.get('name'): t for t in anim.findall('.//timeline')}
        for t_name, t1 in t_dict.items():
            files = set()
            for obj in t1.findall('.//object'):
                files.add(obj.get('file'))
            if len(files) > 1:
                multiple_files_in_timeline = True
                print(f"Multiple files in {anim.get('name')} -> {t_name}: {files}")
                
    if not multiple_files_in_timeline:
        print("No timeline has multiple files!")

if __name__ == '__main__':
    test()
