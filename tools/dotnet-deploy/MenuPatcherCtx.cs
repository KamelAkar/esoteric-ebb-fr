using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

/// <summary>
/// Context-aware MenuPatcher: replaces strings only in MonoBehaviours that do NOT
/// contain a specified "exclusion keyword" in their raw byte data.
///
/// Use case: translate "Credits" label in TextMeshPro components but skip the
/// "Credits" class reference in Unity Button OnClick handlers (which contain
/// "Assembly-CSharp" or class name string in the same MonoBehaviour data).
///
/// Usage: dotnet-deploy menuctx <assets_file> <dict.tsv> <exclude_keywords_comma> [include_keywords_comma]
/// </summary>
class MenuPatcherCtx
{
    static byte[]? PatchRawBytes(byte[] raw, Dictionary<string, string> replacements,
                                   byte[][] exclusionPatterns, byte[][] inclusionPatterns,
                                   out List<string> patched)
    {
        patched = new List<string>();

        // Check if any exclusion pattern is in the raw bytes
        foreach (var pattern in exclusionPatterns)
        {
            if (IndexOf(raw, pattern) >= 0)
            {
                return null; // skip
            }
        }

        // If inclusion patterns are specified, all must be present
        if (inclusionPatterns.Length > 0)
        {
            foreach (var pattern in inclusionPatterns)
            {
                if (IndexOf(raw, pattern) < 0)
                {
                    return null; // missing required inclusion, skip
                }
            }
        }

        bool anyChange = false;
        var output = new List<byte>(raw.Length + 256);
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

                        if (replacements.TryGetValue(str, out string? newStr))
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
                            i += 4 + len + oldPad;
                            continue;
                        }
                    }
                }
            }
            output.Add(raw[i]);
            i++;
        }
        return anyChange ? output.ToArray() : null;
    }

    static int IndexOf(byte[] haystack, byte[] needle)
    {
        if (needle.Length == 0) return -1;
        for (int i = 0; i <= haystack.Length - needle.Length; i++)
        {
            bool match = true;
            for (int j = 0; j < needle.Length; j++)
            {
                if (haystack[i + j] != needle[j]) { match = false; break; }
            }
            if (match) return i;
        }
        return -1;
    }

    public static int Run(string[] args)
    {
        if (args.Length < 3)
        {
            Console.WriteLine("Usage: dotnet-deploy menuctx <assets_file> <dict.tsv> <exclude_kw_comma> [include_kw_comma]");
            return 1;
        }

        string assetsPath = args[0];
        string dictPath = args[1];
        string excludeKw = args[2];
        string includeKw = args.Length > 3 ? args[3] : "";

        var exclusionPatterns = new List<byte[]>();
        foreach (var kw in excludeKw.Split(','))
        {
            if (!string.IsNullOrWhiteSpace(kw))
                exclusionPatterns.Add(Encoding.UTF8.GetBytes(kw.Trim()));
        }

        var inclusionPatterns = new List<byte[]>();
        foreach (var kw in includeKw.Split(','))
        {
            if (!string.IsNullOrWhiteSpace(kw))
                inclusionPatterns.Add(Encoding.UTF8.GetBytes(kw.Trim()));
        }

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
        Console.WriteLine($"Loaded {replacements.Count} replacements, {exclusionPatterns.Count} exclusion patterns");

        string classDataPath = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
        var am = new AssetsManager();
        am.LoadClassPackage(classDataPath);

        var afile = am.LoadAssetsFile(assetsPath, false);
        if (afile == null) { Console.WriteLine("Failed to load"); return 1; }
        am.LoadClassDatabaseFromPackage(afile.file.Metadata.UnityVersion);

        var modifications = new List<AssetsReplacer>();
        int monoCount = 0, modifiedCount = 0, skippedCount = 0;
        var reader = afile.file.Reader;

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.MonoBehaviour && info.TypeId != (int)AssetClassID.TextAsset)
                continue;
            monoCount++;

            reader.Position = info.GetAbsoluteByteStart(afile.file);
            byte[] raw = reader.ReadBytes((int)info.ByteSize);

            var patched = PatchRawBytes(raw, replacements, exclusionPatterns.ToArray(), inclusionPatterns.ToArray(), out var changes);
            if (patched != null)
            {
                Console.WriteLine($"  path_id={info.PathId}:");
                foreach (var c in changes) Console.WriteLine($"    {c}");
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
