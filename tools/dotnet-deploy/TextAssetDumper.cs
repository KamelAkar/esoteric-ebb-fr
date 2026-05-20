using System;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Dumps a TextAsset's m_Script content to a file.
/// Usage: dotnet-deploy dumpta <assets_file> <asset_name> <out_path>
/// </summary>
class TextAssetDumper
{
    public static int Run(string[] args)
    {
        if (args.Length < 3)
        {
            Console.WriteLine("Usage: dotnet-deploy dumpta <assets_file> <asset_name> <out_path>");
            return 1;
        }

        string assetsPath = args[0];
        string targetName = args[1];
        string outPath = args[2];

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);
        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) { Console.WriteLine("Failed to load"); return 1; }
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.TextAsset) continue;
            AssetTypeValueField bf;
            try { bf = am.GetBaseField(afile, info); }
            catch { continue; }
            string name = bf["m_Name"].AsString ?? "";
            if (name != targetName) continue;
            string script = bf["m_Script"].AsString ?? "";
            File.WriteAllText(outPath, script);
            Console.WriteLine($"Dumped {name}: {script.Length} chars to {outPath}");
            am.UnloadAll();
            return 0;
        }
        Console.WriteLine($"NOT FOUND: {targetName}");
        am.UnloadAll();
        return 1;
    }
}
