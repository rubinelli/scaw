"""
This module defines the "World Tools" that the AI Warden can use to interact
with the game world. These functions are the bridge between the LLM's narrative
and the concrete game state stored in the database.
"""

import random
import re
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import models

# --- Helper Functions ---


def _find_entity_by_name(db: Session, name: str) -> models.GameEntity | None:
    """Finds a single entity by name, case-insensitively."""
    return (
        db.query(models.GameEntity)
        .filter(func.lower(models.GameEntity.name) == name.lower())
        .first()
    )


# --- Dice Rolling Tools ---


def roll_dice(dice_string: str) -> Dict[str, Any]:
    """
    Rolls dice based on a standard dice string format (e.g., '1d6', '2d8+2', '1d20-1').

    Args:
        dice_string: The dice to roll, in standard notation.

    Returns:
        A dictionary containing the total result and the individual rolls.
    """
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_string.lower().replace(" ", ""))
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


def deal_damage(db: Session, target_name: str, damage_amount: int) -> Dict[str, Any]:
    """
    Deals a specific amount of damage to a target entity.

    Damage is first applied to HP. If HP is depleted, the remaining damage
    is applied to Strength (STR). If an attack reduces HP to exactly 0,
    the character gets a Scar and their Max HP is reduced. If STR is
    reduced to 0, the character is dead.

    Args:
        db: The database session.
        target_name: The exact name of the target receiving damage.
        damage_amount: The amount of damage to deal.

    Returns:
        A dictionary confirming the action and showing the target's new state.
    """
    print(f"Dealing {damage_amount} damage to {target_name}...")
    entity = _find_entity_by_name(db, target_name)
    if not entity:
        return {"error": f"Target '{target_name}' not found."}

    original_hp = entity.hp
    original_strength = entity.strength
    received_scar = None

    # Check for a Scar before applying damage
    if original_hp > 0 and (original_hp - damage_amount) == 0:
        scar_description = f"A nasty gash across the face, a constant reminder of this day."
        entity.scars = (
            f"{entity.scars}\n{scar_description}" if entity.scars else scar_description
        )
        entity.max_hp = max(0, entity.max_hp - 1)  # Reduce max_hp, ensure it's not negative
        received_scar = scar_description

    # Apply damage to HP first
    hp_damage = min(original_hp, damage_amount)
    entity.hp -= hp_damage
    remaining_damage = damage_amount - hp_damage

    # Apply remaining damage to Strength
    if remaining_damage > 0:
        entity.strength -= remaining_damage

    result = {
        "target_name": entity.name,
        "damage_taken": damage_amount,
        "hp_lost": hp_damage,
        "strength_lost": original_strength - entity.strength,
        "new_hp": entity.hp,
        "new_strength": entity.strength,
        "received_scar": received_scar,
        "is_dead": False,
    }
    print(f"Result after damage: {result}")

    # Check for death
    if entity.strength <= 0:
        entity.is_retired = True  # Mark as dead/retired
        result["is_dead"] = True
        result["final_state"] = f"{entity.name} has been slain."

    return result



# --- Inventory & Item Tools ---


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

    return {"success": True, "message": message}


# --- World & Location Tools ---


def get_location_description(db: Session, character_name: str) -> Dict[str, Any]:
    """
    Retrieves the description of the player character's current location, including other entities and items on the ground.

    Args:
        db: The database session.
        character_name: The name of the character whose location is being described.

    Returns:
        A dictionary containing the location's details.
    """
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
            models.Item.owner_entity_id == None,  # noqa: E711
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

    return {
        "success": True,
        "character_name": character.name,
        "new_location_name": new_location.name,
    }
