using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

class Program
{
    static int Main(string[] args)
    {
        if (args.Length >= 1 && args[0] == "menu")
        {
            return MenuPatcher.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "inspect")
        {
            return InspectTypes.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "textasset")
        {
            return TextAssetPatcher.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "dumpta")
        {
            return TextAssetDumper.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "listta")
        {
            return TextAssetLister.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "noop")
        {
            return NoopRewrite.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "leveltranslate")
        {
            return LevelTranslate.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "tmptext")
        {
            return TmpTextPatcher.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "findtext")
        {
            return InspectMonoText.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "menuctx")
        {
            return MenuPatcherCtx.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "findobj")
        {
            return FindObjAtOffset.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "inkbulk")
        {
            return InkBulkPatcher.Run(args[1..]);
        }
        if (args.Length >= 1 && args[0] == "menusmart")
        {
            return MenuPatcherSmart.Run(args[1..]);
        }

        if (args.Length < 3)
        {
            Console.WriteLine("Usage: dotnet-deploy <assets_file> <french_dir> <names_csv> [extension]");
            Console.WriteLine("       dotnet-deploy menu <assets_file> <dict_file>");
            return 1;
        }

        string assetsPath = args[0];
        string frenchDir = args[1];
        var targetNames = new HashSet<string>(args[2].Split(','));
        string ext = args.Length > 3 ? args[3] : ".json";

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");

        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);

        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null)
        {
            Console.WriteLine("Failed to load assets file");
            return 1;
        }

        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        var modifications = new List<AssetsReplacer>();
        int found = 0;
        int modified = 0;

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.TextAsset)
                continue;

            var baseField = am.GetBaseField(afile, info);
            string name = baseField["m_Name"].AsString;

            if (!targetNames.Contains(name))
                continue;

            found++;

            string frenchPath = Path.Combine(frenchDir, $"{name}{ext}");
            if (!File.Exists(frenchPath))
            {
                Console.WriteLine($"  - {name}: french file missing ({frenchPath})");
                continue;
            }

            string newText = File.ReadAllText(frenchPath);
            baseField["m_Script"].AsString = newText;

            var newBytes = baseField.WriteToByteArray();
            var replacer = new AssetsReplacerFromMemory(afile.file, info, newBytes);
            modifications.Add(replacer);
            modified++;
            Console.WriteLine($"  + {name}");
        }

        if (modifications.Count == 0)
        {
            Console.WriteLine("No modifications to apply.");
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

        Console.WriteLine($"Done: found={found}, modified={modified}");
        return 0;
    }
}
