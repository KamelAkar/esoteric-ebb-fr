using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Patches TextAsset.m_Script content using AssetsTools.NET's BaseField API.
/// More robust than MenuPatcher for TextAssets containing large content (e.g. Ink JSON).
///
/// Usage: dotnet-deploy textasset <assets_file> <patches.tsv>
/// patches.tsv format: <asset_name>\t<find_substring>\t<replacement>
/// </summary>
class TextAssetPatcher
{
    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: dotnet-deploy textasset <assets_file> <patches.tsv>");
            Console.WriteLine("  patches.tsv format: <asset_name>\\t<find>\\t<replacement>");
            return 1;
        }

        string assetsPath = args[0];
        string patchesPath = args[1];

        // Load patches: dict of name -> list of (find, replace)
        var patches = new Dictionary<string, List<(string, string)>>();
        foreach (var line in File.ReadAllLines(patchesPath))
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#")) continue;
            var parts = line.Split('\t');
            if (parts.Length < 3) continue;
            string name = parts[0];
            string find = parts[1].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
            string repl = parts[2].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
            if (!patches.ContainsKey(name)) patches[name] = new List<(string, string)>();
            patches[name].Add((find, repl));
        }
        Console.WriteLine($"Loaded patches for {patches.Count} assets");

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);

        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) { Console.WriteLine("Failed to load"); return 1; }
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        var modifications = new List<AssetsReplacer>();
        int modCount = 0;

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.TextAsset) continue;

            AssetTypeValueField bf;
            try { bf = am.GetBaseField(afile, info); }
            catch { continue; }

            string name = bf["m_Name"].AsString ?? "";
            if (!patches.ContainsKey(name)) continue;

            string script = bf["m_Script"].AsString ?? "";
            string newScript = script;
            int applied = 0;
            foreach (var (find, repl) in patches[name])
            {
                if (newScript.Contains(find))
                {
                    newScript = newScript.Replace(find, repl);
                    applied++;
                }
            }
            if (applied > 0)
            {
                bf["m_Script"].AsString = newScript;
                var newBytes = bf.WriteToByteArray();
                modifications.Add(new AssetsReplacerFromMemory(afile.file, info, newBytes));
                modCount++;
                Console.WriteLine($"  + {name}: {applied} substitution(s)");
            }
        }

        if (modifications.Count == 0)
        {
            Console.WriteLine("No modifications.");
            am.UnloadAll();
            return 0;
        }

        string tempPath = assetsPath + ".tmp";
        using (var fs = new FileStream(tempPath, FileMode.Create, FileAccess.Write))
        using (var writer = new AssetsFileWriter(fs))
        {
            afile.file.Write(writer, 0, modifications);
        }
        am.UnloadAll();
        File.Delete(assetsPath);
        File.Move(tempPath, assetsPath);
        Console.WriteLine($"Done: {modCount} TextAssets modified");
        return 0;
    }
}
