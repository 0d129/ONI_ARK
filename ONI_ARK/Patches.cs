using Database;
using HarmonyLib;
using Klei.AI;
using System.Collections.Generic;

namespace ONI_ARK
{
    public class Patches
    {

        [HarmonyPatch(typeof(Db))]
        [HarmonyPatch("Initialize")]
        public class Db_Initialize_Patch
        {
            public static void Prefix()
            {
                Debug.Log("Cuora execute before Db.Initialize!");
            }

            public static void Postfix()
            {
                Debug.Log("Cuora execute after Db.Initialize!");
                KAnimFile customKanim = Assets.GetAnim("alpha_head_swap_kanim");
                if (customKanim == null)
                {
                    Debug.LogWarning("未找到自定义 Kanim，皮肤可能加载失败。");
                    return;
                }
                // 【关键防坑一步】强制初始化动画数据，确保我们能取到 Symbol
                //customKanim.Initialize();

                // 2. 告诉系统认识这个哈希字符串
                HashCache.Get().Add("headshape_999");

                // 3. 【新改动】提取真正的 Symbol 对象
                KAnim.Build.Symbol myCustomSymbol = customKanim.GetData().build.GetSymbol("headshape_999");
                if (myCustomSymbol == null)
                {
                    Debug.LogWarning("在 kanim 中没有找到名为 headshape_999 的 Symbol！请检查你打包的贴图和 scml 文件名。");
                    return;
                }

                // 4. 使用你查到的最新构造函数实例化 Accessory
                Accessory myCustomHeadshape = new Accessory(
                    id: "headshape_999",
                    parent: Db.Get().Accessories,
                    slot: Db.Get().AccessorySlots.HeadShape,
                    batchSource: customKanim.batchTag,  // 对应 HashedString batchSource
                    symbol: myCustomSymbol,             // 对应 KAnim.Build.Symbol symbol
                    animFile: customKanim               // 对应 KAnimFile animFile
                );

                // 5. 把这个新脸型塞进游戏的“脸型可选池”和“全局饰品池”里
                Db.Get().AccessorySlots.HeadShape.accessories.Add(myCustomHeadshape);
                Db.Get().Accessories.Add(myCustomHeadshape);






                // 1. 找一个“替身”。我们从数据库里抓取"Meep"（米普）作为外观模板
                Personality template = Db.Get().Personalities.GetPersonalityFromNameStringKey("Meep");

                List<Personality> all_persona = Db.Get().Personalities.GetStartingPersonalities();
                for (int i = 0; i < all_persona.Count; i++)
                {
                    Debug.Log(all_persona[i].nameStringKey);
                    Debug.Log(all_persona[i].description);
                    all_persona[i].startingMinion = false;
                }

                 if (template == null)
                {
                    Debug.Log("Cannot find Meep as a persona!");
                    return; // 安全检查
                }
                 
                // 2. 使用你查到的构造函数实例化自定义小人
                Personality myCustomDupe1 = new Personality(
                    name_string_key: "MY_UNIQUE_DUPE_001", // 内部唯一ID，建议全大写且不包含空格
                    name: "测试小人-阿尔法1",                  // 选人界面和游戏中实际显示的中文/英文名字
                    Gender: template.genderStringKey,          // 借用性别标签
                    PersonalityType: template.personalityType, // 借用性格类型
                    StressTrait: template.stresstrait,         // 压力反应（如：破坏狂）
                    JoyTrait: template.joyTrait,               // 喜悦反应（如：气球艺术家）
                    StickerType: template.stickerType,
                    CongenitalTrait: template.congenitaltrait, // 先天天赋

                    // 以下外观部位全部借用模板的整数ID (ID对应了材质图集中的部件)
                    headShape: 999,
                    mouth: template.mouth, // 注意：字段名可能是 mouthShape，这里对应你构造函数的 mouth 参数
                    neck: template.neck,
                    eyes: template.eyes,
                    hair: template.hair,
                    body: template.body,
                    belt: template.belt,
                    cuff: template.cuff,
                    foot: template.foot,
                    hand: template.hand,
                    pelvis: template.pelvis,
                    leg: template.leg,
                    arm_skin: template.arm_skin,
                    leg_skin: template.leg_skin,

                    // 剩余配置
                    description: "这是一个带有自定义名字的测试复制人，目前借用了米普的身体！",
                    isStartingMinion: true,           // 关键点：true 才能在开局选人界面刷出来
                    graveStone: template.graveStone,  // 死亡后的墓碑样式
                    model: template.model,            // 实体模型标签 (通常是 Minion)
                    SpeechMouth: template.speech_mouth // 说话时的嘴型动画索引
                );
                Personality myCustomDupe2 = new Personality(
    name_string_key: "MY_UNIQUE_DUPE_002", // 内部唯一ID，建议全大写且不包含空格
    name: "测试小人-阿尔法2",                  // 选人界面和游戏中实际显示的中文/英文名字
    Gender: template.genderStringKey,          // 借用性别标签
    PersonalityType: template.personalityType, // 借用性格类型
    StressTrait: template.stresstrait,         // 压力反应（如：破坏狂）
    JoyTrait: template.joyTrait,               // 喜悦反应（如：气球艺术家）
    StickerType: template.stickerType,
    CongenitalTrait: template.congenitaltrait, // 先天天赋

    // 以下外观部位全部借用模板的整数ID (ID对应了材质图集中的部件)
    headShape: template.headShape,
    mouth: template.mouth, // 注意：字段名可能是 mouthShape，这里对应你构造函数的 mouth 参数
    neck: template.neck,
    eyes: template.eyes,
    hair: template.hair,
    body: template.body,
    belt: template.belt,
    cuff: template.cuff,
    foot: template.foot,
    hand: template.hand,
    pelvis: template.pelvis,
    leg: template.leg,
    arm_skin: template.arm_skin,
    leg_skin: template.leg_skin,

    // 剩余配置
    description: "这是一个带有自定义名字的测试复制人，目前借用了米普的身体！",
    isStartingMinion: true,           // 关键点：true 才能在开局选人界面刷出来
    graveStone: template.graveStone,  // 死亡后的墓碑样式
    model: template.model,            // 实体模型标签 (通常是 Minion)
    SpeechMouth: template.speech_mouth // 说话时的嘴型动画索引
);
                Personality myCustomDupe3 = new Personality(
    name_string_key: "MY_UNIQUE_DUPE_003", // 内部唯一ID，建议全大写且不包含空格
    name: "测试小人-阿尔法3",                  // 选人界面和游戏中实际显示的中文/英文名字
    Gender: template.genderStringKey,          // 借用性别标签
    PersonalityType: template.personalityType, // 借用性格类型
    StressTrait: template.stresstrait,         // 压力反应（如：破坏狂）
    JoyTrait: template.joyTrait,               // 喜悦反应（如：气球艺术家）
    StickerType: template.stickerType,
    CongenitalTrait: template.congenitaltrait, // 先天天赋

    // 以下外观部位全部借用模板的整数ID (ID对应了材质图集中的部件)
    headShape: template.headShape,
    mouth: template.mouth, // 注意：字段名可能是 mouthShape，这里对应你构造函数的 mouth 参数
    neck: template.neck,
    eyes: template.eyes,
    hair: template.hair,
    body: template.body,
    belt: template.belt,
    cuff: template.cuff,
    foot: template.foot,
    hand: template.hand,
    pelvis: template.pelvis,
    leg: template.leg,
    arm_skin: template.arm_skin,
    leg_skin: template.leg_skin,

    // 剩余配置
    description: "这是一个带有自定义名字的测试复制人，目前借用了米普的身体！",
    isStartingMinion: true,           // 关键点：true 才能在开局选人界面刷出来
    graveStone: template.graveStone,  // 死亡后的墓碑样式
    model: template.model,            // 实体模型标签 (通常是 Minion)
    SpeechMouth: template.speech_mouth // 说话时的嘴型动画索引
);

                // 4. 最重要的一步：把他塞进游戏的选人池数据库里！
                Db.Get().Personalities.Add(myCustomDupe1);
                Db.Get().Personalities.Add(myCustomDupe2);
                Db.Get().Personalities.Add(myCustomDupe3);
            }
        }
    }
}
