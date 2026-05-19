using System;
using System.Collections.Generic;
using System.IO;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Surgically patches TextMeshPro/TMP_Text/Unity UI Text components by modifying
/// only their m_text field. Avoids touching class names, GameObject names,
/// or other strings that would break the game.
///
/// Usage: dotnet-deploy tmptext <assets_file> <dict.tsv>
/// dict.tsv format: <english>\t<french>
/// </summary>
class TmpTextPatcher
{
    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: dotnet-deploy tmptext <assets_file> <dict.tsv>");
            return 1;
        }

        string assetsPath = args[0];
        string dictPath = args[1];

        var dict = new Dictionary<string, string>();
        foreach (var line in File.ReadAllLines(dictPath))
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#")) continue;
            var parts = line.Split('\t', 2);
            if (parts.Length == 2)
            {
                string k = parts[0].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
                string v = parts[1].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
                dict[k] = v;
            }
        }
        Console.WriteLine($"Loaded {dict.Count} translations");

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);

        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) { Console.WriteLine("Failed to load"); return 1; }
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        var modifications = new List<AssetsReplacer>();
        int scanned = 0, modified = 0;

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.MonoBehaviour) continue;
            scanned++;

            AssetTypeValueField bf;
            try { bf = am.GetBaseField(afile, info); }
            catch { continue; }

            // Try common text field names used by TMP and UGUI
            string[] textFieldNames = { "m_text", "m_Text" };
            bool wasModified = false;
            foreach (var fieldName in textFieldNames)
            {
                var field = bf[fieldName];
                if (field == null || field.IsDummy) continue;
                string currentText;
                try { currentText = field.AsString; }
                catch { continue; }
                if (string.IsNullOrEmpty(currentText)) continue;
                if (dict.TryGetValue(currentText, out string newText))
                {
                    field.AsString = newText;
                    Console.WriteLine($"  PathID={info.PathId} {fieldName}: '{currentText}' -> '{newText}'");
                    wasModified = true;
                }
            }
            if (wasModified)
            {
                var newBytes = bf.WriteToByteArray();
                modifications.Add(new AssetsReplacerFromMemory(afile.file, info, newBytes));
                modified++;
            }
        }

        Console.WriteLine($"Scanned {scanned} MonoBehaviours, modified {modified}");

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
