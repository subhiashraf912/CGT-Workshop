filename = "mission01.sch"  # replace with your file path
with open(filename, "rb") as f:
    contents = f.read()

# Look for ASCII strings in the file
for i in range(len(contents) - 4):
    if contents[i : i + 4] == b".psf":
        # Found a .psf file, print the filename
        j = i
        while contents[j] != 0:  # assuming filenames are null-terminated
            j -= 1
        print(contents[j + 1 : i + 4].decode("ascii"))
