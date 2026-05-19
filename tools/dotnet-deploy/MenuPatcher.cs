using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

class MenuPatcher
{
    // Replace length-prefixed strings in raw MonoBehaviour bytes.
    // Unity string format: 4 bytes (little-endian length) + UTF-8 bytes + padding to 4-byte align.
    static byte[]? PatchRawBytes(byte[] raw, Dictionary<string, string> replacements, out List<string> patched)
    {
        patched = new List<string>();
        bool anyChange = false;
        var output = new List<byte>(raw.Length + 256);
        int i = 0;
        while (i < raw.Length)
        {
            // Look for length-prefixed strings: 4-byte LE length, then UTF-8 bytes
            // Strings are 4-byte aligned in Unity serialized data.
            if (i + 4 <= raw.Length && (i % 4 == 0))
            {
                int len = BitConverter.ToInt32(raw, i);
                if (len > 0 && len < 10_000_000 && i + 4 + len <= raw.Length)
                {
                    // Check that the bytes are valid UTF-8 + match a replacement
                    bool looksAscii = true;
                    for (int k = i + 4; k < i + 4 + len; k++)
                    {
                        byte b = raw[k];
                        // Allow ASCII printable + a few common chars
                        if (b < 0x20 && b != 0x09 && b != 0x0A && b != 0x0D) { looksAscii = false; break; }
                    }
                    if (looksAscii)
                    {
                        string str;
                        try { str = Encoding.UTF8.GetString(raw, i + 4, len); }
                        catch { str = ""; }

                        if (replacements.TryGetValue(str, out string? newStr))
                        {
                            // Compute padded length for old and new
                            int oldPad = (4 - (len % 4)) % 4;
                            byte[] newBytes = Encoding.UTF8.GetBytes(newStr);
                            int newLen = newBytes.Length;
                            int newPad = (4 - (newLen % 4)) % 4;

                            // Write: new length (4 bytes) + new bytes + padding
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

    public static int Run(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: MenuPatcher <assets_file> <dict_file>");
            return 1;
        }

        string assetsPath = args[0];
        string dictPath = args[1];

        var replacements = new Dictionary<string, string>();
        foreach (var line in File.ReadAllLines(dictPath))
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#"))
                continue;
            var parts = line.Split('\t', 2);
            if (parts.Length == 2)
            {
                // Interpret literal \n and \r escapes in both key and value
                string key = parts[0].Replace("\\n", "\n").Replace("\\r", "\r");
                string val = parts[1].Replace("\\n", "\n").Replace("\\r", "\r");
                replacements[key] = val;
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

        // Get raw data via reader at file position
        var reader = afile.file.Reader;

        foreach (var info in afile.file.Metadata.AssetInfos)
        {
            if (info.TypeId != (int)AssetClassID.MonoBehaviour && info.TypeId != (int)AssetClassID.TextAsset)
                continue;
            monoCount++;

            // Read raw bytes
            reader.Position = info.GetAbsoluteByteStart(afile.file);
            byte[] raw = reader.ReadBytes((int)info.ByteSize);

            var patched = PatchRawBytes(raw, replacements, out var changes);
            if (patched != null)
            {
                Console.WriteLine($"  path_id={info.PathId}:");
                foreach (var c in changes) Console.WriteLine($"    {c}");
                modifications.Add(new AssetsReplacerFromMemory(afile.file, info, patched));
                modifiedCount++;
            }
        }

        Console.WriteLine($"Scanned {monoCount} MonoBehaviours, modified {modifiedCount}");

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
