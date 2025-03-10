import os, struct, json, importlib, subprocess, sys




# The directory containing your files
directory = "mission05"




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




# The name of the .dat file to save
dat_filename = f"{directory}-modified.dat"

# Load existing mapped files from JSON if it exists
mapped_files = {}
try:
    with open("mapped_files.json", "r") as f:
        mapped_files = json.load(f)
except FileNotFoundError:
    pass

# Swap keys and values in the mapped_files dictionary
mapped_files = {v: k for k, v in mapped_files.items()}


def gather_files(directory):
    # Recursively gather all files in directory and subdirectories
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(foldername, filename)


# Get a list of all the files in the directory, including files in subdirectories
files = list(gather_files(directory))

# The offset into the .dat file where the data will start
offset = len(files) * 12

# Open the .dat file
with open(dat_filename, "wb") as dat_file:
    # Write the table of contents
    for filepath in files:
        filename = os.path.basename(filepath)
        # Get the hash
        if filename in mapped_files:
            hash_ = mapped_files[filename]
        else:
            # The filename is the hash if it's not in the map
            hash_ = filename.split(".")[0]

        # Get the size of the file
        size = os.path.getsize(filepath)

        # Write the hash, offset, and size to the .dat file
        try:
            dat_file.write(bytes.fromhex(hash_))
        except ValueError:
            print(f"Invalid hash: {hash_}")
            continue

        dat_file.write(struct.pack("I", offset))
        dat_file.write(struct.pack("I", size))

        # Update the offset
        offset += size

    # Write the data from each file
    for filepath in files:
        with open(filepath, "rb") as f:
            dat_file.write(f.read())

print(f"Number of files processed: {len(files)}")
