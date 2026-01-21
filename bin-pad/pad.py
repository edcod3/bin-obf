import os
import sys

# 110 MB (shuold be enough for some AVs)
DEFAULT_PAD_AMOUNT = 110 * 1024 * 1024

def get_padded_path(path):
    base, ext = os.path.splitext(path)
    return f"{base}_padded{ext}"

def pad_exe_to_size(path, dst_path, target_size):
    current_size = os.path.getsize(path)
    if current_size > target_size:
        print("[*]", "File is already larger than target size. No Padding necessary...")

    with open(path, "rb") as src, open(dst_path, "wb") as dst:
        dst.write(src.read())
        padding = target_size - current_size
        if padding > 0:
            dst.write(b"\x00" * padding)

    print("[*]", f"Padded '{dst_path}' to {target_size} bytes")

def usage():
    print(f"Usage: {sys.argv[0]} <exe_path> [target_size_bytes] [create_new_file]")
    print("\nParameters:")
    print("\texe_path: Path of executable to be padded. Must be a Windows Executable.")
    print(f"\ttarget_size_bytes: Null Byte Padding to add to executable. Default: 110MB ({DEFAULT_PAD_AMOUNT} Bytes)")
    print("\tcreate_new_file: Don't pad in-place but create a new file. Filename will be appended with '_padded'. Can be 'true' / 'false' or 'y' / 'n'. Default: 'n'")
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

    target_size = DEFAULT_PAD_AMOUNT
    copy_mode = False
    for arg in sys.argv[2:]:
        if arg.isdigit():
            target_size = int(arg)
        elif arg in ["true", "y"]:
            copy_mode = True
    
    dst_path = get_padded_path(path) if copy_mode else path

    pad_exe_to_size(path, dst_path, target_size)

if __name__ == "__main__":
    main()