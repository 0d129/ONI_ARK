import os
from PIL import Image

def extract_arknights_atlas_fixed(atlas_path, image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(atlas_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 主图片转换为 RGBA，准备接收 Alpha 通道
    img = Image.open(image_path).convert("RGBA")

    # 1. 动态读取 Atlas 声明的原始尺寸
    atlas_w, atlas_h = 0, 0
    for line in lines:
        if line.startswith('size:'):
            parts = line.split(':')[1].split(',')
            atlas_w, atlas_h = int(parts[0].strip()), int(parts[1].strip())
            break
    
    # 2. 深度修复：读取灰度图作为 Alpha 蒙版
    alpha_image_path = image_path.replace('.png', '[alpha].png')
    
    if os.path.exists(alpha_image_path):
        print(f"[{os.path.basename(atlas_path)}] 找到对应的 Alpha 图片，正在提取灰度图作为透明蒙版...")
        # 【修改点】：将 Alpha 图片转换为灰度模式 ('L')。在这个模式下，黑色(0)就是完全透明，白色(255)就是不透明。
        alpha_img = Image.open(alpha_image_path).convert("L")
        
        if alpha_img.size != img.size:
            print(f"[{os.path.basename(atlas_path)}] Alpha 图片尺寸与主图不符，正在调整...")
            alpha_img = alpha_img.resize(img.size, Image.Resampling.BILINEAR)
            
        # 【修改点】：在 PIL 中，直接将 'L' 模式的灰度图传给 putalpha，它会自动把明暗度转换为透明度。
        img.putalpha(alpha_img) 
    else:
        print(f"[{os.path.basename(atlas_path)}] 未找到对应的 [alpha] 图片。")

    # 3. 如果实际图片被拉伸，强制等比缩放回原尺寸
    if atlas_w > 0 and atlas_h > 0 and (img.width != atlas_w or img.height != atlas_h):
        print(f"[{os.path.basename(atlas_path)}] 图片尺寸不符 ({img.width}x{img.height})，正在还原为 ({atlas_w}x{atlas_h})...")
        img = img.resize((atlas_w, atlas_h), Image.Resampling.BILINEAR)

    # 4. 开始切图
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.endswith('.png') or any(line.startswith(x) for x in ['size:', 'format:', 'filter:', 'repeat:']):
            i += 1
            continue

        part_name = line.replace('/', '_').replace('\\', '_')
        try:
            rotate = lines[i+1].split(': ')[1].strip() == 'true'
            xy = [int(x) for x in lines[i+2].split(': ')[1].split(',')]
            size = [int(x) for x in lines[i+3].split(': ')[1].split(',')]
            orig = [int(x) for x in lines[i+4].split(': ')[1].split(',')]
            offset = [int(x) for x in lines[i+5].split(': ')[1].split(',')]

            left, top = xy[0], xy[1]
            width, height = (size[1], size[0]) if rotate else (size[0], size[1])

            # 此时的 img 已经是由 [alpha].png 提供明暗透明度的图片了
            part_img = img.crop((left, top, left + width, top + height))

            if rotate:
                part_img = part_img.rotate(90, expand=True)

            final_img = Image.new("RGBA", (orig[0], orig[1]), (0, 0, 0, 0))
            paste_x = offset[0]
            paste_y = orig[1] - size[1] - offset[1]
            
            # 粘贴时，自身自带的 Alpha 会完美剔除掉原来的黑底
            final_img.paste(part_img, (paste_x, paste_y), part_img)
            
            final_img.save(os.path.join(output_dir, f"{part_name}.png"))
            
            i += 7 
        except Exception as e:
            i += 1

def walk_and_unpack(root_path):
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.atlas'):
                atlas_path = os.path.join(root, file)
                image_path = atlas_path.replace('.atlas', '.png')
                
                if os.path.exists(image_path):
                    output_folder = os.path.join(root, file.replace('.atlas', '_extracted'))
                    extract_arknights_atlas_fixed(atlas_path, image_path, output_folder)

if __name__ == "__main__":
    target_root = r'D:\FD_Store\ARK_chara' 
    if os.path.exists(target_root):
        print(f"开始深度修复并切图...")
        walk_and_unpack(target_root)
        print("所有素材处理完毕！")
    else:
        print(f"路径不存在: {target_root}")