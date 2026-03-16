import os
import re
import csv
from collections import defaultdict

def analyze_ark_deep_parts_to_csv(base_folder, output_csv_path):
    if not os.path.exists(base_folder):
        print(f"错误: 找不到根目录 '{base_folder}'")
        return

    part_stats = defaultdict(int)
    valid_char_count = 0

    print("正在扫描深层目录，请稍候...")

    # 遍历 D:\ARK_chara 下的所有角色文件夹
    for char_name in os.listdir(base_folder):
        char_dir = os.path.join(base_folder, char_name)
        
        if not os.path.isdir(char_dir):
            continue
            
        # 拼装深层 extracted 目录路径
        extracted_dir_name = f"build_{char_name}_extracted"
        target_dir = os.path.join(
            char_dir, 
            "Building", 
            f"build_{char_name}", 
            extracted_dir_name
        )
        
        if not os.path.exists(target_dir):
            continue
            
        valid_char_count += 1
        char_parts = set()

        # 遍历 PNG 文件并清洗名称
        for file in os.listdir(target_dir):
            if file.lower().endswith('.png'):
                base_name = os.path.splitext(file)[0]
                
                # 清洗前缀
                clean_name = re.sub(r'^[FBfb]_', '', base_name)
                
                # 循环清洗变体和表情后缀
                while True:
                    prev_name = clean_name
                    clean_name = re.sub(
                        r'_(?:[A-Z]|\d+|anger|close|cloes|cry|stun|happy|sad|open)$', 
                        '', 
                        clean_name, 
                        flags=re.IGNORECASE
                    )
                    if clean_name == prev_name:
                        break
                
                char_parts.add(clean_name)
        
        # 计入总统计
        for part in char_parts:
            part_stats[part] += 1

    if valid_char_count == 0:
        print(f"没有找到任何符合深层目录结构的角色！请检查路径。")
        return

    # 按覆盖率从高到低排序
    sorted_parts = sorted(part_stats.items(), key=lambda item: item[1], reverse=True)

    # --- 导出到 CSV ---
    try:
        # 使用 utf-8-sig 编码，确保 Excel 打开不乱码
        with open(output_csv_path, mode='w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            
            # 写入表头
            writer.writerow(['部件名称 (Part Name)', '出现角色数 (Count)', '覆盖率 (Coverage)'])
            
            # 写入数据
            for part, count in sorted_parts:
                percentage = (count / valid_char_count) * 100
                # 覆盖率保留两位小数并加上百分号
                writer.writerow([part, count, f"{percentage:.2f}%"])
                
        print(f"\n✅ 扫描完毕！共处理了 {valid_char_count} 个角色的基建骨骼。")
        print(f"✅ 统计结果已成功保存至: {os.path.abspath(output_csv_path)}")
        
    except Exception as e:
        print(f"❌ 写入 CSV 文件时发生错误: {e}")

if __name__ == "__main__":
    # 你的方舟根目录
    root_folder = r"D:\ARK_chara"
    
    # 导出的 CSV 文件名（默认保存在脚本运行的同级目录下）
    output_file = "ark_parts_statistics.csv"
    
    analyze_ark_deep_parts_to_csv(root_folder, output_file)