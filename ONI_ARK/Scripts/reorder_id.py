import xml.etree.ElementTree as ET

def reindex_file_ids(input_file, output_file):
    # 解析 XML 文件
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
    except Exception as e:
        print(f"解析 XML 失败: {e}")
        return

    # 初始化计数器
    new_id = 0

    # 遍历所有的 <file> 标签
    # root.iter('file') 会在整个 XML 树中搜索所有名为 'file' 的节点
    for file_elem in root.iter('file'):
        # 将 id 更新为新的连续数字，并转换为字符串格式
        file_elem.set('id', str(new_id))
        new_id += 1

    # 将修改后的内容写入到新的 XML 文件中
    # xml_declaration=True 会保留开头的 <?xml version="1.0"?> 声明
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"处理完成！共重排了 {new_id} 个 file 节点。已保存至: {output_file}")

# 使用示例
if __name__ == "__main__":
    # 你的源文件名
    input_xml = r'D:\FD_Software\kanimal-SE\marked_pngs\char_150_snakek.scml'     # 请将其替换为你的实际文件名
    # 处理后保存的新文件名
    output_xml = r'D:\FD_Software\kanimal-SE\marked_pngs\char_150_snakek_reordered.scml' 

    reindex_file_ids(input_xml, output_xml)
