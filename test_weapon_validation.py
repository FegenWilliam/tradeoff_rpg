#!/usr/bin/env python3
"""Test script for weapon dual wielding validation."""

from tradeoff_rpg import (
    Player, Card, CardType, CardClass, WeaponType
)

def test_dual_wield_swords():
    """Test that dual wielding swords is allowed."""
    print("Test 1: Dual wielding swords (should pass)")
    player = Player("Test Player")
    cards = [
        Card("Sword 1", CardType.WEAPON, CardClass.EQUIPMENT, "Sword",
             attack_bonus=50, weapon_type=WeaponType.SWORD),
        Card("Sword 2", CardType.WEAPON, CardClass.EQUIPMENT, "Sword",
             attack_bonus=50, weapon_type=WeaponType.SWORD),
    ]
    try:
        player.equip_deck(cards)
        print("✓ PASS: Dual wielding swords is allowed\n")
        return True
    except ValueError as e:
        print(f"✗ FAIL: {e}\n")
        return False

def test_dual_wield_wands():
    """Test that dual wielding wands is allowed."""
    print("Test 2: Dual wielding wands (should pass)")
    player = Player("Test Player")
    cards = [
        Card("Wand 1", CardType.WEAPON, CardClass.EQUIPMENT, "Wand",
             magic_attack_bonus=40, weapon_type=WeaponType.WAND),
        Card("Wand 2", CardType.WEAPON, CardClass.EQUIPMENT, "Wand",
             magic_attack_bonus=40, weapon_type=WeaponType.WAND),
    ]
    try:
        player.equip_deck(cards)
        print("✓ PASS: Dual wielding wands is allowed\n")
        return True
    except ValueError as e:
        print(f"✗ FAIL: {e}\n")
        return False

def test_dual_wield_greatsword_without_titans():
    """Test that dual wielding greatswords without Titan's Strength fails."""
    print("Test 3: Dual wielding greatswords without Titan's Strength (should fail)")
    player = Player("Test Player")
    cards = [
        Card("Greatsword 1", CardType.WEAPON, CardClass.EQUIPMENT, "Greatsword",
             attack_bonus=80, weapon_type=WeaponType.GREATSWORD),
        Card("Greatsword 2", CardType.WEAPON, CardClass.EQUIPMENT, "Greatsword",
             attack_bonus=80, weapon_type=WeaponType.GREATSWORD),
    ]
    try:
        player.equip_deck(cards)
        print("✗ FAIL: Dual wielding greatswords should not be allowed without Titan's Strength\n")
        return False
    except ValueError as e:
        print(f"✓ PASS: Correctly blocked dual wielding greatswords: {e}\n")
        return True

def test_dual_wield_greatsword_with_titans():
    """Test that dual wielding greatswords with Titan's Strength is allowed."""
    print("Test 4: Dual wielding greatswords with Titan's Strength (should pass)")
    player = Player("Test Player")
    cards = [
        Card("Titan's Strength", CardType.PASSIVE, CardClass.UNIQUE,
             "Can equip 2 Greatswords/Axes/Spears",
             special_effect="titans_strength"),
        Card("Greatsword 1", CardType.WEAPON, CardClass.EQUIPMENT, "Greatsword",
             attack_bonus=80, weapon_type=WeaponType.GREATSWORD),
        Card("Greatsword 2", CardType.WEAPON, CardClass.EQUIPMENT, "Greatsword",
             attack_bonus=80, weapon_type=WeaponType.GREATSWORD),
    ]
    try:
        player.equip_deck(cards)
        print("✓ PASS: Dual wielding greatswords with Titan's Strength is allowed\n")
        return True
    except ValueError as e:
        print(f"✗ FAIL: {e}\n")
        return False

def test_dual_wield_staff():
    """Test that dual wielding staves is not allowed."""
    print("Test 5: Dual wielding staves (should fail)")
    player = Player("Test Player")
    cards = [
        Card("Staff 1", CardType.WEAPON, CardClass.EQUIPMENT, "Staff",
             magic_attack_bonus=60, weapon_type=WeaponType.STAFF),
        Card("Staff 2", CardType.WEAPON, CardClass.EQUIPMENT, "Staff",
             magic_attack_bonus=60, weapon_type=WeaponType.STAFF),
    ]
    try:
        player.equip_deck(cards)
        print("✗ FAIL: Dual wielding staves should not be allowed\n")
        return False
    except ValueError as e:
        print(f"✓ PASS: Correctly blocked dual wielding staves: {e}\n")
        return True

def test_dual_wield_daggers():
    """Test that dual wielding daggers is not allowed without special card."""
    print("Test 6: Dual wielding daggers (should fail)")
    player = Player("Test Player")
    cards = [
        Card("Dagger 1", CardType.WEAPON, CardClass.EQUIPMENT, "Dagger",
             attack_bonus=40, weapon_type=WeaponType.DAGGER),
        Card("Dagger 2", CardType.WEAPON, CardClass.EQUIPMENT, "Dagger",
             attack_bonus=40, weapon_type=WeaponType.DAGGER),
    ]
    try:
        player.equip_deck(cards)
        print("✗ FAIL: Dual wielding daggers should not be allowed without special card\n")
        return False
    except ValueError as e:
        print(f"✓ PASS: Correctly blocked dual wielding daggers: {e}\n")
        return True

def test_triple_swords():
    """Test that triple wielding swords is not allowed."""
    print("Test 7: Triple wielding swords (should fail)")
    player = Player("Test Player")
    cards = [
        Card("Sword 1", CardType.WEAPON, CardClass.EQUIPMENT, "Sword",
             attack_bonus=50, weapon_type=WeaponType.SWORD),
        Card("Sword 2", CardType.WEAPON, CardClass.EQUIPMENT, "Sword",
             attack_bonus=50, weapon_type=WeaponType.SWORD),
        Card("Sword 3", CardType.WEAPON, CardClass.EQUIPMENT, "Sword",
             attack_bonus=50, weapon_type=WeaponType.SWORD),
    ]
    try:
        player.equip_deck(cards)
        print("✗ FAIL: Triple wielding swords should not be allowed\n")
        return False
    except ValueError as e:
        print(f"✓ PASS: Correctly blocked triple wielding swords: {e}\n")
        return True

def test_mixed_weapons():
    """Test that mixing sword and wand works."""
    print("Test 8: Mixing sword and wand (should pass)")
    player = Player("Test Player")
    cards = [
        Card("Sword", CardType.WEAPON, CardClass.EQUIPMENT, "Sword",
             attack_bonus=50, weapon_type=WeaponType.SWORD),
        Card("Wand", CardType.WEAPON, CardClass.EQUIPMENT, "Wand",
             magic_attack_bonus=40, weapon_type=WeaponType.WAND),
    ]
    try:
        player.equip_deck(cards)
        print("✓ PASS: Mixing sword and wand is allowed\n")
        return True
    except ValueError as e:
        print(f"✗ FAIL: {e}\n")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("WEAPON DUAL WIELDING VALIDATION TESTS")
    print("="*60)
    print()

    tests = [
        test_dual_wield_swords,
        test_dual_wield_wands,
        test_dual_wield_greatsword_without_titans,
        test_dual_wield_greatsword_with_titans,
        test_dual_wield_staff,
        test_dual_wield_daggers,
        test_triple_swords,
        test_mixed_weapons,
    ]

    results = [test() for test in tests]

    print("="*60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("="*60)

    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
