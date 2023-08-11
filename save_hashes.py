import os
import struct
import re
from colorama import Fore, init

init()

# Get all .dat files in the current directory
files = [f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(".dat")]

# We'll use this dictionary to store hashes of already processed files
processed_files = {}

for file in files:
    print(f"{Fore.GREEN}Processing file: {file}{Fore.RESET}")

    # Make parent directory
    parent_dir = os.path.splitext(file)[0]
    try:
        os.makedirs(f"hashes")
    except FileExistsError:
        pass
    with open(file, "rb") as f:
        loop = 0
        while True:
            f.seek(loop)
            hash_ = f.read(4).hex()
            if hash_ == "00000000":
                break

            # If file with this hash has already been processed, skip this loop
            if hash_ in processed_files:
                loop += 12
                continue
            else:
                processed_files[hash_] = True

            f.seek(loop + 4)
            offset = struct.unpack("I", f.read(4))[0]

            f.seek(loop + 8)
            size = struct.unpack("I", f.read(4))[0]

            # Get the file data
            f.seek(offset)
            data = f.read(size)

            filename = hash_  # Only the hashes are used as filenames now

            # Sanitize filename by removing unsupported characters
            filename = re.sub(r'[<>:"/\\|?*]', "", filename)

            save_path = os.path.join(f"hashes", filename)
            with open(save_path, "wb") as save_file:
                print(f"{Fore.YELLOW}Extracting: {filename}{Fore.RESET}")

                save_file.write(data)

            loop += 12

    print(f"{Fore.GREEN}Finished processing file: {file}{Fore.RESET}\n")
