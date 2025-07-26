import random
import re
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import models
from .oracles import OracleRoller
from .condition_tracker import ConditionTracker

"""
This module defines the "World Tools" that the AI Warden can use to interact
with the game world. These functions are the bridge between the LLM's narrative
and the concrete game state stored in the database.
"""

# --- Helper Functions ---


def _find_entity_by_name(db: Session, name: str) -> models.GameEntity | None:
    """Finds a single entity by name, case-insensitively."""
    if not name:
        return None

    if name.lower() == "player":
        return (
            db.query(models.GameEntity)
            .filter_by(entity_type="Character", is_retired=False)
            .first()
        )

    return (
        db.query(models.GameEntity)
        .filter(func.lower(models.GameEntity.name) == name.lower())
        .first()
    )


# --- Dice Rolling Tools ---


def roll_dice(dice_string: str) -> Dict[str, Any]:
    """
    Rolls dice based on a standard dice string format (e.g., '1d6', '2d8+2', '1d20-1') or a fixed number.

    Args:
        dice_string: The dice to roll, in standard notation, or a string representing an integer.

    Returns:
        A dictionary containing the total result and the individual rolls.
    """
    dice_string = dice_string.lower().replace(" ", "")
    if dice_string.isdigit():
        total = int(dice_string)
        return {"total": total, "rolls": [total], "modifier": 0, "final_result": total}

    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_string)
    if not match:
        return {
            "error": "Invalid dice string format. Use format like '1d6' or '2d8+2'."
        }

    num_dice, die_size, modifier_str = match.groups()
    num_dice, die_size = int(num_dice), int(die_size)
    modifier = int(modifier_str) if modifier_str else 0

    rolls = [random.randint(1, die_size) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    return {"total": total, "rolls": rolls, "modifier": modifier, "final_result": total}


# --- Character & Entity Tools ---


def get_character_sheet(db: Session, character_name: str) -> Dict[str, Any]:
    """
    Retrieves the full character sheet for a specified character or NPC.

    Args:
        db: The database session.
        character_name: The name of the character to retrieve (e.g., "Player", "Goblin 1").

    Returns:
        A dictionary representing the character's stats and inventory.
    """
    entity = _find_entity_by_name(db, character_name)
    if not entity:
        return {"error": f"Character '{character_name}' not found."}

    inventory_items = [f"{item.name} (x{item.quantity})" for item in entity.items]

    return {
        "name": entity.name,
        "hp": entity.hp,
        "max_hp": entity.max_hp,
        "strength": entity.strength,
        "dexterity": entity.dexterity,
        "willpower": entity.willpower,
        "fatigue": entity.fatigue,
        "armor": entity.armor,
        "description": entity.description,
        "inventory": inventory_items if inventory_items else "Empty",
    }


def deal_damage(db: Session, attacker_name: str, target_name: str) -> Dict[str, Any]:
    """
    Resolves an attack from an attacker to a target.

    It finds the attacker's primary weapon, rolls the damage, and applies it
    to the target, handling HP, Scars, and Strength loss.

    Args:
        db: The database session.
        attacker_name: The name of the entity making the attack.
        target_name: The exact name of the target receiving damage.

    Returns:
        A dictionary confirming the action and showing the target's new state.
    """
    print(f"Resolving attack from {attacker_name} to {target_name}...")
    attacker = _find_entity_by_name(db, attacker_name)
    if not attacker:
        return {"error": f"Attacker '{attacker_name}' not found."}

    target = _find_entity_by_name(db, target_name)
    if not target:
        return {"error": f"Target '{target_name}' not found."}

    # Determine damage amount by rolling attacker's weapon dice
    try:
        # The 'attacks' attribute is stored as a JSON string in the DB
        attacks_list = json.loads(attacker.attacks)
        # Assuming the first attack in the list is the primary one
        attack_info = attacks_list[0]
        damage_dice = attack_info.get(
            "damage", "1d4"
        )  # Default to 1d4 if no damage specified
    except (IndexError, TypeError, KeyError, json.JSONDecodeError):
        damage_dice = "1d4"  # Default if attacks are missing or malformed

    damage_roll_result = roll_dice(damage_dice)
    damage_amount = damage_roll_result.get("total", 0)

    original_hp = target.hp
    original_strength = target.strength
    received_scar = None

    # Check for a Scar before applying damage
    if original_hp > 0 and (original_hp - damage_amount) == 0:
        scar_description = (
            "A nasty gash across the face, a constant reminder of this day."
        )
        target.scars = (
            f"{target.scars}\n{scar_description}" if target.scars else scar_description
        )
        target.max_hp = max(0, target.max_hp - 1)
        received_scar = scar_description

    # Apply damage to HP first
    hp_damage = min(original_hp, damage_amount)
    new_hp = original_hp - hp_damage
    target.hp = new_hp
    remaining_damage = damage_amount - hp_damage

    # Apply remaining damage to Strength
    if remaining_damage > 0:
        target.strength -= remaining_damage

    result = {
        "attacker_name": attacker.name,
        "target_name": target.name,
        "damage_roll": damage_dice,
        "damage_taken": damage_amount,
        "hp_lost": hp_damage,
        "strength_lost": original_strength - target.strength,
        "new_hp": target.hp,
        "new_strength": target.strength,
        "received_scar": received_scar,
        "is_dead": False,
    }

    # Check for death
    if target.strength <= 0:
        target.is_retired = True
        result["is_dead"] = True
        result["final_state"] = f"{target.name} has been slain."
        
        # Check tension event conditions for entity death
        condition_tracker = ConditionTracker(db)
        condition_tracker.check_all_conditions("entity_death", {
            "entity_name": target.name,
            "entity_id": target.id,
            "killed_by": attacker.name
        })

    print(f"Attack result: {result}")
    return result


# --- Inventory & Item Tools ---


def drop_item(db: Session, character_name: str, item_name: str) -> Dict[str, Any]:
    """
    Removes an item from a character's inventory and places it on the ground in their current location.

    Args:
        db: The database session.
        character_name: The name of the character dropping the item.
        item_name: The name of the item to drop.

    Returns:
        A dictionary confirming the action.
    """
    character = _find_entity_by_name(db, character_name)
    if not character:
        return {"error": f"Character '{character_name}' not found."}
    if not character.current_location:
        return {"error": f"Character '{character_name}' is not in a valid location."}

    item_to_drop = (
        db.query(models.Item)
        .filter(
            models.Item.owner_entity_id == character.id,
            func.lower(models.Item.name) == item_name.lower(),
        )
        .first()
    )

    if not item_to_drop:
        return {
            "error": f"Item '{item_name}' not found in {character_name}'s inventory."
        }

    # Remove from player's inventory and add to the location
    item_to_drop.owner_entity_id = None
    item_to_drop.location_id = character.current_location_id

    db.commit()

    return {
        "success": True,
        "message": f"{character_name} dropped {item_name} on the ground.",
    }


def increase_fatigue(db: Session, character_name: str) -> Dict[str, Any]:
    """
    Increases a character's fatigue by 1. If fatigue exceeds strength, the character drops the last item in their inventory.

    Args:
        db: The database session.
        character_name: The name of the character.

    Returns:
        A dictionary confirming the fatigue increase and any dropped items.
    """
    character = _find_entity_by_name(db, character_name)
    if not character:
        return {"error": f"Character '{character_name}' not found."}

    character.fatigue += 1
    message = f"{character.name}'s fatigue increased to {character.fatigue}."

    if character.fatigue > character.strength:
        if character.items:
            item_to_drop = character.items[-1]
            drop_message = drop_item(db, character.name, item_to_drop.name)["message"]
            message += f" {drop_message}"
        else:
            message += " The character is exhausted but has no items to drop."

    db.commit()

    return {"success": True, "message": message}


def rest(db: Session, character_name: str) -> Dict[str, Any]:
    """
    Allows a character to take a short rest to recover HP.

    Args:
        db: The database session.
        character_name: The name of the character resting.

    Returns:
        A dictionary confirming the character has rested and their HP is restored.
    """
    entity = _find_entity_by_name(db, character_name)
    if not entity:
        return {"error": f"Character '{character_name}' not found."}

    entity.hp = entity.max_hp
    return {
        "success": True,
        "character_name": entity.name,
        "new_hp": entity.hp,
        "message": f"{entity.name} takes a moment to catch their breath, tending to their wounds.",
    }


def make_camp(db: Session, character_name: str) -> Dict[str, Any]:
    """
    Allows a character to make camp for the day to recover fully. (Placeholder)

    Args:
        db: The database session.
        character_name: The name of the character making camp.

    Returns:
        A dictionary confirming the character has made camp.
    """
    entity = _find_entity_by_name(db, character_name)
    if not entity:
        return {"error": f"Character '{character_name}' not found."}

    # Placeholder: In the future, this will handle fatigue, rations, etc.
    entity.hp = entity.max_hp
    return {
        "success": True,
        "message": f"{entity.name} sets up a small, rough camp for the night, finding a brief respite.",
    }


def give_item(db: Session, giver_name: str, receiver_name: str, item_name: str) -> Dict[str, Any]:
    """
    Transfer an item from one entity to another.
    
    Args:
        db: The database session.
        giver_name: The name of the entity giving the item.
        receiver_name: The name of the entity receiving the item.
        item_name: The name of the item to transfer.
        
    Returns:
        A dictionary confirming the item transfer.
    """
    giver = _find_entity_by_name(db, giver_name)
    receiver = _find_entity_by_name(db, receiver_name)
    
    if not giver:
        return {"error": f"Giver '{giver_name}' not found."}
    if not receiver:
        return {"error": f"Receiver '{receiver_name}' not found."}
    
    # Find and transfer the item
    item = (
        db.query(models.Item)
        .filter_by(owner_entity_id=giver.id, name=item_name)
        .first()
    )
    
    if not item:
        return {"error": f"{giver_name} doesn't have {item_name}."}
    
    item.owner_entity_id = receiver.id
    db.commit()
    
    # Check tension event conditions for item delivery
    condition_tracker = ConditionTracker(db)
    condition_tracker.check_all_conditions("item_delivery", {
        "giver_name": giver_name,
        "receiver_name": receiver_name,
        "item_name": item_name,
        "item_id": item.id
    })
    
    return {
        "success": True,
        "message": f"{giver_name} gave {item_name} to {receiver_name}."
    }


def add_item_to_inventory(
    db: Session,
    character_name: str,
    item_name: str,
    quantity: int = 1,
    description: str = None,
    slots: int = 1,
) -> Dict[str, Any]:
    """
    Adds a specified quantity of an item to a character's inventory. If the item already exists, it increases the quantity; otherwise, it creates a new item.

    Args:
        db: The database session.
        character_name: The name of the character receiving the item.
        item_name: The name of the item to add.
        quantity: The number of items to add. Defaults to 1.
        description: A brief description of the item. Required for new items.
        slots: How many inventory slots the item takes. Defaults to 1.

    Returns:
        A dictionary confirming the item was added or updated.
    """
    entity = _find_entity_by_name(db, character_name)
    if not entity:
        return {"error": f"Character '{character_name}' not found."}

    # Check if the character already has this item
    existing_item = (
        db.query(models.Item)
        .filter_by(owner_entity_id=entity.id, name=item_name)
        .first()
    )

    if existing_item:
        existing_item.quantity += quantity
        message = f"Increased quantity of {item_name} to {existing_item.quantity}."
    else:
        if not description:
            return {"error": "A description is required to create a new item."}
        new_item = models.Item(
            name=item_name,
            description=description,
            quantity=quantity,
            slots=slots,
            owner_entity_id=entity.id,
        )
        db.add(new_item)
        message = f"Added {quantity}x {item_name} to {character_name}'s inventory."

    # Check tension event conditions for item received
    condition_tracker = ConditionTracker(db)
    condition_tracker.check_all_conditions("item_received", {
        "recipient_name": character_name,
        "recipient_id": entity.id,
        "item_name": item_name,
        "quantity": quantity
    })

    return {"success": True, "message": message}


# --- World & Location Tools ---


def get_location_description(db: Session, character_name: str) -> Dict[str, Any]:
    """Retrieves the description of the player character's current location, including other entities and items on the ground."""
    character = _find_entity_by_name(db, character_name)
    if not character or not character.current_location:
        return {"error": "Character or their location could not be found."}

    location = character.current_location

    # Find other entities at the same location
    other_entities = (
        db.query(models.GameEntity)
        .filter(
            models.GameEntity.current_location_id == location.id,
            models.GameEntity.id != character.id,
            models.GameEntity.is_retired == False,  # noqa: E712
        )
        .all()
    )

    # Find items on the ground at this location
    ground_items = (
        db.query(models.Item)
        .filter(
            models.Item.location_id == location.id,
            models.Item.owner_entity_id == None, # noqa: E711 (None means it's on the ground, not owned by any entity)
        )
        .all()
    )

    return {
        "location_name": location.name,
        "description": location.description,
        "other_entities_present": [e.name for e in other_entities]
        if other_entities
        else "None",
        "items_on_ground": [i.name for i in ground_items] if ground_items else "None",
    }


def look_around(db: Session, player: models.GameEntity) -> None:
    """
    Generates and logs a description of the player's current location and its contents.
    This is a utility function, not an LLM tool.
    """
    if not player or not player.current_location:
        return

    location = player.current_location
    entities = [
        e.name for e in location.entities if e.id != player.id and not e.is_retired
    ]
    items = [i.name for i in location.items]

    narrative = f"**{location.name}**\n\n{location.description}"

    if entities:
        narrative += f"\n\nYou see: {', '.join(entities)}."
    if items:
        narrative += f"\n\nOn the ground, you notice: {', '.join(items)}."

    # Get connections to other locations within the same MapPoint
    connections = location.connections_from
    if connections:
        connected_locations = [
            conn.destination_location.name for conn in connections
        ]
        narrative += f"\n\nFrom here, you can go to: {', '.join(connected_locations)}."

    # If this is an entry point, also show paths to other MapPoints
    if location.is_entry_point:
        map_point = player.current_map_point
        if map_point:
            paths = map_point.paths_from
            if paths:
                available_paths = [path.end_point.name for path in paths]
                narrative += f"\n\nYou can travel to other areas: {', '.join(available_paths)}."

    if not entities and not items and not connections:
        narrative += "\n\nThe area seems quiet and isolated."

    log_entry = models.LogEntry(source="Warden", content=narrative)
    db.add(log_entry)
    db.commit()


def discover_location(db: Session, location_name: str) -> Dict[str, Any]:

    """
    Changes the status of a hidden MapPoint to 'known'.

    Args:
        db: The database session.
        location_name: The name of the MapPoint to discover.

    Returns:
        A dictionary confirming the location has been discovered.
    """
    map_point = (
        db.query(models.MapPoint)
        .filter(func.lower(models.MapPoint.name) == location_name.lower())
        .first()
    )

    if not map_point:
        return {"error": f"Location '{location_name}' not found."}

    if map_point.status == "hidden":
        map_point.status = "known"
        db.commit()
        return {
            "success": True,
            "message": f"A new location, {location_name}, has been added to your map.",
        }
    else:
        return {"success": False, "message": f"{location_name} is already known."}


def move_character(
    db: Session, character_name: str, new_location_name: str
) -> Dict[str, Any]:
    """
    Moves a character to a new location.

    Args:
        db: The database session.
        character_name: The name of the character to move.
        new_location_name: The name of the location to move to.

    Returns:
        A dictionary indicating the result of the move.
    """
    character = _find_entity_by_name(db, character_name)
    if not character:
        return {"error": f"Character '{character_name}' not found."}

    new_location = (
        db.query(models.Location)
        .filter(func.lower(models.Location.name) == new_location_name.lower())
        .first()
    )
    if not new_location:
        return {"error": f"Location '{new_location_name}' not found."}

    character.current_location_id = new_location.id
    db.commit()

    # Check tension event conditions for location visit
    condition_tracker = ConditionTracker(db)
    condition_tracker.check_all_conditions("location_visit", {
        "character_name": character.name,
        "character_id": character.id,
        "location_name": new_location.name,
        "location_id": new_location.id,
        "map_point_name": new_location.map_point.name if new_location.map_point else None
    })

    # Describe the new location to the player
    look_around(db, character)

    return {
        "success": True,
        "character_name": character.name,
        "new_location_name": new_location.name,
    }


def roll_wilderness_event(db: Session) -> Dict[str, Any]:
    """
    Rolls on the wilderness event table and returns the result.

    Args:
        db: The database session (not used directly, but required for tool signature).

    Returns:
        A dictionary containing the wilderness event description.
    """
    oracle_roller = OracleRoller()
    event = oracle_roller.roll_wilderness_event()
    return {"event_description": event}


def roll_saving_throw(db: Session, character_name: str, stat: str) -> Dict[str, Any]:
    """
    Rolls a d20 to perform a saving throw against a specified stat (strength, dexterity, or willpower).

    Args:
        db: The database session.
        character_name: The name of the character making the saving throw.
        stat: The stat to roll against (strength, dexterity, or willpower).

    Returns:
        A dictionary containing the roll, the target stat, and the result.
    """
    character = _find_entity_by_name(db, character_name)
    if not character:
        return {"error": f"Character '{character_name}' not found."}

    stat_value = getattr(character, stat, None)
    if stat_value is None:
        return {"error": f"Invalid stat '{stat}' for {character_name}."}

    roll = random.randint(1, 20)
    success = roll <= stat_value

    return {
        "roll": roll,
        "stat_tested": stat,
        "stat_value": stat_value,
        "success": success,
        "message": f"{character.name} rolled a {roll} against their {stat} of {stat_value}. {'Success' if success else 'Failure'}!",
    }
