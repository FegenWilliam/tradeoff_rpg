#!/usr/bin/env python3
"""
Test script for save/load functionality
"""

import sys
import os

# Import from the main game file
from tradeoff_rpg import Player, Card, CardType, CardClass, save_game, load_game

def test_save_load():
    """Test that save and load functions work correctly."""
    print("Testing save/load functionality...")

    # Create a test player
    player1 = Player("TestHero")
    player1.level = 10
    player1.current_xp = 500
    player1.highest_floor = 250
    player1.bounty = 1000
    player1.ascension_slots = ["Ancestral Rage"]

    # Add some test cards to the deck
    from tradeoff_rpg import WeaponType

    card1 = Card(
        name="Test Sword",
        card_type=CardType.WEAPON,
        card_class=CardClass.EQUIPMENT,
        description="A test sword",
        attack_bonus=50,
        damage=50,
        weapon_type=WeaponType.SWORD
    )

    card2 = Card(
        name="Test Armor",
        card_type=CardType.ARMOR,
        card_class=CardClass.EQUIPMENT,
        description="Test armor",
        defense_bonus=30,
        hp_bonus=100
    )

    player1.deck = [card1, card2]

    # Save the player
    print("\n1. Saving player...")
    save_game(player1, "test_save.json")

    # Load the player
    print("\n2. Loading player...")
    player2 = load_game("test_save.json")

    # Verify the loaded player matches
    print("\n3. Verifying loaded data...")
    assert player2 is not None, "Failed to load player"
    assert player2.name == player1.name, f"Name mismatch: {player2.name} != {player1.name}"
    assert player2.level == player1.level, f"Level mismatch: {player2.level} != {player1.level}"
    assert player2.current_xp == player1.current_xp, f"XP mismatch: {player2.current_xp} != {player1.current_xp}"
    assert player2.highest_floor == player1.highest_floor, f"Highest floor mismatch: {player2.highest_floor} != {player1.highest_floor}"
    assert player2.bounty == player1.bounty, f"Bounty mismatch: {player2.bounty} != {player1.bounty}"
    assert player2.ascension_slots == player1.ascension_slots, f"Ascension slots mismatch: {player2.ascension_slots} != {player1.ascension_slots}"
    assert len(player2.deck) == len(player1.deck), f"Deck size mismatch: {len(player2.deck)} != {len(player1.deck)}"

    # Check card details
    assert player2.deck[0].name == "Test Sword", f"Card name mismatch: {player2.deck[0].name}"
    assert player2.deck[0].attack_bonus == 50, f"Card attack mismatch: {player2.deck[0].attack_bonus}"
    assert player2.deck[1].name == "Test Armor", f"Card name mismatch: {player2.deck[1].name}"
    assert player2.deck[1].defense_bonus == 30, f"Card defense mismatch: {player2.deck[1].defense_bonus}"

    print("\n✅ All tests passed!")

    # Cleanup
    os.remove("test_save.json")
    print("   Test file cleaned up.")

if __name__ == "__main__":
    test_save_load()
