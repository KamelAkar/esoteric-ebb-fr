using System;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Find which asset object contains a given byte offset in the file.
/// Useful for identifying the MonoBehaviour PathID of a known-problematic byte position.
///
/// Usage: dotnet-deploy findobj <assets_file> <byte_offset>
/// </summary>
class FindObjAtOffset
{
    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: dotnet-deploy findobj <assets_file> <byte_offset>");
            return 1;
        }

        string assetsPath = args[0];
        long targetOffset = long.Parse(args[1]);

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);
        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) return 1;
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            long start = info.GetAbsoluteByteStart(afile.file);
            long end = start + info.ByteSize;
            if (targetOffset >= start && targetOffset < end)
            {
                string typeName = Enum.IsDefined(typeof(AssetClassID), info.TypeId)
                    ? ((AssetClassID)info.TypeId).ToString() : $"Type{info.TypeId}";
                Console.WriteLine($"PathID={info.PathId} Type={typeName} Start={start} End={end} Size={info.ByteSize}");
                long relOffset = targetOffset - start;
                Console.WriteLine($"  Relative offset in object: {relOffset}");
                am.UnloadAll();
                return 0;
            }
        }
        Console.WriteLine($"No object contains offset {targetOffset}");
        am.UnloadAll();
        return 1;
    }
}
