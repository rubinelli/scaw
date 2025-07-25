"""
This module contains all the oracle tables and the logic for rolling on them.
These tables are used by the Warden to generate procedural content during the game.
"""

import random
from typing import Dict, Any

# --- Oracle Tables (Data from Warden's Guide) ---

CULTURE = {
    1: ("Altruistic", "Bounty"),
    2: ("Artistic", "Conquest"),
    3: ("Curious", "Control"),
    4: ("Devious", "Conversion"),
    5: ("Enlightened", "Division"),
    6: ("Hardy", "Dominance"),
    7: ("Harmonious", "Exploration"),
    8: ("Inventive", "Fealty"),
    9: ("Mercantile", "Independence"),
    10: ("Nomadic", "Knowledge"),
    11: ("Reclusive", "Natural Harmony"),
    12: ("Religious", "Peace"),
    13: ("Resilient", "Power"),
    14: ("Scholarly", "Purity"),
    15: ("Stoic", "Recognition"),
    16: ("Struggling", "Return"),
    17: ("Traditional", "Security"),
    18: ("War-like", "Stability"),
    19: ("Wealthy", "Unification"),
    20: ("Xenophobic", "Wealth"),
}
RESOURCES = {
    1: ("Food", "Food"),
    2: ("Fuel", "Fuel"),
    3: ("Gemstones", "Gemstones"),
    4: ("Herbs", "Herbs"),
    5: ("Horses", "Horses"),
    6: ("Knowledge", "Knowledge"),
    7: ("Land", "Land"),
    8: ("Livestock", "Livestock"),
    9: ("Medicine", "Medicine"),
    10: ("Ore", "Ore"),
    11: ("Skilled Labor", "Skilled Labor"),
    12: ("Spices", "Spices"),
    13: ("Stone", "Stone"),
    14: ("Textiles", "Textiles"),
    15: ("Tools", "Tools"),
    16: ("Trade Goods", "Trade Goods"),
    17: ("Vessels", "Vessels"),
    18: ("Water", "Water"),
    19: ("Weapons", "Weapons"),
    20: ("Wood", "Wood"),
}
FACTION_TYPES = {
    1: ("Artisans", "Academic"),
    2: ("Commoners", "Assassin"),
    3: ("Criminals", "Blacksmith"),
    4: ("Cultists", "Farmer"),
    5: ("Exiles", "General"),
    6: ("Explorers", "Gravedigger"),
    7: ("Industrialists", "Guard"),
    8: ("Merchants", "Healer"),
    9: ("Military", "Jailer"),
    10: ("Nobles", "Laborer"),
    11: ("Nomads", "Lord"),
    12: ("Pilgrims", "Merchant"),
    13: ("Protectors", "Monk"),
    14: ("Religious", "Mystic"),
    15: ("Revolutionaries", "Outlander"),
    16: ("Rulers", "Peddler"),
    17: ("Scholars", "Politician"),
    18: ("Settlers", "Spy"),
    19: ("Spies", "Thief"),
    20: ("Tribe", "Thug"),
}
FACTION_TRAITS = {
    1: ("Cautious", "Adaptable"),
    2: ("Connected", "Bankrupt"),
    3: ("Decadent", "Brutal"),
    4: ("Disciplined", "Collaborative"),
    5: ("Discreet", "Corrupt"),
    6: ("Dogmatic", "Craven"),
    7: ("Enigmatic", "Cruel"),
    8: ("Fierce", "Cunning"),
    9: ("Incorruptible", "Cynical"),
    10: ("Intellectual", "Deceptive"),
    11: ("Judicious", "Generous"),
    12: ("Keen", "Incompetent"),
    13: ("Loyal", "Manipulative"),
    14: ("Meticulous", "Mercurial"),
    15: ("Popular", "Repressed"),
    16: ("Pragmatic", "Ruthless"),
    17: ("Resourceful", "Selfish"),
    18: ("Secretive", "Stealthy"),
    19: ("Shrewd", "Threatened"),
    20: ("Tenacious", "Xenophobic"),
}
FACTION_AGENDAS = {
    1: ("Ascend to a Higher Plane", "A geographic barrier or impassable terrain."),
    2: ("Collect Artifacts", "A key piece of information must first be discovered."),
    3: ("Cultivate a Rare Resource", "A particular object or Relic is required."),
    4: ("Defend Something", "A powerful figure or foe must be eliminated."),
    5: ("Destroy Something", "A rare but necessary resource must first be acquired."),
    6: ("Dominate Others", "A serious debt forces the faction to make dire choices."),
    7: ("Enrich Themselves", "A well-known prophecy predicts imminent failure."),
    8: ("Establish a Colony", "An alliance with an enemy must first be brokered."),
    9: (
        "Establish a New Order",
        "An internal schism threatens to tear the faction apart.",
    ),
    10: ("Explore Uncharted Lands", "Another faction has the same goal."),
    11: ("Forge an Alliance", "Another faction stands in opposition."),
    12: ("Infiltrate Another Faction", "Commoners stand openly in opposition."),
    13: ("Preserve the Status Quo", "Considerable capital is required."),
    14: ("Protect a Secret", "Contravenes an established code, with a heavy penalty."),
    15: ("Purge the Land", "Hindered by cultural taboos."),
    16: ("Reveal a Secret", "Many must die, either as a necessity or consequence."),
    17: ("Revenge", "Must be carried out at a rare or exact moment."),
    18: ("Revive a Former Power", "Must be carried out in absolute secrecy."),
    19: ("Seek New Leadership", "Requires a specialist of an uncommon sort."),
    20: ("Spread a Belief", "The outcome would lead to unavoidable war."),
}
TERRAIN_DIE_DROP = {
    1: "Easy",
    2: "Easy",
    3: "Easy",
    4: "Tough",
    5: "Tough",
    6: "Perilous",
}
EASY_TERRAIN = {
    1: ("Bluffs", "Broken Sundial"),
    2: ("Dells", "Circle of Menhirs"),
    3: ("Farmlands", "Circular Maze"),
    4: ("Fells", "Cloud Stairway"),
    5: ("Foothills", "Dead Aqueduct"),
    6: ("Glens", "Enormous Footprint"),
    7: ("Grasslands", "Fallen Column"),
    8: ("Gulleys", "False Oasis"),
    9: ("Heaths", "Giant's Throne"),
    10: ("Lowlands", "Glittering Cascade"),
    11: ("Meadows", "Golden Bridge"),
    12: ("Moors", "Great Stone Face"),
    13: ("Pampas", "Great Waterwheel"),
    14: ("Pastures", "Heart Tree"),
    15: ("Plains", "Opaque Lake"),
    16: ("Plateaus", "Petrified Forest"),
    17: ("Prairies", "Pit of Cold Fire"),
    18: ("Savannas", "Silver Face"),
    19: ("Steppes", "Sinkhole"),
    20: ("Valleys", "Titanic Gate"),
}
TOUGH_TERRAIN = {
    1: ("Barrens", "Algae Falls"),
    2: ("Canyons", "Basalt Columns"),
    3: ("Chaparral", "Behemoth Graveyard"),
    4: ("Coral Reefs", "Canyon Bridge"),
    5: ("Deserts", "Cinder Cones"),
    6: ("Dunes", "Half-Buried Ark"),
    7: ("Estuaries", "Flame Pits"),
    8: ("Fens", "Forest of Arrows"),
    9: ("Forests", "Frozen Waterfall"),
    10: ("Heathlands", "Fungal Forest"),
    11: ("Hills", "Hanging Valley"),
    12: ("Mangroves", "Inverted Lighthouse"),
    13: ("Marshlands", "Leviathan Bones"),
    14: ("Moorlands", "Massive Crater"),
    15: ("Rainforests", "Massive Dung Ball"),
    16: ("Scrublands", "Salt Flat Mirrors"),
    17: ("Taiga", "Shrouded Ziggurat"),
    18: ("Thickets", "Stalagmite Forest"),
    19: ("Tundra", "Sunken Colossus"),
    20: ("Woodlands", "Titan's Table"),
}
PERILOUS_TERRAIN = {
    1: ("Alpine Meadows", "Active Volcano"),
    2: ("Bogs", "Ammonia Caves"),
    3: ("Boulders", "Bone Mountain"),
    4: ("Caverns", "Crystalline Forest"),
    5: ("Cliffs", "Dome of Darkness"),
    6: ("Craters", "Enormous Hive"),
    7: ("Crevasses", "Floating Object"),
    8: ("Geysers", "Inactive Automaton"),
    9: ("Glaciers", "Land Scar"),
    10: ("Gorges", "Large Vents"),
    11: ("Hollows", "Magma Sculptures"),
    12: ("Ice Fields", "Man on the Mountain"),
    13: ("Jungles", "Meteor Garden"),
    14: ("Lava Fields", "Obsidian Needle"),
    15: ("Mountains", "Reverse Waterfall"),
    16: ("Peatlands", "River of Sulfur"),
    17: ("Quagmires", "Siren Stones"),
    18: ("Ravine", "Sky-Root"),
    19: ("Swamps", "Titanic Ribcage"),
    20: ("Wastelands", "Weeping Bubble"),
}
POI_DIE_DROP = {
    1: "Waypoint or Settlement",
    2: "Curiosity",
    3: "Curiosity",
    4: "Lair",
    5: "Dungeon",
    6: "Dungeon",
}
SETTLEMENTS = {
    1: ("Academy", "Built atop Ruins"),
    2: ("Caravan", "Built on Bones of Giants"),
    3: ("Citadel", "Center of Learning"),
    4: ("City", "Close-Knit"),
    5: ("Commune", "Divided"),
    6: ("Compound", "Emits a Mysterious Hum"),
    7: ("Convent", "Famous for its Artisans"),
    8: ("Farmstead", "Famous for its Festivals"),
    9: ("Fortress", "Guarded by Trained Beasts"),
    10: ("Garrison", "Hides a Dangerous Portal"),
    11: ("Hamlet", "High Population Density"),
    12: ("Keep", "Impregnable"),
    13: ("Monastery", "Integrated with Nature"),
    14: ("Outpost", "Known for its Hospitality"),
    15: ("Plantation", "Location of a Legendary Forge"),
    16: ("Prison", "Moves or Revolves"),
    17: ("Stronghold", "Protected by a Great Warrior"),
    18: ("Town", "Ruled by a Powerful Faction"),
    19: ("Villa", "Steeped in Tradition"),
    20: ("Village", "Trading Hub"),
}
WAYPOINTS = {
    1: ("Archive", "A Haven for Outcasts"),
    2: ("Asylum", "Built on Sacred Grounds"),
    3: ("Bazaar", "Contains a Powerful Artifact"),
    4: ("Beacon Tower", "Cursed By Previous Occupants"),
    5: ("Bunker", "Decrepit Buildings"),
    6: ("Cabin", "Distrustful Occupants"),
    7: ("Campground", "Does Not Appear on Any Map"),
    8: ("Guildhall", "Front for Illegal Operations"),
    9: ("Hospice", "Host to a Renowned Artisan"),
    10: ("Hunting Lodge", "Known for its Elaborate Defenses"),
    11: ("Inn", "Occupants Are Lawful to a Fault"),
    12: ("Observatory", "Occupants Are Overly Formal"),
    13: ("Reservoir", "Outsiders Are Barred"),
    14: ("Sanatorium", "Outsiders Cannot Carry Weapons"),
    15: ("Sanctuary", "Part of an Illegal Trade Route"),
    16: ("Shrine", "Popular Pilgrim Destination"),
    17: ("Temple", "Protects a Powerful Object"),
    18: ("Trading Post", "Reclusive Occupants"),
    19: ("Watchtower", "Sits on Natural Deposits"),
    20: ("Work Camp", "Technologically Advanced"),
}
CURIOSITIES = {
    1: ("Ancient Tree", "Abandoned Vessel"),
    2: ("Broken Tower", "Ancient Trash Heap"),
    3: ("Buried Megalith", "Buried Ley Line"),
    4: ("Collapsed Mill", "Buried Library"),
    5: ("Cracked Bell", "Carnivorous Plants"),
    6: ("Crystal Spire", "Celestial Mirror"),
    7: ("Dripping Archway", "Cult Ritual Site"),
    8: ("Echoing Fields", "Edible Fungus"),
    9: ("Enormous Fist", "Floating Debris"),
    10: ("Enormous Footprint", "Hidden Market"),
    11: ("Floating Island", "Illusory"),
    12: ("Frozen Graveyard", "Impossible Music"),
    13: ("Hanging Bridges", "Infested With Vermin"),
    14: ("Illegible Signpost", "Irregular Gravity"),
    15: ("Leviathan Skeleton", "Isolated Weather"),
    16: ("Oddly-Shaped Lake", "Only Appears at Night"),
    17: ("Petrified Trees", "Perpetual Mist"),
    18: ("Purple Geysers", "Perpetual Shadows"),
    19: ("Singing Stones", "Site of Ancient Battle"),
    20: ("Sunken City", "Unstable Ground"),
}
LAIRS = {
    1: ("Abandoned Tower", "Abandoned"),
    2: ("Ancient Prison", "At Crossroads"),
    3: ("Collapsed Mine", "Baited Entrance"),
    4: ("Colossal Hive", "Bioluminescence"),
    5: ("Crashed Ship", "Constant Screaming"),
    6: ("Crumbling Fort", "Entry Forbidden"),
    7: ("Dry Aqueduct", "Faction Hideout"),
    8: ("Enormous Stump", "Hidden Exit"),
    9: ("Forgotten Graveyard", "Odd Machinery"),
    10: ("Hidden Burrow", "Piles of Bones"),
    11: ("Hollow Obelisk", "Previously Occupied"),
    12: ("Overgrown Garden", "Religious Graffiti"),
    13: ("Primeval Menhirs", "Scattered Traps"),
    14: ("Primitive Bridge", "Scavengers Prowl"),
    15: ("Rotted Mill", "Signs Posted"),
    16: ("Ruined Town", "Something Sleeps"),
    17: ("Rusted Construct", "Symbiotic Entity"),
    18: ("Spiked Cave", "Training Camp"),
    19: ("Sunken Grotto", "Underwater"),
    20: ("Unruly Copse", "Waste Pit"),
}
DUNGEONS = {
    1: ("Burial Ground", "Abandoned"),
    2: ("Cave", "Buried"),
    3: ("Cellar", "Burnt"),
    4: ("Crypt", "Clockwork"),
    5: ("Den", "Collapsed"),
    6: ("Estate", "Crumbling"),
    7: ("Fort", "Crystalline"),
    8: ("Great Hall", "Floating"),
    9: ("Laboratory", "Flooded"),
    10: ("Manor", "Fungal"),
    11: ("Mine", "Inverted"),
    12: ("Outpost", "Isolated"),
    13: ("Palace", "Mirrored"),
    14: ("Prison", "Otherworldly"),
    15: ("Ruined City", "Overgrown"),
    16: ("Stronghold", "Petrified"),
    17: ("Temple", "Remote"),
    18: ("Tomb", "Sealed"),
    19: ("Tower", "Toxic"),
    20: ("Workshop", "Warped"),
}
PATH_FEATURES = {
    1: ("Abandoned Fields", "Bandit Ambushes"),
    2: ("Blood-Red", "Blocked by Giant Boulder"),
    3: ("Buried Charms", "Collapsed Bridge"),
    4: ("Cattle Prints", "Confusing to Navigate"),
    5: ("Constant Patrols", "Dense Bramble"),
    6: ("Dead Vegetation", "Divided by Political Dispute"),
    7: ("Disappearing", "Erratic Weather"),
    8: ("Diseased Animals", "Frequent Flash Floods"),
    9: ("Follows the Stars", "Gets Extremely Cold"),
    10: ("Frequent Pilgrims", "Heavy Toll Required"),
    11: ("Massive Grooves", "Labyrinthine Canyons"),
    12: ("Mile Markers", "Night Predators"),
    13: ("Mineral Flecks", "Occasional Stampedes"),
    14: ("Newly Made", "Overcrowded"),
    15: ("Overgrown", "Passes over Rapids"),
    16: ("Rusted Tools", "Poisonous Fruit"),
    17: ("Shredded", "Smoke-filled"),
    18: ("Shriveled Away", "Steep Climb"),
    19: ("Twisted", "Thick Evening Mist"),
    20: ("Ubiquitous Footprints", "Uneven, Soggy Ground"),
}

