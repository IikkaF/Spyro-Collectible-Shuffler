import pymkpsxiso
import os
import configparser
from unpack_wad import unpack_wad
from repack_wad import repack_wad
from modify_data import modify_data

root_path = os.path.dirname(os.getcwd())

name = "spyro1_collectible_shuffler"

"""
These are the moby types I've identified, it would be easy to identify more

RED_GEM = 83
GREEN_GEM = 84
BLUE_GEM = 85
GOLD_GEM = 86
PURPLE_GEM = 87

WOODEN_CHEST = 194
METAL_CHEST = 195
SPRING_CHEST = 329
FAN_CHEST = 390
FIREWORKS_CHEST = 312

KEY = 173
KEY_CHEST = 174
LIFE_CHEST = 421

VORTEX = 9

DRAGON = 250
DRAGON_PEDESTAL = 331

TREE_TOPS_GREEN_THIEF = 293
TREE_TOPS_RED_THIEF = 294

"""

moby_type_to_int = {
    "gem": [83, 84, 85, 86, 87],
    "basic_chest": [194, 195],
    "key": [173],
    "life_chest": [421],
    "spring_chest": [329],
    "fireworks_chest": [312],
    "fan_chest": [390],
    "key_chest": [174],
    "dragon": [250],
    "vortex": [9]
}

def create_iso():
    """
    This is the main part of the program that creates the new ISO with the modified data.
    """

    # Read config
    config = configparser.ConfigParser()
    config_dir = os.path.join(os.path.dirname(os.getcwd()), "config.ini")
    config.read(config_dir)
    weights = {}
    randomized_types = set()

    seed = -1
    if "seeding" in config.sections() and "seed" in config.options("seeding"):
        try:
            seed = config["seeding"].getint("seed")
        except ValueError:
            print("Invalid value for seed in config, using random seed")

    for category in config["weights"]:
        weights[category] = config.getfloat("weights", category)

    for type in config["randomized_types"]:
        if not config.getboolean("randomized_types", type):
            continue
        if type not in moby_type_to_int:
            continue
        for value in moby_type_to_int[type]:
            randomized_types.add(value)

    skip_dragons = True
    if "miscellaneous" in config.sections() and "skip_dragon_cutscenes" in config.options("miscellaneous"):
        try:
            skip_dragons = config.getboolean("miscellaneous", "skip_dragon_cutscenes")
        except ValueError:
            print("Invalid value for skip_dragon_cutscenes in config, using True")

    # Extract the contents of the ISO
    input_file_path = os.path.join(root_path, "input", "spyro1.bin")
    extract_path = os.path.join(root_path, "build", "extract")
    extract_xml_path = os.path.join(root_path, "build", "extract.xml")

    pymkpsxiso.dump(input_file_path, extract_path, extract_xml_path)

    # Unpack the WAD.WAD - file
    base_wad_path = os.path.join(root_path, "build", "extract", "WAD.WAD")
    wad_extract_path = os.path.join(root_path, "build", "wad")
    unpack_wad(base_wad_path, wad_extract_path)

    # Modify the data
    modify_data(seed, weights, randomized_types, skip_dragons)

    # Repack the WAD.WAD - file
    repack_wad()

    # Build the new ISO
    output_bin_path = os.path.join(root_path, "output", f"{name}.bin")
    output_cue_path = os.path.join(root_path, "output", f"{name}.cue")
    pymkpsxiso.make(output_bin_path, output_cue_path, extract_xml_path)

create_iso()