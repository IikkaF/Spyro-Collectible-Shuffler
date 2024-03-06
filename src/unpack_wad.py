import hashlib
import os
from typing import List
import wads

# This part of the program is based on the spyro-unwad tool by AlDeezy
# https://github.com/AlDeezy/spyro-unwad

## prep ##

READ_SIZE = 4
OUTPUT_DIR = os.path.join(os.path.dirname(os.getcwd()), "build", "wad")

NTSC_U_MD5 = '8094f8a9851c5c7a9a306c565750335f'


def extract(file_dir, out_dir, prefix='', name='output', max_files=0x100):
    if not os.path.exists(file_dir):
        print("ERROR: File does not exist.")
        return
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    ref = 0
    file_size = os.path.getsize(file_dir)
    # We will write the file structures into text files so we can reconstruct the WAD later
    file_structure = []
    with open(file_dir, "rb") as input_file:
        # Extract the subfiles
        for i in range(max_files):
            current_start = int.from_bytes(bytearray(input_file.read(READ_SIZE)), 'little')
            current_size = int.from_bytes(bytearray(input_file.read(READ_SIZE)), 'little')
            if current_size == 0:
                input_file.seek((i + 1) * 2 * READ_SIZE)
                continue

            input_file.seek(current_start)
            # If we are extracting the base WAD
            if out_dir == OUTPUT_DIR:
                new_name = wads.filenames[ref]
                output_dir = os.path.join(out_dir, new_name)
                ref += 1
            # If we are extracting one of the sub-WADs
            else:
                new_name = f"{prefix}{name}{i + 1}.dat"
                output_dir = os.path.join(out_dir, new_name)

            file_structure.append([new_name, current_start, current_size])
            with open(output_dir, "wb") as output_file:
                output_file.write(input_file.read(current_size))
            input_file.seek((i + 1) * 2 * READ_SIZE)

    structure_file_dir = os.path.join(out_dir, "file_structure.txt")
    with open(structure_file_dir, "w") as structure_file:
        structure_file.write(f"{file_size}\n")
        for file in file_structure:
            line = f"{file[0]},{file[1]},{file[2]}\n"
            structure_file.write(line)


def get_archives(filepath) -> List[str]:
    num = 0
    infiles = os.listdir(filepath)
    infiles = [f for f in infiles if os.path.isfile(filepath+'/'+f)]
    infiles.sort()
    outfiles = []
    for file in infiles:
        fin = open(f'{filepath}/{file}', "rb")
        w = fin.read(4)
        if w == b'\x00\x08\x00\x00':
            outfiles.append(file)
            tf = os.path.splitext(file)[0]
        fin.close()
    return outfiles


def unpack_wad(file_path, out_dir):
    if not (os.path.exists(file_path)):
        print(f"ERROR: file {file_path} does not exist.")
        return
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    md5.hexdigest()
    if not md5.hexdigest() == NTSC_U_MD5:
        print("ERROR: non-supported WAD.WAD file specified.")
        return

    # Extract base WADs
    print("\nUnpacking WAD.WAD...")
    extract(file_path, out_dir, name='file')

    # Extract sub WADs
    for file in get_archives(out_dir):
        fn = os.path.splitext(file)[0]
        f = f"{out_dir}/{file}"
        d = f"{out_dir}/{fn}/"
        extract(f, d, prefix=f"{fn}_", name='sub', max_files=0xa)
    print("Unpacking done\n")
