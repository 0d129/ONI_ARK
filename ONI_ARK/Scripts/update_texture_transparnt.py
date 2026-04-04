import os
from PIL import Image

def merge_alpha_and_backup(root_path):
    """
    遍历目录，寻找 [alpha].png，并将其应用到对应的原图上。
    原图将被重命名为 _bak.png 作为备份，合并后的透明图将替换原图。
    """
    for root, dirs, files in os.walk(root_path):
        for file in files:
            # 寻找所有的 alpha 贴图
            if file.endswith('[alpha].png'):
                alpha_path = os.path.join(root, file)
                
                # 推导原图路径和备份路径
                # 例如：char_002_amiya[alpha].png -> char_002_amiya.png
                main_file_name = file.replace('[alpha].png', '.png')
                main_path = os.path.join(root, main_file_name)
                
                # 备份路径：char_002_amiya.png -> char_002_amiya_bak.png
                backup_path = os.path.join(root, file.replace('[alpha].png', '_bak.png'))

                if not os.path.exists(main_path):
                    print(f"[-] 找不到对应的原图，跳过: {main_file_name}")
                    continue

                print(f"[*] 正在处理: {main_file_name}")

                try:
                    # 使用 with 语句确保读取到内存后立刻释放文件句柄，防止重命名时报错
                    with Image.open(main_path) as m_img:
                        main_img = m_img.convert("RGBA")
                    
                    with Image.open(alpha_path) as a_img:
                        # 你的观察很对，这里直接作为灰度图读取
                        alpha_img = a_img.convert("L")

                    # 检查尺寸并对齐
                    if alpha_img.size != main_img.size:
                        print(f"    - 尺寸不一致，将 Alpha 图从 {alpha_img.size} 缩放至 {main_img.size}")
                        alpha_img = alpha_img.resize(main_img.size, Image.Resampling.BILINEAR)

                    # 核心合并逻辑
                    main_img.putalpha(alpha_img)

                    # 备份原始文件
                    # 如果之前已经有 _bak.png 了，先删除旧的备份，防止重命名冲突
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    
                    os.rename(main_path, backup_path)
                    print(f"    - 原图已备份为: {os.path.basename(backup_path)}")

                    # 保存合并后的新图片到原路径
                    main_img.save(main_path, "PNG")
                    print(f"    - 成功生成带透明通道的新贴图: {main_file_name}")

                except Exception as e:
                    print(f"[!] 处理 {main_file_name} 时发生错误: {e}")

if __name__ == "__main__":
    # 请确保这是你的目标根路径
    target_root = r'D:\FD_Store\ARK_chara' 
    
    if os.path.exists(target_root):
        print("开始批量合并 Alpha 通道并备份原图...")
        merge_alpha_and_backup(target_root)
        print("所有贴图处理完毕！")
    else:
        print(f"路径不存在: {target_root}")