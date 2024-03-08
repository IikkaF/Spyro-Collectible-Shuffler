import os
import random

# Read size in bytes, 4 works well a lot of the time but some of the data can be for example 1 or 2 bytes
READ_SIZE = 4

build_dir = os.path.join(os.path.dirname(os.getcwd()), "build")

randomized_levels = ["0a_artisans", "0b_stone_hill", "0c_dark_hollow", "0d_town_square", "0e_toasty",
                    "14_peace_keepers", "15_dry_canyon", "16_cliff_town", "17_ice_cavern", "18_doctor_shemp",
                    "1e_magic_crafters", "1f_alpine_ridge", "20_high_caves", "21_wizard_peak", "22_blowhard",
                    "28_beast_makers", "29_terrace_village", "2a_misty_bog", "2b_tree_tops", "2c_metalhead",
                    "32_dream_weavers", "33_dark_passage", "34_lofty_castle", "35_haunted_towers", "36_jacques",
                    "3c_gnorc_gnexus", "3d_gnorc_cove", "3e_twilight_harbor", "3f_gnasty_gnorc", "40_gnastys_loot"]

# Used for finding the start of moby data for each level
sequences_before_moby_data = {
    "0a_artisans": 1,
    "0b_stone_hill": 1,
    "0c_dark_hollow": 1,
    "0d_town_square": 1,
    "0e_toasty": 2,
    "14_peace_keepers": 1,
    "15_dry_canyon": 1,
    "16_cliff_town": 1,
    "17_ice_cavern": 0,
    "18_doctor_shemp": 2,
    "1e_magic_crafters": 0,
    "1f_alpine_ridge": 1,
    "20_high_caves": 1,
    "21_wizard_peak": 1,
    "22_blowhard": 2,
    "28_beast_makers": 2,
    "29_terrace_village": 2,
    "2a_misty_bog": 1,
    "2b_tree_tops": 1,
    "2c_metalhead": 2,
    "32_dream_weavers": 1,
    "33_dark_passage": 2,
    "34_lofty_castle": 0,
    "35_haunted_towers": 0,
    "36_jacques": 1,
    "3c_gnorc_gnexus": 2,
    "3d_gnorc_cove": 0,
    "3e_twilight_harbor": 0,
    "3f_gnasty_gnorc": 2,
    "40_gnastys_loot": 1
}

# For debugging purposes
debugged_levels = {"2b_tree_tops"}


def find_start_of_moby_data(level):
    """
    This function finds the start index of the moby data in the sub4.dat file of the
    specified level.
    There has to be a better way to do this, but this is the one that I found.
    In every level except Twilight Harbor the moby data is preceded by a sequence
    of 8's and 0's. There can be several such sequences before the moby data, so we
    use the sequences_before_moby_data - dictionary to specify how many sequences
    there are before the moby data starts.
    :param level: Name of the specified level in the format '0b_stone_hill'
    :return: The index of the start of moby data for the level
    """

    # I found this value manually because Twilight Harbor data is different
    if level == "3e_twilight_harbor":
        return 12667

    file_dir = os.path.join(build_dir, f"wad/{level}/{level}_sub4.dat")
    filesize = os.path.getsize(file_dir)

    with open(file_dir, "rb") as file:
        i = 0
        sequences = 0
        while ((i + 1) * READ_SIZE < filesize):
            file.seek(i * READ_SIZE)
            current = int.from_bytes(file.read(READ_SIZE), "little")
            i += 1
            if current != 8:
                continue

            file.seek(i * READ_SIZE)
            current = int.from_bytes(file.read(READ_SIZE), "little")
            if current != 0:
                i += 1
                continue

            # Move to the end of the sequence of 0's and 8's
            while current == 0 or current == 8:
                i += 1
                file.seek(i * READ_SIZE)
                current = int.from_bytes(file.read(READ_SIZE), "little")

            if sequences == sequences_before_moby_data[level]:
                # We have found the start of the moby data
                break

            sequences += 1
            i += 1
        return i


