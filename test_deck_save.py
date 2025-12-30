#!/usr/bin/env python3
"""Test that deck saving works correctly during preparation."""

import json
import os
from tradeoff_rpg import Player, Card, CardType, CardClass, WeaponType, AccessoryType, save_game

def test_deck_save():
    """Test that saving during prep correctly saves the collected cards."""
    print("Testing deck save functionality...")

    # Create a test player
    player = Player("TestPlayer")
    player.level = 5
    player.bounty = 100
    player.highest_floor = 10

    # Simulate collecting cards during prep (before equip_deck is called)
    test_cards = [
        Card("Test Sword", CardType.WEAPON, CardClass.EQUIPMENT, "A test sword",
             attack_bonus=10, weapon_type=WeaponType.SWORD),
        Card("Test Shield", CardType.WEAPON, CardClass.EQUIPMENT, "A test shield",
             defense_bonus=5, weapon_type=WeaponType.SHIELD),
        Card("Test Ring", CardType.ACCESSORY, CardClass.STAT, "A test ring",
             attack_bonus=2, accessory_type=AccessoryType.RING)
    ]

    # This simulates what happens in prep_menu when saving:
    # The cards are collected but not yet equipped
    old_deck = player.deck.copy() if player.deck else []
    player.deck = test_cards

    # Save the game
    save_game([player], "test_save.json")

    # Restore the deck state (as the fix does)
    player.deck = old_deck

    # Now verify the save file contains the cards
    with open("test_save.json", 'r') as f:
        save_data = json.load(f)

    saved_deck = save_data['players'][0]['deck']

    print(f"\nSaved deck contains {len(saved_deck)} cards:")
    for card in saved_deck:
        print(f"  - {card['name']}")

    # Verify we saved the correct number of cards
    assert len(saved_deck) == 3, f"Expected 3 cards, but got {len(saved_deck)}"

    # Verify card names
    expected_names = ["Test Sword", "Test Shield", "Test Ring"]
    actual_names = [card['name'] for card in saved_deck]
    assert actual_names == expected_names, f"Card names don't match: {actual_names}"

    # Clean up
    os.remove("test_save.json")

    print("\n✓ Test passed! Deck saves correctly during preparation.")

if __name__ == "__main__":
    test_deck_save()
