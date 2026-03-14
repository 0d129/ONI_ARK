using Database;
using HarmonyLib;
using Klei.AI;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;


namespace ONI_ARK
{
    [HarmonyPatch(typeof(SymbolOverrideController), nameof(SymbolOverrideController.AddSymbolOverride),
        new System.Type[] { typeof(HashedString), typeof(KAnim.Build.Symbol), typeof(int) })]
    public class SymbolOverride_Patch
    {
        public static bool Prefix(HashedString target_symbol, ref KAnim.Build.Symbol source_symbol)
        {
            // 如果目标是 snapto_cheek，并且游戏因为在 head_swap_kanim 里没找到而传入了 null
            if (target_symbol == new HashedString("snapto_cheek") && source_symbol == null)
            {
                // 手动去我们的自定义动画库里找
                KAnimFile customKanim = Assets.GetAnim("char_150_snakek_kanim");
                if (customKanim != null)
                {
                    // 尝试获取纯净名称的 Symbol
                    source_symbol = customKanim.GetData().build.GetSymbol("cheek_1150");

                    // 如果找不到，试着找一下带后缀的名字 (防止打包工具带上了 _15)
                    if (source_symbol == null)
                    {
                        source_symbol = customKanim.GetData().build.GetSymbol("cheek_1150_15");
                    }
                }

                // 如果在我们的库里依然没找到，直接 return false，阻止游戏执行原方法，这样就不会引发 NULL 崩溃
                if (source_symbol == null)
                {
                    Debug.LogWarning("[ONI_ARK] 成功拦截了一次必定崩溃的 AddSymbolOverride：未能找到脸颊贴图 cheek_1150");
                    return false;
                }
            }

            // 正常放行
            return true;
        }
    }
}