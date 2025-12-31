#!/usr/bin/env python3
"""Test script for health regen functionality."""

import sys
sys.path.insert(0, '/home/user/tradeoff_rpg')

from tradeoff_rpg import Player, Card, CardType, CardClass

def test_base_health_regen():
    """Test that player has base health regen of 5."""
    player = Player("Test Hero")
    assert player.base_health_regen == 5, f"Expected base_health_regen=5, got {player.base_health_regen}"
    assert player.health_regen == 5, f"Expected health_regen=5, got {player.health_regen}"
    print("✓ Base health regen is 5")

def test_health_regen_regeneration():
    """Test that regenerate_health() works correctly."""
    player = Player("Test Hero")
    player.current_hp = 50  # Set HP to 50
    player.regenerate_health()
    assert player.current_hp == 55, f"Expected current_hp=55, got {player.current_hp}"
    print("✓ Health regeneration works (50 -> 55)")

    # Test that it doesn't exceed max HP
    player.current_hp = player.max_hp - 2
    player.regenerate_health()
    assert player.current_hp == player.max_hp, f"Expected current_hp={player.max_hp}, got {player.current_hp}"
    print("✓ Health regen caps at max HP")

def test_regeneration_card():
    """Test that Regeneration card increases health_regen."""
    player = Player("Test Hero")

    # Create a Regeneration 1 card (+2 health regen)
    regen_card = Card(
        "Regeneration 1", CardType.PASSIVE, CardClass.STAT,
        "+2 Health Regen",
        health_regen_bonus=2
    )

    player.deck.append(regen_card)
    player.active_cards.append(regen_card)
    player._apply_card_bonuses()

    assert player.health_regen == 7, f"Expected health_regen=7, got {player.health_regen}"
    print("✓ Regeneration 1 card works (+2 health regen)")

    # Test regeneration with the card
    player.current_hp = 50
    player.regenerate_health()
    assert player.current_hp == 57, f"Expected current_hp=57, got {player.current_hp}"
    print("✓ Health regeneration with card works (50 -> 57)")

def test_resilience_card():
    """Test that Resilience card gives both HP and health regen."""
    player = Player("Test Hero")

    # Create a Resilience 2 card (+30 HP, +2 health regen)
    resilience_card = Card(
        "Resilience 2", CardType.PASSIVE, CardClass.STAT,
        "+30 HP, +2 Health Regen",
        hp_bonus=30,
        health_regen_bonus=2
    )

    player.deck.append(resilience_card)
    player.active_cards.append(resilience_card)
    player._apply_card_bonuses()

    assert player.max_hp == 130, f"Expected max_hp=130, got {player.max_hp}"
    assert player.health_regen == 7, f"Expected health_regen=7, got {player.health_regen}"
    print("✓ Resilience 2 card works (+30 HP, +2 health regen)")

def test_vampirism_card():
    """Test that Vampirism card gives health regen but reduces defense."""
    player = Player("Test Hero")

    # Create a Vampirism 3 card (+9 health regen, -9 defense)
    vampirism_card = Card(
        "Vampirism 3", CardType.PASSIVE, CardClass.STAT,
        "+9 Health Regen, -9 Defense",
        health_regen_bonus=9,
        defense_bonus=-9
    )

    player.deck.append(vampirism_card)
    player.active_cards.append(vampirism_card)
    player._apply_card_bonuses()

    assert player.health_regen == 14, f"Expected health_regen=14, got {player.health_regen}"
    assert player.defense == -4, f"Expected defense=-4, got {player.defense}"
    print("✓ Vampirism 3 card works (+9 health regen, -9 defense)")

def test_card_serialization():
    """Test that health_regen_bonus is serialized correctly."""
    from tradeoff_rpg import card_to_dict, dict_to_card

    # Create a card with health_regen_bonus
    card = Card(
        "Test Card", CardType.PASSIVE, CardClass.STAT,
        "+5 Health Regen",
        health_regen_bonus=5
    )

    # Serialize and deserialize
    card_dict = card_to_dict(card)
    assert 'health_regen_bonus' in card_dict, "health_regen_bonus not in serialized card"
    assert card_dict['health_regen_bonus'] == 5, f"Expected health_regen_bonus=5, got {card_dict['health_regen_bonus']}"

    restored_card = dict_to_card(card_dict)
    assert restored_card.health_regen_bonus == 5, f"Expected restored health_regen_bonus=5, got {restored_card.health_regen_bonus}"
    print("✓ Card serialization works")

if __name__ == "__main__":
    print("Testing health regen functionality...\n")

    try:
        test_base_health_regen()
        test_health_regen_regeneration()
        test_regeneration_card()
        test_resilience_card()
        test_vampirism_card()
        test_card_serialization()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
