import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

def process_low_res_folders():
    # 获取当前工作目录
    base_dir = os.getcwd()
    
    # 筛选出所有以 'low_res' 结尾的文件夹
    low_res_dirs = [d for d in os.listdir(base_dir) 
                    if os.path.isdir(os.path.join(base_dir, d)) and d.endswith('low_res')]

    if not low_res_dirs:
        print("当前目录下没有找到以 'low_res' 结尾的文件夹。")
        return

    for d in low_res_dirs:
        folder_path = os.path.join(base_dir, d)
        
        # 查找当前文件夹中的 scml 文件
        scml_files = [f for f in os.listdir(folder_path) if f.endswith('.scml')]
        if not scml_files:
            print(f"⚠️ 文件夹 {d} 中没有找到 .scml 文件，跳过。")
            continue
        
        # 假设每个文件夹只有一个 scml 文件
        scml_path = os.path.join(folder_path, scml_files[0])
        
        # 创建 marked 子文件夹
        marked_dir = os.path.join(folder_path, 'marked')
        os.makedirs(marked_dir, exist_ok=True)
        
        print(f"--- 正在处理文件夹: {d} ---")
        
        # 解析 XML
        try:
            tree = ET.parse(scml_path)
            root = tree.getroot()
        except Exception as e:
            print(f"❌ 解析 {scml_path} 失败: {e}")
            continue

        # 遍历所有的 file 节点
        for file_node in root.iter('file'):
            name = file_node.get('name')
            if not name:
                continue
            
            # 提取属性，如果没写默认按 0 处理
            try:
                width = float(file_node.get('width', 0))
                height = float(file_node.get('height', 0))
                pivot_x = float(file_node.get('pivot_x', 0))
                pivot_y = float(file_node.get('pivot_y', 0))
            except ValueError:
                print(f"⚠️ 解析图片 {name} 的属性时出错，跳过。")
                continue

            # 处理图片路径 (有些 scml 中 name 可能带子路径，提取纯文件名)
            img_filename = os.path.basename(name)
            img_path = os.path.join(folder_path, img_filename)
            
            if not os.path.exists(img_path):
                print(f"⚠️ 找不到图片文件: {img_path}，跳过。")
                continue

            try:
                with Image.open(img_path) as img:
                    # 转换为 RGBA 以确保可以绘制彩色图形（防止原图是纯索引/灰度图）
                    img = img.convert("RGBA")
                    draw = ImageDraw.Draw(img)

                    # 计算像素坐标
                    px = width * pivot_x
                    
                    # 【重要说明】
                    # 标准 Spriter SCML 的 Y 轴起点在左下角 (bottom-up)。
                    # 而图片处理库(PIL)的 Y 轴起点在左上角 (top-down)。
                    # 所以标准的 Y 坐标计算需要用 height 去减。
                    # 如果你的 kanimAL 生成器是左上角起点的，请将此行改为: py = height * pivot_y
                    py = height * (1.0 - pivot_y) 

                    # 绘制红色圆点，半径设为 2 像素
                    r = 2
                    draw.ellipse((px - r, py - r, px + r, py + r), fill='red', outline='red')

                    # 保存到 marked 文件夹
                    save_path = os.path.join(marked_dir, img_filename)
                    img.save(save_path)
                    
            except Exception as e:
                print(f"❌ 处理图片 {name} 时发生错误: {e}")
                
        print(f"✅ 文件夹 {d} 处理完成！")

if __name__ == "__main__":
    process_low_res_folders()