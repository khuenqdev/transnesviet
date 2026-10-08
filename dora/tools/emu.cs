// Minimal libretro host (fceumm_libretro.dll) for scripted testing of the ROM
// build: C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /platform:x64 /out:emu.exe tools\emu.cs
using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Drawing;
using System.Drawing.Imaging;

class Emu
{
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate bool EnvCb(uint cmd, IntPtr data);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate void VideoCb(IntPtr data, uint w, uint h, UIntPtr pitch);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate void AudioCb(short l, short r);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate UIntPtr AudioBatchCb(IntPtr data, UIntPtr frames);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate void PollCb();
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate short InputCb(uint port, uint device, uint index, uint id);

    const string DLL = "fceumm_libretro.dll";
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_set_environment(EnvCb cb);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_set_video_refresh(VideoCb cb);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_set_audio_sample(AudioCb cb);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_set_audio_sample_batch(AudioBatchCb cb);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_set_input_poll(PollCb cb);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_set_input_state(InputCb cb);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_init();
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern bool retro_load_game(ref GameInfo gi);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_run();
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern void retro_reset();
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern UIntPtr retro_serialize_size();
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern bool retro_serialize(byte[] data, UIntPtr size);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern bool retro_unserialize(byte[] data, UIntPtr size);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern IntPtr retro_get_memory_data(uint id);
    [DllImport(DLL, CallingConvention = CallingConvention.Cdecl)] static extern UIntPtr retro_get_memory_size(uint id);

    [StructLayout(LayoutKind.Sequential)]
    struct GameInfo { public IntPtr path; public IntPtr data; public UIntPtr size; public IntPtr meta; }

    static EnvCb envCb; static VideoCb videoCb; static AudioCb audioCb; static AudioBatchCb audioBatchCb; static PollCb pollCb; static InputCb inputCb;
    static int pixFmt = 0;
    static int fw, fh; static int[] frame = new int[256 * 240];
    static int buttons = 0;
    static IntPtr sysDir;

    static readonly Dictionary<string, int> BTN = new Dictionary<string, int> {
        {"B",0},{"SELECT",2},{"START",3},{"UP",4},{"DOWN",5},{"LEFT",6},{"RIGHT",7},{"A",8}
    };

    static bool Env(uint cmd, IntPtr data)
    {
        switch (cmd & 0xFFFF)
        {
            case 3: Marshal.WriteByte(data, 1); return true; // CAN_DUPE
            case 9: case 31: Marshal.WriteIntPtr(data, sysDir); return true; // SYSTEM/SAVE dir
            case 10: pixFmt = Marshal.ReadInt32(data); return true;
            default: return false;
        }
    }

    static void Video(IntPtr data, uint w, uint h, UIntPtr pitch)
    {
        if (data == IntPtr.Zero) return;
        fw = (int)w; fh = (int)h; int p = (int)pitch.ToUInt32();
        if (frame.Length < fw * fh) frame = new int[fw * fh];
        byte[] row = new byte[p];
        for (int y = 0; y < fh; y++)
        {
            Marshal.Copy(data + y * p, row, 0, p);
            for (int x = 0; x < fw; x++)
            {
                int c;
                if (pixFmt == 1) c = BitConverter.ToInt32(row, x * 4) | unchecked((int)0xFF000000);
                else
                {
                    int v = row[x * 2] | (row[x * 2 + 1] << 8);
                    int r, g, b;
                    if (pixFmt == 2) { r = (v >> 11) & 31; g = (v >> 5) & 63; b = v & 31; g = g * 255 / 63; }
                    else { r = (v >> 10) & 31; g = (v >> 5) & 31; b = v & 31; g = g * 255 / 31; }
                    r = r * 255 / 31; b = b * 255 / 31;
                    c = unchecked((int)0xFF000000) | (r << 16) | (g << 8) | b;
                }
                frame[y * fw + x] = c;
            }
        }
    }

    static short Input(uint port, uint device, uint index, uint id)
    {
        if (port != 0 || device != 1) return 0;
        return (short)(((buttons >> (int)id) & 1));
    }

    static void Shot(string path, int scale)
    {
        using (var bmp = new Bitmap(fw * scale, fh * scale, PixelFormat.Format32bppArgb))
        {
            for (int y = 0; y < fh * scale; y++)
                for (int x = 0; x < fw * scale; x++)
                    bmp.SetPixel(x, y, Color.FromArgb(frame[(y / scale) * fw + x / scale]));
            bmp.Save(path, ImageFormat.Png);
        }
    }

    static byte[] Mem(uint id)
    {
        IntPtr p = retro_get_memory_data(id); int n = (int)retro_get_memory_size(id).ToUInt32();
        if (p == IntPtr.Zero || n == 0) return new byte[0];
        byte[] b = new byte[n]; Marshal.Copy(p, b, 0, n); return b;
    }

    static int ParseButtons(string s)
    {
        int m = 0;
        foreach (var t in s.ToUpper().Split('+'))
        {
            if (t == "NONE" || t == "") continue;
            m |= 1 << BTN[t];
        }
        return m;
    }

