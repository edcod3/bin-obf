import os
import sys
import subprocess
import tempfile

def xor(data, key):
    result = bytes(b ^ key for b in data)
    return result

def get_enc_path(path):
    base, ext = os.path.splitext(path)
    return f"{base}_xorenc{ext}"

def gen_cs_source(payload, xor_key):
    payload = ", ".join([hex(x) for x in payload])
    return """
using System;
using System.IO;
using System.Reflection;

namespace XfVaRtk
{
    class Program
    {
        static int Main(string[] hostArgs)
        {
            byte[] exeBytes = new byte[] { [[PAYLOAD]] };

            byte[] exePlain = xor(exeBytes, [[XOR_KEY]]);

            return ExecuteManagedExe(exePlain, hostArgs);
        }

        static byte[] xor(byte[] cipher, int key)
        {
            byte[] xored = new byte[cipher.Length];

            for (int i = 0; i < cipher.Length; i++)
            {
                xored[i] = (byte)(cipher[i] ^ (byte)key);
            }

            return xored;
        }

        static int ExecuteManagedExe(byte[] exeBytes, string[] args)
        {
            if (exeBytes == null || exeBytes.Length == 0)
                throw new ArgumentException("Executable bytes are invalid");


            Assembly assembly = Assembly.Load(exeBytes);

            MethodInfo entryPoint = assembly.EntryPoint
                ?? throw new InvalidOperationException("No entry point found");

            object result;

            // Handle both Main() and Main(string[] args)
            if (entryPoint.GetParameters().Length == 0)
            {
                result = entryPoint.Invoke(null, null);
            }
            else
            {
                result = entryPoint.Invoke(null, new object[] { args });
            }

            // If Main returns int, return it; otherwise assume success
            return result is int exitCode ? exitCode : 0;
        }
    }
}
    """.replace("[[PAYLOAD]]", payload).replace("[[XOR_KEY]]", xor_key)

def compile_cs(cs_source, dst_path):
    with tempfile.NamedTemporaryFile(mode="w") as tmp:
        tmp.write(cs_source)
        try:
            subprocess.check_output(["mcs", tmp.name, f"-out:{dst_path}"])
        except subprocess.CalledProcessError as e:
            print("Failed to compile C# source: ", e.output)
            sys.exit(1)
    
def xor_enc_exe(path: str, dst_path: str, xor_key: str):
    with open(path, "rb") as src:
        src_bytes = src.read()

    xor_key_int = int(xor_key.replace("0x", ""), 16)
    
    xored_src = xor(src_bytes, xor_key_int)

    cs_templ = gen_cs_source(xored_src, xor_key)
    compile_cs(cs_templ, dst_path)

    print("[*]", f"Wrote encrypted executable to '{dst_path}' using key '{xor_key}'")

def usage():
    print(f"Usage: {sys.argv[0]} <exe_path> [xor_key] [create_new_file]")
    print("\nParameters:")
    print("\texe_path: Path of executable to be padded. Must be a Windows Executable.")
    print(f"\txor_key: XOR key to obfuscate executable with. Must be prefixed with '0x'. Default: 0x69")
    print("\tcreate_new_file: Don't pad in-place but create a new file. Filename will be appended with '_padded'. Can be 'true' / 'false' or 'y' / 'n'. Default: 'n'")
    sys.exit(1)

def sanity_checks(path):
    try:
        file_type = subprocess.check_output(["file", path]) 
        if not b"Mono/.Net assembly" in file_type:
            print("[!]", "File is not a .NET assembly. This obfuscation script won't work...")
            sys.exit(1)
        mono_version = subprocess.check_output(["mono", "--version"]) 
        if not b"Mono JIT compiler" in mono_version:
            print("[!]", "Mono is not installed! Install 'mono-complete' or the respective package of your package manager...")
            sys.exit(1)
    except:
        print("[!]", "One of the sanity checks returned an error. Please either install 'file' or 'mono' (or 'mono-complete'). Check your respective package manager...")
        sys.exit(1)
        


def main():
    if len(sys.argv) < 2:
        usage()

    path = sys.argv[1]

    if path == "-h" or path == "--help":
        usage()

    if not os.path.isfile(path):
        print("[!]", "Error: file does not exist!", "\nExiting...")
        sys.exit(1)

    xor_key = "0x69"
    copy_mode = False
    for arg in sys.argv[2:]:
        if arg.startswith("0x"):
            xor_key = arg 
        elif arg in ["true", "y"]:
            copy_mode = True
    
    sanity_checks(path)
    
    dst_path = get_enc_path(path) if copy_mode else path

    xor_enc_exe(path, dst_path, xor_key)

if __name__ == "__main__":
    main()