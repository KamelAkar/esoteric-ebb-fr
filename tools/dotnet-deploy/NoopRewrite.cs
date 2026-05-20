using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Loads an assets file and rewrites it with no modifications.
/// Tests whether AssetsTools.NET preserves byte content.
/// Usage: dotnet-deploy noop <in_assets> <out_assets>
/// </summary>
class NoopRewrite
{
    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: dotnet-deploy noop <in_assets> <out_assets>");
            return 1;
        }
        string inPath = args[0];
        string outPath = args[1];

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);
        var afile = am.LoadAssetsFile(inPath, false);
        if (afile == null) { Console.WriteLine("Failed to load"); return 1; }
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        // Touch a TextAsset to force rewrite
        var modifications = new List<AssetsReplacer>();
        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.TextAsset) continue;
            var bf = am.GetBaseField(afile, info);
            string name = bf["m_Name"].AsString ?? "";
            if (name != "LL_Intro") continue;
            // Just re-serialize without changes
            var newBytes = bf.WriteToByteArray();
            modifications.Add(new AssetsReplacerFromMemory(afile.file, info, newBytes));
            Console.WriteLine($"  Touched: {name}, bytes: {newBytes.Length}");
            break;
        }

        using (var fs = new FileStream(outPath, FileMode.Create, FileAccess.Write))
        using (var writer = new AssetsFileWriter(fs))
        {
            afile.file.Write(writer, 0, modifications);
        }
        am.UnloadAll();
        Console.WriteLine($"Wrote: {outPath}");
        return 0;
    }
}
