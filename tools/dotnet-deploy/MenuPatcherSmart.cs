using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Per-string context check: for each candidate string match, check the IMMEDIATELY
/// preceding length-prefixed string. If it ends with ", Assembly-CSharp" or
/// ", UnityEngine" (UnityEvent m_TargetAssemblyTypeName pattern), the current
/// string is likely a method name → SKIP.
///
/// Usage: dotnet-deploy menusmart <assets_file> <dict.tsv>
/// </summary>
class MenuPatcherSmart
{
    static byte[]? PatchRawBytes(byte[] raw, Dictionary<string, string> replacements, out List<string> patched)
    {
        patched = new List<string>();
        bool anyChange = false;
        var output = new List<byte>(raw.Length + 256);

        // Track the LAST seen length-prefixed string (for context check)
        string? lastString = null;

        int i = 0;
        while (i < raw.Length)
        {
            if (i + 4 <= raw.Length && (i % 4 == 0))
            {
                int len = BitConverter.ToInt32(raw, i);
                if (len > 0 && len < 10_000_000 && i + 4 + len <= raw.Length)
                {
                    bool looksAscii = true;
                    for (int k = i + 4; k < i + 4 + len; k++)
                    {
                        byte b = raw[k];
                        if (b < 0x20 && b != 0x09 && b != 0x0A && b != 0x0D) { looksAscii = false; break; }
                    }
                    if (looksAscii)
                    {
                        string str;
                        try { str = Encoding.UTF8.GetString(raw, i + 4, len); }
                        catch { str = ""; }

                        // Per-string context: skip if previous string looks like UnityEvent type name
                        bool isMethodNameContext = lastString != null && (
                            lastString.EndsWith(", Assembly-CSharp") ||
                            lastString.EndsWith(", UnityEngine") ||
                            lastString.EndsWith(", UnityEngine.UI") ||
                            lastString.EndsWith(", Unity.TextMeshPro") ||
                            lastString.Contains(", Assembly-CSharp,")
                        );

                        if (!isMethodNameContext && replacements.TryGetValue(str, out string? newStr))
                        {
                            int oldPad = (4 - (len % 4)) % 4;
                            byte[] newBytes = Encoding.UTF8.GetBytes(newStr);
                            int newLen = newBytes.Length;
                            int newPad = (4 - (newLen % 4)) % 4;

                            output.AddRange(BitConverter.GetBytes(newLen));
                            output.AddRange(newBytes);
                            for (int p = 0; p < newPad; p++) output.Add(0);

                            patched.Add($"{str} -> {newStr}");
                            anyChange = true;
                            lastString = newStr;
                            i += 4 + len + oldPad;
                            continue;
                        }

                        // Update lastString for next iteration's context check
                        lastString = str;
                    }
                }
            }
            output.Add(raw[i]);
            i++;
        }
        return anyChange ? output.ToArray() : null;
    }

    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: dotnet-deploy menusmart <assets_file> <dict.tsv>");
            return 1;
        }

        string assetsPath = args[0];
        string dictPath = args[1];

        var replacements = new Dictionary<string, string>();
        foreach (var line in File.ReadAllLines(dictPath))
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#")) continue;
            var parts = line.Split('\t', 2);
            if (parts.Length == 2)
            {
                string k = parts[0].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
                string v = parts[1].Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t");
                replacements[k] = v;
            }
        }
        Console.WriteLine($"Loaded {replacements.Count} replacements");

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);

        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) { Console.WriteLine("Failed to load"); return 1; }
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        var modifications = new List<AssetsReplacer>();
        int monoCount = 0, modifiedCount = 0;
        var reader = afile.file.Reader;

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.MonoBehaviour && info.TypeId != (int)AssetClassID.TextAsset)
                continue;
            monoCount++;

            reader.Position = info.GetAbsoluteByteStart(afile.file);
            byte[] raw = reader.ReadBytes((int)info.ByteSize);

            var patched = PatchRawBytes(raw, replacements, out var changes);
            if (patched != null)
            {
                modifications.Add(new AssetsReplacerFromMemory(afile.file, info, patched));
                modifiedCount++;
            }
        }

        Console.WriteLine($"Scanned {monoCount}, modified {modifiedCount}");

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