    static int Main(string[] args)
    {
        if (args.Length < 2) { Console.Error.WriteLine("usage: emu rom.nes script.txt|-"); return 1; }
        string baseDir = AppDomain.CurrentDomain.BaseDirectory;
        sysDir = Marshal.StringToHGlobalAnsi(baseDir);
        envCb = Env; videoCb = Video; audioCb = (l, r) => { }; audioBatchCb = (d, f) => f; pollCb = () => { }; inputCb = Input;
        retro_set_environment(envCb);
        retro_init();
        retro_set_video_refresh(videoCb); retro_set_audio_sample(audioCb); retro_set_audio_sample_batch(audioBatchCb);
        retro_set_input_poll(pollCb); retro_set_input_state(inputCb);

        string romPath = Path.GetFullPath(args[0]);
        byte[] rom = File.ReadAllBytes(romPath);
        GCHandle h = GCHandle.Alloc(rom, GCHandleType.Pinned);
        GameInfo gi = new GameInfo();
        gi.path = Marshal.StringToHGlobalAnsi(romPath); gi.data = h.AddrOfPinnedObject(); gi.size = (UIntPtr)rom.Length;
        if (!retro_load_game(ref gi)) { Console.Error.WriteLine("load failed"); return 1; }

        TextReader rd = args[1] == "-" ? Console.In : new StreamReader(args[1]);
        string line; long frameNo = 0;
        while ((line = rd.ReadLine()) != null)
        {
            line = line.Trim();
            if (line == "" || line.StartsWith("#")) continue;
            string[] a = line.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            string c = a[0].ToLower();
            try
            {
                switch (c)
                {
                    case "run": { int n = int.Parse(a[1]); for (int i = 0; i < n; i++) { retro_run(); frameNo++; } break; }
                    case "hold": buttons = ParseButtons(a[1]); break;
                    case "press":
                        {
                            buttons = ParseButtons(a[1]); int n = a.Length > 2 ? int.Parse(a[2]) : 4;
                            for (int i = 0; i < n; i++) { retro_run(); frameNo++; }
                            buttons = 0; int w = a.Length > 3 ? int.Parse(a[3]) : 4;
                            for (int i = 0; i < w; i++) { retro_run(); frameNo++; }
                            break;
                        }
                    case "tap": // tap BTN count interval : repeated presses
                        {
                            int m = ParseButtons(a[1]); int cnt = int.Parse(a[2]); int iv = a.Length > 3 ? int.Parse(a[3]) : 10;
                            for (int k = 0; k < cnt; k++)
                            {
                                buttons = m; for (int i = 0; i < 3; i++) { retro_run(); frameNo++; }
                                buttons = 0; for (int i = 0; i < iv; i++) { retro_run(); frameNo++; }
                            }
                            break;
                        }
                    case "shot": Shot(a[1], a.Length > 2 ? int.Parse(a[2]) : 1); break;
                    case "save": { int n = (int)retro_serialize_size().ToUInt32(); byte[] s = new byte[n]; retro_serialize(s, (UIntPtr)n); File.WriteAllBytes(a[1], s); break; }
                    case "load": { byte[] s = File.ReadAllBytes(a[1]); if (!retro_unserialize(s, (UIntPtr)s.Length)) Console.WriteLine("load state failed"); break; }
                    case "ram": File.WriteAllBytes(a[1], Mem(2)); break;
                    case "sram": File.WriteAllBytes(a[1], Mem(0)); break;
                    case "vram": File.WriteAllBytes(a[1], Mem(3)); break;
                    case "poke":
                        {
                            IntPtr p = retro_get_memory_data(2);
                            Marshal.WriteByte(p, Convert.ToInt32(a[1], 16), (byte)Convert.ToInt32(a[2], 16)); break;
                        }
                    case "peek":
                        {
                            IntPtr p = retro_get_memory_data(2); int ad = Convert.ToInt32(a[1], 16); int n = a.Length > 2 ? int.Parse(a[2]) : 1;
                            var sb = new System.Text.StringBuilder();
                            for (int i = 0; i < n; i++) sb.Append(Marshal.ReadByte(p, ad + i).ToString("X2")).Append(' ');
                            Console.WriteLine(sb.ToString()); break;
                        }
                    case "frame": Console.WriteLine(frameNo); break;
                    case "reset": retro_reset(); break;
                    case "spoke": // spoke offset hexval : write battery RAM ($6000 = offset 0)
                        {
                            IntPtr p = retro_get_memory_data(0);
                            Marshal.WriteByte(p, Convert.ToInt32(a[1], 16), (byte)Convert.ToInt32(a[2], 16)); break;
                        }
                    case "echo": Console.WriteLine(line.Substring(4).Trim()); break;
                    case "quit": return 0;
                    default: Console.WriteLine("unknown: " + c); break;
                }
            }
            catch (Exception e) { Console.WriteLine("error: " + line + ": " + e.Message); }
            Console.Out.Flush();
        }
        return 0;
    }
}
