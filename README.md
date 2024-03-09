# Spyro 1 Collectible Shuffler

This tool creates a new Spyro 1 disc image where collectibles have been moved around randomly in the maps.

# Instructions

## Basic usage

Put your spyro1.bin - file (must be the NTSC-U version and named like that) in the input-folder.
Open config.ini with a text editor to edit the configuration. Run the program through create_iso.bat if on Windows,
or run src/create_iso.py with Python. The new .bin/.cue - files are created into the output-folder.
Crashes and softlocks are possible, so remember to save the game regularly. The next sections discuss the configuration.

## Seeding

You can set a seed for the randomization, or set it to -1 for a random seed. Even with a set seed results are only guaranteed to be the same if the other settings are also the same.

## Weights

The possible locations that stuff can be moved into are categorized into three categories: Easy, Medium, and Hard.
- Easy locations can be reached without any advanced movement tech or game knowledge.
- Medium locations require basic speedrunning movement tech (charge gliding, wall gliding, damage boosting, etc.) and/or game knowledge, but don't require specific advanced tricks.
- Hard locations either require specific advanced tricks, specific game knowledge, or just need a precise execution.
If the weights for all of the categories are equal, every location has the same probability regardless of category. Because most of the levels have an overwhelming majority of locations in the Easy-category, this means that with equal weights most of the locations will be from the Easy-category. Feel free to give the other categories a bit more weight if that's what you're looking for.
Disclaimer: These categorizations are very subjective, and especially the Hard-category has a wide range of difficulties, some locations being extremely hard while others are basically trivial when you know what to do.

## Randomized_types

You can set for which moby types you want to change locations (True/False).

The following types should be safe to shuffle:
- Gems
- Basic chests (wooden and metal)
- Life chests
- Keys

The following types can be problematic:
-  Dragons: If you're using skip_dragon_cutscenes = True, dragons should be safe to randomize. They can sometimes despawn
   when flamed, but they will respawn upon death or level re-entry. If you absolutely
   want to see the cutscenes and set it to False, the game sometimes crashes on dragon rescues.
- Spring chests and fan chests: can be hard/impossible to break if moved to a location with no room to stand next to them.
-  Level exit vortexes: similarly to previous, can be hard to reach if moved to a location with no room to stand next to.
   They should always spawn somewhere with enough space above to exit through.
-  Fireworks chests and key chests: when you collect a certain gem from the gem fountain, the chest will no longer
   respawn and instead explodes instantly upon Spyro respawning or re-entering the level. The gems can become
   unobtainable if they fly into the void.
   
## Miscellaneous

skip_dragon_cutscenes should be set to True to prevent crashes on dragon rescues. I left the option to set this to False
because I'm unreasonably amused by some cutscenes that can happen with this randomizer.

# Under construction

I still need to add the code that creates the level location files using the Blender level models.
I may document the technical stuff just in case someone is interested in that.

# Acknowledgments

Thanks to AlDeezy for the level models I used to define the locations that stuff can be moved into:

https://www.youtube.com/watch?v=jkbUmt6-qwQ

As well as the spyro-unwad - tool I used as a basis for unpacking and repacking the game data:

https://github.com/AlDeezy/spyro-unwad