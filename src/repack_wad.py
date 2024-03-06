import os

READ_SIZE = 4
wad_dir = os.path.join(os.path.dirname(os.getcwd()), "build/wad")

def pack_folder(dir):
    # Get the structure of the current wad to be repacked
    file_structure = os.path.join(dir, "file_structure.txt")
    if not os.path.exists(file_structure):
        print("ERROR: No file_structure.txt in folder.")
        return
    with open(file_structure, "r") as file:
        file_structure = file.read().split("\n")

    # Get the path to the repacked wad
    dir_name = os.path.basename(dir)
    parent_dir = os.path.dirname(dir)
    if dir_name != "wad":
        repacked_dir = os.path.join(parent_dir, f"{dir_name}.wad")
    else:
        repacked_dir = os.path.join(parent_dir, "extract/WAD.WAD")

    with open(repacked_dir, "r+b") as repacked_wad:
        for i in range(1, len(file_structure) - 1):
            current_file_info = file_structure[i].split(",")
            current_start = int(current_file_info[1])
            current_size = int(current_file_info[2])

            with open(os.path.join(dir, current_file_info[0]), "rb") as current_file:
                repacked_wad.seek(current_start)
                repacked_wad.write(current_file.read())

def repack_wad():
    print("\nRepacking WAD.WAD...")
    # Repack the sub-wads
    for dir in os.listdir(wad_dir):
        if "." not in dir:
            pack_folder(os.path.join(wad_dir, dir))
    # Repack the base-wad
    pack_folder(wad_dir)
    print("Repacking done\n")
