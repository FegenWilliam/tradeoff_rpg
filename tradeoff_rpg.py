"""
Tower Climbing Roguelike
A competitive game where up to 4 players climb a 1000-floor tower using card-based builds.
"""

import random
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


class CardType(Enum):
    """Types of cards available in the game."""
    WEAPON = "weapon"
    ARMOR = "armor"
    SPELL = "spell"
    PASSIVE = "passive"
    CONSUMABLE = "consumable"


@dataclass
class Card:
    """
    Cards are the core mechanic - they provide everything from weapons to stats.
    """
    name: str
    card_type: CardType
    description: str

    # Stat modifiers
    hp_bonus: int = 0
    attack_bonus: int = 0
    defense_bonus: int = 0
    magic_attack_bonus: int = 0
    mana_bonus: int = 0
    mana_regen_bonus: int = 0
    crit_chance_bonus: float = 0.0  # Percentage
    crit_damage_bonus: float = 0.0  # Multiplier addition
    dodge_chance_bonus: float = 0.0  # Percentage
    attack_speed_bonus: float = 0.0  # Additional attacks
    luck_bonus: int = 0

    # Special effects (to be expanded)
    special_effect: Optional[str] = None
    damage: int = 0  # For weapon cards
    magic_damage: int = 0  # For spell cards
    mana_cost: int = 0  # For spell cards

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

    def equip_deck(self, cards: List[Card]):
        """Equip cards before entering the tower."""
        self.deck = cards
        self.active_cards = cards.copy()
        self._apply_card_bonuses()

    def _apply_card_bonuses(self):
        """Apply all stat bonuses from equipped cards."""
        total_hp_bonus = sum(card.hp_bonus for card in self.active_cards)
        total_attack_bonus = sum(card.attack_bonus for card in self.active_cards)
        total_defense_bonus = sum(card.defense_bonus for card in self.active_cards)
        total_magic_attack_bonus = sum(card.magic_attack_bonus for card in self.active_cards)
        total_mana_bonus = sum(card.mana_bonus for card in self.active_cards)
        total_mana_regen_bonus = sum(card.mana_regen_bonus for card in self.active_cards)
        total_crit_chance_bonus = sum(card.crit_chance_bonus for card in self.active_cards)
        total_crit_damage_bonus = sum(card.crit_damage_bonus for card in self.active_cards)
        total_dodge_chance_bonus = sum(card.dodge_chance_bonus for card in self.active_cards)
        total_attack_speed_bonus = sum(card.attack_speed_bonus for card in self.active_cards)
        total_luck_bonus = sum(card.luck_bonus for card in self.active_cards)

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

        self.current_hp = min(self.current_hp, self.max_hp)
        self.current_mana = min(self.current_mana, self.max_mana)

    def take_damage(self, damage: int) -> bool:
        """
        Take damage and check if player needs to escape.
        Returns True if player escaped (hit 1 HP).
        """
        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage

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
        """Calculate total damage from weapon cards."""
        weapon_damage = sum(card.damage for card in self.active_cards
                          if card.card_type == CardType.WEAPON)
        return self.attack + weapon_damage

    def regenerate_mana(self):
        """Regenerate mana at the start of each turn."""
        self.current_mana = min(self.current_mana + self.mana_regen, self.max_mana)

    def can_dodge(self) -> bool:
        """Check if player can dodge (can't dodge twice in a row)."""
        if self.dodged_last_attack:
            return False

        # Use luck to potentially roll twice
        if self.luck > 0 and random.randint(1, 100) <= self.luck:
            # Roll twice, take the better result
            roll1 = random.randint(1, 100)
            roll2 = random.randint(1, 100)
            success = max(roll1, roll2) <= self.dodge_chance
        else:
            success = random.randint(1, 100) <= self.dodge_chance

        self.dodged_last_attack = success
        return success

    def calculate_damage(self, base_damage: int) -> tuple[int, bool]:
        """
        Calculate damage with crit chance.
        Returns (damage, is_crit).
        """
        # Check for crit with luck
        is_crit = False
        if self.luck > 0 and random.randint(1, 100) <= self.luck:
            # Roll twice, take the better result
            roll1 = random.randint(1, 100)
            roll2 = random.randint(1, 100)
            is_crit = min(roll1, roll2) <= self.crit_chance
        else:
            is_crit = random.randint(1, 100) <= self.crit_chance

        if is_crit:
            return int(base_damage * self.crit_damage), True
        return base_damage, False

    def reset_for_floor(self):
        """Reset stats for a new floor (heal between floors for now)."""
        self.current_hp = self.max_hp
        self.current_mana = self.max_mana
        self.dodged_last_attack = False

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

    def can_dodge(self) -> bool:
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

    def calculate_damage(self, base_damage: int) -> tuple[int, bool]:
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
    def _perform_attack(attacker, defender, damage: int, attack_type: str = "physical") -> bool:
        """
        Perform a single attack with dodge and crit mechanics.
        Returns True if defender was defeated.
        """
        attacker_name = attacker.name if hasattr(attacker, 'name') else str(attacker)
        defender_name = defender.name if hasattr(defender, 'name') else str(defender)

        # Check if defender dodges
        if defender.can_dodge():
            print(f"  💨 {defender_name} DODGED the attack!")
            return False

        # If attack wasn't dodged, reset the dodge flag
        defender.dodged_last_attack = False

        # Calculate damage with crit
        final_damage, is_crit = attacker.calculate_damage(damage)

        # Display attack
        crit_marker = " 💥 CRITICAL HIT!" if is_crit else ""
        type_marker = "⚡" if attack_type == "magic" else "⚔️"
        print(f"  {type_marker} {attacker_name} attacks {defender_name} for {final_damage} damage!{crit_marker}")

        # Apply damage
        return defender.take_damage(final_damage)

    @staticmethod
    def battle(player: Player, enemies: List[Enemy]) -> bool:
        """
        Execute combat between player and enemies.
        Returns True if player wins, False if player escaped.
        """
        print(f"\n{'='*60}")
        print(f"FLOOR {player.current_floor} - BATTLE START!")
        print(f"{'='*60}")
        print(f"{player.name}: {player.current_hp}/{player.max_hp} HP, {player.current_mana}/{player.max_mana} MP")
        for i, enemy in enumerate(enemies, 1):
            print(f"  Enemy {i}: {enemy}")
        print()

        turn = 0
        while enemies and player.is_alive:
            turn += 1
            print(f"--- Turn {turn} ---")

            # Regenerate mana
            player.regenerate_mana()
            for enemy in enemies:
                enemy.regenerate_mana()

            # Player turn - attack speed determines number of attacks
            num_attacks = int(player.attack_speed)
            has_partial_attack = (player.attack_speed % 1) > 0

            # If there's a fractional part, check if we get a bonus attack
            if has_partial_attack and random.random() < (player.attack_speed % 1):
                num_attacks += 1

            for attack_num in range(num_attacks):
                if not enemies:
                    break

                target = enemies[0]

                # Decide between physical and magic attack
                # Use magic if we have mana and magic attack is higher
                use_magic = (player.magic_attack > 0 and
                           player.current_mana >= 20 and
                           player.magic_attack > player.get_weapon_damage())

                if use_magic:
                    damage = player.magic_attack
                    player.current_mana -= 20
                    attack_type = "magic"
                else:
                    damage = player.get_weapon_damage()
                    attack_type = "physical"

                if Combat._perform_attack(player, target, damage, attack_type):
                    print(f"  ✓ {target.name} defeated!")
                    enemies.pop(0)
                    if not enemies:
                        print(f"\n🎉 {player.name} wins the battle!")
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

                    if Combat._perform_attack(enemy, player, damage, attack_type):
                        print(f"\n💀 {player.name} HP dropped to 1! AUTO-ESCAPE activated!")
                        print(f"🏃 {player.name} escaped from floor {player.current_floor}.")
                        return False

            print(f"📊 {player.name}: {player.current_hp}/{player.max_hp} HP, {player.current_mana}/{player.max_mana} MP\n")

        return True


