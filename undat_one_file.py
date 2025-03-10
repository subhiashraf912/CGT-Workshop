import os, struct, re, json, importlib, subprocess, sys



file = "mission01.dat"




def ensure_installed(package_name: str, install_name: str | None = None) -> None:
    if not install_name:
        install_name = package_name

    try:
        importlib.import_module(package_name)
    except ImportError:
        print(f"Installing '{package_name}' ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Could not install package '{install_name}'. "
                "Check permissions or internet connection."
            ) from e

required_libraries = [

    {
        "import_name": "colorama",
        "install_name": "colorama"
    }

]

for required_lib in required_libraries:
    ensure_installed(required_lib["import_name"], required_lib["install_name"])


from colorama import Fore, init

init()

# dictionary to store hashes of already processed files
processed_files = {}

# load existing mapped files from JSON if it exists
mapped_files = {}
try:
    with open("mapped_files.json", "r") as f:
        mapped_files = json.load(f)
except FileNotFoundError:
    pass

print(f"{Fore.GREEN}Processing file: {file}{Fore.RESET}")

# make parent directory
parent_dir = os.path.splitext(file)[0]
os.makedirs(parent_dir, exist_ok=True)

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

        f.seek(offset)
        ext = f.read(4)

        filename_prefix = ""  # Initialize to an empty string

        # Get extension and directory
        f.seek(offset)
        data = f.read(size)

        if ext == b"DDS ":
            dir_ext = "dds"
        elif ext == b"PSF ":
            dir_ext = "psf"
        elif ext == b"SCH ":
            dir_ext = "sch"
        elif ext == b"EOBJ":
            dir_ext = "eobj"
        elif ext[1:4] == b"PNG":
            dir_ext = "png"
        elif ext.hex() == "02000000":
            dir_ext = "bin"
        elif ext == b"imgf":
            dir_ext = "imgf"
        elif ext == b"SLOC":
            dir_ext = "sloc"
        elif ext[:2] == b"BM":
            dir_ext = "bmp"
        elif (
            (ext[0:1].hex() > "47" and ext[0:1].hex() < "58")
            or ext == b"Vers"
            or ext[:2] == b"//"
            or ext[:2] == b"\r\n"
            or ext[0:1] == b'"'
        ):
            dir_ext = "txt"
        else:
            try:
                data.decode("ascii")
                dir_ext = "unknown-readable"
            except UnicodeDecodeError:
                dir_ext = "unknown"

        # Create subdirectory for this prefix if it doesn't exist
        prefix_dir = os.path.join(parent_dir, dir_ext)
        os.makedirs(prefix_dir, exist_ok=True)

        # Remove the hash part from the filename if the mapped name is available
        if hash_ in mapped_files:
            filename = mapped_files[hash_]
        else:
            filename = f"{hash_}.{dir_ext}"

        # Sanitize filename by removing unsupported characters
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)

        save_path = os.path.join(prefix_dir, f"{filename}")
        with open(save_path, "wb") as save_file:
            print(f"{Fore.YELLOW}Extracting: {filename}{Fore.RESET}")

            save_file.write(data)

        loop += 12

print(f"{Fore.GREEN}Finished processing file: {file}{Fore.RESET}\n")
