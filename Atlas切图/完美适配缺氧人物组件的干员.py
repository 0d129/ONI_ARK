import os
import re

def find_oni_compatible_operators(base_folder):
    if not os.path.exists(base_folder):
        print(f"错误: 找不到根目录 '{base_folder}'")
        return

    # 【核心升级】中英双语/拼音词根混合映射表
    oni_to_ark_mapping = {
        'mouth': ['mouth', 'zui'],                             # zui (嘴)
        'neck':  ['neck', 'collar', 'bo', 'ling'],             # bozi (脖子), yiling (衣领)
        'eyes':  ['eye', 'yan', 'face_default'],                               # yan (眼/左眼/右眼)
        'hair':  ['hair', 'fa', 'liuhai'],                     # fa (头发/前发/后发), liuhai (刘海)
        'body':  ['body', 'chest', 'xiong', 'shen', 'waitao'], # xiong (胸), shen (身体), waitao (外套)
        'belt':  ['belt', 'yao', 'waist'],                              # yao (腰/腰带)
        'cuff':  ['cuff', 'sleeve', 'xiu'],                    # xiu (袖子/袖口)
        'foot':  ['foot', 'shoe', 'boot', 'xie', 'jiao'],      # xie (鞋), jiao (脚)
        'hand':  ['hand', 'palm', 'finger', 'shou', 'zhi'],    # shou (手/手掌), zhi (手指/食指/拇指)
        'pelvis':['pelvis', 'hip', 'crotch', 'ku', 'tun', 'skirt'],     # ku (裤子), tun (臀部)
        'leg':   ['leg', 'thigh', 'shin', 'tui', 'wheel', 'tyre']               # tui (腿/大腿/小腿)
    }

    operator_scores = []

    print("正在寻找完美契合《缺氧》骨骼的方舟干员 (兼容拼音命名)...\n")

    for char_name in os.listdir(base_folder):
        char_dir = os.path.join(base_folder, char_name)
        if not os.path.isdir(char_dir):
            continue
            
        target_dir = os.path.join(
            char_dir, "Building", f"build_{char_name}", f"build_{char_name}_extracted"
        )
        
        if not os.path.exists(target_dir):
            continue
            
        char_parts = set()
        for file in os.listdir(target_dir):
            if file.lower().endswith('.png'):
                base_name = os.path.splitext(file)[0].lower()
                # 去除 F_L_, B_R_, F_, B_ 等前缀
                clean_name = re.sub(r'^[fb]_[lr]_|^[fb]_', '', base_name)
                char_parts.add(clean_name)
                
        matched_oni_parts = []
        missing_oni_parts = []
        
        for oni_part, ark_keywords in oni_to_ark_mapping.items():
            has_match = False
            for part in char_parts:
                # 只要文件名包含词根 (例如 shouzhang 包含 shou)，就算匹配成功
                if any(keyword in part for keyword in ark_keywords):
                    has_match = True
                    break
                    
            if has_match:
                matched_oni_parts.append(oni_part)
            else:
                missing_oni_parts.append(oni_part)
                
        match_count = len(matched_oni_parts)
        total_needed = len(oni_to_ark_mapping)
        score = (match_count / total_needed) * 100
        
        operator_scores.append({
            'name': char_name,
            'score': score,
            'match_count': match_count,
            'missing': missing_oni_parts
        })

    # 按匹配分数降序排列
    operator_scores.sort(key=lambda x: x['score'], reverse=True)

    # 打印排行榜
    print(f"{'干员文件夹名':<25} | {'契合度':<8} | {'缺失的缺氧部位 (需后期合并或丢弃)'}")
    print("-" * 80)
    for op in operator_scores:
        missing_str = ", ".join(op['missing']) if op['missing'] else "无 (完美匹配!)"
        print(f"{op['name']:<25} | {op['score']:>6.1f}% | 缺: {missing_str}")

if __name__ == "__main__":
    root_folder = r"D:\ARK_chara"
    find_oni_compatible_operators(root_folder)