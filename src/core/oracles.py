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
            1: "There was an explosion, and you lost your sense of smell. Well, almost: you can sniff out gold as a pig does truffles. Take a Tin of Snuff (6 uses) to dampen the impact. Use it every day or become deprived.",
            2: "You dematerialized a beloved pet. Now it follows you around, invisible but always present. Although it cannot interact with the physical realm, you are able to share its sense. (Add a Fatigue each time.) It follows basic commands.",
            3: "You were exposed to a long-acting truth serum whose effects have yet to wear off. The disorder has its advantages: you cannot repeat lies you've heard, either.",
            4: "You were adept at creating fake gold, which is almost as good. Eventually, your ruse was discovered, and you had to make a hasty retreat. Take a heavy Metal Ingot and Gold Powder (3 uses).",
            5: "Your alchemical recipe worked, but a rival stole the blueprint before your claims could be proven. Take a prototype Blunderbuss (d12, blast, bulky) that takes one round to reload, and a taste for revenge.",
            6: "Ridiculed for discovering how to turn gold into lead, you were a laughing stock. Take a bottle of Universal Solvent (2 uses) that dissolves anything it touches into its constituent parts.",
        },
        "what_alchemical_marvel_is_the_product_of_your_latest_ingenuity": {
            1: "Pyrophoric Gel: A sticky green fluid that catches fire when exposed to air, then burns for 8 hours. Cannot be extinguished (1 use).",
            2: "Blast Sphere: A head-sized iron ball filled with explosive powder that explodes on impact (d12, blast, bulky, 1 use).",
            3: "Aqua Vita: Purifies any liquid, converting it to pure water. Drinking it cures 1d6 STR (1 use).",
            4: "Mimic Stone: Records a short phrase that can later be played back.",
            5: "Spark Dust: Ignites easily and quickly. Useful for starting a fire or as an incendiary device (3 uses).",
            6: "Homunculus: A miniature clay replica of yourself that follows your every command. It hates being enthralled to you and complains bitterly whenever possible. Any damage done to the homunculus is also done to you. 3 HP, 4 STR, 13 DEX, 5 WIL",
        },
    },
    2: {
        "name": "Barber-Surgeon",
        "starting_gear": ["Rations (3 uses)", "Saw (d6)", "Scissors (d6)", "Needle & Thread", "Twisted Pole"],
        "names": ["Cullen", "Galen", "Suspectra", "Celsus", "Paracelsus", "Avicenna", "Rashid", "Zosimos", "Folke", "Hippocrates"],
    },
    3: {
        "name": "Beast Handler",
        "starting_gear": ["Rations (3 uses)", "Thick Gloves", "Whistle (petty)", "Net", "Muzzle"],
        "names": ["Ursula", "Grizzly", "Marl", "Lynx", "Corbin", "Drake", "Finch", "Hawk", "Newt", "Sorrel"],
    },
    4: {
        "name": "Bonekeeper",
        "starting_gear": ["Rations (3 uses)", "Shovel", "Crowbar", "Sack", "Trowel"],
        "names": ["Agnes", "Marrow", "Scapula", "Spine", "Femur", "Tibia", "Patella", "Clavicle", "Cranium", "Carcass"],
    },
    5: {
        "name": "Cutpurse",
        "starting_gear": ["Rations (3 uses)", "Dagger (d6)", "Grappling Hook", "Rope (25ft)", "Thieving Tools"],
        "names": ["Fingers", "Shadow", "Silk", "Whisper", "Gutter", "Rat", "Alley", "Tumble", "Nimble", "Gallows"],
    },
    6: {
        "name": "Fieldwarden",
        "starting_gear": ["Rations (3 uses)", "Bow (d6, bulky)", "Sheaf of Arrows (3 uses)", "Hand-axe (d6)", "Spiked Boots"],
        "names": ["Elara", "Briar", "Hawthorn", "Rowan", "Yarrow", "Fen", "Heath", "Dell", "Glen", "Dale"],
    },
    7: {
        "name": "Fletchwind",
        "starting_gear": ["Rations (3 uses)", "Shortbow (d6)", "Quiver of Arrows (3 uses)", "Knife (d6)", "Weather Vane"],
        "names": ["Zephyr", "Gale", "Storm", "Breeze", "Tempest", "Squall", "Gust", "Chinook", "Sirocco", "Mistral"],
    },
    8: {
        "name": "Foundling",
        "starting_gear": ["Rations (3 uses)", "Staff (d6)", "Sling (d6)", "Pouch of Pebbles", "Tattered Blanket"],
        "names": ["Pip", "Cricket", "Scamp", "Urchin", "Gamin", "Waif", "Stray", "Ragamuffin", "Gamin", "Tatterdemalion"],
    },
    9: {
        "name": "Fungal Forager",
        "starting_gear": ["Rations (3 uses)", "Hand-rake", "Basket", "Spore Mask", "Trowel"],
        "names": ["Mycena", "Amanita", "Morel", "Truffle", "Shiitake", "Chanterelle", "Porcini", "Enoki", "Maitake", "Oyster"],
    },
    10: {
        "name": "Greenwise",
        "starting_gear": ["Rations (3 uses)", "Mortar & Pestle", "Pouch of Herbs", "Sickle (d6)", "Book of Herbal Remedies"],
        "names": ["Sage", "Rosemary", "Thyme", "Basil", "Parsley", "Lavender", "Mint", "Coriander", "Dill", "Fennel"],
    },
    11: {
        "name": "Half Witch",
        "starting_gear": ["Rations (3 uses)", "Gnarled Staff (d6)", "Pouch of Salt", "Black Cat", "Spellbook (1 spell)"],
        "names": ["Sabrina", "Willow", "Rowan", "Hazel", "Morgana", "Circe", "Hecate", "Medea", "Freyja", "Rhiannon"],
    },
    12: {
        "name": "Hexenbane",
        "starting_gear": ["Rations (3 uses)", "Crossbow (d8, bulky)", "Case of Bolts (3 uses)", "Silver Dagger (d6)", "Holy Symbol"],
        "names": ["Van Helsing", "Geralt", "Solomon", "Constantine", "Blade", "Buffy", "Hellboy", "Ash", "Winchester", "Belmont"],
    },
    13: {
        "name": "Jongleur",
        "starting_gear": ["Rations (3 uses)", "Lute", "Colorful Costume", "Juggling Balls", "Trick Dagger (d4)"],
        "names": ["Jester", "Harlequin", "Troubadour", "Minstrel", "Bard", "Gleeman", "Skald", "Scop", "Filidh", "Ollamh"],
    },
    14: {
        "name": "Kettlewright",
        "starting_gear": ["Rations (3 uses)", "Hammer (d6)", "Tongs", "Cauldron", "Scrap Metal"],
        "names": ["Tinker", "Smith", "Wright", "Cooper", "Fletcher", "Chandler", "Potter", "Mason", "Weaver", "Fuller"],
    },
    15: {
        "name": "Marchguard",
        "starting_gear": ["Rations (3 uses)", "Spear (d8)", "Shield (+1 Armor)", "Helmet (+1 Armor)", "Horn"],
        "names": ["Warden", "Guardian", "Sentinel", "Protector", "Keeper", "Watchman", "Ranger", "Scout", "Outrider", "Vanguard"],
    },
    16: {
        "name": "Mountebank",
        "starting_gear": ["Rations (3 uses)", "Loaded Dice", "Card Deck", "Bottle of Fake Tonic", "Dagger (d6)"],
        "names": ["Charlatan", "Quack", "Swindler", "Huckster", "Trickster", "Imposter", "Rogue", "Scoundrel", "Knave", "Rascal"],
    },
    17: {
        "name": "Outrider",
        "starting_gear": ["Rations (3 uses)", "Horse", "Saddlebags", "Long Sword (d10, bulky)", "Bedroll"],
        "names": ["Rider", "Scout", "Ranger", "Tracker", "Guide", "Pathfinder", "Explorer", "Pioneer", "Voyager", "Wanderer"],
    },
    18: {
        "name": "Prowler",
        "starting_gear": ["Rations (3 uses)", "Garrote", "Blowgun & Darts", "Vial of Poison", "Black Clothes"],
        "names": ["Shadow", "Stalker", "Lurker", "Ghost", "Wraith", "Specter", "Phantom", "Shade", "Nightshade", "Umbra"],
    },
    19: {
        "name": "Rill Runner",
        "starting_gear": ["Rations (3 uses)", "Pole (10ft)", "Waterproof Sack", "Fishing Net", "Gaff Hook (d6)"],
        "names": ["River", "Brook", "Creek", "Stream", "Beck", "Burn", "Gill", "Rivulet", "Runnel", "Sike"],
    },
    20: {
        "name": "Scrivener",
        "starting_gear": ["Rations (3 uses)", "Ink & Quill", "Parchment (3 uses)", "Sealing Wax", "Letter Opener (d4)"],
        "names": ["Scribe", "Clerk", "Amanuensis", "Notary", "Copyist", "Librarian", "Archivist", "Chronicler", "Historiographer", "Calligrapher"],
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
