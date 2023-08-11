import os
import hashlib
import json


# Function to calculate SHA-256 hash of a file
def calculate_hash(file_path):
    with open(file_path, "rb") as file:
        bytes = file.read()  # read entire file as bytes
        readable_hash = hashlib.sha256(bytes).hexdigest()
        return readable_hash


named_dir = "NamedFiles"
unnamed_dir = "UnNamedFiles"

# Now iterate through each file in the directories and compute hashes
named_files = {}
unnamed_files = {}

# Iterate through named files
for dirpath, dirnames, filenames in os.walk(named_dir):
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        file_hash = calculate_hash(filepath)
        # Split the filename and extension
        filename_without_ext = os.path.splitext(filename)[0]
        named_files[file_hash] = filename  # Store filename with extension

# Iterate through unnamed files
for dirpath, dirnames, filenames in os.walk(unnamed_dir):
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        file_hash = calculate_hash(filepath)
        # Split the filename and extension
        filename_without_ext = os.path.splitext(filename)[0]
        unnamed_files[
            file_hash
        ] = filename_without_ext  # Store filename without extension

# Load existing mapped files from JSON if it exists
mapped_files = {}
try:
    with open("mapped_files.json", "r") as f:
        mapped_files = json.load(f)
except FileNotFoundError:
    pass

# Now map the unnamed files to the named ones if not already mapped
for file_hash, unnamed_file in unnamed_files.items():
    if file_hash in named_files and unnamed_file not in mapped_files:
        mapped_files[unnamed_file] = named_files[file_hash]

# Now you can print or save your hash groups to a JSON file
with open("mapped_files.json", "w") as f:
    json.dump(mapped_files, f, indent=4)
