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

    # Special effects (to be expanded)
    special_effect: Optional[str] = None
    damage: int = 0  # For weapon cards

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

        # TODO: Implement full RPG stat system
        # Base stats (will be modified by cards)
        self.base_hp = 100
        self.base_attack = 10
        self.base_defense = 5

        # Current stats
        self.max_hp = self.base_hp
        self.current_hp = self.max_hp
        self.attack = self.base_attack
        self.defense = self.base_defense

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

        self.max_hp = self.base_hp + total_hp_bonus
        self.attack = self.base_attack + total_attack_bonus
        self.defense = self.base_defense + total_defense_bonus
        self.current_hp = min(self.current_hp, self.max_hp)

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

    def reset_for_floor(self):
        """Reset stats for a new floor (heal between floors for now)."""
        self.current_hp = self.max_hp

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
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return int(base * factor + (floor * 2.5 * factor))

    def _scale_attack(self, floor: int) -> int:
        """Scale attack based on floor number."""
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
        }
        factor = scaling_factor.get(self.enemy_type, 1.0)
        return int(base * factor + (floor * 0.8 * factor))

    def take_damage(self, damage: int) -> bool:
        """
        Enemy takes damage.
        Returns True if enemy is defeated.
        """
        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage
        return self.current_hp <= 0

    def __str__(self):
        return f"{self.name} - HP: {self.current_hp}/{self.max_hp}, ATK: {self.attack}, DEF: {self.defense}"


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
    Combat system for player vs enemies.
    """
    @staticmethod
    def battle(player: Player, enemies: List[Enemy]) -> bool:
        """
        Execute combat between player and enemies.
        Returns True if player wins, False if player escaped.
        """
        print(f"\n{'='*60}")
        print(f"FLOOR {player.current_floor} - BATTLE START!")
        print(f"{'='*60}")
        print(f"{player.name}: {player.current_hp}/{player.max_hp} HP")
        for i, enemy in enumerate(enemies, 1):
            print(f"  Enemy {i}: {enemy}")
        print()

        turn = 0
        while enemies and player.is_alive:
            turn += 1
            print(f"--- Turn {turn} ---")

            # Player attacks first enemy
            target = enemies[0]
            damage = player.get_weapon_damage()
            print(f"{player.name} attacks {target.name} for {damage} damage!")

            if target.take_damage(damage):
                print(f"{target.name} defeated!")
                enemies.pop(0)
                if not enemies:
                    print(f"\n{player.name} wins the battle!")
                    return True

            # Enemies attack player
            for enemy in enemies:
                damage = enemy.attack
                print(f"{enemy.name} attacks {player.name} for {damage} damage!")

                if player.take_damage(damage):
                    print(f"\n{player.name} HP dropped to 1! AUTO-ESCAPE activated!")
                    print(f"{player.name} escaped from floor {player.current_floor}.")
                    return False

            print(f"{player.name}: {player.current_hp}/{player.max_hp} HP\n")

        return True


def create_starter_deck() -> List[Card]:
    """Create a basic starter deck for testing."""
    return [
        Card("Iron Sword", CardType.WEAPON, "A basic sword", damage=15),
        Card("Leather Armor", CardType.ARMOR, "Basic protection", defense_bonus=5),
        Card("Vitality Charm", CardType.PASSIVE, "Increases max HP", hp_bonus=50),
        Card("Power Ring", CardType.PASSIVE, "Increases attack", attack_bonus=5),
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

        # For now, use starter deck
        # TODO: Implement card selection system
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
