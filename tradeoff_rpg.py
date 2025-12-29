"""
Tower Climbing Roguelike
A competitive game where up to 4 players climb a 1000-floor tower using card-based builds.
"""

import random
from enum import Enum
from typing import List, Optional, Tuple


class CardType(Enum):
    """Types of cards available in the game."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    SPELL = "spell"
    PASSIVE = "passive"
    CONSUMABLE = "consumable"


class CardClass(Enum):
    """Card classifications for the deck building system."""
    STAT = "stat"  # Simple stat modifiers
    UNIQUE = "unique"  # Special mechanics
    EQUIPMENT = "equipment"  # Base attack/defense items


class WeaponType(Enum):
    """Types of weapons with different dual wielding rules."""
    SWORD = "sword"  # Can dual wield by default
    WAND = "wand"  # Can dual wield by default
    GREATSWORD = "greatsword"  # Requires Titan's Strength for dual wield
    AXE = "axe"  # Requires Titan's Strength for dual wield
    SPEAR = "spear"  # Requires Titan's Strength for dual wield
    STAFF = "staff"  # Cannot dual wield (unless special card)
    TOME = "tome"  # Arcane Tome Wielder allows up to 4
    DAGGER = "dagger"  # Cannot dual wield by default (unless special card)
    BOW = "bow"  # Cannot dual wield (unless special card)


class Card:
    """
    Cards are the core mechanic - they provide everything from weapons to stats.
    """
    def __init__(self, name: str, card_type: CardType, card_class: CardClass, description: str,
                 hp_bonus: int = 0, attack_bonus: int = 0, defense_bonus: int = 0,
                 magic_attack_bonus: int = 0, mana_bonus: int = 0, mana_regen_bonus: int = 0,
                 crit_chance_bonus: float = 0.0, crit_damage_bonus: float = 0.0,
                 dodge_chance_bonus: float = 0.0, attack_speed_bonus: float = 0.0,
                 luck_bonus: int = 0, special_effect: Optional[str] = None,
                 damage: int = 0, magic_damage: int = 0, mana_cost: int = 0,
                 weapon_type: Optional['WeaponType'] = None):
        self.name = name
        self.card_type = card_type
        self.card_class = card_class
        self.description = description
        self.weapon_type = weapon_type  # Type of weapon for dual wielding rules

        # Stat modifiers
        self.hp_bonus = hp_bonus
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.magic_attack_bonus = magic_attack_bonus
        self.mana_bonus = mana_bonus
        self.mana_regen_bonus = mana_regen_bonus
        self.crit_chance_bonus = crit_chance_bonus  # Percentage
        self.crit_damage_bonus = crit_damage_bonus  # Multiplier addition
        self.dodge_chance_bonus = dodge_chance_bonus  # Percentage
        self.attack_speed_bonus = attack_speed_bonus  # Additional attacks
        self.luck_bonus = luck_bonus

        # Special effects (to be expanded)
        self.special_effect = special_effect
        self.damage = damage  # For weapon cards
        self.magic_damage = magic_damage  # For spell cards
        self.mana_cost = mana_cost  # For spell cards

    def __str__(self):
        return f"{self.name} ({self.card_type.value}): {self.description}"


class Player:
    """
    Player class for tower climbers.
    """
    def __init__(self, name: str):
        self.name = name
        self.current_floor = 0
        self.is_alive = True
        self.escaped_floor = None  # Track which floor they escaped from

        # Base stats (will be modified by cards)
        self.base_hp = 100
        self.base_attack = 10
        self.base_defense = 5
        self.base_magic_attack = 0
        self.base_mana = 50
        self.base_mana_regen = 10
        self.base_crit_chance = 5.0  # Percentage
        self.base_crit_damage = 1.5  # Multiplier (1.5 = 150% damage)
        self.base_dodge_chance = 5.0  # Percentage
        self.base_attack_speed = 1.0  # Attacks per turn
        self.base_luck = 0  # Bonus luck stat

        # Current stats
        self.max_hp = self.base_hp
        self.current_hp = self.max_hp
        self.attack = self.base_attack
        self.defense = self.base_defense
        self.magic_attack = self.base_magic_attack
        self.max_mana = self.base_mana
        self.current_mana = self.max_mana
        self.mana_regen = self.base_mana_regen
        self.crit_chance = self.base_crit_chance
        self.crit_damage = self.base_crit_damage
        self.dodge_chance = self.base_dodge_chance
        self.attack_speed = self.base_attack_speed
        self.luck = self.base_luck

        # Combat state
        self.dodged_last_attack = False  # Track if last attack was dodged

        # Card system
        self.deck: List[Card] = []
        self.active_cards: List[Card] = []

        # Unique card special effects tracking
        self.has_unparalleled_swiftness = False
        self.has_reactive_armor = False
        self.has_lucky_7 = False
        self.has_mana_amplifier = False
        self.has_mana_conduit = False
        self.has_titans_strength = False
        self.has_arcane_tome_wielder = False
        self.has_berserkers_rage = False
        self.has_barrier = False

        # Reactive Armor state
        self.reactive_armor_active = False  # True after taking damage, gives 50% reduction on next hit

        # Lucky 7 state
        self.lucky_7_failed_crit_rolls = 0  # Count of failed crit luck rolls
        self.lucky_7_failed_dodge_rolls = 0  # Count of failed dodge luck rolls

        # Berserker's Rage state
        self.rage_stacks = 0  # Current rage stacks (max 50)

        # Barrier state
        self.shield = 0  # Current shield value

        # Battle statistics
        self.monsters_killed = 0
        self.total_damage_dealt = 0
        self.total_damage_taken = 0
        self.floors_cleared = 0
        self.total_turns_in_combat = 0
        self.crits_landed = 0
        self.dodges_made = 0

        # Leveling system
        self.level = 1
        self.current_xp = 0
        self.highest_floor = 0  # Best floor ever reached (for bonus packs)

        # Currency system
        self.bounty = 0  # Gained per monster kill, persists across runs

        # Ascension Cards (unlocked at level 10 and 20)
        self.ascension_slots = []  # List of equipped ascension card names
        self.has_ancestral_rage = False
        self.has_impaler = False
        self.has_blood_magic = False
        self.has_blind_master = False
        self.has_finishing_strike = False

        # Ancestral Rage state (different from Berserker's Rage)
        self.ancestral_rage_stacks = 0  # Rage stacks from Ancestral Rage

    def equip_deck(self, cards: List[Card]):
        """Equip cards before entering the tower."""
        self.deck = cards
        self.active_cards = cards.copy()
        self._apply_ascension_cards()

        # Validate weapon dual wielding rules
        validation_errors = self._validate_weapon_limits()
        if validation_errors:
            print("\n⚠️  DECK VALIDATION ERRORS:")
            for error in validation_errors:
                print(f"  - {error}")
            print("\nPlease adjust your deck to fix these issues.")
            raise ValueError("Deck contains invalid weapon combinations")

        self._apply_card_bonuses()

    def _apply_ascension_cards(self):
        """Detect which ascension cards are equipped."""
        self.has_ancestral_rage = "Ancestral Rage" in self.ascension_slots
        self.has_impaler = "Impaler" in self.ascension_slots
        self.has_blood_magic = "Blood Magic" in self.ascension_slots
        self.has_blind_master = "Blind Master" in self.ascension_slots
        self.has_finishing_strike = "Finishing Strike" in self.ascension_slots

    def _validate_weapon_limits(self) -> List[str]:
        """
        Validate weapon dual wielding rules.
        Returns a list of error messages if validation fails.
        """
        errors = []

        # Check for Titan's Strength unique card
        has_titans_strength = any(c.special_effect == "titans_strength" for c in self.active_cards)

        # Count weapons by type
        weapon_counts = {}
        for card in self.active_cards:
            if card.card_type == CardType.WEAPON and card.weapon_type:
                weapon_type = card.weapon_type
                weapon_counts[weapon_type] = weapon_counts.get(weapon_type, 0) + 1

        # Validate each weapon type
        for weapon_type, count in weapon_counts.items():
            if count <= 1:
                continue  # Single weapon is always OK

            # Check dual wielding rules
            if weapon_type in [WeaponType.SWORD, WeaponType.WAND]:
                # Swords and Wands can always be dual wielded
                if count > 2:
                    errors.append(f"Cannot equip more than 2 {weapon_type.value}s (found {count})")

            elif weapon_type in [WeaponType.GREATSWORD, WeaponType.AXE, WeaponType.SPEAR]:
                # These require Titan's Strength for dual wielding
                if not has_titans_strength:
                    errors.append(
                        f"Cannot dual wield {weapon_type.value}s without 'Titan's Strength' unique card (found {count})"
                    )
                elif count > 2:
                    errors.append(f"Cannot equip more than 2 {weapon_type.value}s even with Titan's Strength (found {count})")

            elif weapon_type == WeaponType.TOME:
                # Tome has special handling via Arcane Tome Wielder (allows up to 4)
                # This is validated elsewhere, but we'll allow it here
                pass

            else:
                # Other weapon types (Staff, Dagger, Bow) cannot be dual wielded without special cards
                errors.append(
                    f"Cannot dual wield {weapon_type.value}s - only 1 allowed (found {count})"
                )

        return errors

    def _apply_card_bonuses(self):
        """Apply all stat bonuses from equipped cards, including unique card effects."""
        # First, detect which unique cards are equipped
        self.has_unparalleled_swiftness = any(c.special_effect == "unparalleled_swiftness" for c in self.active_cards)
        self.has_reactive_armor = any(c.special_effect == "reactive_armor" for c in self.active_cards)
        self.has_lucky_7 = any(c.special_effect == "lucky_7" for c in self.active_cards)
        self.has_mana_amplifier = any(c.special_effect == "mana_amplifier" for c in self.active_cards)
        self.has_mana_conduit = any(c.special_effect == "mana_conduit" for c in self.active_cards)
        self.has_titans_strength = any(c.special_effect == "titans_strength" for c in self.active_cards)
        self.has_arcane_tome_wielder = any(c.special_effect == "arcane_tome_wielder" for c in self.active_cards)
        self.has_berserkers_rage = any(c.special_effect == "berserkers_rage" for c in self.active_cards)
        self.has_barrier = any(c.special_effect == "barrier" for c in self.active_cards)

        # Calculate base bonuses (excluding unique cards with special mechanics)
        total_hp_bonus = sum(card.hp_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_attack_bonus = sum(card.attack_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_defense_bonus = sum(card.defense_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_magic_attack_bonus = sum(card.magic_attack_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_mana_bonus = sum(card.mana_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_mana_regen_bonus = sum(card.mana_regen_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_crit_chance_bonus = sum(card.crit_chance_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_crit_damage_bonus = sum(card.crit_damage_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_dodge_chance_bonus = sum(card.dodge_chance_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_attack_speed_bonus = sum(card.attack_speed_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)
        total_luck_bonus = sum(card.luck_bonus for card in self.active_cards if card.card_class != CardClass.UNIQUE)

        # Apply base stats
        self.max_hp = self.base_hp + total_hp_bonus
        self.attack = self.base_attack + total_attack_bonus
        self.defense = self.base_defense + total_defense_bonus
        self.magic_attack = self.base_magic_attack + total_magic_attack_bonus
        self.max_mana = self.base_mana + total_mana_bonus
        self.mana_regen = self.base_mana_regen + total_mana_regen_bonus
        self.crit_chance = self.base_crit_chance + total_crit_chance_bonus
        self.crit_damage = self.base_crit_damage + total_crit_damage_bonus
        self.dodge_chance = self.base_dodge_chance + total_dodge_chance_bonus
        self.attack_speed = self.base_attack_speed + total_attack_speed_bonus
        self.luck = self.base_luck + total_luck_bonus

        # Apply unique card effects
        # Unparalleled Swiftness: -30% damage, -30% magic damage, +3 attack speed
        if self.has_unparalleled_swiftness:
            self.attack = int(self.attack * 0.7)
            self.magic_attack = int(self.magic_attack * 0.7)
            self.attack_speed += 3.0

        # Reactive Armor: -90% magic damage
        if self.has_reactive_armor:
            self.magic_attack = int(self.magic_attack * 0.1)

        # Mana Conduit: -100% attack, +25% max mana regen
        if self.has_mana_conduit:
            self.attack = 0
            self.mana_regen += int(self.max_mana * 0.25)

        # Titan's Strength: halve attack speed bonuses (only the bonus part, not base)
        if self.has_titans_strength:
            bonus_speed = self.attack_speed - self.base_attack_speed
            self.attack_speed = self.base_attack_speed + (bonus_speed * 0.5)

        # Arcane Tome Wielder: -100% attack, +25% magic attack per tome equipped
        if self.has_arcane_tome_wielder:
            self.attack = 0
            num_tomes = sum(1 for card in self.active_cards if card.name == "Tome")
            # Ensure max 4 tomes count (validation should be done elsewhere)
            num_tomes = min(num_tomes, 4)
            self.magic_attack = int(self.magic_attack * (1.0 + 0.25 * num_tomes))

        # Berserker's Rage: -50 HP penalty (already applied via hp_bonus in card)
        # Rage stacking is handled dynamically in combat

        # Apply Ascension Card effects
        # Blind Master: +100% dodge chance, cannot deal critical hits
        if self.has_blind_master:
            self.dodge_chance += 100.0
            self.crit_chance = 0.0

        self.current_hp = min(self.current_hp, self.max_hp)
        self.current_mana = min(self.current_mana, self.max_mana)

    def take_damage(self, damage: int, silent: bool = False) -> bool:
        """
        Take damage and check if player needs to escape.
        Returns True if player escaped (hit 1 HP).
        Handles Reactive Armor and Barrier unique card effects.
        """
        actual_damage = max(1, damage - self.defense)

        # Reactive Armor: Apply 50% reduction if active
        if self.has_reactive_armor and self.reactive_armor_active:
            actual_damage = int(actual_damage * 0.5)
            self.reactive_armor_active = False  # Consumed the protection
            if not silent:
                print(f"  🛡️ Reactive Armor reduces damage by 50%!")

        # Barrier: Shield absorbs damage first
        if self.shield > 0:
            if self.shield >= actual_damage:
                self.shield -= actual_damage
                if not silent:
                    print(f"  🛡️ Shield absorbed {actual_damage} damage! ({self.shield} shield remaining)")
                actual_damage = 0
            else:
                remaining_damage = actual_damage - self.shield
                if not silent:
                    print(f"  🛡️ Shield absorbed {self.shield} damage! Shield broken!")
                self.shield = 0
                actual_damage = remaining_damage

        # Apply damage to HP
        if actual_damage > 0:
            self.current_hp -= actual_damage
            self.total_damage_taken += actual_damage

        # Reactive Armor: Activate for next hit (if we have the card and took damage)
        if self.has_reactive_armor and actual_damage > 0:
            self.reactive_armor_active = True

        if self.current_hp <= 1:
            self.current_hp = 1
            self.escaped_floor = self.current_floor
            self.is_alive = False  # Functionally out of the competition
            return True
        return False

    def heal(self, amount: int):
        """Heal the player."""
        self.current_hp = min(self.current_hp + amount, self.max_hp)

    def get_weapon_damage(self) -> int:
        """Calculate total damage from weapon cards and rage bonus."""
        weapon_damage = sum(card.damage for card in self.active_cards
                          if card.card_type == CardType.WEAPON)
        rage_bonus = self.rage_stacks * 5 if self.has_berserkers_rage else 0

        # Ancestral Rage: bonus from stacks
        ancestral_rage_bonus = self.ancestral_rage_stacks * 5 if self.has_ancestral_rage else 0

        return self.attack + weapon_damage + rage_bonus + ancestral_rage_bonus

    def get_attack_speed(self) -> float:
        """Calculate attack speed including Ancestral Rage bonus."""
        speed = self.attack_speed

        # Ancestral Rage: +0.1 speed per 5 stacks
        if self.has_ancestral_rage:
            speed += (self.ancestral_rage_stacks // 5) * 0.1

        return speed

    def regenerate_mana(self):
        """Regenerate mana at the start of each turn."""
        self.current_mana = min(self.current_mana + self.mana_regen, self.max_mana)

    def can_dodge(self, silent: bool = False) -> bool:
        """Check if player can dodge (can't dodge twice in a row). Handles Lucky 7."""
        if self.dodged_last_attack:
            return False

        # Lucky 7: Check if we should guarantee the luck roll
        lucky_7_guaranteed = False
        if self.has_lucky_7 and self.lucky_7_failed_dodge_rolls >= 7:
            lucky_7_guaranteed = True
            self.lucky_7_failed_dodge_rolls = 0  # Reset counter
            if not silent:
                print(f"  🎰 Lucky 7 activates! Luck roll guaranteed!")

        # Use luck to potentially roll twice
        luck_triggered = False
        if self.luck > 0:
            if lucky_7_guaranteed:
                luck_triggered = True
            else:
                luck_roll = random.randint(1, 100)
                luck_triggered = luck_roll <= self.luck

                # Track failed luck rolls for Lucky 7
                if not luck_triggered and self.has_lucky_7:
                    self.lucky_7_failed_dodge_rolls += 1

        if luck_triggered:
            # Roll twice, take the better result
            roll1 = random.randint(1, 100)
            roll2 = random.randint(1, 100)
            success = max(roll1, roll2) <= self.dodge_chance
        else:
            success = random.randint(1, 100) <= self.dodge_chance

        self.dodged_last_attack = success
        if success:
            self.dodges_made += 1
        return success

    def calculate_damage(self, base_damage: int, silent: bool = False) -> Tuple[int, bool]:
        """
        Calculate damage with crit chance. Handles Lucky 7.
        Returns (damage, is_crit).
        """
        # Lucky 7: Check if we should guarantee the luck roll
        lucky_7_guaranteed = False
        if self.has_lucky_7 and self.lucky_7_failed_crit_rolls >= 7:
            lucky_7_guaranteed = True
            self.lucky_7_failed_crit_rolls = 0  # Reset counter
            if not silent:
                print(f"  🎰 Lucky 7 activates! Luck roll guaranteed!")

        # Check for crit with luck
        is_crit = False
        luck_triggered = False
        if self.luck > 0:
            if lucky_7_guaranteed:
                luck_triggered = True
            else:
                luck_roll = random.randint(1, 100)
                luck_triggered = luck_roll <= self.luck

                # Track failed luck rolls for Lucky 7
                if not luck_triggered and self.has_lucky_7:
                    self.lucky_7_failed_crit_rolls += 1

        if luck_triggered:
            # Roll twice, take the better result (min for crit because lower is better)
            roll1 = random.randint(1, 100)
            roll2 = random.randint(1, 100)
            is_crit = min(roll1, roll2) <= self.crit_chance
        else:
            is_crit = random.randint(1, 100) <= self.crit_chance

        if is_crit:
            self.crits_landed += 1
            return int(base_damage * self.crit_damage), True
        return base_damage, False

    def reset_for_floor(self):
        """Reset stats for a new floor (heal between floors for now)."""
        self.current_hp = self.max_hp
        self.current_mana = self.max_mana
        self.dodged_last_attack = False
        self.reactive_armor_active = False  # Reset Reactive Armor between floors
        self.rage_stacks = 0  # Reset Berserker's Rage stacks between floors
        self.shield = 0  # Reset Barrier shield between floors
        self.ancestral_rage_stacks = 0  # Reset Ancestral Rage stacks between floors

    def get_xp_for_next_level(self) -> int:
        """Calculate XP required to reach the next level."""
        # Formula: level*level*1000 + (level//10*10000)
        return self.level * self.level * 1000 + (self.level // 10 * 10000)

    def get_xp_from_floor(self, floor: int) -> int:
        """Calculate XP gained from completing a floor."""
        # Floor 1 = 100 XP, each floor after +10%
        # floor 1: 100
        # floor 2: 100 * 1.1 = 110
        # floor 3: 100 * 1.1^2 = 121
        return int(100 * (1.1 ** (floor - 1)))

    def get_floor_bonus_packs(self) -> int:
        """Calculate bonus packs from highest floor reached."""
        # +1 pack per 50 floors (floor 100 = +2, floor 500 = +10)
        return self.highest_floor // 50

    def get_max_packs(self) -> int:
        """Calculate max packs player can open based on level and highest floor."""
        # Base packs from level
        if self.level < 20:
            base_packs = 9 + self.level  # Level 1 = 10, Level 2 = 11, etc.
        else:
            base_packs = 30  # Level 20 = 30 (gets +2 instead of +1)

        # Add bonus from highest floor
        floor_bonus = self.get_floor_bonus_packs()

        return base_packs + floor_bonus

    def gain_xp(self, floor: int, silent: bool = False) -> bool:
        """
        Gain XP from completing a floor and level up if applicable.
        Returns True if player leveled up.
        """
        xp_gained = self.get_xp_from_floor(floor)
        self.current_xp += xp_gained

        if not silent:
            print(f"  📈 {self.name} gained {xp_gained} XP! ({self.current_xp}/{self.get_xp_for_next_level()})")

        # Check for level ups (can level up multiple times if enough XP)
        leveled_up = False
        while self.level < 20 and self.current_xp >= self.get_xp_for_next_level():
            self.current_xp -= self.get_xp_for_next_level()
            old_level = self.level
            self.level += 1
            leveled_up = True

            # Calculate pack increase
            if self.level == 20:
                pack_increase = 2  # Level 20 gives +2
            else:
                pack_increase = 1  # Other levels give +1

            new_max_packs = self.get_max_packs()

            if not silent:
                print(f"  🎉 LEVEL UP! {self.name} reached level {self.level}!")
                print(f"  📦 Max packs increased by +{pack_increase}! (Next run: {new_max_packs} packs)")

                # Check for ascension card unlock
                if self.level == 10:
                    print(f"  🌟 ASCENSION CARD SLOT 1 UNLOCKED! Choose your first ascension card next run!")
                elif self.level == 20:
                    print(f"  🌟 ASCENSION CARD SLOT 2 UNLOCKED! Choose your second ascension card next run!")

        return leveled_up

    def gain_bounty(self, amount: int = 1, silent: bool = False):
        """Gain bounty from killing a monster."""
        self.bounty += amount
        if not silent:
            print(f"  💰 +{amount} Bounty! (Total: {self.bounty})")

    def __str__(self):
        status = "ESCAPED" if not self.is_alive else "CLIMBING"
        return f"{self.name} - Floor {self.current_floor} [{status}] HP: {self.current_hp}/{self.max_hp}"


class EnemyType(Enum):
    """Different enemy types with different scaling patterns."""
    GOBLIN = "Goblin"
    SKELETON = "Skeleton"
    SLIME = "Slime"
    WRAITH = "Wraith"
    DRAGON = "Dragon"
    GOLEM = "Golem"
    DEMON = "Demon"
    VAMPIRE = "Vampire"
    MAGE = "Mage"
    WARLOCK = "Warlock"
    SORCERER = "Sorcerer"


class Enemy:
    """
    Enemy class with floor-based scaling.
    """
    def __init__(self, floor: int, enemy_type: Optional[EnemyType] = None):
        self.floor = floor
        self.enemy_type = enemy_type or random.choice(list(EnemyType))
        self.name = self._generate_name()

        # Scale stats based on floor
        self.max_hp = self._scale_hp(floor)
        self.current_hp = self.max_hp
        self.attack = self._scale_attack(floor)
        self.defense = self._scale_defense(floor)
        self.magic_attack = self._scale_magic_attack(floor)
        self.max_mana = self._scale_mana(floor)
        self.current_mana = self.max_mana
        self.mana_regen = self._scale_mana_regen(floor)
        self.crit_chance = self._scale_crit_chance(floor)
        self.crit_damage = self._scale_crit_damage(floor)
        self.dodge_chance = self._scale_dodge_chance(floor)
        self.attack_speed = self._scale_attack_speed(floor)
        self.luck = self._scale_luck(floor)

        # Combat state
        self.dodged_last_attack = False
        self.impaled = False  # Impale status from Impaler ascension card

    def _generate_name(self) -> str:
        """Generate enemy name based on floor and type."""
        prefixes = ["Lesser", "Common", "Greater", "Elite", "Ancient", "Legendary"]
        floor_tier = min(self.floor // 200, len(prefixes) - 1)
        prefix = prefixes[floor_tier]
        return f"{prefix} {self.enemy_type.value}"

    def _scale_hp(self, floor: int) -> int:
        """Scale HP based on floor number."""
        base = 50
        scaling_factor = {
            EnemyType.SLIME: 1.2,      # High HP
            EnemyType.GOLEM: 1.5,      # Very high HP
            EnemyType.GOBLIN: 0.8,     # Low HP
            EnemyType.WRAITH: 0.9,     # Medium-low HP
            EnemyType.SKELETON: 1.0,   # Medium HP
            EnemyType.VAMPIRE: 1.1,    # Medium-high HP
            EnemyType.DEMON: 1.0,      # Medium HP
            EnemyType.DRAGON: 1.3,     # High HP
            EnemyType.MAGE: 0.7,       # Low HP (glass cannon)
            EnemyType.WARLOCK: 0.8,    # Low HP
            EnemyType.SORCERER: 0.75,  # Low HP
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return int(base * factor + (floor * 2.5 * factor))

    def _scale_attack(self, floor: int) -> int:
        """Scale physical attack based on floor number."""
        base = 8
        scaling_factor = {
            EnemyType.DEMON: 1.4,      # Very high attack
            EnemyType.DRAGON: 1.3,     # High attack
            EnemyType.VAMPIRE: 1.2,    # Medium-high attack
            EnemyType.GOBLIN: 1.1,     # Medium attack
            EnemyType.SKELETON: 1.0,   # Medium attack
            EnemyType.WRAITH: 1.1,     # Medium attack
            EnemyType.SLIME: 0.7,      # Low attack
            EnemyType.GOLEM: 0.8,      # Low attack
            EnemyType.MAGE: 0.5,       # Very low physical attack (magic users)
            EnemyType.WARLOCK: 0.4,    # Very low physical attack
            EnemyType.SORCERER: 0.3,   # Very low physical attack
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return int(base * factor + (floor * 1.2 * factor))

    def _scale_defense(self, floor: int) -> int:
        """Scale defense based on floor number."""
        base = 3
        scaling_factor = {
            EnemyType.GOLEM: 1.8,      # Very high defense
            EnemyType.DRAGON: 1.4,     # High defense
            EnemyType.SKELETON: 1.2,   # Medium-high defense
            EnemyType.DEMON: 1.1,      # Medium defense
            EnemyType.VAMPIRE: 1.0,    # Medium defense
            EnemyType.SLIME: 0.8,      # Low defense
            EnemyType.GOBLIN: 0.6,     # Very low defense
            EnemyType.WRAITH: 0.5,     # Very low defense
            EnemyType.MAGE: 0.4,       # Very low defense (glass cannon)
            EnemyType.WARLOCK: 0.5,    # Very low defense
            EnemyType.SORCERER: 0.4,   # Very low defense
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return int(base * factor + (floor * 0.8 * factor))

    def _scale_magic_attack(self, floor: int) -> int:
        """Scale magic attack based on floor number."""
        base = 10
        scaling_factor = {
            EnemyType.SORCERER: 1.5,   # Very high magic attack
            EnemyType.WARLOCK: 1.4,    # High magic attack
            EnemyType.MAGE: 1.3,       # High magic attack
            EnemyType.DEMON: 1.1,      # Medium magic attack
            EnemyType.DRAGON: 1.0,     # Medium magic attack
            EnemyType.WRAITH: 0.9,     # Low magic attack
            EnemyType.VAMPIRE: 0.5,    # Very low magic attack
            # Others have negligible magic attack
        }
        factor = scaling_factor.get(self.enemy_type, 0.0)
        return int(base * factor + (floor * 1.5 * factor))

    def _scale_mana(self, floor: int) -> int:
        """Scale max mana based on floor number."""
        base = 100
        scaling_factor = {
            EnemyType.SORCERER: 1.3,
            EnemyType.WARLOCK: 1.2,
            EnemyType.MAGE: 1.1,
            EnemyType.DEMON: 0.8,
            EnemyType.WRAITH: 0.6,
        }
        factor = scaling_factor.get(self.enemy_type, 0.0)
        return int(base * factor + (floor * 1.0 * factor))

    def _scale_mana_regen(self, floor: int) -> int:
        """Scale mana regen based on floor number."""
        base = 15
        scaling_factor = {
            EnemyType.SORCERER: 1.2,
            EnemyType.WARLOCK: 1.1,
            EnemyType.MAGE: 1.0,
            EnemyType.DEMON: 0.7,
            EnemyType.WRAITH: 0.5,
        }
        factor = scaling_factor.get(self.enemy_type, 0.0)
        return int(base * factor + (floor * 0.3 * factor))

    def _scale_crit_chance(self, floor: int) -> float:
        """Scale crit chance based on floor number."""
        base = 5.0
        scaling_factor = {
            EnemyType.VAMPIRE: 1.8,    # Very high crit
            EnemyType.DEMON: 1.5,      # High crit
            EnemyType.GOBLIN: 1.3,     # Medium-high crit
            EnemyType.WRAITH: 1.2,     # Medium crit
            EnemyType.SORCERER: 1.1,   # Medium crit
            EnemyType.GOLEM: 0.3,      # Very low crit
            EnemyType.SLIME: 0.5,      # Low crit
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return min(50.0, base * factor + (floor * 0.05 * factor))  # Cap at 50%

    def _scale_crit_damage(self, floor: int) -> float:
        """Scale crit damage multiplier based on floor number."""
        base = 1.5
        scaling_factor = {
            EnemyType.VAMPIRE: 1.4,
            EnemyType.DEMON: 1.3,
            EnemyType.DRAGON: 1.2,
            EnemyType.SORCERER: 1.2,
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return base * factor + (floor * 0.001 * factor)  # Slow scaling

    def _scale_dodge_chance(self, floor: int) -> float:
        """Scale dodge chance based on floor number."""
        base = 3.0
        scaling_factor = {
            EnemyType.WRAITH: 2.0,     # Very high dodge
            EnemyType.GOBLIN: 1.5,     # High dodge
            EnemyType.VAMPIRE: 1.3,    # Medium-high dodge
            EnemyType.MAGE: 1.2,       # Medium dodge
            EnemyType.GOLEM: 0.2,      # Very low dodge
            EnemyType.DRAGON: 0.3,     # Very low dodge
            EnemyType.SLIME: 0.4,      # Low dodge
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return min(40.0, base * factor + (floor * 0.04 * factor))  # Cap at 40%

    def _scale_attack_speed(self, floor: int) -> float:
        """Scale attack speed based on floor number."""
        base = 1.0
        scaling_factor = {
            EnemyType.GOBLIN: 1.3,     # Fast attacks
            EnemyType.VAMPIRE: 1.2,    # Fast attacks
            EnemyType.WRAITH: 1.2,     # Fast attacks
            EnemyType.GOLEM: 0.7,      # Slow attacks
            EnemyType.DRAGON: 0.8,     # Slow attacks
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return base * factor + (floor * 0.001 * factor)  # Very slow scaling

    def _scale_luck(self, floor: int) -> int:
        """Scale luck based on floor number."""
        base = 0
        scaling_factor = {
            EnemyType.GOBLIN: 1.5,
            EnemyType.VAMPIRE: 1.2,
            EnemyType.DEMON: 1.0,
        }
        factor = scaling_factor.get(self.enemy_type, 0.0)
        return int(base + (floor * 0.02 * factor))

    def regenerate_mana(self):
        """Regenerate mana at the start of each turn."""
        if self.max_mana > 0:
            self.current_mana = min(self.current_mana + self.mana_regen, self.max_mana)

    def can_dodge(self, silent: bool = False) -> bool:
        """Check if enemy can dodge (can't dodge twice in a row)."""
        if self.dodged_last_attack:
            return False

        # Use luck to potentially roll twice
        if self.luck > 0 and random.randint(1, 100) <= self.luck:
            roll1 = random.randint(1, 100)
            roll2 = random.randint(1, 100)
            success = max(roll1, roll2) <= self.dodge_chance
        else:
            success = random.randint(1, 100) <= self.dodge_chance

        self.dodged_last_attack = success
        return success

    def calculate_damage(self, base_damage: int) -> Tuple[int, bool]:
        """
        Calculate damage with crit chance.
        Returns (damage, is_crit).
        """
        is_crit = False
        if self.luck > 0 and random.randint(1, 100) <= self.luck:
            roll1 = random.randint(1, 100)
            roll2 = random.randint(1, 100)
            is_crit = min(roll1, roll2) <= self.crit_chance
        else:
            is_crit = random.randint(1, 100) <= self.crit_chance

        if is_crit:
            return int(base_damage * self.crit_damage), True
        return base_damage, False

    def take_damage(self, damage: int) -> bool:
        """
        Enemy takes damage.
        Returns True if enemy is defeated.
        """
        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage
        return self.current_hp <= 0

    def __str__(self):
        parts = [f"{self.name}", f"HP: {self.current_hp}/{self.max_hp}"]
        if self.attack > 0:
            parts.append(f"ATK: {self.attack}")
        if self.magic_attack > 0:
            parts.append(f"MAG: {self.magic_attack}")
        if self.defense > 0:
            parts.append(f"DEF: {self.defense}")
        return " - ".join(parts)


class Tower:
    """
    The tower - 1000 floors of challenge.
    """
    MAX_FLOORS = 1000

    def __init__(self):
        self.current_floor = 0

    def generate_enemy(self, floor: int) -> Enemy:
        """Generate an enemy for the given floor."""
        return Enemy(floor)

    def generate_enemies(self, floor: int) -> List[Enemy]:
        """Generate multiple enemies for a floor (scales with floor number)."""
        # More enemies on higher floors
        num_enemies = 1 + (floor // 100)  # 1 enemy base, +1 every 100 floors
        num_enemies = min(num_enemies, 5)  # Cap at 5 enemies

        return [self.generate_enemy(floor) for _ in range(num_enemies)]


class Combat:
    """
    Combat system for player vs enemies with full RPG mechanics.
    """
    @staticmethod
    def _perform_attack(attacker, defender, damage: int, attack_type: str = "physical", silent: bool = False) -> Tuple[bool, int, bool]:
        """
        Perform a single attack with dodge and crit mechanics.
        Returns (defender_defeated, actual_damage_dealt, is_crit).
        """
        attacker_name = attacker.name if hasattr(attacker, 'name') else str(attacker)
        defender_name = defender.name if hasattr(defender, 'name') else str(defender)

        # Check if defender dodges
        dodged = defender.can_dodge(silent=silent)

        if dodged:
            if not silent:
                print(f"  💨 {defender_name} DODGED the attack!")
            return False, 0, False

        # If attack wasn't dodged, reset the dodge flag
        defender.dodged_last_attack = False

        # Calculate damage with crit
        # Player has silent parameter, Enemy doesn't
        if hasattr(attacker, 'total_damage_dealt'):
            final_damage, is_crit = attacker.calculate_damage(damage, silent=silent)
        else:
            final_damage, is_crit = attacker.calculate_damage(damage)

        # Display attack
        if not silent:
            crit_marker = " 💥 CRITICAL HIT!" if is_crit else ""
            type_marker = "⚡" if attack_type == "magic" else "⚔️"
            print(f"  {type_marker} {attacker_name} attacks {defender_name} for {final_damage} damage!{crit_marker}")

        # Track damage dealt for players
        if hasattr(attacker, 'total_damage_dealt'):
            attacker.total_damage_dealt += final_damage

        # Apply damage
        # Player has silent parameter, Enemy doesn't
        if hasattr(defender, 'total_damage_taken'):
            defeated = defender.take_damage(final_damage, silent=silent)
        else:
            defeated = defender.take_damage(final_damage)

        return defeated, final_damage, is_crit

    @staticmethod
    def battle(player: Player, enemies: List[Enemy], silent: bool = False) -> bool:
        """
        Execute combat between player and enemies.
        Returns True if player wins, False if player escaped.
        """
        # Barrier: Initialize shield at battle start
        if player.has_barrier:
            player.shield = int(player.magic_attack * 0.5)
            if not silent and player.shield > 0:
                print(f"  🛡️ Barrier activates! Shield: {player.shield}")

        if not silent:
            print(f"\n{'='*60}")
            print(f"FLOOR {player.current_floor} - BATTLE START!")
            print(f"{'='*60}")
            shield_str = f", Shield: {player.shield}" if player.shield > 0 else ""
            print(f"{player.name}: {player.current_hp}/{player.max_hp} HP, {player.current_mana}/{player.max_mana} MP{shield_str}")
            for i, enemy in enumerate(enemies, 1):
                print(f"  Enemy {i}: {enemy}")
            print()

        turn = 0
        while enemies and player.is_alive:
            turn += 1
            player.total_turns_in_combat += 1
            if not silent:
                print(f"--- Turn {turn} ---")

            # Regenerate mana
            player.regenerate_mana()
            for enemy in enemies:
                enemy.regenerate_mana()

            # Player turn - attack speed determines number of attacks
            player_speed = player.get_attack_speed()
            num_attacks = int(player_speed)
            has_partial_attack = (player_speed % 1) > 0

            # If there's a fractional part, check if we get a bonus attack
            if has_partial_attack and random.random() < (player_speed % 1):
                num_attacks += 1

            for attack_num in range(num_attacks):
                if not enemies:
                    break

                target = enemies[0]

                # Initialize variables
                attack_type = "physical"  # Default
                defeated = False
                damage_dealt = 0

                # Finishing Strike: Instant kill if enemy below 10% HP
                if player.has_finishing_strike and target.current_hp <= target.max_hp * 0.1:
                    if not silent:
                        print(f"  💀 Finishing Strike! {target.name} is below 10% HP - instant kill!")
                    target.current_hp = 0
                    defeated = True
                    damage_dealt = 0
                else:
                    # Mana Amplifier: Special attack mechanic
                    if player.has_mana_amplifier:
                        mana_cost = int(player.max_mana * 0.5)
                        if player.current_mana >= mana_cost:
                            damage = player.magic_attack * 3
                            player.current_mana -= mana_cost
                            attack_type = "magic"
                            if not silent:
                                print(f"  ⚡ Mana Amplifier: Consuming {mana_cost} mana for 3x magic damage!")
                        else:
                            # Blood Magic: Use HP as mana if we have it
                            if player.has_blood_magic and player.current_hp > 1:
                                hp_cost = mana_cost - player.current_mana
                                if player.current_hp - hp_cost > 1:
                                    # Use remaining mana + HP
                                    hp_to_use = hp_cost
                                    player.current_mana = 0
                                    player.current_hp -= hp_to_use
                                    damage = player.magic_attack * 3
                                    attack_type = "magic"
                                    if not silent:
                                        print(f"  🩸 Blood Magic! Using {hp_to_use} HP as mana!")
                                        print(f"  ⚡ Mana Amplifier: Consuming mana for 3x magic damage!")
                                else:
                                    # Not enough HP+mana for Mana Amplifier, skip attack
                                    if not silent:
                                        print(f"  ⚠️ Not enough mana/HP for Mana Amplifier!")
                                    continue
                            else:
                                # Not enough mana for Mana Amplifier, skip attack
                                if not silent:
                                    print(f"  ⚠️ Not enough mana for Mana Amplifier! ({player.current_mana}/{mana_cost})")
                                continue
                    else:
                        # Normal attack logic
                        # Decide between physical and magic attack
                        # Use magic if we have mana and magic attack is higher
                        use_magic = (player.magic_attack > 0 and
                                   player.current_mana >= 20 and
                                   player.magic_attack > player.get_weapon_damage())

                        # Blood Magic: Use HP if out of mana
                        if use_magic and player.current_mana < 20:
                            if player.has_blood_magic and player.current_hp > 1:
                                hp_cost = 20 - player.current_mana
                                if player.current_hp - hp_cost > 1:
                                    # Use remaining mana + HP
                                    hp_to_use = hp_cost
                                    player.current_mana = 0
                                    player.current_hp -= hp_to_use
                                    damage = player.magic_attack
                                    attack_type = "magic"
                                    if not silent:
                                        print(f"  🩸 Blood Magic! Using {hp_to_use} HP as mana!")
                                else:
                                    # Not enough HP, fall back to physical
                                    use_magic = False

                        if use_magic and player.current_mana >= 20:
                            damage = player.magic_attack
                            player.current_mana -= 20
                            attack_type = "magic"
                        else:
                            damage = player.get_weapon_damage()
                            attack_type = "physical"

                    # Check for Impale from previous crit
                    impale_damage = 0
                    if player.has_impaler and target.impaled:
                        impale_damage = int(damage * 0.7)
                        target.impaled = False  # Consume impale
                        if not silent:
                            print(f"  🗡️ Impale triggers! Additional hit for {impale_damage} damage (70% of main hit)")

                    defeated, damage_dealt, is_crit = Combat._perform_attack(player, target, damage, attack_type, silent=silent)

                    # Apply impale damage if the enemy survived the main hit
                    if impale_damage > 0 and not defeated:
                        actual_impale_damage = max(1, impale_damage - target.defense)
                        target.current_hp -= actual_impale_damage
                        player.total_damage_dealt += actual_impale_damage
                        if not silent:
                            print(f"  🗡️ Impale deals {actual_impale_damage} damage!")
                        if target.current_hp <= 0:
                            defeated = True

                    # Impaler: Apply impale on crit (for next hit)
                    if player.has_impaler and is_crit and not defeated:
                        target.impaled = True
                        if not silent:
                            print(f"  🗡️ Impale applied! Next hit will deal +70% damage")

                # Berserker's Rage: Gain rage on successful physical hit
                if player.has_berserkers_rage and attack_type == "physical" and damage_dealt > 0:
                    if player.rage_stacks < 50:
                        player.rage_stacks += 1
                        if not silent:
                            print(f"  🔥 Rage +1! (Rage: {player.rage_stacks}/50, Bonus: +{player.rage_stacks * 5} Attack)")

                # Ancestral Rage: Gain rage on successful physical hit
                if player.has_ancestral_rage and attack_type == "physical" and damage_dealt > 0:
                    if player.ancestral_rage_stacks < 50:
                        player.ancestral_rage_stacks += 1
                        speed_bonus = (player.ancestral_rage_stacks // 5) * 0.1
                        if not silent:
                            print(f"  ⚡ Ancestral Rage +1! (Stacks: {player.ancestral_rage_stacks}/50, +{player.ancestral_rage_stacks * 5} Attack, +{speed_bonus:.1f} Speed)")

                if defeated:
                    if not silent:
                        print(f"  ✓ {target.name} defeated!")
                    player.monsters_killed += 1
                    player.gain_bounty(1, silent=silent)  # Gain 1 bounty per monster kill
                    enemies.pop(0)
                    if not enemies:
                        if not silent:
                            print(f"\n🎉 {player.name} wins the battle!")
                        player.floors_cleared += 1
                        return True

            # Enemies turn
            for enemy in enemies[:]:  # Copy list since we might remove enemies
                # Each enemy gets attacks based on their attack speed
                num_attacks = int(enemy.attack_speed)
                has_partial_attack = (enemy.attack_speed % 1) > 0

                if has_partial_attack and random.random() < (enemy.attack_speed % 1):
                    num_attacks += 1

                for attack_num in range(num_attacks):
                    # Decide between physical and magic attack
                    use_magic = (enemy.magic_attack > 0 and
                               enemy.current_mana >= 20 and
                               enemy.magic_attack > enemy.attack)

                    if use_magic:
                        damage = enemy.magic_attack
                        enemy.current_mana -= 20
                        attack_type = "magic"
                    else:
                        damage = enemy.attack
                        attack_type = "physical"

                    defeated, damage_dealt, _ = Combat._perform_attack(enemy, player, damage, attack_type, silent=silent)
                    if defeated:
                        if not silent:
                            print(f"\n💀 {player.name} HP dropped to 1! AUTO-ESCAPE activated!")
                            print(f"🏃 {player.name} escaped from floor {player.current_floor}.")
                        return False

            if not silent:
                print(f"📊 {player.name}: {player.current_hp}/{player.max_hp} HP, {player.current_mana}/{player.max_mana} MP\n")

        return True


def create_stat_card_pool() -> List[Card]:
    """
    Create a pool of stat cards with 4 levels each.
    20 different stat types × 4 levels = 80 total cards.
    """
    cards = []

    # Original 10 stat types - 4 levels each

    # 1. Vitality (HP) - 4 levels
    for level in range(1, 5):
        hp_value = level * 20
        cards.append(Card(
            f"Vitality {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{hp_value} HP",
            hp_bonus=hp_value
        ))

    # 2. Strength (Attack) - 4 levels
    for level in range(1, 5):
        atk_value = level * 5
        cards.append(Card(
            f"Strength {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{atk_value} Attack",
            attack_bonus=atk_value
        ))

    # 3. Toughness (Defense) - 4 levels
    for level in range(1, 5):
        def_value = level * 4
        cards.append(Card(
            f"Toughness {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{def_value} Defense",
            defense_bonus=def_value
        ))

    # 4. Intellect (Magic Attack) - 4 levels
    for level in range(1, 5):
        mag_value = level * 8
        cards.append(Card(
            f"Intellect {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{mag_value} Magic Attack",
            magic_attack_bonus=mag_value
        ))

    # 5. Precision (Crit Chance) - 4 levels
    for level in range(1, 5):
        crit_value = level * 2.5
        cards.append(Card(
            f"Precision {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{crit_value}% Crit Chance",
            crit_chance_bonus=crit_value
        ))

    # 6. Agility (Dodge) - 4 levels
    for level in range(1, 5):
        dodge_value = level * 3.0
        cards.append(Card(
            f"Agility {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{dodge_value}% Dodge Chance",
            dodge_chance_bonus=dodge_value
        ))

    # 7. Wisdom (Mana) - 4 levels
    for level in range(1, 5):
        mana_value = level * 30
        cards.append(Card(
            f"Wisdom {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{mana_value} Mana",
            mana_bonus=mana_value
        ))

    # 8. Meditation (Mana Regen) - 4 levels
    for level in range(1, 5):
        regen_value = level * 3
        cards.append(Card(
            f"Meditation {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{regen_value} Mana Regen",
            mana_regen_bonus=regen_value
        ))

    # 9. Fortune (Luck) - 4 levels
    for level in range(1, 5):
        luck_value = level * 5
        cards.append(Card(
            f"Fortune {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{luck_value} Luck",
            luck_bonus=luck_value
        ))

    # 10. Swiftness (Attack Speed) - 4 levels
    for level in range(1, 5):
        speed_value = level * 0.15
        cards.append(Card(
            f"Swiftness {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{speed_value:.2f} Attack Speed",
            attack_speed_bonus=speed_value
        ))

    # NEW: 10 additional stat types - 4 levels each

    # 11. Focus (Crit Damage) - 4 levels
    for level in range(1, 5):
        crit_dmg_value = level * 0.2
        cards.append(Card(
            f"Focus {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{int(crit_dmg_value*100)}% Crit Damage",
            crit_damage_bonus=crit_dmg_value
        ))

    # 12. Endurance (HP + Defense combo) - 4 levels
    for level in range(1, 5):
        hp_value = level * 15
        def_value = level * 3
        cards.append(Card(
            f"Endurance {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{hp_value} HP, +{def_value} Defense",
            hp_bonus=hp_value,
            defense_bonus=def_value
        ))

    # 13. Power (Attack + Crit Chance combo) - 4 levels
    for level in range(1, 5):
        atk_value = level * 3
        crit_value = level * 2.0
        cards.append(Card(
            f"Power {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{atk_value} Attack, +{crit_value}% Crit Chance",
            attack_bonus=atk_value,
            crit_chance_bonus=crit_value
        ))

    # 14. Fury (Attack + Attack Speed combo) - 4 levels
    for level in range(1, 5):
        atk_value = level * 3
        speed_value = level * 0.1
        cards.append(Card(
            f"Fury {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{atk_value} Attack, +{speed_value:.2f} Attack Speed",
            attack_bonus=atk_value,
            attack_speed_bonus=speed_value
        ))

    # 15. Spirit (Mana + Mana Regen combo) - 4 levels
    for level in range(1, 5):
        mana_value = level * 25
        regen_value = level * 2
        cards.append(Card(
            f"Spirit {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{mana_value} Mana, +{regen_value} Mana Regen",
            mana_bonus=mana_value,
            mana_regen_bonus=regen_value
        ))

    # 16. Reflex (Dodge + Attack Speed combo) - 4 levels
    for level in range(1, 5):
        dodge_value = level * 2.5
        speed_value = level * 0.1
        cards.append(Card(
            f"Reflex {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{dodge_value}% Dodge, +{speed_value:.2f} Attack Speed",
            dodge_chance_bonus=dodge_value,
            attack_speed_bonus=speed_value
        ))

    # 17. Arcane (Magic Attack + Mana combo) - 4 levels
    for level in range(1, 5):
        mag_value = level * 6
        mana_value = level * 20
        cards.append(Card(
            f"Arcane {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{mag_value} Magic Attack, +{mana_value} Mana",
            magic_attack_bonus=mag_value,
            mana_bonus=mana_value
        ))

    # 18. Guardian (Defense + Dodge combo) - 4 levels
    for level in range(1, 5):
        def_value = level * 3
        dodge_value = level * 2.0
        cards.append(Card(
            f"Guardian {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{def_value} Defense, +{dodge_value}% Dodge",
            defense_bonus=def_value,
            dodge_chance_bonus=dodge_value
        ))

    # 19. Warrior (HP + Attack combo) - 4 levels
    for level in range(1, 5):
        hp_value = level * 15
        atk_value = level * 3
        cards.append(Card(
            f"Warrior {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{hp_value} HP, +{atk_value} Attack",
            hp_bonus=hp_value,
            attack_bonus=atk_value
        ))

    # 20. Assassin (Crit Chance + Crit Damage combo) - 4 levels
    for level in range(1, 5):
        crit_chance = level * 2.0
        crit_dmg = level * 0.15
        cards.append(Card(
            f"Assassin {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{crit_chance}% Crit Chance, +{int(crit_dmg*100)}% Crit Damage",
            crit_chance_bonus=crit_chance,
            crit_damage_bonus=crit_dmg
        ))

    # 21. Reckless (Attack Speed - Defense tradeoff) - 4 levels
    for level in range(1, 5):
        speed_value = level * 0.25
        def_value = level * 6
        cards.append(Card(
            f"Reckless {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{speed_value:.2f} Attack Speed, -{def_value} Defense",
            attack_speed_bonus=speed_value,
            defense_bonus=-def_value
        ))

    # 22. Tank (HP - Dodge tradeoff) - 4 levels
    for level in range(1, 5):
        hp_value = level * 50
        dodge_value = level * 5.0
        cards.append(Card(
            f"Tank {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{hp_value} HP, -{dodge_value}% Dodge Chance",
            hp_bonus=hp_value,
            dodge_chance_bonus=-dodge_value
        ))

    # 23. Capacitor (Mana Regen - Mana tradeoff) - 4 levels
    for level in range(1, 5):
        regen_value = level * 5
        mana_value = level * 15
        cards.append(Card(
            f"Capacitor {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{regen_value} Mana Regen, -{mana_value} Mana",
            mana_regen_bonus=regen_value,
            mana_bonus=-mana_value
        ))

    # 24. Pinpoint (Crit Chance - Attack/Magic Attack tradeoff) - 4 levels
    for level in range(1, 5):
        crit_value = level * 7.5
        atk_value = level * 10
        cards.append(Card(
            f"Pinpoint {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{crit_value}% Crit Chance, -{atk_value} Attack, -{atk_value} Magic Attack",
            crit_chance_bonus=crit_value,
            attack_bonus=-atk_value,
            magic_attack_bonus=-atk_value
        ))

    # 25. Fatal Hits (Crit Damage - Crit Chance tradeoff) - 4 levels
    for level in range(1, 5):
        crit_dmg_value = level * 0.5
        crit_chance_value = level * 5.0
        cards.append(Card(
            f"Fatal Hits {level}", CardType.PASSIVE, CardClass.STAT,
            f"+{int(crit_dmg_value*100)}% Crit Damage, -{crit_chance_value}% Crit Chance",
            crit_damage_bonus=crit_dmg_value,
            crit_chance_bonus=-crit_chance_value
        ))

    return cards


def create_equipment_card_pool() -> List[Card]:
    """
    Create a pool of 21 equipment cards.
    These provide base attack or defense stats.
    """
    cards = []

    # Weapons - Base Attack (5 cards)
    weapons = [
        ("Sword", 60, "A balanced weapon for physical combat", WeaponType.SWORD),
        ("Greatsword", 80, "A powerful two-handed weapon, deals high damage", WeaponType.GREATSWORD),
        ("Dagger", 40, "A quick weapon for fast strikes", WeaponType.DAGGER),
        ("Axe", 70, "A heavy weapon with crushing power", WeaponType.AXE),
        ("Spear", 55, "A reach weapon with good attack", WeaponType.SPEAR),
    ]
    for name, attack, desc, wtype in weapons:
        cards.append(Card(
            name, CardType.WEAPON, CardClass.EQUIPMENT,
            desc,
            attack_bonus=attack,
            weapon_type=wtype
        ))

    # Magic Weapons - Base Magic Attack (3 cards)
    magic_weapons = [
        ("Staff", 60, "A magical staff for spellcasting", WeaponType.STAFF),
        ("Wand", 45, "A quick magic weapon", WeaponType.WAND),
        ("Tome", 75, "An ancient spellbook with powerful magic", WeaponType.TOME),
    ]
    for name, magic, desc, wtype in magic_weapons:
        cards.append(Card(
            name, CardType.WEAPON, CardClass.EQUIPMENT,
            desc,
            magic_attack_bonus=magic,
            weapon_type=wtype
        ))

    # Armor - Base Defense (4 cards)
    armors = [
        ("Plate Armor", 40, "Heavy armor providing excellent protection"),
        ("Leather Armor", 25, "Light armor for mobility"),
        ("Chain Mail", 32, "Medium armor with good protection"),
        ("Robes", 15, "Magical robes with some protection"),
    ]
    for name, defense, desc in armors:
        cards.append(Card(
            name, CardType.ARMOR, CardClass.EQUIPMENT,
            desc,
            defense_bonus=defense
        ))

    # Hybrid Equipment (3 cards)
    hybrids = [
        ("Shield", 0, "A sturdy shield", 25, 50),  # defense, hp
        ("Battle Armor", 0, "Armor designed for combat", 28, 30),  # defense, hp
        ("Mystic Robe", 0, "Enchanted robes", 12, 0),  # defense, mana
    ]
    for name, _, desc, defense, bonus in hybrids:
        if name == "Mystic Robe":
            cards.append(Card(
                name, CardType.ARMOR, CardClass.EQUIPMENT,
                desc,
                defense_bonus=defense,
                mana_bonus=100
            ))
        else:
            cards.append(Card(
                name, CardType.ARMOR, CardClass.EQUIPMENT,
                desc,
                defense_bonus=defense,
                hp_bonus=bonus
            ))

    # Accessories - Rings (3 cards)
    cards.append(Card(
        "Ring of Power", CardType.ACCESSORY, CardClass.EQUIPMENT,
        "A ring imbued with raw strength",
        attack_bonus=35,
        magic_attack_bonus=35
    ))
    cards.append(Card(
        "Ring of Precision", CardType.ACCESSORY, CardClass.EQUIPMENT,
        "Enhances accuracy and critical strikes",
        crit_chance_bonus=8.0,
        crit_damage_bonus=0.25
    ))
    cards.append(Card(
        "Ring of Swiftness", CardType.ACCESSORY, CardClass.EQUIPMENT,
        "Increases attack speed and dodge chance",
        attack_speed_bonus=0.3,
        dodge_chance_bonus=5.0
    ))

    # Accessories - Amulets (3 cards)
    cards.append(Card(
        "Amulet of Vitality", CardType.ACCESSORY, CardClass.EQUIPMENT,
        "Grants increased health and vitality",
        hp_bonus=100
    ))
    cards.append(Card(
        "Amulet of the Arcane", CardType.ACCESSORY, CardClass.EQUIPMENT,
        "Enhances magical power and reserves",
        mana_bonus=120,
        mana_regen_bonus=8
    ))
    cards.append(Card(
        "Amulet of Warding", CardType.ACCESSORY, CardClass.EQUIPMENT,
        "Provides magical protection and resilience",
        defense_bonus=18,
        dodge_chance_bonus=6.0,
        hp_bonus=40
    ))

    return cards


def create_unique_card_pool() -> List[Card]:
    """
    Create a pool of unique cards with special mechanics.
    These are rare pulls from specific packs.
    """
    cards = []

    # 1. Unparalleled Swiftness (Speed Pack)
    # -30% damage, -30% magic damage, +3 attack speed (3 attacks per turn)
    cards.append(Card(
        "Unparalleled Swiftness", CardType.PASSIVE, CardClass.UNIQUE,
        "-30% Damage, -30% Magic Damage, +3 Attack Speed (3 attacks per turn)",
        attack_bonus=-3,  # Will be calculated as percentage in combat
        magic_attack_bonus=-3,  # Will be calculated as percentage in combat
        attack_speed_bonus=3.0,
        special_effect="unparalleled_swiftness"
    ))

    # 2. Reactive Armor (Defense Pack)
    # After taking damage from a hit, the next hit deals 50% less damage, -90% Magic Damage
    cards.append(Card(
        "Reactive Armor", CardType.PASSIVE, CardClass.UNIQUE,
        "After taking damage, next hit deals 50% less damage. -90% Magic Damage",
        magic_attack_bonus=-9,  # Will be calculated as percentage in combat
        special_effect="reactive_armor"
    ))

    # 3. Lucky 7 (Utility Pack)
    # When luck fails to roll 7 times, guarantee the next roll
    cards.append(Card(
        "Lucky 7", CardType.PASSIVE, CardClass.UNIQUE,
        "After luck fails 7 times, guarantee next luck roll (crit/dodge)",
        special_effect="lucky_7"
    ))

    # 4. Mana Amplifier (Magic Pack)
    # Every attack consumes 50% of mana, but deals 3x magic damage
    cards.append(Card(
        "Mana Amplifier", CardType.PASSIVE, CardClass.UNIQUE,
        "Attacks consume 50% max mana but deal 3x magic damage",
        special_effect="mana_amplifier"
    ))

    # 5. Mana Conduit (Magic Pack)
    # Regenerate 25% of mana every turn, -100% attack
    cards.append(Card(
        "Mana Conduit", CardType.PASSIVE, CardClass.UNIQUE,
        "Regenerate 25% max mana per turn, -100% Attack",
        attack_bonus=-100,  # Will be calculated as percentage in combat
        special_effect="mana_conduit"
    ))

    # 6. Titan's Strength (Physical Weapons Pack)
    # Enables equipping 2 greatswords, axes and spears. All attack speed bonuses halved
    cards.append(Card(
        "Titan's Strength", CardType.PASSIVE, CardClass.UNIQUE,
        "Can equip 2 Greatswords/Axes/Spears. Attack speed bonuses halved",
        special_effect="titans_strength"
    ))

    # 7. Arcane Tome Wielder (Magic Weapons Pack)
    # Can equip up to 4 Tomes, Cannot equip Armor, -100% Attack, +25% magic attack per tome
    cards.append(Card(
        "Arcane Tome Wielder", CardType.PASSIVE, CardClass.UNIQUE,
        "Equip up to 4 Tomes. No Armor. -100% Attack, +25% Magic Attack per Tome",
        attack_bonus=-100,  # Will be calculated as percentage in combat
        special_effect="arcane_tome_wielder"
    ))

    # 8. Berserker's Rage (Offense Pack)
    # Gain 1 Rage per physical hit. Rage gives +5 Attack per stack, max 50. -50 HP
    cards.append(Card(
        "Berserker's Rage", CardType.PASSIVE, CardClass.UNIQUE,
        "Gain 1 Rage per physical hit. Rage: +5 Attack per stack (max 50). -50 HP",
        hp_bonus=-50,
        special_effect="berserkers_rage"
    ))

    # 9. Barrier (Defense Pack)
    # Gains Shield at start of battle = 50% of Magic Attack. Shield absorbs damage before HP
    cards.append(Card(
        "Barrier", CardType.PASSIVE, CardClass.UNIQUE,
        "Gain Shield at battle start equal to 50% of Magic Attack. Shield absorbs damage before HP",
        special_effect="barrier"
    ))

    return cards


def create_card_packs() -> dict:
    """
    Create card packs for the pack-based selection system.
    Returns a dictionary where keys are pack names and values are lists of cards.
    Each pack has common cards and unique (rare) cards.
    """
    stat_pool = create_stat_card_pool()
    equipment_pool = create_equipment_card_pool()
    unique_pool = create_unique_card_pool()

    packs = {}

    # Find unique cards by their special effects
    unique_cards = {
        "unparalleled_swiftness": next(c for c in unique_pool if c.special_effect == "unparalleled_swiftness"),
        "reactive_armor": next(c for c in unique_pool if c.special_effect == "reactive_armor"),
        "lucky_7": next(c for c in unique_pool if c.special_effect == "lucky_7"),
        "mana_amplifier": next(c for c in unique_pool if c.special_effect == "mana_amplifier"),
        "mana_conduit": next(c for c in unique_pool if c.special_effect == "mana_conduit"),
        "titans_strength": next(c for c in unique_pool if c.special_effect == "titans_strength"),
        "arcane_tome_wielder": next(c for c in unique_pool if c.special_effect == "arcane_tome_wielder"),
        "berserkers_rage": next(c for c in unique_pool if c.special_effect == "berserkers_rage"),
        "barrier": next(c for c in unique_pool if c.special_effect == "barrier"),
    }

    # Physical Weapons Pack - all physical weapons + Titan's Strength (unique)
    packs["Physical Weapons"] = {
        "common": [card for card in equipment_pool
                   if card.card_type == CardType.WEAPON and card.attack_bonus > 0],
        "unique": [unique_cards["titans_strength"]]
    }

    # Magic Weapons Pack - all magic weapons + Arcane Tome Wielder (unique)
    packs["Magic Weapons"] = {
        "common": [card for card in equipment_pool
                   if card.card_type == CardType.WEAPON and card.magic_attack_bonus > 0],
        "unique": [unique_cards["arcane_tome_wielder"]]
    }

    # Armor Pack - all armor (no unique)
    packs["Armor"] = {
        "common": [card for card in equipment_pool if card.card_type == CardType.ARMOR],
        "unique": []
    }

    # Offense Pack - Strength, Power, Fury, Assassin, Pinpoint, Fatal Hits (all levels) + Berserker's Rage (unique)
    packs["Offense"] = {
        "common": [card for card in stat_pool
                   if any(card.name.startswith(prefix) for prefix in ["Strength", "Power", "Fury", "Assassin", "Pinpoint", "Fatal Hits"])],
        "unique": [unique_cards["berserkers_rage"]]
    }

    # Defense Pack - Toughness, Endurance, Guardian, Tank (all levels) + Reactive Armor + Barrier (unique)
    packs["Defense"] = {
        "common": [card for card in stat_pool
                   if any(card.name.startswith(prefix) for prefix in ["Toughness", "Endurance", "Guardian", "Tank"])],
        "unique": [unique_cards["reactive_armor"], unique_cards["barrier"]]
    }

    # Speed Pack - Swiftness, Reflex, Agility, Reckless (all levels) + Unparalleled Swiftness (unique)
    packs["Speed"] = {
        "common": [card for card in stat_pool
                   if any(card.name.startswith(prefix) for prefix in ["Swiftness", "Reflex", "Agility", "Reckless"])],
        "unique": [unique_cards["unparalleled_swiftness"]]
    }

    # Magic Pack - Intellect, Wisdom, Meditation, Spirit, Arcane, Capacitor (all levels) + Mana Amplifier + Mana Conduit (unique)
    packs["Magic"] = {
        "common": [card for card in stat_pool
                   if any(card.name.startswith(prefix) for prefix in ["Intellect", "Wisdom", "Meditation", "Spirit", "Arcane", "Capacitor"])],
        "unique": [unique_cards["mana_amplifier"], unique_cards["mana_conduit"]]
    }

    # Utility Pack - Vitality, Precision, Fortune, Focus, Warrior (all levels) + Lucky 7 (unique)
    packs["Utility"] = {
        "common": [card for card in stat_pool
                   if any(card.name.startswith(prefix) for prefix in ["Vitality", "Precision", "Fortune", "Focus", "Warrior"])],
        "unique": [unique_cards["lucky_7"]]
    }

    return packs


def open_pack(pack_data: dict) -> Card:
    """
    Open a pack and get 1 random card from it.
    Unique cards have a 5% drop rate.

    Args:
        pack_data: Dictionary with 'common' and 'unique' card lists

    Returns:
        A random card from the pack
    """
    common_cards = pack_data["common"]
    unique_cards = pack_data["unique"]

    # 5% chance to get a unique card (if any exist in this pack)
    if unique_cards and random.random() < 0.05:
        return random.choice(unique_cards)

    # Otherwise, get a common card
    return random.choice(common_cards)


def print_battle_report(players: List[Player]):
    """
    Print a detailed battle report for all players.
    Shows floors reached, monsters killed, damage dealt/taken, etc.
    """
    print("\n" + "="*80)
    print("BATTLE REPORT - AUTO-SIMULATION COMPLETE")
    print("="*80)
    print()

    # Sort players by floors reached (descending)
    sorted_players = sorted(players, key=lambda p: p.current_floor, reverse=True)

    # Print summary table
    print("FINAL STANDINGS:")
    print("-" * 80)
    print(f"{'Rank':<6} {'Player':<20} {'Floor':<8} {'Level':<8} {'Status':<15} {'Monsters':<10}")
    print("-" * 80)

    for i, player in enumerate(sorted_players, 1):
        status = f"Escaped" if player.escaped_floor else "Victorious"
        print(f"{i:<6} {player.name:<20} {player.current_floor:<8} {player.level:<8} {status:<15} {player.monsters_killed:<10}")

    print("-" * 80)
    print()

    # Detailed stats for each player
    print("DETAILED STATISTICS:")
    print("="*80)

    for player in sorted_players:
        # Calculate pack breakdown
        if player.level < 20:
            level_packs = 9 + player.level
        else:
            level_packs = 30
        floor_bonus_packs = player.get_floor_bonus_packs()
        total_packs = player.get_max_packs()

        print(f"\n{player.name}:")
        print(f"  Final Floor:        {player.current_floor}")
        print(f"  Status:             {'Escaped at floor ' + str(player.escaped_floor) if player.escaped_floor else 'Reached the top!'}")
        print(f"  Highest Floor Ever: {player.highest_floor}")
        print(f"  Final Level:        {player.level} ({player.current_xp}/{player.get_xp_for_next_level()} XP)")
        print(f"  Next Run Packs:     {total_packs} (Level: {level_packs}, Floor Bonus: +{floor_bonus_packs})")
        print(f"  Bounty:             {player.bounty} 💰")

        # Show ascension cards
        if len(player.ascension_slots) > 0:
            ascension_str = ", ".join(player.ascension_slots)
            print(f"  Ascension Cards:    {ascension_str}")

        print(f"  Floors Cleared:     {player.floors_cleared}")
        print(f"  Monsters Killed:    {player.monsters_killed}")
        print(f"  Total Damage Dealt: {player.total_damage_dealt}")
        print(f"  Total Damage Taken: {player.total_damage_taken}")
        print(f"  Total Turns:        {player.total_turns_in_combat}")
        print(f"  Critical Hits:      {player.crits_landed}")
        print(f"  Dodges:             {player.dodges_made}")

        # Calculate averages
        if player.total_turns_in_combat > 0:
            avg_dmg_per_turn = player.total_damage_dealt / player.total_turns_in_combat
            print(f"  Avg Dmg/Turn:       {avg_dmg_per_turn:.1f}")

        if player.floors_cleared > 0:
            avg_turns_per_floor = player.total_turns_in_combat / player.floors_cleared
            avg_monsters_per_floor = player.monsters_killed / player.floors_cleared
            print(f"  Avg Turns/Floor:    {avg_turns_per_floor:.1f}")
            print(f"  Avg Monsters/Floor: {avg_monsters_per_floor:.1f}")

    print("\n" + "="*80)


def select_packs_interactive(player: Player) -> List[Card]:
    """
    Allow player to select and open packs based on their level.
    Each pack gives 1 random card.
    Level 1: 10 packs, Level 2: 11 packs, ..., Level 20: 30 packs
    Supports rerolling cards for 10 bounty each.
    """
    level = player.level
    # Calculate number of packs based on level
    if level < 20:
        num_packs = 9 + level
    else:
        num_packs = 30

    packs = create_card_packs()
    pack_names = list(packs.keys())
    selected_cards = []

    print("\n" + "="*60)
    print("PACK SELECTION")
    print("="*60)
    print(f"Level {level}: Select {num_packs} packs to open. Each pack gives you 1 random card!")
    print(f"Current Bounty: {player.bounty} 💰")
    print(f"Reroll cost: 10 bounty per card")
    print()

    # Show pack descriptions
    print("Available packs:")
    for i, pack_name in enumerate(pack_names, 1):
        num_common = len(packs[pack_name]["common"])
        num_unique = len(packs[pack_name]["unique"])
        unique_str = f" + {num_unique} UNIQUE" if num_unique > 0 else ""
        print(f"  {i}. {pack_name:20s} ({num_common} cards{unique_str})")

    print("\nTIP: You can pick the same pack multiple times!")
    print()

    for pick_num in range(1, num_packs + 1):
        print(f"\n--- Pick {pick_num}/{num_packs} ---")

        while True:
            try:
                choice = input(f"Select pack (1-{len(pack_names)}): ").strip()
                idx = int(choice) - 1

                if 0 <= idx < len(pack_names):
                    pack_name = pack_names[idx]
                    card = open_pack(packs[pack_name])

                    # Show the card drawn
                    unique_marker = " ✨ UNIQUE!" if card.card_class == CardClass.UNIQUE else ""
                    print(f"✓ Opened {pack_name}! Got: {card.name}{unique_marker}")
                    print(f"   {card.description}")

                    # Offer reroll option
                    while player.bounty >= 10:
                        reroll_choice = input(f"Reroll this card? (10 bounty, current: {player.bounty}) [y/n]: ").strip().lower()
                        if reroll_choice == 'y':
                            player.bounty -= 10
                            card = open_pack(packs[pack_name])
                            unique_marker = " ✨ UNIQUE!" if card.card_class == CardClass.UNIQUE else ""
                            print(f"🔄 Rerolled! Got: {card.name}{unique_marker}")
                            print(f"   {card.description}")
                        elif reroll_choice == 'n':
                            break
                        else:
                            print("Invalid input. Enter 'y' or 'n'.")

                    selected_cards.append(card)
                    break
                else:
                    print(f"Invalid choice. Enter a number between 1 and {len(pack_names)}.")
            except ValueError:
                print("Invalid input. Enter a number.")

    print("\n" + "="*60)
    print(f"FINAL DECK ({num_packs} cards)")
    print(f"Remaining Bounty: {player.bounty} 💰")
    print("="*60)
    for card in selected_cards:
        print(f"  - {card.name}")

    return selected_cards


def get_ascension_cards() -> dict:
    """
    Get the list of available ascension cards with their descriptions.
    Returns a dictionary mapping card names to descriptions.
    """
    return {
        "Ancestral Rage": "Gain 1 Rage Stack per physical hit (max 50). Rage gives +5 Attack per stack. Rage also gives bonus to speed at +0.1 per 5 stacks.",
        "Impaler": "Critical Hits Impale Enemies. Impaled enemies take an additional 70% damage on the next hit (effectively 170% damage total).",
        "Blood Magic": "Use HP as mana when out of mana. Won't kill you - minimum HP is 1, and you must have HP > 1 to use this ability.",
        "Blind Master": "+100% Dodge Chance, cannot deal critical hits.",
        "Finishing Strike": "Physical attacks instantly kill enemies below 10% HP."
    }


def select_ascension_card_interactive(player: Player, slot_number: int) -> str:
    """
    Interactive selection of an ascension card for a specific slot.
    Returns the selected card name.
    """
    ascension_cards = get_ascension_cards()
    card_names = list(ascension_cards.keys())

    print("\n" + "="*60)
    print(f"ASCENSION CARD SELECTION - SLOT {slot_number}")
    print("="*60)
    print(f"Level {player.level}: Choose your ascension card!")
    print("\nAvailable Ascension Cards:")
    print()

    for i, (name, desc) in enumerate(ascension_cards.items(), 1):
        print(f"{i}. {name}")
        print(f"   {desc}")
        print()

    while True:
        try:
            choice = input(f"Select ascension card (1-{len(card_names)}): ").strip()
            idx = int(choice) - 1

            if 0 <= idx < len(card_names):
                selected = card_names[idx]
                confirm = input(f"Confirm '{selected}'? [y/n]: ").strip().lower()
                if confirm == 'y':
                    print(f"\n✓ {selected} selected for Slot {slot_number}!")
                    return selected
            else:
                print(f"Invalid choice. Enter a number between 1 and {len(card_names)}.")
        except ValueError:
            print("Invalid input. Enter a number.")


def change_ascension_card_interactive(player: Player) -> bool:
    """
    Interactive menu to change ascension cards for 100 bounty each.
    Returns True if any changes were made.
    """
    ascension_cards = get_ascension_cards()
    card_names = list(ascension_cards.keys())
    changes_made = False

    print("\n" + "="*60)
    print("CHANGE ASCENSION CARDS")
    print("="*60)
    print(f"Current Bounty: {player.bounty} 💰")
    print(f"Cost to change: 100 bounty per slot")
    print()

    # Show current ascension cards
    print("Current Ascension Cards:")
    for i, card in enumerate(player.ascension_slots, 1):
        print(f"  Slot {i}: {card}")
    print()

    if player.bounty < 100:
        print("Not enough bounty to change ascension cards!")
        return False

    while player.bounty >= 100:
        print("\nWhich slot do you want to change?")
        for i, card in enumerate(player.ascension_slots, 1):
            print(f"  {i}. Slot {i}: {card}")
        print(f"  0. Done (Exit)")
        print()

        try:
            choice = input("Select slot to change (or 0 to exit): ").strip()
            slot_idx = int(choice)

            if slot_idx == 0:
                break

            if 1 <= slot_idx <= len(player.ascension_slots):
                # Show available cards
                print(f"\nChanging Slot {slot_idx} (current: {player.ascension_slots[slot_idx-1]})")
                print("\nAvailable Ascension Cards:")
                for i, (name, desc) in enumerate(ascension_cards.items(), 1):
                    print(f"{i}. {name}")
                    print(f"   {desc}")
                    print()

                card_choice = input(f"Select new card (1-{len(card_names)}): ").strip()
                card_idx = int(card_choice) - 1

                if 0 <= card_idx < len(card_names):
                    new_card = card_names[card_idx]
                    old_card = player.ascension_slots[slot_idx-1]

                    if new_card == old_card:
                        print("That's the same card! No change needed.")
                    else:
                        confirm = input(f"Change '{old_card}' to '{new_card}' for 100 bounty? [y/n]: ").strip().lower()
                        if confirm == 'y':
                            player.bounty -= 100
                            player.ascension_slots[slot_idx-1] = new_card
                            changes_made = True
                            print(f"\n✓ Slot {slot_idx} changed to {new_card}!")
                            print(f"Remaining Bounty: {player.bounty} 💰")
                else:
                    print(f"Invalid choice. Enter a number between 1 and {len(card_names)}.")
            else:
                print(f"Invalid slot. Enter a number between 1 and {len(player.ascension_slots)}.")
        except ValueError:
            print("Invalid input. Enter a number.")

    return changes_made


def create_bounty_shop_inventory() -> List[Tuple[Card, int]]:
    """
    Create the bounty shop inventory with cards and their prices.
    Returns a list of (Card, price) tuples.
    Pricing:
    - Weapons: 10 bounty (all 8 weapons available)
    - Armor: 20 bounty (3 armors)
    - Low-tier stat cards: 20 bounty (5 random)
    - Mid-tier stat cards: 30 bounty (3 random)
    - High-tier stat cards: 40 bounty (2 random)
    - Unique card: 200 bounty (1 only per shop)
    """
    inventory = []
    stat_pool = create_stat_card_pool()
    equipment_pool = create_equipment_card_pool()
    unique_pool = create_unique_card_pool()

    # Weapons: 10 bounty each (at least 3)
    weapons = [card for card in equipment_pool if card.card_type == CardType.WEAPON]
    for weapon in weapons:
        inventory.append((weapon, 10))

    # Armor: 20 bounty each
    armors = [card for card in equipment_pool if card.card_type == CardType.ARMOR]
    for armor in armors[:3]:  # Add 3 armors
        inventory.append((armor, 20))

    # Low-tier stat cards (Level 1-2): 20 bounty
    low_stat_cards = [card for card in stat_pool if any(card.name.endswith(f" {level}") for level in [1, 2])]
    for card in random.sample(low_stat_cards, min(5, len(low_stat_cards))):
        inventory.append((card, 20))

    # Mid-tier stat cards (Level 3): 30 bounty
    mid_stat_cards = [card for card in stat_pool if card.name.endswith(" 3")]
    for card in random.sample(mid_stat_cards, min(3, len(mid_stat_cards))):
        inventory.append((card, 30))

    # High-tier stat cards (Level 4): 40 bounty
    high_stat_cards = [card for card in stat_pool if card.name.endswith(" 4")]
    for card in random.sample(high_stat_cards, min(2, len(high_stat_cards))):
        inventory.append((card, 40))

    # Unique cards: 200 bounty (only 1 per shop)
    unique_card = random.choice(unique_pool)
    inventory.append((unique_card, 200))

    return inventory


def bounty_shop_interactive(player: Player) -> List[Card]:
    """
    Interactive bounty shop where players can buy cards for bounty.
    Returns list of purchased cards.
    """
    inventory = create_bounty_shop_inventory()
    purchased_cards = []

    print("\n" + "="*60)
    print("💰 BOUNTY SHOP 💰")
    print("="*60)
    print(f"Welcome, {player.name}!")
    print(f"Your Bounty: {player.bounty}")
    print("\nCards bought here are ONLY for the next tower run!")
    print("Weapon limits still apply (staff is two-handed, etc.)")
    print()

    while True:
        print("\n" + "-"*60)
        print("SHOP INVENTORY:")
        print("-"*60)
        print(f"{'#':<4} {'Card':<30} {'Type':<12} {'Price':<8}")
        print("-"*60)

        for i, (card, price) in enumerate(inventory, 1):
            unique_marker = " ✨" if card.card_class == CardClass.UNIQUE else ""
            print(f"{i:<4} {card.name:<30} {card.card_type.value:<12} {price} 💰{unique_marker}")

        print("-"*60)
        print(f"Your Bounty: {player.bounty} 💰")
        print(f"Purchased so far: {len(purchased_cards)} cards")
        print()

        choice = input("Enter card # to buy (or 'done' to finish shopping): ").strip().lower()

        if choice == 'done':
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(inventory):
                card, price = inventory[idx]

                if player.bounty >= price:
                    confirm = input(f"Buy '{card.name}' for {price} bounty? [y/n]: ").strip().lower()
                    if confirm == 'y':
                        player.bounty -= price
                        purchased_cards.append(card)
                        print(f"✓ Purchased {card.name}!")
                        print(f"   {card.description}")
                        # Remove from inventory (can only buy once)
                        inventory.pop(idx)
                else:
                    print(f"Not enough bounty! Need {price}, have {player.bounty}")
            else:
                print(f"Invalid choice. Enter a number between 1 and {len(inventory)}.")
        except ValueError:
            print("Invalid input. Enter a number or 'done'.")

    print("\n" + "="*60)
    print(f"PURCHASE COMPLETE")
    print(f"Remaining Bounty: {player.bounty} 💰")
    print(f"Purchased {len(purchased_cards)} cards for next run")
    print("="*60)

    if purchased_cards:
        print("\nPurchased cards:")
        for card in purchased_cards:
            print(f"  - {card.name}")

    return purchased_cards


def main():
    """Main game loop."""
    print("="*60)
    print("TOWER CLIMBING ROGUELIKE")
    print("Climb the 1000-floor tower and compete for the highest floor!")
    print("="*60)
    print()

    # Setup players
    num_players = int(input("Enter number of players (1-4): "))
    num_players = max(1, min(4, num_players))

    players = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        player = Player(name)

        # Check for ascension card unlocks based on level
        num_slots_needed = 0
        if player.level >= 20:
            num_slots_needed = 2
        elif player.level >= 10:
            num_slots_needed = 1

        # Select ascension cards if player has unlocked slots but hasn't selected them
        if num_slots_needed > len(player.ascension_slots):
            for slot in range(len(player.ascension_slots) + 1, num_slots_needed + 1):
                print(f"\n🌟 You've unlocked Ascension Card Slot {slot}!")
                selected_card = select_ascension_card_interactive(player, slot)
                player.ascension_slots.append(selected_card)

        # Offer to change ascension cards if player has any and enough bounty
        if len(player.ascension_slots) > 0 and player.bounty >= 100:
            change_choice = input("\nDo you want to change your ascension cards? (100 bounty each) [y/n]: ").strip().lower()
            if change_choice == 'y':
                change_ascension_card_interactive(player)

        # Visit bounty shop
        shop_cards = bounty_shop_interactive(player)

        # Select and open packs to build deck (based on player level)
        pack_cards = select_packs_interactive(player)

        # Combine shop cards and pack cards for the deck
        deck = shop_cards + pack_cards

        player.equip_deck(deck)
        players.append(player)

    print("\n" + "="*60)
    print("PREP PHASE COMPLETE - ENTERING AUTO-BATTLE MODE")
    print("="*60)
    print("\nAll players will now automatically enter the tower.")
    print("Battles will be simulated and results reported at the end.")
    print("\nSimulating battles...")
    print()

    # Tower climbing - AUTO-BATTLE MODE
    tower = Tower()
    active_players = players.copy()

    while active_players:
        floor = active_players[0].current_floor + 1

        # Show progress every 10 floors
        if floor % 10 == 0 or floor == 1:
            player_status = ", ".join([f"{p.name} (Floor {p.current_floor})" for p in active_players])
            print(f"  Floor {floor}: {player_status}")

        # Each active player attempts this floor
        for player in active_players[:]:  # Copy list to modify during iteration
            player.current_floor = floor

            # Generate enemies for this floor
            enemies = tower.generate_enemies(floor)

            # Battle - SILENT MODE
            won = Combat.battle(player, enemies, silent=True)

            if won:
                # Player beat the floor
                # Gain XP and potentially level up
                leveled_up = player.gain_xp(floor, silent=True)

                # Show level up notification
                if leveled_up:
                    print(f"  ⚡ {player.name} leveled up to {player.level}! (Next run: {player.get_max_packs()} packs)")

                player.reset_for_floor()  # Heal for next floor
            else:
                # Player escaped
                # Update highest floor if this is a new record
                if player.current_floor > player.highest_floor:
                    old_highest = player.highest_floor
                    player.highest_floor = player.current_floor
                    bonus_increase = player.highest_floor // 50 - old_highest // 50
                    if bonus_increase > 0:
                        print(f"  🏆 New record! Floor {player.highest_floor} (+{bonus_increase} bonus pack(s) next run)")

                active_players.remove(player)
                print(f"  ⚠️  {player.name} escaped at floor {player.current_floor}!")

        # Check if we've reached the top or all players are out
        if not active_players:
            break

        if floor >= Tower.MAX_FLOORS:
            print("\n  🎉 TOP OF THE TOWER REACHED!")
            break

    # Update highest floor for all players before final report
    for player in players:
        if player.current_floor > player.highest_floor:
            player.highest_floor = player.current_floor

    # Final results - BATTLE REPORT
    print_battle_report(players)


if __name__ == "__main__":
    main()
