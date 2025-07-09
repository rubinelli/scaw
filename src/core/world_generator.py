
import random
from sqlalchemy.orm import Session
from database.models import WorldState, MapPoint, Path

# Data from Warden's Guide
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
FACTION_ADVANTAGES = {
    1: (1, "Alliances"),
    2: (1, "Anonymity"),
    3: (1, "Apparatus"),
    4: (1, "Beliefs"),
    5: (1, "Charisma"),
    6: (1, "Conviction"),
    7: (1, "Fealty"),
    8: (2, "Force"),
    9: (2, "Information"),
    10: (2, "Lineage"),
    11: (2, "Magic"),
    12: (2, "Members"),
    13: (3, "Popularity"),
    14: (3, "Position"),
    15: (3, "Renown"),
    16: (3, "Resources"),
    17: (3, "Ruthlessness"),
    18: (4, "Specialization"),
    19: (4, "Subterfuge"),
    20: (4, "Wealth"),
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
    9: ("Establish a New Order", "An internal schism threatens to tear the faction apart."),
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
TERRAIN_DIE_DROP = {1: "Easy", 2: "Easy", 3: "Easy", 4: "Tough", 5: "Tough", 6: "Perilous"}
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
POI_DIE_DROP = {1: "Waypoint or Settlement", 2: "Curiosity", 3: "Curiosity", 4: "Lair", 5: "Dungeon", 6: "Dungeon"}
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

class WorldGenerator:
    """Procedurally generates a new world state based on Cairn rules."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def generate_new_world(self):
        """Main method to orchestrate the world generation process."""
        self._generate_region_theme()
        self._generate_factions()
        self._generate_topography_and_pois()
        self._generate_paths()

    def _d20(self):
        return random.randint(1, 20)

    def _d6(self):
        return random.randint(1, 6)

    def _generate_region_theme(self):
        culture = CULTURE.get(self._d20(), ("Artistic", "Control"))
        resources = RESOURCES.get(self._d20(), ("Herbs", "Medicine"))
        theme = {"culture": f"{culture[0]} ({culture[1]})", "resources": f"{resources[0]} (Scarce: {resources[1]})"}
        self.db.add(WorldState(key="region_theme", value=theme))
        self.db.commit()

    def _generate_factions(self):
        num_factions = random.randint(1, 3)
        factions = []
        for _ in range(num_factions):
            faction_type = FACTION_TYPES.get(self._d20(), ("Criminals", "Blacksmith"))
            trait1, trait2 = FACTION_TRAITS.get(self._d20(), ("Dogmatic", "Craven"))
            agenda, obstacle = FACTION_AGENDAS.get(self._d20(), ("Protect a Secret", "Hindered by cultural taboos"))
            factions.append({
                "name": f"The {trait1} {faction_type[0]}",
                "type": f"{faction_type[0]} ({faction_type[1]})",
                "traits": f"{trait1}, {trait2}",
                "agenda": f"{agenda} (Obstacle: {obstacle})"
            })
        self.db.add(WorldState(key="factions", value=factions))
        self.db.commit()

    def _generate_topography_and_pois(self):
        # Simplified die drop for topography and POIs
        num_pois = random.randint(3, 8)
        pois = []
        for i in range(num_pois):
            poi_type_roll = self._d6()
            poi_type = POI_DIE_DROP.get(poi_type_roll, "Curiosity")
            
            if "Settlement" in poi_type:
                poi_details = SETTLEMENTS.get(self._d20(), ("Hamlet", "High Population Density"))
            elif "Curiosity" in poi_type:
                poi_details = CURIOSITIES.get(self._d20(), ("Broken Tower", "Ancient Trash Heap"))
            elif "Lair" in poi_type:
                poi_details = LAIRS.get(self._d20(), ("Collapsed Mine", "Baited Entrance"))
            else: # Dungeon or Waypoint
                poi_details = DUNGEONS.get(self._d20(), ("Cave", "Buried"))

            poi_name = f"{poi_details[0]} of the {EASY_TERRAIN.get(self._d20(), ("Valleys", "Titanic Gate"))[1]}"
            new_poi = MapPoint(
                name=poi_name,
                type=poi_type,
                description=f"{poi_details[0]} - {poi_details[1]}",
                status="hidden",
                position_x=random.randint(50, 750),
                position_y=random.randint(50, 450)
            )
            pois.append(new_poi)
        
        # Set starting POI
        start_poi = random.choice(pois)
        start_poi.status = "explored"
        self.db.add_all(pois)
        self.db.commit()

    def _generate_paths(self):
        pois = self.db.query(MapPoint).all()
        if len(pois) < 2:
            return

        for i in range(len(pois)):
            # Create 1-2 paths from each POI to others
            for _ in range(random.randint(1, 2)):
                start_poi = pois[i]
                end_poi = random.choice(pois)
                if start_poi.id == end_poi.id:
                    continue

                # Avoid duplicate paths
                existing_path = self.db.query(Path).filter(
                    ((Path.start_point_id == start_poi.id) & (Path.end_point_id == end_poi.id)) |
                    ((Path.start_point_id == end_poi.id) & (Path.end_point_id == start_poi.id))
                ).first()
                if existing_path:
                    continue

                feature, condition = PATH_FEATURES.get(self._d20(), ("Twisted", "Thick Evening Mist"))
                new_path = Path(
                    start_point_id=start_poi.id,
                    end_point_id=end_poi.id,
                    status="hidden",
                    watches=random.randint(1, 3),
                    feature=f"{feature} ({condition})"
                )
                self.db.add(new_path)
        self.db.commit()