def create_starter_deck() -> List[Card]:
    """Create a basic starter deck for testing."""
    return [
        Card("Iron Sword", CardType.WEAPON, "A basic sword",
             damage=15, crit_chance_bonus=5.0),
        Card("Leather Armor", CardType.ARMOR, "Basic protection",
             defense_bonus=5, hp_bonus=30),
        Card("Vitality Charm", CardType.PASSIVE, "Increases max HP",
             hp_bonus=50),
        Card("Power Ring", CardType.PASSIVE, "Increases attack and crit",
             attack_bonus=5, crit_damage_bonus=0.2),
        Card("Lucky Coin", CardType.PASSIVE, "Increases luck",
             luck_bonus=10, dodge_chance_bonus=5.0),
        Card("Swift Boots", CardType.PASSIVE, "Increases attack speed",
             attack_speed_bonus=0.5),
    ]


def create_mage_deck() -> List[Card]:
    """Create a mage starter deck for testing."""
    return [
        Card("Apprentice Staff", CardType.WEAPON, "A basic magic staff",
             magic_attack_bonus=20, magic_damage=15, mana_cost=15),
        Card("Mage Robes", CardType.ARMOR, "Light magical protection",
             defense_bonus=2, mana_bonus=100),
        Card("Crystal Focus", CardType.PASSIVE, "Enhances magic power",
             magic_attack_bonus=15, mana_regen_bonus=10),
        Card("Arcane Intellect", CardType.PASSIVE, "Increases mana pool",
             mana_bonus=50, mana_regen_bonus=5),
        Card("Critical Focus", CardType.PASSIVE, "Increases spell crit",
             crit_chance_bonus=10.0, crit_damage_bonus=0.3),
        Card("Blink", CardType.PASSIVE, "Increases dodge",
             dodge_chance_bonus=10.0),
    ]


