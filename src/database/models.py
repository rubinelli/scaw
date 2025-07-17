import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class WorldState(Base):
    __tablename__ = "world_state"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON)


class GameEntity(Base):
    __tablename__ = "game_entity"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # "Character", "NPC", "Monster"
    hp = Column(Integer, default=0)
    max_hp = Column(Integer, default=0)
    strength = Column(Integer, default=0)
    max_strength = Column(Integer, default=0)
    dexterity = Column(Integer, default=0)
    max_dexterity = Column(Integer, default=0)
    willpower = Column(Integer, default=0)
    max_willpower = Column(Integer, default=0)
    fatigue = Column(Integer, default=0)
    armor = Column(Integer, default=0)
    disposition = Column(String, default="neutral")
    age = Column(Integer)
    pronouns = Column(String)
    description = Column(Text)
    background = Column(String)
    bond = Column(String)
    omen = Column(String)
    is_retired = Column(Boolean, default=False)
    attacks = Column(JSON)

    current_map_point_id = Column(Integer, ForeignKey("map_point.id"))
    current_map_point = relationship("MapPoint", back_populates="entities")

    current_location_id = Column(Integer, ForeignKey("location.id"), nullable=True)
    current_location = relationship("Location", back_populates="entities")

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=1)
    slots = Column(Integer, default=1)
    tags = Column(JSON)

    owner_entity_id = Column(Integer, ForeignKey("game_entity.id"))
    owner = relationship("GameEntity", back_populates="items")

    location_id = Column(Integer, ForeignKey("location.id"))
    location = relationship("Location", back_populates="items")


class LogEntry(Base):
    __tablename__ = "log_entry"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String, nullable=False)  # "Player" or "Warden"
    content = Column(Text, nullable=False)
    metadata_dict = Column(JSON)
    involved_entities = Column(JSON)


class MapPoint(Base):
    __tablename__ = "map_point"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    description = Column(Text)
    notes = Column(Text)
    status = Column(String, nullable=False)  # "hidden", "rumored", "known", "explored"
    position_x = Column(Integer)
    position_y = Column(Integer)

    default_location_id = Column(
        Integer, ForeignKey("location.id", use_alter=True), nullable=True
    )
    default_location = relationship("Location", foreign_keys=[default_location_id])

    entities = relationship("GameEntity", back_populates="current_map_point")
    locations = relationship(
        "Location", back_populates="map_point", foreign_keys="Location.map_point_id"
    )

    paths_from = relationship(
        "Path", foreign_keys="Path.start_point_id", back_populates="start_point"
    )
    paths_to = relationship(
        "Path", foreign_keys="Path.end_point_id", back_populates="end_point"
    )


class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    contents = Column(JSON)

    map_point_id = Column(Integer, ForeignKey("map_point.id"), nullable=False)
    map_point = relationship(
        "MapPoint", back_populates="locations", foreign_keys=[map_point_id]
    )

    items = relationship("Item", back_populates="location")
    entities = relationship("GameEntity", back_populates="current_location")

    connections_from = relationship(
        "LocationConnection",
        foreign_keys="LocationConnection.source_location_id",
        back_populates="source_location",
        cascade="all, delete-orphan",
    )
    connections_to = relationship(
        "LocationConnection",
        foreign_keys="LocationConnection.destination_location_id",
        back_populates="destination_location",
        cascade="all, delete-orphan",
    )


class LocationConnection(Base):
    __tablename__ = "location_connection"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    is_two_way = Column(Boolean, default=True)

    source_location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    destination_location_id = Column(Integer, ForeignKey("location.id"), nullable=False)

    source_location = relationship(
        "Location", foreign_keys=[source_location_id], back_populates="connections_from"
    )
    destination_location = relationship(
        "Location",
        foreign_keys=[destination_location_id],
        back_populates="connections_to",
    )


class Path(Base):
    __tablename__ = "path"

    id = Column(Integer, primary_key=True)
    type = Column(String, default="Standard")
    status = Column(String, nullable=False)  # "hidden", "known", "explored"
    watches = Column(Integer, default=1)
    feature = Column(String)

    start_point_id = Column(Integer, ForeignKey("map_point.id"), nullable=False)
    end_point_id = Column(Integer, ForeignKey("map_point.id"), nullable=False)

    start_point = relationship(
        "MapPoint", foreign_keys=[start_point_id], back_populates="paths_from"
    )
    end_point = relationship(
        "MapPoint", foreign_keys=[end_point_id], back_populates="paths_to"
    )
