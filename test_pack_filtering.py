#!/usr/bin/env python3
"""Test weapon pack filtering logic."""

from tradeoff_rpg import (
    Card, CardType, CardClass, WeaponType,
    create_card_packs, open_pack, get_compatible_weapon_types
)

def test_quiver_filtering():
    """Test that quivers cannot be drawn without a bow."""
    print("="*60)
    print("TEST: Quiver cannot be drawn as first weapon")
    print("="*60)

    packs = create_card_packs()

    # Simulate drawing from Physical Weapons pack with no weapons equipped
    # compatible_types = None (no weapons equipped)
    # is_weapon_pack = True

    draws = []
    for _ in range(100):
        card = open_pack(packs["Physical Weapons"], player=None, compatible_weapon_types=None, is_weapon_pack=True)
        if card and card.card_type == CardType.WEAPON:
            draws.append(card.weapon_type)

    quiver_count = sum(1 for wt in draws if wt == WeaponType.QUIVER)
    print(f"Drew {len(draws)} weapons from Physical Weapons pack")
    print(f"Quivers drawn: {quiver_count}")

    if quiver_count == 0:
        print("✓ PASS: No quivers drawn without a bow")
    else:
        print("✗ FAIL: Quivers were drawn without a bow!")

    print()

def test_bow_quiver_filtering():
    """Test that quivers CAN be drawn after a bow."""
    print("="*60)
    print("TEST: Quiver CAN be drawn with a bow equipped")
    print("="*60)

    packs = create_card_packs()

    # Create a mock bow
    bow = Card("Test Bow", CardType.WEAPON, CardClass.EQUIPMENT, "Test bow", weapon_type=WeaponType.BOW)
    equipped_weapons = [bow]

    # Get compatible types (should include QUIVER)
    compatible_types = get_compatible_weapon_types(equipped_weapons)
    print(f"Compatible types with bow: {[wt.value for wt in compatible_types]}")

    # Draw from Physical Weapons pack
    draws = []
    for _ in range(100):
        card = open_pack(packs["Physical Weapons"], player=None, compatible_weapon_types=compatible_types, is_weapon_pack=True)
        if card and card.card_type == CardType.WEAPON:
            draws.append(card.weapon_type)

    quiver_count = sum(1 for wt in draws if wt == WeaponType.QUIVER)
    print(f"Drew {len(draws)} weapons from Physical Weapons pack")
    print(f"Quivers drawn: {quiver_count}")

    if quiver_count > 0:
        print("✓ PASS: Quivers can be drawn with a bow")
    else:
        print("⚠ WARNING: No quivers drawn (might be unlucky)")

    print()

def test_sword_filtering():
    """Test that only swords and shields can be drawn after a sword."""
    print("="*60)
    print("TEST: Only compatible weapons after sword")
    print("="*60)

    packs = create_card_packs()

    # Create a mock sword
    sword = Card("Test Sword", CardType.WEAPON, CardClass.EQUIPMENT, "Test sword", weapon_type=WeaponType.SWORD)
    equipped_weapons = [sword]

    # Get compatible types (should be SWORD and SHIELD)
    compatible_types = get_compatible_weapon_types(equipped_weapons)
    print(f"Compatible types with sword: {[wt.value for wt in compatible_types]}")

    # Draw from Physical Weapons pack
    draws = []
    for _ in range(50):
        card = open_pack(packs["Physical Weapons"], player=None, compatible_weapon_types=compatible_types, is_weapon_pack=True)
        if card and card.card_type == CardType.WEAPON:
            draws.append(card.weapon_type)

    invalid_draws = [wt for wt in draws if wt not in compatible_types]
    print(f"Drew {len(draws)} weapons from Physical Weapons pack")
    print(f"Invalid weapons drawn: {len(invalid_draws)}")

    if len(invalid_draws) == 0:
        print("✓ PASS: Only compatible weapons drawn")
    else:
        print(f"✗ FAIL: Invalid weapons drawn: {invalid_draws}")

    print()

if __name__ == "__main__":
    test_quiver_filtering()
    test_bow_quiver_filtering()
    test_sword_filtering()
    print("="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
