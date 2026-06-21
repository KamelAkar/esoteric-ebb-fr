using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Re-translate a Unity scene/level file by copying string values from the
/// previous translator's (broken-serialized) FR level file into a VANILLA copy,
/// then re-serializing with AssetsTools.NET (correct Unity/TMP types => no crash).
///
/// Scene build-settings names are NEVER copied (kept English) so SceneManager works.
///
/// Usage: dotnet-deploy leveltranslate &lt;vanilla_level&gt; &lt;fr_level&gt; &lt;out_level&gt;
/// </summary>
class LevelTranslate
{
    // French scene names that must stay English (do not copy these values).
    static readonly HashSet<string> SceneNamesFr = new HashSet<string>
    {
        "Jardin Gobelin", "Sphinx Ivre", "Entrepôt de la Guilde", "Nid de Darrow",
        "Tour de Garde", "Bureau de Snurre", "Trou de Simii", "Salon de Thé",
        "Tunnel Secret", "Temple d'Urth", "Croisée du Pilier", "Cité d'En Bas",
        "Vieille Prison", "Croisée de Jor", "Chez Lisa", "Logis de Snell",
        "Chemin de la Côte d'En Bas",
    };

    static int copied = 0;

    public static int Run(string[] args)
    {
        if (args.Length < 3)
        {
            Console.WriteLine("Usage: dotnet-deploy leveltranslate <vanilla_level> <fr_level> <out_level>");
            return 1;
        }
        string vanPath = args[0], frPath = args[1], outPath = args[2];
        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");

        var amV = new AssetsManager(); amV.LoadClassPackage(classDataPath);
        var amF = new AssetsManager(); amF.LoadClassPackage(classDataPath);
        var vf = amV.LoadAssetsFile(vanPath, false);
        var ff = amF.LoadAssetsFile(frPath, false);
        if (vf == null || ff == null) { Console.WriteLine("load failed"); return 1; }
        amV.LoadClassDatabaseFromPackage(vf.file.Metadata.UnityVersion);
        amF.LoadClassDatabaseFromPackage(ff.file.Metadata.UnityVersion);

        // index FR assets by PathID
        var frById = new Dictionary<long, AssetFileInfo>();
        foreach (var info in ff.file.Metadata.AssetInfos)
            frById[info.PathId] = info;

        var mods = new List<AssetsReplacer>();
        int changedAssets = 0;
        int considered = 0, matched = 0;

        foreach (var info in vf.file.Metadata.AssetInfos)
        {
            // Only types that hold display text: MonoBehaviour(114) and GameObject(1)
            if (info.TypeId != (int)AssetClassID.MonoBehaviour && info.TypeId != (int)AssetClassID.GameObject)
                continue;
            considered++;
            if (!frById.TryGetValue(info.PathId, out var frInfo)) continue;
            if (frInfo.TypeId != info.TypeId) continue;
            matched++;

            AssetTypeValueField vBase, fBase;
            try { vBase = amV.GetBaseField(vf, info); fBase = amF.GetBaseField(ff, frInfo); }
            catch { continue; }

            int before = copied;
            CopyStrings(vBase, fBase);
            if (copied > before)
            {
                var bytes = vBase.WriteToByteArray();
                mods.Add(new AssetsReplacerFromMemory(vf.file, info, bytes));
                changedAssets++;
            }
        }

        Console.WriteLine($"  [debug] considered={considered} pathid-matched={matched}");
        if (mods.Count == 0)
        {
            Console.WriteLine("No strings copied.");
            // still write a copy so pipeline is uniform
            File.Copy(vanPath, outPath, true);
            return 0;
        }

        using (var fs = new FileStream(outPath, FileMode.Create, FileAccess.Write))
        using (var w = new AssetsFileWriter(fs))
            vf.file.Write(w, 0, mods);

        amV.UnloadAll(); amF.UnloadAll();
        Console.WriteLine($"{Path.GetFileName(outPath)}: {copied} strings translated across {changedAssets} objects");
        return 0;
    }

    // Recursively walk two parallel field trees; copy FR string -> vanilla when different.
    static void CopyStrings(AssetTypeValueField v, AssetTypeValueField f)
    {
        if (v == null || f == null) return;
        var vt = v.TemplateField;
        if (vt.ValueType == AssetValueType.String)
        {
            string vs = v.AsString ?? "";
            string fs = f.AsString ?? "";
            if (fs != vs && fs.Length > 0 && !SceneNamesFr.Contains(fs))
            {
                v.AsString = fs;
                copied++;
            }
            return;
        }
        // recurse children in parallel (same structure / same template)
        int n = Math.Min(v.Children.Count, f.Children.Count);
        for (int i = 0; i < n; i++)
            CopyStrings(v.Children[i], f.Children[i]);
    }
}