def modify_data(seed, weights, randomized_types, skip_dragons):
    """
    This function modifies the data of all the levels.
    :param weights:
    :return:
    """

    print("\nModifying data...")

    if seed != -1:
        random.seed(seed)
    # Directory that contains the files that define the possible locations for moving stuff into
    randomizer_locations_dir = os.path.join(os.path.dirname(build_dir), "randomizer_locations")
    # Get all the categories for the locations (default has Easy, Medium, and Hard)
    randomizer_categories_dir = os.path.join(randomizer_locations_dir, "randomizer_categories.txt")
    categories = []
    with open(randomizer_categories_dir) as categories_file:
        for category in categories_file.readlines():
            categories.append(category.strip())

    for level in randomized_levels:
        level_data_dir = os.path.join(build_dir, "wad", level, f"{level}_sub4.dat")
        level_data_size = os.path.getsize(level_data_dir)
        level_locations_dir = os.path.join(randomizer_locations_dir, f"{level}_randomizer_locations.bin")
        if not os.path.isfile(level_locations_dir):
            print(f"No locations-file for {level}")
            continue

        i = find_start_of_moby_data(level)

        # Weights for the different categories
        level_weights = weights.copy()
        with open(level_data_dir, "r+b") as level_data, open(level_locations_dir, "rb") as level_locations:
            # Dictionary where keys are the different categories and values are arrays
            # that have the indices of all the available locations for that category
            location_indices = {}

            latest_idx = 0
            # Build the location_indices - dictionary
            for category in categories:
                category = category.lower()
                nof_locations = int.from_bytes(level_locations.read(READ_SIZE), "little")
                location_indices[category] = [latest_idx + i + 1 for i in range(nof_locations)]
                latest_idx = latest_idx + nof_locations
                level_weights[category] = level_weights[category] * nof_locations

            # Start reading level data from the start of the moby data
            while ((i + 1) * READ_SIZE < level_data_size and sum(level_weights.values()) > 0):
                # Get the type of the current moby
                level_data.seek((i + 15) * READ_SIZE + 2)
                current_type = int.from_bytes(level_data.read(2), "little")

                if current_type not in randomized_types:
                    i += 22
                    continue

                # If any of the supposed coordinates are 0, we have reached the end of moby data
                level_data.seek((i + 5) * READ_SIZE)
                current_x = int.from_bytes(level_data.read(READ_SIZE), "little")
                current_y = int.from_bytes(level_data.read(READ_SIZE), "little")
                current_z = int.from_bytes(level_data.read(READ_SIZE), "little")
                if current_x == 0 or current_y == 0 or current_z == 0:
                    break

                # Don't know what this technically does but it makes dragons collect instantly without cutscene
                if current_type == 250:
                    if skip_dragons:
                        level_data.seek((i + 2) * READ_SIZE)
                        level_data.write((0).to_bytes(READ_SIZE, "little"))
                    # Don't randomize the dragon in Gnorc Gnexus
                    if level == "3c_gnorc_gnexus":
                        i += 22
                        continue

                # Pick the category from which the location is picked
                selected_category = random.choices(list(level_weights.keys()), list(level_weights.values()), k=1)[0]
                # Pick a location from that category
                selected_location = random.choice(location_indices[selected_category])
                level_locations.seek(selected_location * READ_SIZE * 3)

                # Write the new coordinates
                level_data.seek((i + 5) * READ_SIZE)
                level_data.write(level_locations.read(READ_SIZE))
                level_data.write(level_locations.read(READ_SIZE))
                level_data.write(level_locations.read(READ_SIZE))

                # Again, don't know what exactly this does but it makes stuff render properly
                level_data.seek((i + 20) * READ_SIZE + 2)
                level_data.write((255).to_bytes(1, "little"))

                # Remove the just used location from the available ones
                # and recalculate weights
                location_indices[selected_category].remove(selected_location)
                new_weight = weights[selected_category] * len(location_indices[selected_category])
                level_weights[selected_category] = new_weight

                # Move on to the next moby
                i += 22

    print("Data modified\n")


def debug():
    """
    For debugging purposes
    Prints data values for levels in the debugged_levels - set
    """
    for level in debugged_levels:
        print(level)
        level_data_dir = os.path.join(build_dir, "wad", level, f"{level}_sub4.dat")
        level_data_size = os.path.getsize(level_data_dir)
        i = 0

        with open(level_data_dir, "rb") as level_data:
            """
            while ((i + 1) * READ_SIZE < level_data_size):
                level_data.seek(i * READ_SIZE)
                current = int.from_bytes(level_data.read(READ_SIZE), "little")
                print(current, i)
                i += 1
            """

            i = find_start_of_moby_data(level)
            while (i + 1) * READ_SIZE < level_data_size:
                # Get the type of the current moby
                level_data.seek((i + 15) * READ_SIZE + 2)
                current_type = int.from_bytes(level_data.read(2), "little")
                if current_type not in [293, 294, 85]:
                    i += 22
                    continue

                print(f"\n{i}")
                print(current_type)
                for j in range(0, 22):
                    level_data.seek((i + j) * READ_SIZE)
                    current = int.from_bytes(level_data.read(READ_SIZE), "little")
                    print(j, current)

                i += 22

# debug()