import os
import sys

# 110 MB (shuold be enough for some AVs)
DEFAULT_PAD_AMOUNT = 110 * 1024 * 1024

def pad_exe_to_size(path, target_size):
    current_size = os.path.getsize(path)
    if current_size > target_size:
        print("[*]", "File is already larger than target size. No Padding necessary...")

    with open(path, "ab") as f:
        f.write(b"\x00" * (target_size - current_size))

def usage():
    print(f"Usage: {sys.argv[0]} <exe_path> [target_size_bytes]")
    print("\nParameters:")
    print("\texe_path: Path of executable to be padded. Must be a Windows Executable.")
    print(f"\ttarget_size_bytes: Null Byte Padding to add to executable. Default: 110MB ({DEFAULT_PAD_AMOUNT} Bytes)")
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
    if len(sys.argv) >= 3:
        try:
            target_size = int(sys.argv[2])
        except ValueError:
            print("[!]", "Error: target size must be an integer (bytes)", "\nExiting...")
            sys.exit(1)

    pad_exe_to_size(path, target_size)

if __name__ == "__main__":
    main()