PHYSIQUE = {
    1: "Athletic",
    2: "Brawny",
    3: "Flabby",
    4: "Lanky",
    5: "Rugged",
    6: "Scrawny",
    7: "Short",
    8: "Statuesque",
    9: "Stout",
    10: "Towering",
}

SKIN = {
    1: "Birthmarked",
    2: "Marked",
    3: "Oily",
    4: "Rosy",
    5: "Scarred",
    6: "Soft",
    7: "Tanned",
    8: "Tattooed",
    9: "Weathered",
    10: "Webbed",
}

HAIR = {
    1: "Bald",
    2: "Braided",
    3: "Curly",
    4: "Filthy",
    5: "Frizzy",
    6: "Long",
    7: "Luxurious",
    8: "Oily",
    9: "Wavy",
    10: "Wispy",
}

FACE = {
    1: "Bony",
    2: "Broken",
    3: "Chiseled",
    4: "Elongated",
    5: "Pale",
    6: "Perfect",
    7: "Rakish",
    8: "Sharp",
    9: "Square",
    10: "Sunken",
}

SPEECH = {
    1: "Blunt",
    2: "Booming",
    3: "Cryptic",
    4: "Droning",
    5: "Formal",
    6: "Gravelly",
    7: "Precise",
    8: "Squeaky",
    9: "Stuttering",
    10: "Whispery",
}

CLOTHING = {
    1: "Antique",
    2: "Bloody",
    3: "Elegant",
    4: "Filthy",
    5: "Foreign",
    6: "Frayed",
    7: "Frumpy",
    8: "Livery",
    9: "Rancid",
    10: "Soiled",
}

VIRTUE = {
    1: "Ambitious",
    2: "Cautious",
    3: "Courageous",
    4: "Disciplined",
    5: "Gregarious",
    6: "Honorable",
    7: "Humble",
    8: "Merciful",
    9: "Serene",
    10: "Tolerant",
}

VICE = {
    1: "Aggressive",
    2: "Bitter",
    3: "Craven",
    4: "Deceitful",
    5: "Greedy",
    6: "Lazy",
    7: "Nervous",
    8: "Rude",
    9: "Vain",
    10: "Vengeful",
}

