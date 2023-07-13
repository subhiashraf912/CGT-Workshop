import os
import struct
import re
from colorama import Fore, init
import time

EXTENSION_MAP = {
    "56657273": {"prefix": "PhysicsVehicle"},
    "56455253": {"prefix": "SoundPack"},
    "53544154": {"prefix": "CharacterAnimations"},
    "52454658": {"prefix": "3DModel"},
    "224c6f61": {"prefix": "RenderingStats"},
    "4f564552": {"prefix": "CharacterAnimations"},
    "4d495353": {"prefix": "MissionScript"},
    "4c4d4246": {"prefix": "ObjectNames"},
    "2f2f4330": {"prefix": "REFX"},
    "0d0a2f2f": {"prefix": "REFX_DETAIL"},
    "466f6c65": {"prefix": "Foley"},
    "42726164": {"prefix": "Bradley"},
    "4369765f": {"prefix": "VehcilesRelated"},
    "4330345f": {"prefix": "ObjectsRelated"},
    "302c4272": {"prefix": "SoldiersSkills"},
}

EXTENSION_CONTENT_MAP = {
    "Kerned Pairs": {"prefix": "FontsMaybe", "dir": "txt"},
    "COL_Soldier,TR_WPN_AK47,WEAPON,0": {"prefix": "DefaultWeapons", "dir": "txt"},
    "TR_VEH_ZSU_232_AA_Gun C04_AAGunZU232 C04_AAGunZU232_DEAD": {
        "prefix": "VehiclesConnectors",
        "dir": "txt",
    },
    "TR_WPN_NORINCO_QBZ_97,-1,C04_Rifle_CHIN_NorincoQBZ97": {
        "prefix": "WeaponsConnectors",
        "dir": "txt",
    },
    "RamirezSkin": {"prefix": "Conners", "dir": "txt"},
    "JonesSkin": {"prefix": "Jones"},
    "Rookie,0,1.00": {"prefix": "Difficluties", "dir": "txt"},
    "MediKit,MEDI KIT,C04_MediKit": {"prefix": "ItemsConnectors", "dir": "txt"},
    "US_50cal_Heavy_machine_gun,US_WPN_Browning_50Cal,WEAPON": {
        "prefix": "VehiclesWeapons",
        "dir": "txt",
    },
    "Wheels,Wheels,Truck.sbk": {"prefix": "SoundPacks", "dir": "txt"},
}

init()

# Get all .dat files in the current directory
files = [f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(".dat")]

# We'll use this dictionary to store hashes of already processed files
processed_files = {}

for file in files:
    print(f"{Fore.GREEN}Processing file: {file}{Fore.RESET}")

    # Make parent directory
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
                or EXTENSION_MAP.get(ext.hex())
                or ext == b"Vers"
                or ext[:2] == b"//"
                or ext[:2] == b"\r\n"
                or ext[0:1] == b'"'
            ):
                # print(f"{Fore.RED} ext: {ext.hex()} {Fore.RESET}")
                dir_ext = "txt"

            else:
                try:
                    data.decode("ascii")
                    dir_ext = "unknownreadable"
                except UnicodeDecodeError:
                    dir_ext = "unknown"

            prefix = ""  # Initialize prefix as an empty string

            # Determine prefix based on extension
            decoded_data = data.decode("utf-8", errors="ignore")
            for extension, map_data in EXTENSION_MAP.items():
                if ext.hex() == extension:
                    prefix = map_data["prefix"]
                    if prefix == "PhysicsVehicle":
                        if "HLOU" in decoded_data:
                            prefix = "Map"
                        elif "ENVSND" in decoded_data:
                            prefix = "EnvironmentSounds"
                        elif "ENVFOGSETTING" in decoded_data:
                            prefix = "LightingSettings"
                        elif "EMOVIES" in decoded_data:
                            prefix = "Cutscenes"
                        elif "Version 8" in decoded_data:
                            prefix = "Textures"

            for content_to_be_checked, map_data in EXTENSION_CONTENT_MAP.items():
                if content_to_be_checked in decoded_data:
                    prefix = map_data["prefix"]
                    if map_data.get("dir"):
                        dir_ext: str = map_data.get("dir")  # type: ignore

            # # If prefix isn't determined, set it as 'NoPrefix'
            # if prefix == "":
            #     prefix = "NoPrefix"

            # Create subdirectory for this prefix if it doesn't exist
            prefix_dir = os.path.join(parent_dir, dir_ext, prefix)
            os.makedirs(prefix_dir, exist_ok=True)

            # If the file extension is 'eobj', assign a different filename
            if dir_ext == "eobj":
                f.seek(offset + 12)  # Move file cursor to the start of the filename
                raw_filename = f.read(64).decode("utf-8").replace("\x00", "")
                filename = "".join(re.findall(r"\w+", raw_filename)) + "." + hash_
            else:
                filename = (
                    f"{filename_prefix}_{hash_}" if filename_prefix else f"{hash_}"
                )

            # Process character animation files
            if prefix == "CharacterAnimations":  # type: ignore
                lines = decoded_data.split("\n")
                if len(lines) > 0:
                    animation_name_line = lines[0].strip()
                    # Extract animation name until the first non-alphanumeric character (excluding underscores)
                    match = re.search(r"^[a-zA-Z0-9_]+", animation_name_line)
                    if match:
                        animation_name = match.group(0)
                        # Remove leading and trailing whitespace and replace spaces with underscores
                        animation_name = animation_name.strip().replace(" ", "_")
                        # Truncate animation name to a maximum of 100 characters
                        animation_name = animation_name[:100]
                        # Update the filename
                        filename = f"{animation_name}.{filename}"

            # Sanitize filename by removing unsupported characters
            filename = re.sub(r'[<>:"/\\|?*]', "", filename)

            save_path = os.path.join(prefix_dir, f"{filename}.{dir_ext}")
            with open(save_path, "wb") as save_file:
                print(f"{Fore.YELLOW}Extracting: {filename}.{dir_ext}{Fore.RESET}")

                save_file.write(data)

            loop += 12

    print(f"{Fore.GREEN}Finished processing file: {file}{Fore.RESET}\n")
