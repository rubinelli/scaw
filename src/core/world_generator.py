import random
import json
from sqlalchemy.orm import Session
from database.models import (
    WorldState,
    MapPoint,
    Path,
    Location,
    LocationConnection,
    GameEntity,
    Item,
)
from .oracles import (
    CULTURE,
    RESOURCES,
    FACTION_TYPES,
    FACTION_TRAITS,
    FACTION_AGENDAS,
    POI_DIE_DROP,
    SETTLEMENTS,
    CURIOSITIES,
    LAIRS,
    DUNGEONS,
    EASY_TERRAIN,
    PATH_FEATURES,
)
from core.llm_service import LLMService


class WorldGenerator:
    """Procedurally generates a new world state based on Cairn rules."""

    def __init__(self, db_session: Session, llm_service: LLMService):
        self.db = db_session
        self.llm_service = llm_service

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
        theme = {
            "culture": f"{culture[0]} ({culture[1]})",
            "resources": f"{resources[0]} (Scarce: {resources[1]})",
        }
        self.db.add(WorldState(key="region_theme", value=theme))
        self.db.commit()

    def _generate_factions(self):
        num_factions = random.randint(1, 3)
        factions = []
        for _ in range(num_factions):
            faction_type = FACTION_TYPES.get(self._d20(), ("Criminals", "Blacksmith"))
            trait1, trait2 = FACTION_TRAITS.get(self._d20(), ("Dogmatic", "Craven"))
            agenda, obstacle = FACTION_AGENDAS.get(
                self._d20(), ("Protect a Secret", "Hindered by cultural taboos")
            )
            factions.append(
                {
                    "name": f"The {trait1} {faction_type[0]}",
                    "type": f"{faction_type[0]} ({faction_type[1]})",
                    "traits": f"{trait1}, {trait2}",
                    "agenda": f"{agenda} (Obstacle: {obstacle})",
                }
            )
        self.db.add(WorldState(key="factions", value=factions))
        self.db.commit()

    def _enrich_map_point_with_llm(self, map_point: MapPoint):
        """Uses the LLM to generate a rich description and interconnected locations for a MapPoint."""
        prompt = f"""
        You are a creative, dark fantasy Game Master generating a new area for a solo RPG based on the game Cairn.
        The player is exploring a newly discovered point of interest.

        **Point of Interest Type:** {map_point.type}
        **Initial Name:** {map_point.name}
        **Initial Description:** {map_point.description}

        Your task is to expand this basic concept into a rich, explorable area.
        Generate a JSON object with the following structure:
        1.  `summary`: A 2-3 sentence, evocative summary of the entire area. This will be shown to the player on the world map.
        2.  `locations`: A list of 2 to 4 distinct, interconnected locations within this area. For each location, provide:
            *   `name`: A short, evocative name (e.g., "The Sunken Chapel", "Goblin Guard Post").
            *   `description`: A 2-4 sentence description of the location, focusing on sights, sounds, and smells.
            *   `contents`: A list of suggested creatures or items found here. Be specific (e.g., ["A rusty sword", "A hungry goblin with 3 HP"]). Keep it simple.
        3.  `connections`: A dictionary describing how the locations are connected. The key is a location name, and the value is a list of other location names it connects to. Ensure all locations are reachable. The first location in the `locations` list will be the entry point.

        **Example JSON Output:**
        {{
            "summary": "A crumbling watchtower stands precariously on the edge of a cliff, battered by salty winds. It has been long abandoned by its original builders, but is now home to something new.",
            "locations": [
                {{
                    "name": "Base of the Tower",
                    "description": "The tower's base is choked with weeds and rubble. The main door is made of splintered, salt-bleached wood, hanging loosely on a single hinge. A faint, unpleasant smell wafts from within.",
                    "contents": ["A discarded, empty waterskin", "A set of old, humanoid footprints in the mud"]
                }},
                {{
                    "name": "Guard Room",
                    "description": "Just inside the door, this small, circular room is filled with debris. A rickety wooden table and a broken chair are the only furnishings. A crude ladder ascends to the next level.",
                    "contents": ["A goblin guard (HP: 4, Spear)", "A half-eaten, questionable-looking piece of meat"]
                }},
                {{
                    "name": "Rookery",
                    "description": "The top level is open to the sky, with crumbling crenellations offering a stunning, windswept view of the sea. Nests made of driftwood and bone are crammed into every corner.",
                    "contents": ["3 Blood-Feather Gulls (HP: 2 each, Sharp Beaks)", "A tarnished silver locket"]
                }}
            ],
            "connections": {{
                "Base of the Tower": ["Guard Room"],
                "Guard Room": ["Base of the Tower", "Rookery"],
                "Rookery": ["Guard Room"]
            }}
        }}

        Now, generate the JSON for the provided Point of Interest.
        """
        llm_response_str = self.llm_service.generate_response(prompt)

        try:
            # The response might be wrapped in markdown, so we need to extract the JSON
            json_str = llm_response_str.strip().replace("```json", "").replace("```", "").strip()
            enriched_data = json.loads(json_str)

            map_point.summary = enriched_data.get("summary")

            # Create locations
            created_locations = {}
            for i, loc_data in enumerate(enriched_data.get("locations", [])):
                new_loc = Location(
                    name=loc_data.get("name"),
                    description=loc_data.get("description"),
                    map_point=map_point,
                    is_entry_point=(i == 0),  # First location is the entry point
                )
                self.db.add(new_loc)
                self.db.flush()  # Flush to get the ID for connections
                created_locations[new_loc.name] = new_loc

                # Populate contents
                for item_or_entity_name in loc_data.get("contents", []):
                    # Simple check to differentiate items from entities
                    if "hp" in item_or_entity_name.lower():
                        # It's likely a creature
                        new_entity = GameEntity(
                            name=item_or_entity_name.split("(")[0].strip(),
                            entity_type="Monster",
                            description=item_or_entity_name,
                            current_location_id=new_loc.id,
                            current_map_point_id=map_point.id,
                        )
                        self.db.add(new_entity)
                    else:
                        # It's likely an item
                        new_item = Item(
                            name=item_or_entity_name,
                            description="An item of interest.",
                            location_id=new_loc.id,
                        )
                        self.db.add(new_item)

            # Create connections
            for source_name, dest_names in enriched_data.get("connections", {}).items():
                source_loc = created_locations.get(source_name)
                if source_loc:
                    for dest_name in dest_names:
                        dest_loc = created_locations.get(dest_name)
                        if dest_loc:
                            # Avoid duplicate connections
                            existing = self.db.query(LocationConnection).filter(
                                (LocationConnection.source_location_id == source_loc.id) &
                                (LocationConnection.destination_location_id == dest_loc.id)
                            ).first()
                            if not existing:
                                conn = LocationConnection(
                                    source_location_id=source_loc.id,
                                    destination_location_id=dest_loc.id,
                                    description=f"A path leads from {source_name} to {dest_name}.",
                                    is_two_way=True, # Assuming two-way for now
                                )
                                self.db.add(conn)

        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error processing LLM response for world generation: {e}")
            # Fallback to a single, simple location if enrichment fails
            fallback_location = Location(
                name=f"Entrance to {map_point.name}",
                description=f"The main entrance to {map_point.name}.",
                map_point=map_point,
                is_entry_point=True,
            )
            self.db.add(fallback_location)


    def _generate_topography_and_pois(self):
        # Simplified die drop for topography and POIs
        num_pois = random.randint(3, 8)
        pois = []
        for i in range(num_pois):
            poi_type_roll = self._d6()
            poi_type = POI_DIE_DROP.get(poi_type_roll, "Curiosity")

            if "Settlement" in poi_type:
                poi_details = SETTLEMENTS.get(
                    self._d20(), ("Hamlet", "High Population Density")
                )
            elif "Curiosity" in poi_type:
                poi_details = CURIOSITIES.get(
                    self._d20(), ("Broken Tower", "Ancient Trash Heap")
                )
            elif "Lair" in poi_type:
                poi_details = LAIRS.get(
                    self._d20(), ("Collapsed Mine", "Baited Entrance")
                )
            else:  # Dungeon or Waypoint
                poi_details = DUNGEONS.get(self._d20(), ("Cave", "Buried"))

            poi_name = f"{poi_details[0]} of the {EASY_TERRAIN.get(self._d20(), ('Valleys', 'Titanic Gate'))[1]}"
            new_poi = MapPoint(
                name=poi_name,
                type=poi_type,
                description=f"{poi_details[0]} - {poi_details[1]}",
                status="hidden",
                position_x=random.randint(50, 750),
                position_y=random.randint(50, 450),
            )
            self.db.add(new_poi)
            self.db.flush() # Flush to get ID for enrichment

            # Enrich the POI with LLM-generated locations and descriptions
            self._enrich_map_point_with_llm(new_poi)

            pois.append(new_poi)

        # Set starting POI
        if pois:
            start_poi = random.choice(pois)
            start_poi.status = "explored"

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
                existing_path = (
                    self.db.query(Path)
                    .filter(
                        (
                            (Path.start_point_id == start_poi.id)
                            & (Path.end_point_id == end_poi.id)
                        )
                        | (
                            (Path.start_point_id == end_poi.id)
                            & (Path.end_point_id == start_poi.id)
                        )
                    )
                    .first()
                )
                if existing_path:
                    continue

                feature, condition = PATH_FEATURES.get(
                    self._d20(), ("Twisted", "Thick Evening Mist")
                )
                new_path = Path(
                    start_point_id=start_poi.id,
                    end_point_id=end_poi.id,
                    status="hidden",
                    watches=random.randint(1, 3),
                    feature=f"{feature} ({condition})",
                )
                self.db.add(new_path)
        self.db.commit()