BONDS = {
    1: "You inherited a single Gem (500gp, cold and brittle) from a long-dead relative. It arrived with a warning: squander your newfound riches, and a debt long thought forgotten would be called in.",
    2: "A distant cousin left you a small inheritance. Take 20gp and a Strange Compass (petty) that always points towards something deep in the Wood.",
    3: "You carry a hand-drawn Portrait (petty) of a past love who disappeared into the Wood long ago. Somehow you know that they are still alive.",
    4: "You found a Tiny Crystal Prism (petty) buried in the dirt. When held up to the light, it shows visions of an unknown location deep within the Wood. Sometimes you feel a presence looking back at you.",
    5: "You once freed a Naiad from a choked stream. In return, it gave you some Silver Moss (petty). Swallow it near water, and the creature will come, once, to repay its debt.",
    6: "You inherited an old Journal, bound in bark. Each evening, its pages are filled with the events of the day, crassly written from the journal's perspective. The writing is crude but accurate.",
    7: "You protect a long-dormant family secret. Take one half of an Ancient Key (petty). They say that if joined with its twin, it opens a Gate through any door.",
    8: "You received a Letter (petty) detailing incontrovertible proof that your true parentage is that of Fae nobility. The note also indicates a date and location where you are to meet the letter's author, deep in the Wood.",
    9: "You owe a great debt to a member of the nobility and carry their Signet Ring (petty), which serves as proof of their protection as well as your obligation.",
    10: "You consumed a Mischievous Spirit that wreaks havoc on your insides, demanding to be taken home, deep in the Wood. It occupies one slot but absorbs one Fatigue each day. It wants you alive (for now).",
    11: "A roaming storyteller once spun you tales of great treasure hidden deep in the Wood. You thought it naught but fancy, till they gave you a Rolled-up Map (petty) marked with an X.",
    12: "During your travels, you met a dying hunter who asked you to deliver a message to their loved ones. Take a Letter (petty), sealed with tree sap. It is addressed only to the Lord of Winter.",
    13: "You found a wounded beast in the forest but chose to ignore it. You see it everywhere now, but only when you're alone. It looks sad but not angry. You cannot become panicked when acting alone.",
    14: "You promised a childhood friend that you'd bring them back a rare gift, something unique in all the world. Take a Bracelet (petty) woven from twine and wildflowers.",
    15: "You crossed a creature of the Wood, and it cursed you with a Stone Heart. With each passing month, the stone grows heavier by one slot. Until your debt is lifted, you cannot truly die.",
    16: "You carved a Whistle (petty) from an Oak Lord's branch. Your act did not go unnoticed. You cannot seem to rid yourself of the whistle either.",
    17: "The Dawn Brigade did your family a service, giving you a dried Blood-Red Flower (petty) as proof. When the flower turns white, it means the favor is owed.",
    18: "An entertainer once visited your home, filling it with story and song. He left one day without a word, leaving behind only a Miniature Lute. Something rattles inside.",
    19: "A white crow appeared to you in a dream, holding a twig in its mouth. You awoke the next morning with the Twig (petty) in your hand. You believe it brings you luck. It smells faintly of sulfur.",
    20: "One of your ancestors wronged a Moss Witch, who cursed their bloodline. Your visage causes mirrors to shatter. You've noticed that the shards can sometimes reveal illusions.",
}

OMENS = {
    1: "The once rich waters of a life-giving river have turned black and putrid, tainting the land and sickening those who drink from it. A village elder points to some recent desecration as the cause, but most do not heed their words.",
    2: "It feels like winter has arrived too quickly this year, frost and snows making their appearance much earlier than expected. There is talk of a pattern to the frost found in windows, ponds, and cracks in the ground. It almost looks like a map.",
    3: "A thick, unnatural fog has begun encroaching upon an ancient and holy grove. It is said to be the work of a great forest spirit, angered by nearby deforestation.",
    4: "The night sky grows dimmer each evening, as if stars are disappearing one by one. Rumors of hellish creatures capturing farmers and pulling them into the Roots are spreading like wildfire. Village elders believe the two are connected.",
    5: "The songbirds of the Wood have fallen eerily silent as of late. Hunters claim that a spectral figure has been spotted wandering the forest, gazing longingly at anyone it encounters.",
    6: 'Strange, tear-shaped stones have been found throughout the region, sparking a "gold rush" of sorts for jewelers and thieves alike. The locals believe they are the tears of the earth itself, weeping for a great tragedy yet to come.',
    7: "Swarming pests gnaw away at the edges of dreams, and farmers speak of a loud buzzing sound emanating from deep within the Wood. They also say that the sound is getting closer.",
    8: "There is a village known far and wide for its impressive “mother tree,” said to shelter the town's secrets in its boughs. Recently it has begun bleeding red sap, worrying the elders.",
    9: "The moon turns a deep crimson, bathing the night in an eerie, blood-red light. Some say it heralds a time of chaos and strife, as the boundaries between the Wood and the mortal realm grow thin.",
    10: "Strange cracks have appeared in the night sky, revealing a swirling vortex of light and color. Some say that the divide between realms is at its weakest in centuries and fear what may emerge from the other side.",
    11: "A night-blooming flower once thought extinct is sprouting up throughout the Wood. Its scent is intoxicating but also causes vivid nightmares.",
    12: "Local livestock have grown increasingly agitated and unmanageable as of late. An old shepherd says it is due to an unsettling howl that emanates from the Wood each full moon.",
    13: "Swarms of insects are fleeing from the Wood in droves, destroying any wooden structures they come across. The sound of their wings hum a familiar tune as they pass overhead, like a forgotten nursery rhyme.",
    14: "Hunters talk of a curse that befalls any who kill any beast with a streak of white fur: soon after, they are found dead in their homes. Each day, there are fewer and fewer creatures to hunt.",
    15: "Folks say that a faint laughter can be heard echoing out of wells all over the city, and that the echoes change to sobs at night.",
    16: "The constellations have slowly started shifting in the night sky, forming unfamiliar patterns that have stargazers and sages perplexed. Even the animals seem disturbed.",
    17: "An ancient tree at the heart of a sleepy village has suddenly withered and died, despite showing no signs of disease. After its trunk was cut, a bloody hand was found in its core.",
    18: "Statues have been weeping blood for months on end, and the wombs of the village have lain barren since. A single child has been the only exception, hidden away by elders overcome with fear and dread.",
    19: "Local fauna is behaving oddly, displaying heightened aggression or fleeing the area entirely. Hunters talk of a shadowy figure that roams the Wood, calling to the animals.",
    20: "Border towns have become riotous in recent weeks after multiple claims of a red-robed figure appearing in their children's dreams, uttering the same warning: A fire is coming, and it will consume everything.",
}

