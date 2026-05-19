using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Search MonoBehaviours for any string field containing a target substring,
/// and print the structure path. Useful for finding where button labels live.
///
/// Usage: dotnet-deploy findtext <assets_file> <search_string>
/// </summary>
class InspectMonoText
{
    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: dotnet-deploy findtext <assets_file> <search_string>");
            return 1;
        }

        string assetsPath = args[0];
        string searchStr = args[1];

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);

        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) return 1;
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        int matched = 0;
        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.MonoBehaviour) continue;
            AssetTypeValueField bf;
            try { bf = am.GetBaseField(afile, info); }
            catch { continue; }
            FindInField(bf, "", searchStr, info.PathId, ref matched);
            if (matched > 20) break;
        }
        Console.WriteLine($"Total matches found: {matched}");
        am.UnloadAll();
        return 0;
    }

    static void FindInField(AssetTypeValueField field, string path, string searchStr, long pathId, ref int matched)
    {
        if (field == null) return;
        if (field.TemplateField.Type == "string")
        {
            string val;
            try { val = field.AsString; }
            catch { return; }
            if (val != null && val.Contains(searchStr))
            {
                Console.WriteLine($"  PathID={pathId} {path}: '{val}'");
                matched++;
            }
            return;
        }
        try
        {
            foreach (var child in field.Children)
            {
                FindInField(child, path + "/" + child.FieldName, searchStr, pathId, ref matched);
            }
        }
        catch { }
    }
}
