import random
from sqlalchemy.orm import Session
from database.models import WorldState, MapPoint, Path, Location
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

            # Create a default location for the MapPoint
            default_location = Location(
                name=f"Entrance to {new_poi.name}",
                description=f"The main entrance to {new_poi.name}.",
                contents=[],
            )
            new_poi.locations.append(
                default_location
            )  # Add location to the map_point's locations
            new_poi.default_location = default_location  # Set as default location

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
