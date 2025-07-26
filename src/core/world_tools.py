import random
import re
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import models
from .oracles import OracleRoller
from .condition_tracker import ConditionTracker
import datetime

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
    Allows a character to make camp for the night, recovering HP and fatigue while advancing time.

    Args:
        db: The database session.
        character_name: The name of the character making camp.

    Returns:
        A dictionary confirming the character has made camp and any tension escalations.
    """
    entity = _find_entity_by_name(db, character_name)
    if not entity:
        return {"error": f"Character '{character_name}' not found."}

    # Restore HP and reduce fatigue
    entity.hp = entity.max_hp
    entity.fatigue = max(0, entity.fatigue - 1)
    
    # Advance time by 1 watch and check for tension escalations
    condition_tracker = ConditionTracker(db)
    escalated_events = condition_tracker.advance_time(watches=1)
    
    # Build response message
    message = f"{entity.name} sets up camp for the night, tending to wounds and resting. **Time passes: 1 watch**"
    
    # Handle tension escalations
    escalation_messages = []
    for event in escalated_events:
        if event.status == "failed":
            escalation_messages.append(f"**TENSION FAILURE:** {event.title} has spiraled out of control!")
            # Apply failure consequences
            _apply_tension_failure_consequences(db, event)
        else:
            escalation_messages.append(f"**TENSION ESCALATION:** {event.title} grows more urgent (Severity {event.severity_level})!")
    
    if escalation_messages:
        message += "\n\n" + "\n".join(escalation_messages)
    
    return {
        "success": True,
        "message": message,
        "time_advanced": 1,
        "escalated_events": len(escalated_events)
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
    
    # Update NPC relationships based on the gift
    player = _find_entity_by_name(db, "player")
    if player:
        if giver.id == player.id and receiver.entity_type == "NPC":
            # Player gave item to NPC - positive relationship change
            update_npc_relationship(
                db, receiver.name, "received_gift", 1, 
                f"Grateful for receiving {item_name}"
            )
        elif receiver.id == player.id and giver.entity_type == "NPC":
            # NPC gave item to player - positive relationship change
            update_npc_relationship(
                db, giver.name, "gave_gift", 1,
                f"Pleased to help by giving {item_name}"
            )
    
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


# --- NPC Relationship Management Tools ---


def _get_npc_relationship(npc: models.GameEntity) -> Dict[str, Any]:
    """Helper function to parse NPC relationship data from bond field"""
    if not npc.bond:
        # Initialize default relationship
        return {
            "relationship_level": 0,
            "relationship_type": "neutral",
            "history": [],
            "trust_level": "cautious",
            "fear_level": "none"
        }
    
    try:
        return json.loads(npc.bond)
    except (json.JSONDecodeError, TypeError):
        # If bond contains old-style text, preserve it in history
        return {
            "relationship_level": 0,
            "relationship_type": "neutral", 
            "history": [{"action": "initial_bond", "impact": 0, "description": npc.bond}],
            "trust_level": "cautious",
            "fear_level": "none"
        }


def _set_npc_relationship(npc: models.GameEntity, relationship_data: Dict[str, Any]) -> None:
    """Helper function to save NPC relationship data to bond field"""
    npc.bond = json.dumps(relationship_data)


def _get_relationship_type(level: int) -> str:
    """Convert relationship level to descriptive type"""
    if level <= -3:
        return random.choice(["enemy", "rival", "nemesis"])
    elif level <= -1:
        return random.choice(["suspicious", "resentful", "disappointed"])
    elif level == 0:
        return random.choice(["indifferent", "professional", "cautious"])
    elif level <= 2:
        return random.choice(["respectful", "grateful", "fond"])
    else:
        return random.choice(["devoted", "loyal", "protective"])


def _get_trust_level(relationship_level: int, fear_level: str) -> str:
    """Determine trust level based on relationship and fear"""
    if fear_level in ["afraid", "terrified"]:
        return "distrustful"
    elif relationship_level <= -2:
        return "distrustful"
    elif relationship_level <= 0:
        return "cautious"
    elif relationship_level <= 2:
        return "trusting"
    else:
        return "devoted"


def update_npc_relationship(
    db: Session, 
    npc_name: str, 
    action_type: str, 
    impact: int, 
    description: str,
    fear_change: str = None
) -> Dict[str, Any]:
    """
    Updates an NPC's relationship with the player based on an action.
    
    Args:
        db: The database session.
        npc_name: The name of the NPC.
        action_type: Type of action (e.g., "gave_item", "witnessed_violence", "helped").
        impact: Relationship level change (-5 to +5).
        description: Human-readable description of what happened.
        fear_change: Optional fear level change ("increase", "decrease", "none").
        
    Returns:
        A dictionary with the updated relationship information.
    """
    npc = _find_entity_by_name(db, npc_name)
    if not npc or npc.entity_type not in ["NPC", "Character"]:
        return {"error": f"NPC '{npc_name}' not found."}
    
    # Get current relationship
    relationship = _get_npc_relationship(npc)
    
    # Update relationship level
    old_level = relationship["relationship_level"]
    new_level = max(-5, min(5, old_level + impact))
    relationship["relationship_level"] = new_level
    
    # Update relationship type
    relationship["relationship_type"] = _get_relationship_type(new_level)
    
    # Handle fear changes
    if fear_change == "increase":
        fear_levels = ["none", "wary", "afraid", "terrified"]
        current_index = fear_levels.index(relationship.get("fear_level", "none"))
        relationship["fear_level"] = fear_levels[min(3, current_index + 1)]
    elif fear_change == "decrease":
        fear_levels = ["none", "wary", "afraid", "terrified"]
        current_index = fear_levels.index(relationship.get("fear_level", "none"))
        relationship["fear_level"] = fear_levels[max(0, current_index - 1)]
    
    # Update trust level
    relationship["trust_level"] = _get_trust_level(new_level, relationship["fear_level"])
    
    # Add to history
    relationship["history"].append({
        "action": action_type,
        "impact": impact,
        "description": description,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    # Keep only last 10 history entries
    relationship["history"] = relationship["history"][-10:]
    
    # Update disposition based on relationship level
    if new_level <= -3:
        npc.disposition = "hostile"
        npc.is_hostile = True
    elif new_level <= -1:
        npc.disposition = "unfriendly"
        npc.is_hostile = False
    elif new_level <= 2:
        npc.disposition = "friendly"
        npc.is_hostile = False
    else:
        npc.disposition = "allied"
        npc.is_hostile = False
    
    # Save relationship data
    _set_npc_relationship(npc, relationship)
    db.commit()
    
    return {
        "success": True,
        "npc_name": npc.name,
        "old_level": old_level,
        "new_level": new_level,
        "relationship_type": relationship["relationship_type"],
        "trust_level": relationship["trust_level"],
        "fear_level": relationship["fear_level"],
        "disposition": npc.disposition,
        "message": f"{npc.name}'s relationship changed from {old_level} to {new_level} ({relationship['relationship_type']})"
    }


def get_npc_relationship_info(db: Session, npc_name: str) -> Dict[str, Any]:
    """
    Retrieves detailed relationship information for an NPC.
    
    Args:
        db: The database session.
        npc_name: The name of the NPC.
        
    Returns:
        A dictionary with the NPC's relationship information.
    """
    npc = _find_entity_by_name(db, npc_name)
    if not npc or npc.entity_type not in ["NPC", "Character"]:
        return {"error": f"NPC '{npc_name}' not found."}
    
    relationship = _get_npc_relationship(npc)
    
    return {
        "npc_name": npc.name,
        "relationship_level": relationship["relationship_level"],
        "relationship_type": relationship["relationship_type"],
        "trust_level": relationship["trust_level"],
        "fear_level": relationship["fear_level"],
        "disposition": npc.disposition,
        "is_hostile": npc.is_hostile,
        "recent_history": relationship["history"][-3:] if relationship["history"] else []
    }


# --- Travel & Time Advancement Tools ---


def travel_to_map_point(db: Session, character_name: str, destination_name: str) -> Dict[str, Any]:
    """
    Moves a character to a different MapPoint, advancing time based on the path's watch cost.

    Args:
        db: The database session.
        character_name: The name of the character traveling.
        destination_name: The name of the destination MapPoint.

    Returns:
        A dictionary confirming the travel and any tension escalations.
    """
    character = _find_entity_by_name(db, character_name)
    if not character:
        return {"error": f"Character '{character_name}' not found."}
    
    if not character.current_map_point:
        return {"error": f"Character '{character_name}' is not at a valid location."}
    
    # Find the destination MapPoint
    destination = (
        db.query(models.MapPoint)
        .filter(func.lower(models.MapPoint.name) == destination_name.lower())
        .first()
    )
    if not destination:
        return {"error": f"Destination '{destination_name}' not found."}
    
    # Find the path between current and destination MapPoints
    path = (
        db.query(models.Path)
        .filter(
            models.Path.start_point_id == character.current_map_point.id,
            models.Path.end_point_id == destination.id
        )
        .first()
    )
    
    if not path:
        return {"error": f"No path found from {character.current_map_point.name} to {destination_name}."}
    
    # Find the entry point location at the destination
    entry_location = (
        db.query(models.Location)
        .filter(
            models.Location.map_point_id == destination.id,
            models.Location.is_entry_point == True
        )
        .first()
    )
    
    if not entry_location:
        return {"error": f"No entry point found at {destination_name}."}
    
    # Move the character
    character.current_location_id = entry_location.id
    character.current_map_point_id = destination.id
    
    # Advance time by the path's watch cost
    condition_tracker = ConditionTracker(db)
    escalated_events = condition_tracker.advance_time(watches=path.watches)
    
    # Build response message
    message = f"{character.name} travels to {destination.name}. **Time passes: {path.watches} watch{'es' if path.watches != 1 else ''}**"
    
    # Handle tension escalations
    escalation_messages = []
    for event in escalated_events:
        if event.status == "failed":
            escalation_messages.append(f"**TENSION FAILURE:** {event.title} has spiraled out of control!")
            # Apply failure consequences
            _apply_tension_failure_consequences(db, event)
        else:
            escalation_messages.append(f"**TENSION ESCALATION:** {event.title} grows more urgent (Severity {event.severity_level})!")
    
    if escalation_messages:
        message += "\n\n" + "\n".join(escalation_messages)
    
    # Describe the new location
    look_around(db, character)
    
    return {
        "success": True,
        "message": message,
        "destination": destination.name,
        "time_advanced": path.watches,
        "escalated_events": len(escalated_events)
    }


# --- Tension Event Consequence Tools ---


def _apply_tension_failure_consequences(db: Session, failed_event: models.TensionEvent) -> None:
    """
    Apply consequences when a tension event fails completely.
    Uses LLM to intelligently select appropriate consequences.
    
    Args:
        db: The database session.
        failed_event: The tension event that failed.
    """
    # Import here to avoid circular imports
    from .llm_service import LLMService
    
    # Available consequence tools
    available_tools = [
        "spawn_hostile_entity",
        "block_location_access", 
        "create_cascading_tension_event",
        "update_npc_relationship"
    ]
    
    try:
        llm_service = LLMService()
        consequence_response = llm_service.generate_tension_failure_consequences(
            failed_event, available_tools
        )
        
        # Parse the LLM response and execute consequences
        # For now, apply a simple default consequence based on severity
        if failed_event.max_severity >= 4:
            # High severity: spawn hostile entity
            spawn_hostile_entity(
                db,
                entity_name=f"Consequence of {failed_event.title}",
                description=f"A hostile presence manifested by the failure of {failed_event.title}"
            )
        elif failed_event.max_severity >= 2:
            # Medium severity: create cascading event
            create_cascading_tension_event(
                db,
                title=f"Aftermath of {failed_event.title}",
                description=f"The failure of {failed_event.title} has created new problems.",
                source_event_id=failed_event.id,
                severity_level=1,
                deadline_watches=3
            )
        
        # Log the consequence application
        log_entry = models.LogEntry(
            source="Warden",
            content=f"**CONSEQUENCE:** The failure of '{failed_event.title}' has reshaped the world. {consequence_response}",
            metadata_dict={"failed_tension_event_id": failed_event.id}
        )
        db.add(log_entry)
        db.commit()
        
    except Exception as e:
        # Fallback if LLM fails
        print(f"Error applying tension consequences: {e}")
        log_entry = models.LogEntry(
            source="Warden",
            content=f"**CONSEQUENCE:** The failure of '{failed_event.title}' has permanent consequences for the world.",
            metadata_dict={"failed_tension_event_id": failed_event.id}
        )
        db.add(log_entry)
        db.commit()


def spawn_hostile_entity(
    db: Session, 
    entity_name: str, 
    entity_type: str = "NPC",
    location_name: str = None,
    description: str = "A hostile entity spawned by escalating tensions."
) -> Dict[str, Any]:
    """
    Creates a new hostile entity as a consequence of failed tension events.
    
    Args:
        db: The database session.
        entity_name: The name of the new hostile entity.
        entity_type: The type of entity ("NPC" or "Monster").
        location_name: The location to spawn the entity (defaults to player's location).
        description: Description of the entity.
        
    Returns:
        A dictionary confirming the entity was spawned.
    """
    # Find target location
    target_location = None
    if location_name:
        target_location = (
            db.query(models.Location)
            .filter(func.lower(models.Location.name) == location_name.lower())
            .first()
        )
    else:
        # Default to player's current location
        player = _find_entity_by_name(db, "player")
        if player:
            target_location = player.current_location
    
    if not target_location:
        return {"error": "Could not determine spawn location."}
    
    # Create the hostile entity
    new_entity = models.GameEntity(
        name=entity_name,
        entity_type=entity_type,
        hp=random.randint(3, 8),
        max_hp=random.randint(3, 8),
        strength=random.randint(8, 12),
        max_strength=random.randint(8, 12),
        dexterity=random.randint(8, 12),
        max_dexterity=random.randint(8, 12),
        willpower=random.randint(8, 12),
        max_willpower=random.randint(8, 12),
        armor=random.randint(0, 2),
        disposition="hostile",
        is_hostile=True,
        description=description,
        current_location_id=target_location.id,
        current_map_point_id=target_location.map_point_id,
        attacks='[{"name": "Attack", "damage": "1d6"}]'
    )
    
    db.add(new_entity)
    db.commit()
    
    return {
        "success": True,
        "message": f"A hostile {entity_name} has appeared at {target_location.name}!",
        "entity_name": entity_name,
        "location": target_location.name
    }


def block_location_access(db: Session, location_name: str, reason: str = "blocked by consequences") -> Dict[str, Any]:
    """
    Blocks access to a location as a consequence of failed tension events.
    
    Args:
        db: The database session.
        location_name: The name of the location to block.
        reason: The reason for blocking access.
        
    Returns:
        A dictionary confirming the location was blocked.
    """
    location = (
        db.query(models.Location)
        .filter(func.lower(models.Location.name) == location_name.lower())
        .first()
    )
    
    if not location:
        return {"error": f"Location '{location_name}' not found."}
    
    # Add a blocking description to the location
    if location.description:
        location.description += f"\n\n**BLOCKED:** {reason}"
    else:
        location.description = f"**BLOCKED:** {reason}"
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Access to {location_name} has been blocked: {reason}",
        "location": location_name
    }


def create_cascading_tension_event(
    db: Session,
    title: str,
    description: str,
    source_event_id: int,
    severity_level: int = 1,
    deadline_watches: int = 5
) -> Dict[str, Any]:
    """
    Creates a new tension event as a consequence of another event's failure.
    
    Args:
        db: The database session.
        title: The title of the new tension event.
        description: The description of the new tension event.
        source_event_id: The ID of the event that caused this one.
        severity_level: The starting severity level.
        deadline_watches: The number of watches until escalation.
        
    Returns:
        A dictionary confirming the new tension event was created.
    """
    new_event = models.TensionEvent(
        title=title,
        description=description,
        source_type="cascading_failure",
        source_data=json.dumps({"source_event_id": source_event_id}),
        severity_level=severity_level,
        max_severity=5,
        deadline_watches=deadline_watches,
        watches_remaining=deadline_watches,
        status="active"
    )
    
    db.add(new_event)
    db.commit()
    
    return {
        "success": True,
        "message": f"A new crisis has emerged: {title}",
        "event_title": title,
        "severity": severity_level
    }
