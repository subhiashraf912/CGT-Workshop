import os
import struct
import re

# The directory containing your files
directory = "mission02"

# The name of the .dat file to save
dat_filename = f"{directory}.dat"


def gather_files(directory):
    """Recursively gather all files in directory and subdirectories."""
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
        if filename.split(".")[-1] == "eobj" or "CharacterAnimations" in filepath:
            hash = re.findall(r"\b[a-fA-F0-9]{8}\b", filename)
            if hash:
                hash = hash[0]
            else:
                hash = filename.split(".")[0]
        else:
            hash = filename.split(".")[0]

        # Get the size of the file
        size = os.path.getsize(filepath)

        # Write the hash, offset, and size to the .dat file
        dat_file.write(bytes.fromhex(hash))
        dat_file.write(struct.pack("I", offset))
        dat_file.write(struct.pack("I", size))

        # Update the offset
        offset += size

    # Write the data from each file
    for filepath in files:
        with open(filepath, "rb") as f:
            dat_file.write(f.read())

print(f"Number of files processed: {len(files)}")