def create_warrior_deck() -> List[Card]:
    """Create a warrior starter deck for testing."""
    return [
        Card("Steel Greatsword", CardType.WEAPON, "A heavy two-handed sword",
             damage=25, crit_damage_bonus=0.5),
        Card("Plate Armor", CardType.ARMOR, "Heavy protection",
             defense_bonus=15, hp_bonus=100),
        Card("Berserker Rage", CardType.PASSIVE, "Raw power",
             attack_bonus=15, crit_chance_bonus=10.0),
        Card("Iron Will", CardType.PASSIVE, "Increases survivability",
             hp_bonus=80, defense_bonus=5),
        Card("Battle Fury", CardType.PASSIVE, "Attack faster",
             attack_speed_bonus=0.3, attack_bonus=5),
    ]


def create_rogue_deck() -> List[Card]:
    """Create a rogue starter deck for testing."""
    return [
        Card("Twin Daggers", CardType.WEAPON, "Fast dual weapons",
             damage=12, attack_speed_bonus=0.8),
        Card("Shadow Cloak", CardType.ARMOR, "Light armor for mobility",
             defense_bonus=3, dodge_chance_bonus=15.0),
        Card("Assassin's Mark", CardType.PASSIVE, "Deadly precision",
             crit_chance_bonus=20.0, crit_damage_bonus=0.8),
        Card("Shadow Step", CardType.PASSIVE, "Evasive maneuvers",
             dodge_chance_bonus=10.0, attack_speed_bonus=0.2),
        Card("Lucky Strike", CardType.PASSIVE, "Fortune favors the bold",
             luck_bonus=20, crit_chance_bonus=5.0),
    ]


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

        # Choose deck type
        print(f"\nChoose a deck for {name}:")
        print("  1. Balanced (balanced stats)")
        print("  2. Mage (high magic attack, mana regen)")
        print("  3. Warrior (high HP and defense)")
        print("  4. Rogue (high crit, dodge, attack speed)")

        deck_choice = input("Enter choice (1-4): ").strip()
        if deck_choice == "2":
            deck = create_mage_deck()
        elif deck_choice == "3":
            deck = create_warrior_deck()
        elif deck_choice == "4":
            deck = create_rogue_deck()
        else:
            deck = create_starter_deck()

        player.equip_deck(deck)

        print(f"\n{player.name}'s deck:")
        for card in deck:
            print(f"  - {card}")

        players.append(player)

    print("\n" + "="*60)
    print("ENTERING THE TOWER")
    print("="*60)

    # Tower climbing
    tower = Tower()
    active_players = players.copy()

    while active_players:
        floor = active_players[0].current_floor + 1

        print(f"\n{'#'*60}")
        print(f"FLOOR {floor}")
        print(f"{'#'*60}")

        # Each active player attempts this floor
        for player in active_players[:]:  # Copy list to modify during iteration
            player.current_floor = floor

            # Generate enemies for this floor
            enemies = tower.generate_enemies(floor)

            # Battle
            won = Combat.battle(player, enemies)

            if won:
                # Player beat the floor
                player.reset_for_floor()  # Heal for next floor
                print(f"{player.name} advances to floor {floor + 1}!")
            else:
                # Player escaped
                active_players.remove(player)
                print(f"{player.name} is out of the competition!")

        # Check if we've reached the top or all players are out
        if not active_players:
            break

        if floor >= Tower.MAX_FLOORS:
            print("\nTOP OF THE TOWER REACHED!")
            break

    # Final results
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)

    players.sort(key=lambda p: p.current_floor, reverse=True)
    for i, player in enumerate(players, 1):
        status = f"ESCAPED at floor {player.escaped_floor}" if player.escaped_floor else "VICTORIOUS"
        print(f"{i}. {player.name} - Floor {player.current_floor} ({status})")


if __name__ == "__main__":
    main()
