import random
import json
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database.models import (
    WorldState,
    MapPoint,
    Path,
    Location,
    LocationConnection,
    GameEntity,
    Item,
    TensionEvent,
    ResolutionCondition,
    LogEntry,
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
    BACKGROUNDS,
    PHYSIQUE,
    SPEECH,
    VIRTUE,
    VICE,
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

    def _enrich_regular_poi_with_llm(self, map_point: MapPoint):
        """Uses the LLM to generate a rich description and interconnected locations for a regular POI."""
        prompt = f"""
        You are a creative, dark fantasy Game Master generating a new area for a solo RPG based on the game Cairn.
        The player is exploring a newly discovered point of interest.

        **Point of Interest Type:** {map_point.type}
        **Initial Name:** {map_point.name}
        **Initial Description:** {map_point.description}

        Your task is to expand this basic concept into a rich, explorable area.
        Generate a JSON object with the following structure:
        1.  `summary`: A 2-3 sentence, evocative summary of the entire area. This will be shown to the player on the world map.
        2.  `locations`: A list of 2 to 5 distinct, interconnected locations within this area. The first location is where the player arrives when they first enter the area. For each location, provide:
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
                                LocationConnection.source_location_id == source_loc.id,
                                LocationConnection.destination_location_id == dest_loc.id
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

    def _enrich_settlement_with_llm(self, map_point: MapPoint):
        """Uses the LLM to generate a populated settlement with NPCs and tension events."""
        # Get regional context for settlement generation
        region_theme = self.db.query(WorldState).filter(WorldState.key == "region_theme").first()
        culture_resources = region_theme.value if region_theme else {"culture": "Artistic (Control)", "resources": "Herbs (Scarce: Medicine)"}
        
        # Extract settlement type from the MapPoint type
        settlement_type = map_point.type.replace("Settlement - ", "")
        settlement_trait = map_point.description.split(" - ")[1] if " - " in map_point.description else "High Population Density"
        
        prompt = f"""
You are a masterful Game Master creating a living, breathing settlement for a dark fantasy RPG based on Cairn. This settlement will serve as the starting hub where new adventurers begin their journey, so it must feel populated, urgent, and full of opportunity.

**Settlement Details:**
- **Type:** {settlement_type}
- **Defining Trait:** {settlement_trait}
- **Regional Culture:** {culture_resources.get('culture', 'Artistic (Control)')}
- **Regional Resources:** {culture_resources.get('resources', 'Herbs (Scarce: Medicine)')}
- **Settlement Name:** {map_point.name}

**Your Task:**
Generate a JSON object describing this settlement as a hub of activity with urgent problems that demand attention. The settlement should feel like a place where things are happening RIGHT NOW, not a sleepy backwater.

**Required JSON Structure:**
{{
  "summary": "2-3 sentence overview of the entire settlement, emphasizing its current state and pressing atmosphere",
  "locations": [
    {{
      "name": "Location Name",
      "description": "Rich 3-4 sentence description focusing on sights, sounds, smells, and current activity",
      "function": "What this location does for the community",
      "current_situation": "What urgent or notable thing is happening here right now",
      "contents": ["List of people, items, or creatures currently present"]
    }}
  ],
  "connections": {{
    "Location Name": ["Connected Location Names"]
  }},
  "active_tensions": [
    {{
      "title": "Brief tension title",
      "description": "What's wrong and why it matters",
      "source_location": "Where this problem is centered",
      "urgency": "immediate/urgent/pressing",
      "potential_solutions": ["Different ways this could be resolved"]
    }}
  ]
}}

**Location Requirements:**
1. **Entry Point** (REQUIRED - first location, where travelers arrive)
2. **Social Hub** (REQUIRED - where people gather, talk, trade)
3. **Authority Center** (REQUIRED - where decisions are made)
4. **2-3 Thematic Locations** (specific to the settlement type)
5. **1 Problem Location** (where something is actively going wrong)

**Description Guidelines:**
- **Sensory Rich**: Include what characters see, hear, smell
- **Active Present**: Describe what's happening NOW, not what usually happens
- **Population Density**: Show how the settlement trait affects daily life
- **Cultural Flavor**: Reflect the regional culture in architecture, customs, behavior
- **Resource Scarcity**: Show how the scarce resource affects the community
- **Urgent Atmosphere**: Every location should hint at problems, opportunities, or tensions

**Content Guidelines:**
- **People**: Name 2-3 key NPCs per location with brief descriptions
- **Items**: Include tools, goods, or objects that hint at stories
- **Current Events**: What's happening right now that adventurers could get involved in

**Tension Guidelines:**
- **Immediate Problems**: Things that need solving within days, not weeks
- **Multiple Solutions**: Each tension should have 2-3 different resolution approaches
- **Interconnected**: Some tensions should affect multiple locations
- **Escalation Potential**: What happens if these problems aren't solved

**Tone:** Dark fantasy, urgent, lived-in, slightly desperate but not hopeless. This is a place where ordinary people face extraordinary challenges and need heroes to step forward.

Now generate the settlement JSON:
"""

        try:
            llm_response_str = self.llm_service.generate_response(prompt)
            json_str = llm_response_str.strip().replace("```json", "").replace("```", "").strip()
            settlement_data = json.loads(json_str)
            
            # Process settlement summary
            self.db.query(MapPoint).filter(MapPoint.id == map_point.id).update({
                "summary": settlement_data.get("summary", "A bustling settlement with urgent problems.")
            })
            
            # Create locations with settlement-specific data
            created_locations = {}
            for i, loc_data in enumerate(settlement_data.get("locations", [])):
                new_loc = Location(
                    name=loc_data.get("name"),
                    description=loc_data.get("description"),
                    map_point=map_point,
                    is_entry_point=(i == 0),  # First location is always entry point
                    contents={
                        "function": loc_data.get("function"),
                        "current_situation": loc_data.get("current_situation"),
                        "raw_contents": loc_data.get("contents", [])
                    }
                )
                self.db.add(new_loc)
                self.db.flush()
                created_locations[new_loc.name] = new_loc
                
                # Populate location contents (NPCs, items, etc.)
                self._populate_settlement_location_contents(new_loc, loc_data.get("contents", []))
            
            # Create location connections
            connections_map = settlement_data.get("connections", {})
            for source_name, destination_names in connections_map.items():
                source_location = created_locations.get(source_name)
                if not source_location:
                    continue
                    
                for dest_name in destination_names:
                    dest_location = created_locations.get(dest_name)
                    if not dest_location:
                        continue
                        
                    # Check for existing connection to avoid duplicates
                    existing = self.db.query(LocationConnection).filter(
                        LocationConnection.source_location_id == source_location.id,
                        LocationConnection.destination_location_id == dest_location.id
                    ).first()
                    
                    if not existing:
                        connection = LocationConnection(
                            source_location_id=source_location.id,
                            destination_location_id=dest_location.id,
                            description=f"A path connects {source_name} to {dest_name}.",
                            is_two_way=True
                        )
                        self.db.add(connection)
            
            # Create tension events
            tensions = settlement_data.get("active_tensions", [])
            for tension_data in tensions:
                self._create_tension_event_from_data(tension_data, map_point, created_locations)
                
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error processing settlement LLM response: {e}")
            # Fallback to basic settlement
            self._create_fallback_settlement(map_point)

    def _populate_settlement_location_contents(self, location: Location, contents_list: list):
        """Populates a settlement location with NPCs, items, and other content."""
        for content_item in contents_list:
            content_lower = content_item.lower()
            
            # Detect NPCs (people with names, roles, or descriptive terms)
            if any(indicator in content_lower for indicator in [
                "elder", "merchant", "guard", "priest", "blacksmith", "innkeeper", 
                "farmer", "scholar", "captain", "healer", "worried", "angry", 
                "desperate", "busy", "talking", "standing", "working"
            ]):
                self._create_settlement_npc(location, content_item)
            
            # Detect items or atmospheric elements
            else:
                # Store as atmospheric description in location contents
                current_contents = location.contents if location.contents else {}
                atmospheric = current_contents.get("atmospheric", [])
                atmospheric.append(content_item)
                current_contents["atmospheric"] = atmospheric
                # Update the location contents properly
                self.db.query(Location).filter(Location.id == location.id).update({
                    "contents": current_contents
                })

    def _create_settlement_npc(self, location: Location, description: str):
        """Creates an NPC GameEntity from a description string."""
        # Extract name (first capitalized word or phrase before parentheses/commas)
        name_parts = description.split("(")[0].split(",")[0].strip()
        name = name_parts if name_parts else "Local Resident"
        
        # Basic NPC stats (settlement NPCs are generally non-hostile)
        npc = GameEntity(
            name=name,
            entity_type="NPC",
            description=description,
            current_location_id=location.id,
            current_map_point_id=location.map_point_id,
            disposition="neutral",
            is_hostile=False,
            hp=3,
            max_hp=3,
            strength=10,
            max_strength=10,
            dexterity=10,
            max_dexterity=10,
            willpower=10,
            max_willpower=10
        )
        
        self.db.add(npc)

    def _create_tension_event_from_data(self, tension_data: dict, map_point: MapPoint, created_locations: dict):
        """Creates a TensionEvent and ResolutionConditions from settlement data."""
        urgency_to_watches = {
            "immediate": 2,
            "urgent": 4,
            "pressing": 6,
            "moderate": 8
        }
        
        urgency = tension_data.get("urgency", "urgent")
        deadline_watches = urgency_to_watches.get(urgency, 4)
        
        tension_event = TensionEvent(
            title=tension_data.get("title"),
            description=tension_data.get("description"),
            source_type="settlement_problem",
            source_data={
                "settlement_id": map_point.id,
                "source_location": tension_data.get("source_location"),
                "urgency_level": urgency
            },
            severity_level=1,
            max_severity=5,
            deadline_watches=deadline_watches,
            watches_remaining=deadline_watches,
            status="active",
            origin_map_point_id=map_point.id
        )
        
        self.db.add(tension_event)
        self.db.flush()
        
        # Create resolution conditions for each potential solution
        solutions = tension_data.get("potential_solutions", [])
        for solution in solutions:
            condition = self._create_resolution_condition_from_solution(tension_event.id, solution)
            self.db.add(condition)

    def _create_resolution_condition_from_solution(self, tension_event_id: int, solution_description: str) -> ResolutionCondition:
        """Creates a ResolutionCondition from a solution description."""
        solution_lower = solution_description.lower()
        
        # Parse solution type from description
        if "kill" in solution_lower or "defeat" in solution_lower or "eliminate" in solution_lower:
            return ResolutionCondition(
                tension_event_id=tension_event_id,
                condition_type="entity_death",
                description=solution_description,
                target_data={"entity_name": "threatening creature"},
                is_met=False
            )
        elif "deliver" in solution_lower or "bring" in solution_lower or "find" in solution_lower:
            return ResolutionCondition(
                tension_event_id=tension_event_id,
                condition_type="item_delivery",
                description=solution_description,
                target_data={"item_name": "needed item", "receiver_name": "requesting NPC"},
                is_met=False
            )
        elif "visit" in solution_lower or "go to" in solution_lower or "travel" in solution_lower:
            return ResolutionCondition(
                tension_event_id=tension_event_id,
                condition_type="location_visit",
                description=solution_description,
                target_data={"location_name": "target location"},
                is_met=False
            )
        else:
            # Generic condition for complex solutions
            return ResolutionCondition(
                tension_event_id=tension_event_id,
                condition_type="custom",
                description=solution_description,
                target_data={"description": solution_description},
                is_met=False
            )

    def _create_fallback_settlement(self, map_point: MapPoint):
        """Creates a basic settlement if LLM generation fails."""
        map_point.summary = f"A small {map_point.type.lower()} with urgent problems that need attention."
        
        # Create basic entry location
        entry_location = Location(
            name=f"Entrance to {map_point.name}",
            description=f"The main entrance to {map_point.name}. People move about with worried expressions.",
            map_point=map_point,
            is_entry_point=True,
            contents={"function": "Entry point", "current_situation": "Travelers arrive seeking help"}
        )
        self.db.add(entry_location)
        self.db.flush()
        
        # Create a basic NPC with a problem
        worried_elder = GameEntity(
            name="Worried Elder",
            entity_type="NPC",
            description="An elderly resident with deep concern etched on their weathered face",
            current_location_id=entry_location.id,
            current_map_point_id=map_point.id,
            disposition="neutral",
            is_hostile=False,
            hp=2, max_hp=2, strength=8, max_strength=8,
            dexterity=8, max_dexterity=8, willpower=12, max_willpower=12
        )
        self.db.add(worried_elder)
        
        # Create a basic tension event
        basic_tension = TensionEvent(
            title="Settlement in Crisis",
            description="The settlement faces an urgent problem that requires outside help.",
            source_type="settlement_problem",
            source_data={"settlement_id": map_point.id, "urgency_level": "urgent"},
            severity_level=1, max_severity=5,
            deadline_watches=4, watches_remaining=4,
            status="active", origin_map_point_id=map_point.id
        )
        self.db.add(basic_tension)


    def _generate_topography_and_pois(self):
        """Generate POIs with guaranteed settlement as starting point."""
        pois = []
        
        # TASK 34.1: Force first POI to be a settlement
        settlement_roll = self._d20()
        settlement_details = SETTLEMENTS.get(settlement_roll, ("Hamlet", "High Population Density"))
        settlement_name = f"{settlement_details[0]} of the {EASY_TERRAIN.get(self._d20(), ('Valleys', 'Titanic Gate'))[1]}"
        
        starting_settlement = MapPoint(
            name=settlement_name,
            type=f"Settlement - {settlement_details[0]}",
            description=f"{settlement_details[0]} - {settlement_details[1]}",
            status="explored",  # This makes it visible and the starting point
            position_x=random.randint(200, 400),  # Center-ish position
            position_y=random.randint(200, 300),
        )
        
        self.db.add(starting_settlement)
        self.db.flush()
        
        # Use specialized settlement enrichment
        self._enrich_settlement_with_llm(starting_settlement)
        pois.append(starting_settlement)
        
        # Generate remaining POIs (2-7 additional ones)
        remaining_pois = random.randint(2, 7)
        for i in range(remaining_pois):
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
            self.db.flush()

            # Use regular POI enrichment for non-settlements
            self._enrich_regular_poi_with_llm(new_poi)
            pois.append(new_poi)

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
                        or_(
                            and_(Path.start_point_id == start_poi.id, Path.end_point_id == end_poi.id),
                            and_(Path.start_point_id == end_poi.id, Path.end_point_id == start_poi.id)
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
