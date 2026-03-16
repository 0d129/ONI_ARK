import re

def reassign_file_ids(input_file, output_file):
    # 以 UTF-8 编码读取所有行
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_id = 167
    # Python 列表索引从 0 开始，因此第 172 行的索引是 171
    start_index = 171 
    
    # 从第 172 行开始遍历
    for i in range(start_index, len(lines)):
        line = lines[i]
        
        # 遇到结束标签，停止修改
        if '</folder>' in line:
            break
            
        # 确保只修改包含 <file 且有 id 属性的行
        if '<file ' in line and 'id=' in line:
            # 使用正则表达式匹配 id="任意数字" 并替换为新的顺序 ID
            # count=1 确保每行只替换第一个匹配项
            lines[i] = re.sub(r'id="\d+"', f'id="{current_id}"', line, count=1)
            current_id += 1

    # 将修改后的全部内容写入新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print(f"✅ 处理完成！最后一个分配的 ID 是: {current_id - 1}")

# --- 使用方法 ---
# 请将 'input.xml' 替换为你的实际文件名
# 修改后的内容会存入 'output.xml'，这样不会直接覆盖原文件，更安全
if __name__ == '__main__':
    input_filename = 'char_150_snakek.scml'   
    output_filename = 'char_150_snakek_reordered.scml' 
    reassign_file_ids(input_filename, output_filename)