BACKGROUNDS = {
    1: {
        "name": "Aurifex",
        "starting_gear": ["Rations (3 uses)", "Lantern", "Oil Can (6 uses)", "Needle-Knife (d6)", "Protective Gloves (petty)"],
        "names": ["Hestia", "Basil", "Rune", "Prism", "Ember", "Quintess", "Aludel", "Mordant", "Salaman", "Jazia"],
        "what_experiment_went_horribly_wrong": {
            1: {"description": "There was an explosion, and you lost your sense of smell. Well, almost: you can sniff out gold as a pig does truffles. Use it every day or become deprived.", "items": ["Tin of Snuff (6 uses)"]},
            2: {"description": "You dematerialized a beloved pet. Now it follows you around, invisible but always present. Although it cannot interact with the physical realm, you are able to share its sense. (Add a Fatigue each time.) It follows basic commands.", "items": []},
            3: {"description": "You were exposed to a long-acting truth serum whose effects have yet to wear off. The disorder has its advantages: you cannot repeat lies you've heard, either.", "items": []},
            4: {"description": "You were adept at creating fake gold, which is almost as good. Eventually, your ruse was discovered, and you had to make a hasty retreat.", "items": ["Metal Ingot", "Gold Powder (3 uses)"]},
            5: {"description": "Your alchemical recipe worked, but a rival stole the blueprint before your claims could be proven. You have a taste for revenge.", "items": ["Blunderbuss (d12, blast, bulky)"]},
            6: {"description": "Ridiculed for discovering how to turn gold into lead, you were a laughing stock.", "items": ["Universal Solvent (2 uses)"]},
        },
        "what_alchemical_marvel_is_the_product_of_your_latest_ingenuity": {
            1: {"description": "Pyrophoric Gel: A sticky green fluid that catches fire when exposed to air, then burns for 8 hours. Cannot be extinguished (1 use).", "items": ["Pyrophoric Gel (1 use)"]},
            2: {"description": "Blast Sphere: A head-sized iron ball filled with explosive powder that explodes on impact (d12, blast, bulky, 1 use).", "items": ["Blast Sphere (1 use)"]},
            3: {"description": "Aqua Vita: Purifies any liquid, converting it to pure water. Drinking it cures 1d6 STR (1 use).", "items": ["Aqua Vita (1 use)"]},
            4: {"description": "Mimic Stone: Records a short phrase that can later be played back.", "items": ["Mimic Stone"]},
            5: {"description": "Spark Dust: Ignites easily and quickly. Useful for starting a fire or as an incendiary device (3 uses).", "items": ["Spark Dust (3 uses)"]},
            6: {"description": "Homunculus: A miniature clay replica of yourself that follows your every command. It hates being enthralled to you and complains bitterly whenever possible. Any damage done to the homunculus is also done to you. 3 HP, 4 STR, 13 DEX, 5 WIL", "items": ["Homunculus"]},
        },
    },
    2: {
        "name": "Barber-Surgeon",
        "starting_gear": ["Rations (3 uses)", "Saw (d6)", "Scissors (d6)", "Needle & Thread", "Twisted Pole"],
        "names": ["Cullen", "Galen", "Suspectra", "Celsus", "Paracelsus", "Avicenna", "Rashid", "Zosimos", "Folke", "Hippocrates"],
        "how_have_you_improved_yourself": {
            1: {"description": "You have a replacement eye that can magnify objects, act as a telescope, and provide minimal night vision. You cannot wear anything metal on your head, and the presence of strong magnets make you deprived.", "items": []},
            2: {"description": "One foot is mostly metal (kick, d6), and you treat some Tough terrain as Easy. Without a daily application of oil, you are deprived and noisy.", "items": ["Oil Can (6 uses)"]},
            3: {"description": "One of your fingers has been swapped, the bone replaced by gold and iron.", "items": ["Hook", "Screwdriver"]},
            4: {"description": "Both ears have been surgically enhanced, tripling your hearing. You can focus on a specific sound, such as a conversation, at a great distance. You wear an ear flap to protect against sudden loud noises (WIL save to avoid temporary paralysis).", "items": []},
            5: {"description": "Your chest is lined with alchemical sigils, toughening the skin (1 Armor). Wearing other metallic armor nullifies the effect.", "items": []},
            6: {"description": "One arm is fully metal and comes off at the shoulder. It can be used as a weapon (d8, bulky when not attached) and can move independently if you are within sight of it.", "items": []}
        },
        "what_rare_tool_is_essential_to_your_work": {
            1: {"description": "Regrowth Salve: Regrows a body part over the course of a day.", "items": ["Regrowth Salve (1 use)"]},
            2: {"description": "Graftgrub: A small worm that can fuse inanimate objects with parts of the body.", "items": ["Graftgrub (1 use)"]},
            3: {"description": "Woundwax: Heals wounds from fire or chemicals (restoring full STR) but nothing else.", "items": ["Woundwax (2 uses)"]},
            4: {"description": "Quicksilver: A stimulant. Go first in combat, and automatically pass any WIL saves for one hour. Addictive: Save STR or become deprived after 24 hours without it.", "items": ["Quicksilver (4 uses)"]},
            5: {"description": "Pneuma Pump: Portable iron lungs (bulky). Enables life-saving surgery or underwater breathing.", "items": ["Pneuma Pump"]},
            6: {"description": "Lodestone: Draws out dangerous elements from the body and acts as a powerful magnetic force.", "items": ["Lodestone"]}
        }
    },
    3: {
        "name": "Beast Handler",
        "starting_gear": ["Rations (3 uses)", "Thick Gloves", "Whistle (petty)", "Net", "Muzzle"],
        "names": ["Ursula", "Grizzly", "Marl", "Lynx", "Corbin", "Drake", "Finch", "Hawk", "Newt", "Sorrel"],
        "what_creature_is_your_specialty": {
            1: {"description": "Arachnids: It can destroy a large spider nest in seconds.", "items": ["Quick-Flame Rod", "Oil Can (6 uses)"]},
            2: {"description": "Felines: Its odor can calm and control even the largest of cats.", "items": ["Sack of Whiskerwort"]},
            3: {"description": "Canines: Effective against werewolves as well.", "items": ["Wreath of Wolfsbane", "Large Net"]},
            4: {"description": "Birds: It can imitate any bird call and can even be used to send simple messages. Recharge: Feed a baby bird as its mother would, then blow.", "items": ["Warble-Whistle (3 charges)"]},
            5: {"description": "Rodents: So long as you play, they will follow, even to their deaths.", "items": ["Pan Flute"]},
            6: {"description": "Serpents: Take a Warming Stone that generates an irresistible heat.", "items": ["Warming Stone", "Antitoxin (2 uses)"]}
        },
        "what_have_you_learned_from_the_creatures_of_the_wild": {
            1: {"description": "That there is far more to the world than meets the eye. With quiet concentration, you can borrow the senses of a nearby creature of your specialty.", "items": []},
            2: {"description": "That the behavior of beasts is a language in itself. When observing beasts of your specialty you gain insight into weather patterns and impending disasters.", "items": []},
            3: {"description": "That the pulse of the hunt is a powerful impulse. You have a sense for when predators, even those not of your specialty are near.", "items": []},
            4: {"description": "That the land is a language unto itself. Your chance of becoming lost in a terrain dominated by the beasts of your specialty is reduced by one step (e.g. 4-in-6 becomes 3-in-6).", "items": []},
            5: {"description": "That nature's symphony can be heard if you attune to its rhythm. When surrounded by creatures of your specialty, they can alert you to approaching danger before it arrives.", "items": []},
            6: {"description": "That survival is all about adaptability. Once per day, you may take on a simple feature from a creature of your specialty (webbed fingers, night vision, etc.). Add a Fatigue each time.", "items": []}
        }
    },
    4: {
        "name": "Bonekeeper",
        "starting_gear": ["Rations (3 uses)", "Shovel", "Crowbar", "Sack", "Trowel"],
        "names": ["Agnes", "Marrow", "Scapula", "Spine", "Femur", "Tibia", "Patella", "Clavicle", "Cranium", "Carcass"],
        "what_did_you_take_from_the_dead": {
            1: {"description": "A crow-shaped amulet. You can ask a question of the dead but must add a Fatigue each time. They do not always speak truthfully.", "items": ["Crow-shaped Amulet"]},
            2: {"description": "A mortal wound from a freed revenant. You were healed, but the disfigurement has made you a pariah. You require neither air nor sustenance but are still subject to pain and death. Trapped between worlds, the dead see you as one of their own.", "items": []},
            3: {"description": "A Blood Pail (bulky) from a local death-cult. Empty it to raise a servant built from whatever is buried below, with 6 HP, 1 Armor, 13 STR, 11 DEX, 4 WIL, and shard fists (d8+d8). Only one servant can be raised at a time. If destroyed, you permanently lose 1d4 STR. Recharge: Fill with the blood of a dying warrior.", "items": ["Blood Pail (bulky)"]},
            4: {"description": "A burial wagon (+6 slots, slow) from your last job. It came with a stubborn old donkey (+4 slots, only +2 slots if pulling wagon).", "items": ["Burial Wagon", "Donkey"]},
            5: {"description": "The Detect Magic Spellbook, stolen from an ancient library. Your family worked in service to an obscure underworld deity, but you lost your faith. Though exiled, you continue to serve, even as an apostate. Detect Magic: You can see or hear nearby magical auras. Becomes warm to the touch when magic is used nearby.", "items": ["Detect Magic Spellbook"]},
            6: {"description": "A plague doctor's mask, after its owner succumbed to the disease that wiped out everyone you once knew. They should have kept it on.", "items": ["Plague Doctor's Mask"]}
        },
        "what_tool_was_invaluable_in_your_work": {
            1: {"description": "Manacles: Though old, it's still effective even against the very strong. You don't have the key.", "items": ["Manacles"]},
            2: {"description": "Sponge: Supposedly made from the remains of a rare sea creature. It never seems to dry out.", "items": ["Sponge"]},
            3: {"description": "Pulley: Great for moving gravestones, rocks, or even bodies.", "items": ["Pulley"]},
            4: {"description": "Incense: Perfect for rituals or to keep the flies at bay. Cools the blood.", "items": ["Incense"]},
            5: {"description": "Crowbar: d6 damage. Sometimes you just need to get the damn thing open!", "items": ["Crowbar (d6)"]},
            6: {"description": "Repellent: Powerful stuff. Its faded label makes it unclear what it is actually meant to repel, though. Perhaps everything.", "items": ["Repellent (3 uses)"]}
        }
    },
    5: {
        "name": "Cutpurse",
        "starting_gear": ["Rations (3 uses)", "Dagger (d6)", "Grappling Hook", "Rope (25ft)", "Thieving Tools"],
        "names": ["Fingers", "Shadow", "Silk", "Whisper", "Gutter", "Rat", "Alley", "Tumble", "Nimble", "Gallows"],
        "what_was_your_last_big_job": {
            1: {"description": "A noble's summer home. The place was full of fancy wine (+20gp) but not much else.", "items": ["Fence Cutters", "Fancy Wine (20gp)"]},
            2: {"description": "A bank. (You were caught.) You bear a brand only visible by firelight, and anyone who sees the mark can ask you for a beer.", "items": ["Retractable Wires"]},
            3: {"description": "A guild warehouse.", "items": ["Ladder (bulky, 10ft)", "Blinding Powder (1 use)"]},
            4: {"description": "Moneylender. Someone beat you to the job but left behind a Scroll of Arcane Eye (petty). Arcane Eye: You can see through a magical floating eyeball that flies around at your command.", "items": ["Scroll of Arcane Eye (petty)"]},
            5: {"description": "Constable's quarters. You escaped but left some friends behind. You have a queasy feeling.", "items": ["Strong Silk Rope (30ft)"]},
            6: {"description": "A university. You were seen but not pursued. You still don't know why.", "items": ["Smoke Pellets (3 uses)"]}
        },
        "what_helps_you_steal": {
            1: {"description": "Catring: 2 charges. Climb up walls and fall safely. Recharge: Place the ring on a stray cat's tail.", "items": ["Catring"]},
            2: {"description": "Gildfinger: 1 charge. A finger glove that mimics any mundane key. Recharge: Bundle it with at least 100gp for a night.", "items": ["Gildfinger"]},
            3: {"description": "Glimpse Glass: 3 uses. A monocle that lets you see through walls or other obstructions. It shatters after the last use.", "items": ["Glimpse Glass (3 uses)"]},
            4: {"description": "Sweetwhistle: 1 charge. Listeners hear a soft, familiar voice in the distance that they cannot resist following. Recharge: Lose a dear memory. (Describe it.)", "items": ["Sweetwhistle"]},
            5: {"description": "Vagrant's Veil: 1 charge. Wear it to blend seamlessly into crowds, appearing as a simple pauper. Recharge: Donate the day's winnings to the poor. Petty", "items": ["Vagrant's Veil"]},
            6: {"description": "Reverse Teetotum: 1 use. When spun, time skips backwards 30 seconds. Everyone remembers what happened.", "items": ["Reverse Teetotum (1 use)"]}
        }
    },
    6: {
        "name": "Fieldwarden",
        "starting_gear": ["Rations (3 uses)", "Bow (d6, bulky)", "Sheaf of Arrows (3 uses)", "Hand-axe (d6)", "Spiked Boots"],
        "names": ["Elara", "Briar", "Hawthorn", "Rowan", "Yarrow", "Fen", "Heath", "Dell", "Glen", "Dale"],
        "what_got_the_better_of_you": {
            1: {"description": "A voracious swarm of pests that swallowed crops and animals alike. With nothing to defend, you left. Ingesting the extract lets you sprint with a speed four times your regular rate. Afterward you add two Fatigue.", "items": ["Gale Seed Extract (3 uses)"]},
            2: {"description": "A crop spirit, angered by a poor tithing. The fires consumed nearly everything.", "items": ["Fireseeds (d8, blast, 4 uses)"]},
            3: {"description": "An antlered, toothy demon that nearly ended you. On Critical Damage, its next attack becomes enhanced from contact with blood.", "items": ["Bone Knife (d6)"]},
            4: {"description": "The Withering, a type of stem rot from the Roots.", "items": ["Diseased Crop (6 uses)"]},
            5: {"description": "Wolves, or so you thought. You are now a Werewolf [8 HP, 15 STR, 14 DEX, claws (d6+d6), bite (d8)]. Your WIL remains the same. You can turn at will (once per day) but must make a WIL save to revert. Anyone left alive from your attacks must make a WIL save to avoid infection.", "items": []},
            6: {"description": "Crop thieves. Not all of them survived, but you were outnumbered. Start with +d4 HP.", "items": ["Cusped Falchion (d8)"]}
        },
        "what_tool_saved_your_life": {
            1: {"description": "Bloodvine Whip: d8 damage. On Critical Damage, it drains the target's blood, granting the weapon's next attack the blast quality", "items": ["Bloodvine Whip (d8)"]},
            2: {"description": "Clatter Keeper: A hand-cranked device that emits a loud noise, frightening away most creatures.", "items": ["Clatter Keeper"]},
            3: {"description": "Sun Stick: Provides ample warmth and light for up to one hour. Recharge: Leave in heavy sunlight for a full day.", "items": ["Sun Stick (1 use)"]},
            4: {"description": "Root Tether: When thrown, binds a creature as large as a wolf to the soil for a short time.", "items": ["Root Tether"]},
            5: {"description": "Greenwhistle: A small flute that calms plants, making passage through areas heavy with plant life a bit easier.", "items": ["Greenwhistle"]},
            6: {"description": "Everbloom Band: A circlet adorned with flowers that never wilt. On Critical Damage, the flowers dissolve into dust, but you act as if your save succeeded (STR loss still occurs).", "items": ["Everbloom Band"]}
        }
    },
    7: {
        "name": "Fletchwind",
        "starting_gear": ["Rations (3 uses)", "Shortbow (d6)", "Quiver of Arrows (3 uses)", "Knife (d6)", "Weather Vane"],
        "names": ["Zephyr", "Gale", "Storm", "Breeze", "Tempest", "Squall", "Gust", "Chinook", "Sirocco", "Mistral"],
        "how_did_you_earn_your_bow": {
            1: {"description": "War. If you are first to attack, your bow gains the blast property for the first round.", "items": []},
            2: {"description": "Falconry. You keep a falcon [3 hp, 5 STR, 16 DEX, 4 WIL, claws (d6+d6), bite (d8)]. It only eats live game.", "items": ["Falcon"]},
            3: {"description": "Hunting. When taking the Supply action, your ability to secure Rations increases by one step (e.g. 1d4 becomes 1d6).", "items": []},
            4: {"description": "Tournaments. Attacks with your bow are enhanced if the target is immobile.", "items": []},
            5: {"description": "Training. If you are the first to attack, melee attacks against you are impaired until you take STR damage.", "items": []},
            6: {"description": "Scouting. When taking the Travel action, your presence decreases the chance of getting lost by one step (e.g. 4-in-6 becomes 3-in-6).", "items": []}
        },
        "what_kind_of_wood_is_your_bow_made_from": {
            1: {"description": "Western Yew (d6, bulky). Can be wielded as a blunt weapon (d6). Noisy.", "items": ["Western Yew Bow (d6, bulky)"]},
            2: {"description": "Sessile Oak (d8, bulky). Slams into targets. On Critical Damage something is torn off.", "items": ["Sessile Oak Bow (d8, bulky)"]},
            3: {"description": "Stone Pine (d6, bulky). Produces one use of Sticky Sap per day. The sap is highly explosive.", "items": ["Stone Pine Bow (d6, bulky)"]},
            4: {"description": "White Ash (d6, bulky). Can be used in place of a shield in melee combat (+1 Armor).", "items": ["White Ash Bow (d6, bulky)"]},
            5: {"description": "Striped Bamboo (d6). Collapsible, it only requires one slot (but still requires both hands).", "items": ["Striped Bamboo Bow (d6)"]},
            6: {"description": "Wych Elm (d6, bulky). Protects the bearer from poisons and toxins, so long as they are holding it.", "items": ["Wych Elm Bow (d6, bulky)"]}
        }
    },
    8: {
        "name": "Foundling",
        "starting_gear": ["Rations (3 uses)", "Staff (d6)", "Sling (d6)", "Pouch of Pebbles", "Tattered Blanket"],
        "names": ["Pip", "Cricket", "Scamp", "Urchin", "Gamin", "Waif", "Stray", "Ragamuffin", "Gamin", "Tatterdemalion"],
        "who_took_you_in": {
            1: {"description": "An old hunter. You were both quite happy, until it all ended.", "items": ["Weathered Longbow (d8, bulky)", "Leather Jerkin (1 Armor)"]},
            2: {"description": "A wizened apothecary, who taught you the healing arts but maintained a clinical detachment.", "items": ["Healing Unguent (1 use)"]},
            3: {"description": "A druid, who taught you the language of trees. When it came time to leave, you left a promise that one day you would return.", "items": ["Gnarled Staff (d8)"]},
            4: {"description": "A gruff blacksmith from a sleepy river town. You were always kept at arm's length. Now the forge is cold, and you've moved on.", "items": ["Smith's Apron (petty)", "Oft-mended Chain Mail (2 Armor, bulky)"]},
            5: {"description": "A troupe of traveling entertainers. For a time, they were like family to you. One day you woke up and they were gone with no explanation. You have some burning questions.", "items": ["Storybook", "Dagger (d6)"]},
            6: {"description": "The monks of a secluded forest monastery. When their rules became too strict, you snuck away. Control Plants: Nearby plants and trees obey you and gain the ability to move at a slow pace. Leaves grow along the spine, and it smells faintly of decay.", "items": ["Monk's Habit (warm, petty)", "Spellbook of Control Plants"]}
        },
        "what_keeps_bad_tidings_at_bay": {
            1: {"description": "Pipeweed: Your good luck charm. Conversations tend to flow more easily after a smoke.", "items": ["Pipeweed (6 uses)"]},
            2: {"description": "Stink Jar: Shattering this jar releases an odor so foul all nearby must make a STR save or immediately vomit.", "items": ["Stink Jar (1 use)"]},
            3: {"description": "Ivy Worm: A green worm often mistaken for a weed. Swallowed whole, it absorbs any toxins or rot in the body before exiting through the usual way.", "items": ["Ivy Worm"]},
            4: {"description": "Dream Stone: A smooth blue stone that helps recall dreams more clearly. Overuse can cause dream-addiction.", "items": ["Dream Stone"]},
            5: {"description": "Drowning Rod: A finger-sized wooden stick that doubles in size each time it is fully submerged in water. It does not shrink down again.", "items": ["Drowning Rod"]},
            6: {"description": "Rabbit's Foot: You were wearing it when they found you. They say it is the foot of she who left you and that it protects you from witch magic. Petty.", "items": ["Rabbit's Foot (petty)"]}
        }
    },
    9: {
        "name": "Fungal Forager",
        "starting_gear": ["Rations (3 uses)", "Hand-rake", "Basket", "Spore Mask", "Trowel"],
        "names": ["Mycena", "Amanita", "Morel", "Truffle", "Shiitake", "Chanterelle", "Porcini", "Enoki", "Maitake", "Oyster"],
        "what_strange_fungus_did_you_discover": {
            1: {"description": "Shrieking Trumpet. When exposed to light, it screams so loudly that all nearby attacks (including your own) are impaired.", "items": ["Shrieking Trumpet (2 uses)"]},
            2: {"description": "Torch Fungus. When crushed, it creates a cold blue light for a short while.", "items": ["Torch Fungus (2 uses)"]},
            3: {"description": "Murderous Truffle. Pungent, highly toxic, and very rare (worth 50gp to assassins). Illegal pretty much everywhere.", "items": ["Murderous Truffle (1 use)"]},
            4: {"description": "Hellcap. Exposure to its aroma causes intense nausea and vomiting. Either way, it clears the room.", "items": ["Bottled Hellcap (1 use)"]},
            5: {"description": "Sproutcup. Ingest to shrink down to the size of a mouse. (Your belongings stay the same size.) You return to normal size within the hour, often in fits and starts.", "items": ["Sproutcup (1 use)"]},
            6: {"description": "Rootflower. A white fungus found only on corpses deep underground. Ingest to restore d6 WIL. You will dream of the dead and their stories.", "items": ["Rootflower (1 use)"]}
        },
        "what_keeps_you_sane_even_in_utter_darkness": {
            1: {"description": "Glowsnail: Casts a soft, bioluminescent light. Feeds on one ration every two days.", "items": ["Glowsnail"]},
            2: {"description": "Silk Moth Shawl: A weatherproof blanket, it can also douse a fire without being damaged.", "items": ["Silk Moth Shawl"]},
            3: {"description": "Milkflower: A gentle stimulant. Chewing it makes you immune to panic for the next hour.", "items": ["Milkflower (3 uses)"]},
            4: {"description": "Luxcompass: Hums softly as it moves closer to the Sun. Eventually the noise becomes unbearably loud.", "items": ["Luxcompass"]},
            5: {"description": "Sloth-Tarp: A tough and weatherproof fabric, useful for hanging off trees. When inside, you have +1 Armor.", "items": ["Sloth-Tarp"]},
            6: {"description": "Miner's Grease: Great for dislodging a gem, tool, or limb from a tight crack. Highly explosive.", "items": ["Miner's Grease (3 uses)"]}
        }
    },
    10: {
        "name": "Greenwise",
        "starting_gear": ["Rations (3 uses)", "Mortar & Pestle", "Pouch of Herbs", "Sickle (d6)", "Book of Herbal Remedies"],
        "names": ["Sage", "Rosemary", "Thyme", "Basil", "Parsley", "Lavender", "Mint", "Coriander", "Dill", "Fennel"],
        "how_has_the_wood_failed_you": {
            1: {"description": "An ill-tempered forest spirit cursed you for stealing, marking you as an enemy of their kind. Ingesting the stone cures any poison (1 use, unless retrieved).", "items": ["Bezoar Stone"]},
            2: {"description": "A close friend disappeared into the forest. Now you see their face in any tea you brew.", "items": ["Soporific Concoction (3 uses)"]},
            3: {"description": "You were poisoned, losing your sense of taste and smell. You can now withstand noxious fumes.", "items": ["Antitoxin (2 uses)"]},
            4: {"description": "Your radical experiments turned your skin green, and you now gain nourishment as a plant. You don't need Rations, but a day without sufficient sunlight and water leaves you deprived.", "items": []},
            5: {"description": "Your impressive corpseflower won a local contest then promptly killed a judge. You fled with a warrant for your arrest.", "items": ["Prize Money (100gp)"]},
            6: {"description": "You created a restorative tincture that also causes accidental infertility. Only you know of its unintended side-effects.", "items": ["Healing Potion"]}
        },
        "what_keeps_you_safe_while_in_the_wood": {
            1: {"description": "Amadou: A vermilion fungus that catches fire quite easily.", "items": ["Amadou (3 uses)"]},
            2: {"description": "Delphinium: Breathe water for up to one hour. Can be divided into fractional doses.", "items": ["Delphinium (1 use)"]},
            3: {"description": "Tacky Stalk: A woody reed that hardens into a permanent adhesive when chewed.", "items": ["Tacky Stalk (2 uses)"]},
            4: {"description": "Wisp Lantern: Caged in wrought iron, provides a dim light so long as the wisp is able to feed on nearby pain and fear.", "items": ["Wisp Lantern"]},
            5: {"description": "Seed Bomb: A canvas sack filled with seeds that explode on impact.", "items": ["Seed Bomb (d6, blast, 3 uses)"]},
            6: {"description": "Briarvine: Entangles any creature up to horse size (STR to break free). Reusable.", "items": ["Briarvine"]}
        }
    },
    11: {
        "name": "Half Witch",
        "starting_gear": ["Rations (3 uses)", "Gnarled Staff (d6)", "Pouch of Salt", "Black Cat", "Spellbook (1 spell)"],
        "names": ["Sabrina", "Willow", "Rowan", "Hazel", "Morgana", "Circe", "Hecate", "Medea", "Freyja", "Rhiannon"],
        "what_did_you_bring_back_from_the_unseelie_court": {
            1: {"description": "A Black Rose Fiddle (bulky). Its music causes intense sadness and immobility in nearby mortals. (Others are merely fascinated.) You don't know how to play.", "items": ["Black Rose Fiddle (bulky)"]},
            2: {"description": "Paper legs. You are extremely light, and can fall a few stories without getting hurt. Try to avoid tearing them or getting them wet.", "items": []},
            3: {"description": "A Living Nightmare that dwells within you but manifests whenever you are in danger. It has your same Attributes and HP and attacks with claws (d8+d8). It disappears on Critical Damage (take 1d4 WIL damage), re-appearing again on the next full moon.", "items": []},
            4: {"description": "A Raven Familiar [8 HP, 3 STR, 11 DEX, 13 WIL, beak, (d6)]. It speaks as an intelligent being and is entirely devoted to you.", "items": ["Raven Familiar"]},
            5: {"description": "A Briar Thorn. It can pierce any organic material (quite painfully) but when removed leaves no trace of the intrusion.", "items": ["Briar Thorn"]},
            6: {"description": "A Fae creature's True Name. Use it to summon its owner for an act of great service, but only once. It could also fetch a hefty price, from the right buyer.", "items": ["Fae Creature's True Name"]}
        },
        "what_concoction_do_you_carry_and_what_rare_ingredients_did_you_gather_to_make_it": {
            1: {"description": "Rebirth Ash: Remnants of a bark spirit. Sprinkle to reignite a fire that has died or return to life a creature that has died only moments before.", "items": ["Rebirth Ash (3 uses)"]},
            2: {"description": "Glamour Feather: Plume of a firebird. Can make any creature appear convincingly as someone (or something) else.", "items": ["Glamour Feather (1 use)"]},
            3: {"description": "Hawthorn Seed: An acorn from the other side, gathered on the spring equinox. When planted, it sprouts a luxurious shelter, collapsing at moonrise the next day.", "items": ["Hawthorn Seed (1 use)"]},
            4: {"description": "Stonetree Sap: Sap obtained in exchange for blood. Hardens when rubbed on any surface (+1 Armor).", "items": ["Stonetree Sap (3 uses)"]},
            5: {"description": "Nightdust Powder: Made from the ritual burning of six owls. When tossed in the air, day turns to night for a short while.", "items": ["Nightdust Powder (2 uses)"]},
            6: {"description": "Hex Stone: Gathered from a river that flows from the other side. Removed from its iron tin, it can absorb the effects of an active magical effect. If destroyed, the magic is released.", "items": ["Hex Stone (1 use)"]}
        }
    },
    12: {
        "name": "Hexenbane",
        "starting_gear": ["Rations (3 uses)", "Crossbow (d8, bulky)", "Case of Bolts (3 uses)", "Silver Dagger (d6)", "Holy Symbol"],
        "names": ["Van Helsing", "Geralt", "Solomon", "Constantine", "Blade", "Buffy", "Hellboy", "Ash", "Winchester", "Belmont"],
        "to_which_order_do_you_belong": {
            1: {"description": "Order of the Crossroads. It points to nearby ley lines and other sources of arcane power. If you lose it, the punishment is death.", "items": ["Pocket Leyfinder"]},
            2: {"description": "Order of the Bleeding Star. It shines faintly in darkness and becomes very hot in the presence of witchcraft.", "items": ["Star-Iron Mace (d8)"]},
            3: {"description": "Order of the Glass Sigil. You have contacts in most towns (the more rural, the better) willing to provide aid, food, or even weapons.", "items": ["Short Sword (d8)", "Chainmail (2 Armor, bulky)"]},
            4: {"description": "Order of the Blank Eye. Peer through it to see invisible marks, creatures, and other magical effects. Lose the use of your eye for an hour afterwards (you are deprived).", "items": ["Voidglass Shard"]},
            5: {"description": "Order of Canaas. Once per day, you can change into a wolf. Without the chain, you are unable to shift back.", "items": ["Quicksilver Chain"]},
            6: {"description": "Order of the Silent Veil. Extinguishes any nearby flames once exposed to air.", "items": ["Quell Stone (2 uses)"]}
        },
        "what_was_your_vow": {
            1: {"description": "Honesty. Choose a weapon type (blunt, blade, etc). Attacks against you of this type are impaired. If your vow is broken, you lose d4 WIL.", "items": []},
            2: {"description": "Poverty. You carry the Disassemble Spellbook. Only you can use it. If your vow is broken, it explodes (d12 STR damage). Disassemble: Any of your body parts may be detached and reattached at will, without causing pain or damage. You can still control them. Regenerates any torn or defaced pages.", "items": ["Disassemble Spellbook"]},
            3: {"description": "Selflessness. You are immune to mind-altering magical effects, such as charm, hatred, frenzy, and so on. If you break this vow, you lose d6 WIL.", "items": []},
            4: {"description": "Mercy. Choose a weapon type (blunt, blade, etc). Attacks with this weapon are enhanced. If your vow is broken, you can never use that weapon type again.", "items": []},
            5: {"description": "Charity. Once per day you can shrug off a Fatigue. If your vow is ever broken, you permanently lose one inventory slot.", "items": []},
            6: {"description": "Valor. The first time you inflict Critical Damage, you receive +d4 HP, returning to the previous limit at the end of combat. If your vow is broken, you die.", "items": []}
        }
    },
    13: {
        "name": "Jongleur",
        "starting_gear": ["Rations (3 uses)", "Lute", "Colorful Costume", "Juggling Balls", "Trick Dagger (d4)"],
        "names": ["Jester", "Harlequin", "Troubadour", "Minstrel", "Bard", "Gleeman", "Skald", "Scop", "Filidh", "Ollamh"],
        "what_happened_at_your_final_performance": {
            1: {"description": "Despite your training in the deadly arts, an actor died and you were blamed. You have a false identity.", "items": ["Rapier (d6)"]},
            2: {"description": "The crowd loved your catchy tune about a noble and his romantic failings. The noble in question, not so much. You have a warrant for your arrest. Read Mind: You can hear the surface thoughts of nearby creatures. Long-term possession can cause the reader to mistake the thoughts of others as their own.", "items": ["Read Mind Spellbook"]},
            3: {"description": "Your debut composition reduced the audience to a gibbering mess, murmuring of bright creatures descending from the night sky. Later you noticed that the notes resembled stellar constellations. You have a lot of questions.", "items": ["Book On Astronomy"]},
            4: {"description": "You mocked a forgotten trickster god and were cursed for it. You speak only in perfect rhyme. Ironically, this has only made you more popular among your peers. Without the thesaurus, you are deprived.", "items": ["Thesaurus (20gp)"]},
            5: {"description": "You were scarred in an on-stage accident. The crowd cheered, thinking it was part of the act. You have a memorable scar and a fear of applause.", "items": ["Stage Mail (1 Armor)"]},
            6: {"description": "Your respectable puppeteering skills were matched only by your mimicry. You were so good you were branded a witch (literally) and banished. The skull protects against charms.", "items": ["Uncanny Hand-Puppet", "Rabbit Skull (petty)"]}
        },
        "what_trinket_were_you_unable_to_leave_behind": {
            1: {"description": "False Cuffs: Comfortable, realistic-looking cuffs. Only you know the trick to get out of them.", "items": ["False Cuffs"]},
            2: {"description": "Pocket Theatre: A set of small puppets and a folding stage. Good for quick distractions.", "items": ["Pocket Theatre"]},
            3: {"description": "Ghost Violin: A dark-gray violin that plays a haunting tune, mirrored by an invisible, distant twin.", "items": ["Ghost Violin"]},
            4: {"description": "Tragic Tales: Banned in proper company, this book becomes less bawdy and more harrowing towards the end. Worth 100gp.", "items": ["Tragic Tales"]},
            5: {"description": "Mythos Mask: A plaster mask that allows one to take on a monster's countenance. Once it comes off, add a Fatigue.", "items": ["Mythos Mask"]},
            6: {"description": "Rebreak Glass: A wine flute that can be broken multiple times, reforming after 24 hours. Makes a really loud noise.", "items": ["Rebreak Glass"]}
        }
    },
    14: {
        "name": "Kettlewright",
        "starting_gear": ["Rations (3 uses)", "Hammer (d6)", "Tongs", "Cauldron", "Scrap Metal"],
        "names": ["Tinker", "Smith", "Wright", "Cooper", "Fletcher", "Chandler", "Potter", "Mason", "Weaver", "Fuller"],
        "what_is_your_trade": {
            1: {"description": "You build small contraptions for local guilds (and don't ask too many questions). You have a wanted poster with your face on it. Given time and materials, you can open almost any door or vault.", "items": ["40gp"]},
            2: {"description": "You deal in home goods and tools, hawking your wares to townspeople across the lands. You are fluent in the Traveler's Cant.", "items": ["20gp worth of items from the gear table"]},
            3: {"description": "You were a military smelter, before peace destroyed your livelihood. Given time and adequate materials, you can repair armor.", "items": ["Smelting Hammer (d10, bulky)", "Tin Helm (+1 Armor)"]},
            4: {"description": "You sell rare and quality items to monasteries and nobles alike.", "items": ["Spyglass", "Necklace (petty, 20gp)", "Scroll of Mirrorwalk (petty)"]},
            5: {"description": "You offer protection as a service, quietly watching for threats as money exchanges hands. You start with +d4 HP.", "items": ["Long Sword (d10, bulky)", "Gambeson (+1 Armor)"]},
            6: {"description": "You scavenge raw tin and iron from battlefields, pulling teeth from still-twitching corpses.", "items": ["Donkey", "Crossbow (d8, bulky)", "Saw (d6)"]}
        },
        "what_never_fails_to_get_you_out_of_trouble": {
            1: {"description": "Fire Eggs: Six small pellets made of sea salt, wood, and crockery-dust. They explode at low heat (d8, blast) but the flames dissipate quickly.", "items": ["Fire Eggs (6 uses)"]},
            2: {"description": "Black Tar: Versatile: both sticky and highly flammable.", "items": ["Black Tar (3 uses)"]},
            3: {"description": "Spiked Boots: Cracks heads (d8) as easily as it does ice and muck. Travel is also a bit slower, but easier.", "items": ["Spiked Boots (d8)"]},
            4: {"description": "Tinker's Paste: Seals shut any fist-sized opening.", "items": ["Tinker's Paste (3 uses)"]},
            5: {"description": "Fireworks: A dazzling albeit dangerous display. Enough explosive material to blow off a finger or three.", "items": ["Fireworks (2 uses)"]},
            6: {"description": "Carrion Cat: A clever pet, small enough to hide in your pack (bulky), but strong enough to scare off smaller predators. Requires one Ration a day, and it must be meat.", "items": ["Carrion Cat"]}
        }
    },
    15: {
        "name": "Marchguard",
        "starting_gear": ["Rations (3 uses)", "Spear (d8)", "Shield (+1 Armor)", "Helmet (+1 Armor)", "Horn"],
        "names": ["Warden", "Guardian", "Sentinel", "Protector", "Keeper", "Watchman", "Ranger", "Scout", "Outrider", "Vanguard"],
        "why_did_you_take_the_oath": {
            1: {"description": "Your family has a long tradition of serving, and you were trained from an early age on how to survive in the wild. When taking the Supply action, your yield increases by one step (e.g. 1d4 > 1d6).", "items": []},
            2: {"description": "As a convict, the Oath was simply a means of avoiding punishment.", "items": ["Lockpicks", "Key (petty)"]},
            3: {"description": "Noble-born, you joined to escape family trouble. You stole the tarp before leaving home.", "items": ["Goosefelt Tarp"]},
            4: {"description": "When your family lost everything, you took the Oath to avoid becoming a burden.", "items": ["Rations (3 uses)", "Throwing Knives (d6)"]},
            5: {"description": "Your life was saved by a member of the Marchguard, and you were inspired to join their ranks.", "items": ["Snare Trap", "Sketchbook"]},
            6: {"description": "You were in a dark place and decided that your life needed a little direction. You're still not so sure it was the right choice.", "items": ["Oilskin Coat", "Mapping Paper"]}
        },
        "what_do_you_carry_as_proof_of_your_oath": {
            1: {"description": "Impressive Pin: A metal badge of honor from the Guard. It can open doors but leaves a trail. Petty.", "items": ["Impressive Pin (petty)"]},
            2: {"description": "Oath Compass: Points not towards North, but instead to the nearest member of the Guard. It also lets you know when they're getting close.", "items": ["Oath Compass"]},
            3: {"description": "Pullstones: Two jet-black stones. When separated, the stones will always roll toward one another.", "items": ["Pullstones"]},
            4: {"description": "Fireflask: Highly alcoholic, yet strangely delicious. When thrown, it creates a wall of flames 10ft high that burns out after a few minutes.", "items": ["Fireflask (1 use)"]},
            5: {"description": "Pain Band: Touch an injured creature to transfer their wounds to you. (Exchange their lost STR with your own.) Recharge: Wear the ring while in perfect health. You will lose 1 STR, permanently. Petty.", "items": ["Pain Band (petty)"]},
            6: {"description": "Poacher's Woe: Strongly-scented arrows. The scent is powerful enough to track with ease.", "items": ["Poacher's Woe Arrows (3 uses)"]}
        }
    },
    16: {
        "name": "Mountebank",
        "starting_gear": ["Rations (3 uses)", "Loaded Dice", "Card Deck", "Bottle of Fake Tonic", "Dagger (d6)"],
        "names": ["Charlatan", "Quack", "Swindler", "Huckster", "Trickster", "Imposter", "Rogue", "Scoundrel", "Knave", "Rascal"],
        "how_was_your_fraud_exposed": {
            1: {"description": "Your 'patients' kept reporting miraculous recoveries, despite your lack of training. You have a knack for healing.", "items": ["Bandages (3 uses)"]},
            2: {"description": "After seducing a wealthy patron, their family hired a criminal gang to retrieve you. You got away and need to lay low. Apply to appear irresistibly beautiful for the next 12 hours.", "items": ["Beauty Cream (2 uses)"]},
            3: {"description": "You were a peddler of fake prophesies, but when one turned out to be true, it drew unwanted attention. Roll on the Omens table, but keep the result to yourself.", "items": ["Concealable Knife (d6, petty)"]},
            4: {"description": "Your latest stunt destroyed a priceless artifact and injured a dozen bystanders.", "items": ["Captain's Uniform (petty)", "Ceremonial Sword (harmless, 60gp)", "Bouquet of Flowers"]},
            5: {"description": "You were cursed by a hedgewitch for fooling some innocent village folk. Magic acts unpredictably in your hands (WIL save to avoid disaster). If you are the target of magic, the same applies to its wielder.", "items": []},
            6: {"description": "Your 'seances' with the dead were in actuality a ruse involving a cleverly hidden spellbook of Auditory Illusion. Inevitably, a patron discovered your secret. Auditory Illusion: You create illusory sounds that seem to come from a direction of your choice.Long-term possession can cause the reader to mistake the thoughts of others as their own.", "items": ["Spellbook of Auditory Illusion", "Bundle of Scarves"]}
        },
        "what_keepsake_could_always_identify_you": {
            1: {"description": "Royal Crest: Born into royalty, you chose a different life. The crest grants you access but also alerts your family of your whereabouts. Petty.", "items": ["Royal Crest (petty)"]},
            2: {"description": "Miracle Oil: A smelly, slippery concoction.", "items": ["Miracle Oil (2 uses)"]},
            3: {"description": "Surgeon's Soap: A lye and ash block that makes skin temporarily transparent, revealing the anatomy within.", "items": ["Surgeon's Soap (4 uses)"]},
            4: {"description": "Goat Powder: Derived from the placenta of a baby goat. Temporarily cures any affliction, but symptoms return within hours.", "items": ["Goat Powder"]},
            5: {"description": "Cursed Sapphire: Worth 200gp, it noticeably returns to your pocket shortly after you spend it. You can't seem to get rid of it.", "items": ["Cursed Sapphire (200gp)"]},
            6: {"description": "Alchemical Tattoo: A dog, cat, or bird that can leave your body on demand. It follows your commands to the best of its abilities and can pass its injuries (as STR loss) back onto you. Petty.", "items": ["Alchemical Tattoo (petty)"]}
        }
    },
    17: {
        "name": "Outrider",
        "starting_gear": ["Rations (3 uses)", "Horse", "Saddlebags", "Long Sword (d10, bulky)", "Bedroll"],
        "names": ["Rider", "Scout", "Ranger", "Tracker", "Guide", "Pathfinder", "Explorer", "Pioneer", "Voyager", "Wanderer"],
        "what_personal_code_or_principle_do_you_uphold": {
            1: {"description": "No innocent blood: No bystander will come to harm on your watch. While holding this shield, you cannot be moved so long as both feet are planted on firm ground.", "items": ["Steadymade Buckler (+1 Armor)"]},
            2: {"description": "Revere the tools of death: Weapons are to be respected and maintained. Following a half-hour ritual sharpening, attacks with the weapon are enhanced until STR damage is dealt.", "items": ["Wyrmbone Whetstone"]},
            3: {"description": "To the death, always: You never back down from a fight, no matter the odds. Its scream frightens away all who hear it (save WIL or flee). Recharge: Capture the final breath of a dying warrior.", "items": ["Death-Whistle (1 charge)"]},
            4: {"description": "Revere the dead: Death is a journey we all take, and it deserves respect. You always place two gold pieces on the eyelids of a slain foe. Somehow, you always find the coin.", "items": ["30gp"]},
            5: {"description": "Loyalty to the work: Your word is your bond. Once you've accepted a job, you see it through to the end. Once a vow is marked onto its face, the stick hardens (d8) until it is complete. The stick will snap in half if the vow is ever broken.", "items": ["Tally Stick"]},
            6: {"description": "Always pay your debts: You always repay what you owe, whether in coin or in kind. You expect nothing less from all others. You also roll a second time on the Bonds table.", "items": ["Blacked-Out Ledger"]}
        },
        "what_breed_is_your_horse": {
            1: {"description": "Heavy Destrier: A beast built for war, an imposing creature. 8 HP, 1 Armor, hooves (d10+d10), +2 slots.", "items": ["Heavy Destrier"]},
            2: {"description": "Blacklegged Dandy: Hardy and adaptable. Tough or Perilous terrain are one step easier. 6 HP. +4 slots.", "items": ["Blacklegged Dandy"]},
            3: {"description": "Rivertooth: Impressively strong, capable of carrying heavy loads. 4 HP. +6 slots (only +2 slots if carrying two people).", "items": ["Rivertooth"]},
            4: {"description": "Piebald Cob: Intelligent, it can understand simple commands and even has an instinct for danger. 6 HP. +4 slots.", "items": ["Piebald Cob"]},
            5: {"description": "Linden White: Highly trained and agile, it can perform intricate maneuvers in a time of need (no DEX save to flee). 4 HP. +3 slots.", "items": ["Linden White"]},
            6: {"description": "Stray Fogger: Wild but very fast (even in Tough terrain). Rides light. 4 HP. +2 slots.", "items": ["Stray Fogger"]}
        }
    },
    18: {
        "name": "Prowler",
        "starting_gear": ["Rations (3 uses)", "Garrote", "Blowgun & Darts", "Vial of Poison", "Black Clothes"],
        "names": ["Shadow", "Stalker", "Lurker", "Ghost", "Wraith", "Specter", "Phantom", "Shade", "Nightshade", "Umbra"],
        "what_did_you_last_hunt": {
            1: {"description": "A mock firefly, baiting water carriers with its glowing lure. You have an alchemical limb (d8, petty when worn) to replace the one it tore off. The limb is immune to heat and poison. Needs to be oiled daily.", "items": ["Alchemical Limb (d8, petty)", "Oil Can (6 uses)"]},
            2: {"description": "An ice nettle, trapping and draining sheep. You lost your commission when the fungus you introduced killed half the flock. It freezes any body of water, no matter the size. Don't eat it.", "items": ["Rime Seed (1 use)"]},
            3: {"description": "A silver marsh crawler that killed someone close to you. You now carry its tooth on a chain around your neck as a warning to others of its kind. The tooth hums softly when something is stalking you.", "items": ["Crawler Tooth Necklace (petty)"]},
            4: {"description": "A malicious forest spirit that poisoned a homestead. You saved a Heartseed from the roots of a dying tree. (Plant it to create a new forest.)", "items": ["Heartseed", "Iron Bracers (+1 Armor, bulky)"]},
            5: {"description": "A hollow wolf that had been frightening travelers. You took pity on the half-starved creature and nursed it back to health. Now it is loyal to you unto death. It is also a great tunneler. 5 HP, 11 STR, 13 DEX, 8 WIL, teeth (d6).", "items": ["Hollow Wolf"]},
            6: {"description": "An azure warbler. The gametes attract a sizeable profit, if properly extracted. You succeeded but left its nest to the wolves. You have a pang of regret.", "items": ["Paring Knife (d6)", "20gp"]}
        },
        "what_tool_is_always_in_your_pack": {
            1: {"description": "Fermented Spirits: Keeps you warm at the best of times and as an explosive at the worst.", "items": ["Fermented Spirits (3 uses)"]},
            2: {"description": "Trail Shaker: A noisy instrument that reveals nearby trails, even when deeply hidden.", "items": ["Trail Shaker"]},
            3: {"description": "Drowse Balm: A wax bar. If boiled in water, the steam acts as a soporific agent.", "items": ["Drowse Balm"]},
            4: {"description": "Spike and Cord: For traversing difficult terrain or for creating makeshift traps and structures.", "items": ["Spike and Cord"]},
            5: {"description": "Iron Rattle: A noisemaker for distracting or scaring your quarry. Sounds convincingly like a snake.", "items": ["Iron Rattle"]},
            6: {"description": "Hardening Glue: Makes any flat material (cloth, leather, sand) as hard as stone. Expensive (20gp a bottle).", "items": ["Hardening Glue (3 uses)"]}
        }
    },
    19: {
        "name": "Rill Runner",
        "starting_gear": ["Rations (3 uses)", "Pole (10ft)", "Waterproof Sack", "Fishing Net", "Gaff Hook (d6)"],
        "names": ["River", "Brook", "Creek", "Stream", "Beck", "Burn", "Gill", "Rivulet", "Runnel", "Sike"],
        "what_songs_are_you_best_known_for": {
            1: {"description": "The Tinker's Two-Step. A humorous fairy tale about a gift-giving traveler. Anyone in earshot must pass a WIL save to perform an act of violence.", "items": ["Reed Whistle"]},
            2: {"description": "The Sylph and Her Lover. A bawdy tale of lost love. Creates a strong breeze. Recharge: Tie it to a mast during a storm.", "items": ["Breeze Knot (3 charges)"]},
            3: {"description": "Harper's Devotion. A sad, short tale about a musician that falls in love with a star. Reveals the constellations above, no matter the weather.", "items": ["Celestial Lute"]},
            4: {"description": "The Reed Fisher. A celebrated song about a massive carp that always seems to get away. Each dip into the river guarantees a catch, though it might not be pleasant.", "items": ["River Twine (5 uses)"]},
            5: {"description": "Song of the Silver Stream. A wordless lullaby that mimics flowing water.", "items": ["Stone Flute"]},
            6: {"description": "The Thrush and the Meadow. A moody tale told in alternating chorus. A map drawn with this quill reveals the most expedient course between any two points.", "items": ["Feather Quill (1 use, petty)"]}
        },
        "what_pays_your_way_across_the_land": {
            1: {"description": "Performance: Performing at taverns always yields both room and board. Sometimes you even get tips!", "items": ["10gp"]},
            2: {"description": "Bodyguard: You are a protector for those afraid to travel alone.", "items": ["Rapier (d8)"]},
            3: {"description": "Wares: You buy low and sell high, always making just enough to get by.", "items": ["Item worth 20gp or less"]},
            4: {"description": "Transport: You deliver 'delicate' packages throughout the lands. You have at least one contact in any major town.", "items": []},
            5: {"description": "Sailor's Friend: Over troubled waters and dangerous winds, you always make sure a ship reaches its destination. For you, passage is always free.", "items": []},
            6: {"description": "Guide: You shepherd caravans and travelers across water-soaked lands.", "items": ["Map (petty)"]}
        }
    },
    20: {
        "name": "Scrivener",
        "starting_gear": ["Rations (3 uses)", "Ink & Quill", "Parchment (3 uses)", "Sealing Wax", "Letter Opener (d4)"],
        "names": ["Scribe", "Clerk", "Amanuensis", "Notary", "Copyist", "Librarian", "Archivist", "Chronicler", "Historiographer", "Calligrapher"],
        "what_work_did_you_keep_for_yourself": {
            1: {"description": "The Wild Tongue. A bundle of leather-bound scrolls. A seminal work, cataloging the hidden languages of beasts and how to understand them.", "items": ["The Wild Tongue"]},
            2: {"description": "The Silent Symphony. Bound in fluorescent wrap. Very rare, it chronicles the subtle signs used by those employing invisibility magic.", "items": ["The Silent Symphony"]},
            3: {"description": "A Treatise on the Abyss. A nondescript black book. An in-depth, largely theoretical text describing the Roots, as well as information about the location of a nearby Gate.", "items": ["A Treatise on the Abyss"]},
            4: {"description": "The Star Waltz. A comet-shaped clasp bound in a fine leather cover. Detailed astronomical charts, celestial movements, and stellar festivals. Highly valued (100gp) for its usefulness to travelers.", "items": ["The Star Waltz"]},
            5: {"description": "The Cathedral and the Canopy. Large-leaf binding over vellum. Nominally a children's storybook, the margins detail information about traveling, eating, and sleeping in the cloud forests.", "items": ["The Cathedral and the Canopy"]},
            6: {"description": "Garden of Glass. Bound in the cover of another book. A heretical work, it describes the materials, procedures, and optimal locations required to open a Gate.", "items": ["Garden of Glass"]}
        },
        "how_do_you_transcribe_sensitive_information": {
            1: {"description": "Fib Ink: Glows when used to write true statements but fades if used to write false ones.", "items": ["Fib Ink"]},
            2: {"description": "Cipher Stone: A pair of sharp black stones. Each one decrypts any message written by the other.", "items": ["Cipher Stone"]},
            3: {"description": "Everquill: A quill that writes on any surface. You still need ink. Petty.", "items": ["Everquill (petty)"]},
            4: {"description": "Whisper Vial: Whisper a message into the vial, and it will play it back to whoever opens it next.", "items": ["Whisper Vial"]},
            5: {"description": "Sanguine Lens: Extracts blood from a target without their knowledge. A stolen drop placed on the eye reveals memories from the past day.", "items": ["Sanguine Lens"]},
            6: {"description": "Echo Leaf: A blank parchment. Whomever unfurls it sees their actions of the day slowly revealed in a tight scrawl. Petty.", "items": ["Echo Leaf (petty)"]}
        }
    },
}


# --- Oracle Roller Class ---


class OracleRoller:
    """A class to handle rolling on various oracle tables."""

    def _d20(self) -> int:
        return random.randint(1, 20)

    def _d6(self) -> int:
        return random.randint(1, 6)

    def roll_on_table(self, table: Dict[int, Any]) -> Any:
        """
        Rolls a d20 and returns the corresponding result from the given table.

        Args:
            table: The oracle table to roll on.

        Returns:
            The result from the table.
        """
        roll = self._d20()
        return table.get(roll)

    def roll_wilderness_event(self) -> str:
        """Rolls for a random wilderness event."""
        # This is a placeholder for a more complex wilderness event table.
        # For now, we'll just use a simple list of events.
        events = [
            "You find a hidden stash of supplies.",
            "A group of travelers passes by.",
            "The weather takes a sudden turn for the worse.",
            "You discover the tracks of a large, unknown creature.",
            "A strange, magical phenomenon occurs.",
            "You encounter a friendly animal.",
        ]
        return random.choice(events)
