using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Bulk-translate ALL TextAssets in an .assets file by applying every (find, replace)
/// pair from a simple dict to each TextAsset's m_Script content.
///
/// Optimized: loads dict once, processes all TextAssets in one file load.
///
/// Usage: dotnet-deploy inkbulk <assets_file> <dict.tsv>
/// dict.tsv format: <find>\t<replace>
/// Replacements are applied in order (longest-first recommended).
/// </summary>
class InkBulkPatcher
{
    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: dotnet-deploy inkbulk <assets_file> <dict.tsv>");
            return 1;
        }

        string assetsPath = args[0];
        string dictPath = args[1];

        // Load dict
        var pairs = new List<(string, string)>();
        foreach (var line in File.ReadAllLines(dictPath))
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#")) continue;
            var parts = line.Split('\t', 2);
            if (parts.Length != 2) continue;
            string find = parts[0].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
            string repl = parts[1].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
            if (find.Length > 0 && find != repl)
                pairs.Add((find, repl));
        }
        Console.WriteLine($"Loaded {pairs.Count} translation pairs");

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);
        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) return 1;
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        var modifications = new List<AssetsReplacer>();
        int modCount = 0;
        long totalOrigBytes = 0, totalNewBytes = 0;

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.TextAsset) continue;

            AssetTypeValueField bf;
            try { bf = am.GetBaseField(afile, info); }
            catch { continue; }

            string name = bf["m_Name"]?.AsString ?? "";
            string script = bf["m_Script"]?.AsString ?? "";
            if (string.IsNullOrEmpty(script)) continue;

            long origLen = script.Length;
            string newScript = script;
            int applied = 0;
            foreach (var (find, repl) in pairs)
            {
                if (newScript.Contains(find))
                {
                    newScript = newScript.Replace(find, repl);
                    applied++;
                }
            }
            if (applied > 0 && newScript != script)
            {
                bf["m_Script"].AsString = newScript;
                var newBytes = bf.WriteToByteArray();
                modifications.Add(new AssetsReplacerFromMemory(afile.file, info, newBytes));
                modCount++;
                totalOrigBytes += origLen;
                totalNewBytes += newScript.Length;
                Console.WriteLine($"  + {name}: {applied} unique substitutions, {origLen} -> {newScript.Length} chars");
            }
        }

        Console.WriteLine($"Modified {modCount} TextAssets, total size {totalOrigBytes} -> {totalNewBytes}");
        if (modifications.Count == 0)
        {
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
        Console.WriteLine("Done.");
        return 0;
    }
}
