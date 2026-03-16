import xml.etree.ElementTree as ET

def test_write():
    tree = ET.parse('achievement_fixed.scml')
    tree.write('test_out.scml', encoding='utf-8', xml_declaration=False)

if __name__ == '__main__':
    test_write()
