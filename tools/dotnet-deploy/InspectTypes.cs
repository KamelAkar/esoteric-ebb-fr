using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

class InspectTypes
{
    public static int Run(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: dotnet-deploy inspect <assets_file>");
            return 1;
        }

        string assetsPath = args[0];
        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");

        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);
        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) return 1;
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        var typeCounts = new Dictionary<int, int>();
        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            int tid = info.TypeId;
            typeCounts.TryGetValue(tid, out int c);
            typeCounts[tid] = c + 1;
        }

        Console.WriteLine("Type counts:");
        foreach (var kv in typeCounts)
        {
            string typeName = Enum.IsDefined(typeof(AssetClassID), kv.Key)
                ? ((AssetClassID)kv.Key).ToString()
                : "Unknown";
            Console.WriteLine($"  Type {kv.Key} ({typeName}): {kv.Value}");
        }

        // List all TextAssets (regardless of size)
        Console.WriteLine("\nAll TextAssets:");
        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId == (int)AssetClassID.TextAsset)
            {
                try
                {
                    var bf = am.GetBaseField(afile, info);
                    string name = bf["m_Name"]?.AsString ?? "";
                    Console.WriteLine($"  PathID={info.PathId}, Size={info.ByteSize:N0}, Name='{name}'");
                }
                catch { }
            }
        }

        // Large objects of any type
        Console.WriteLine("\nLarge objects (>10KB):");
        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.ByteSize > 10000)
            {
                try
                {
                    var bf = am.GetBaseField(afile, info);
                    string name = "";
                    if (bf["m_Name"] != null && !bf["m_Name"].IsDummy)
                        name = bf["m_Name"].AsString;
                    Console.WriteLine($"  PathID={info.PathId}, TypeId={info.TypeId}, Size={info.ByteSize:N0}, Name='{name}'");
                } catch (Exception e) {
                    Console.WriteLine($"  PathID={info.PathId}, TypeId={info.TypeId}, Size={info.ByteSize:N0}, ERROR: {e.Message[..Math.Min(80, e.Message.Length)]}");
                }
            }
        }

        am.UnloadAll();
        return 0;
    }
}
