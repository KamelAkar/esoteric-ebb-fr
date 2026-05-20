using System;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Lists all TextAsset names + script length in an assets file.
/// Usage: dotnet-deploy listta <assets_file>
/// </summary>
class TextAssetLister
{
    public static int Run(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: dotnet-deploy listta <assets_file>");
            return 1;
        }
        string assetsPath = args[0];
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
            string script = bf["m_Script"].AsString ?? "";
            Console.WriteLine($"{script.Length,10}  {name}");
        }
        am.UnloadAll();
        return 0;
    }
}
