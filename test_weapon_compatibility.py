#!/usr/bin/env python3
"""
Test script for weapon compatibility checking during pack opening.
"""

from tradeoff_rpg import (
    Card, CardType, CardClass, WeaponType,
    get_compatible_weapon_types, can_equip_weapon
)

# Create test weapon cards
sword = Card("Sword", CardType.WEAPON, CardClass.EQUIPMENT, "A sword", weapon_type=WeaponType.SWORD)
bow = Card("Bow", CardType.WEAPON, CardClass.EQUIPMENT, "A bow", weapon_type=WeaponType.BOW)
quiver = Card("Quiver", CardType.WEAPON, CardClass.EQUIPMENT, "A quiver", weapon_type=WeaponType.QUIVER)
shield = Card("Shield", CardType.WEAPON, CardClass.EQUIPMENT, "A shield", weapon_type=WeaponType.SHIELD)
dagger = Card("Dagger", CardType.WEAPON, CardClass.EQUIPMENT, "A dagger", weapon_type=WeaponType.DAGGER)
greatsword = Card("Greatsword", CardType.WEAPON, CardClass.EQUIPMENT, "A greatsword", weapon_type=WeaponType.GREATSWORD)
wand = Card("Wand", CardType.WEAPON, CardClass.EQUIPMENT, "A wand", weapon_type=WeaponType.WAND)

print("="*60)
print("WEAPON COMPATIBILITY TESTS")
print("="*60)

# Test 1: No weapons equipped - all should be compatible
print("\nTest 1: No weapons equipped")
equipped = []
print(f"  Equipped: None")
print(f"  Can equip Sword? {can_equip_weapon(sword, equipped)}")  # Should be True
print(f"  Can equip Bow? {can_equip_weapon(bow, equipped)}")      # Should be True
print(f"  Compatible types: All weapons allowed")

# Test 2: Sword equipped - can equip another sword or shield
print("\nTest 2: Sword equipped")
equipped = [sword]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip Sword? {can_equip_weapon(sword, equipped)}")      # Should be True
print(f"  Can equip Shield? {can_equip_weapon(shield, equipped)}")    # Should be True
print(f"  Can equip Quiver? {can_equip_weapon(quiver, equipped)}")    # Should be False
print(f"  Can equip Bow? {can_equip_weapon(bow, equipped)}")          # Should be False
compatible = get_compatible_weapon_types(equipped)
print(f"  Compatible types: {[wt.value for wt in compatible] if compatible else 'All'}")

# Test 3: Bow equipped - can equip quiver or dagger
print("\nTest 3: Bow equipped")
equipped = [bow]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip Quiver? {can_equip_weapon(quiver, equipped)}")    # Should be True
print(f"  Can equip Dagger? {can_equip_weapon(dagger, equipped)}")    # Should be True
print(f"  Can equip Sword? {can_equip_weapon(sword, equipped)}")      # Should be False
print(f"  Can equip Shield? {can_equip_weapon(shield, equipped)}")    # Should be False
compatible = get_compatible_weapon_types(equipped)
print(f"  Compatible types: {[wt.value for wt in compatible] if compatible else 'All'}")

# Test 4: Sword + Shield equipped - no more weapons allowed
print("\nTest 4: Sword + Shield equipped")
equipped = [sword, shield]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip another Sword? {can_equip_weapon(sword, equipped)}")  # Should be False
print(f"  Can equip Bow? {can_equip_weapon(bow, equipped)}")              # Should be False
compatible = get_compatible_weapon_types(equipped)
print(f"  Compatible types: {[wt.value for wt in compatible] if compatible is not None else 'All' if compatible is None else 'None'}")

# Test 5: Bow + Quiver equipped - no more weapons allowed
print("\nTest 5: Bow + Quiver equipped")
equipped = [bow, quiver]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip Dagger? {can_equip_weapon(dagger, equipped)}")    # Should be False
print(f"  Can equip Sword? {can_equip_weapon(sword, equipped)}")      # Should be False
compatible = get_compatible_weapon_types(equipped)
print(f"  Compatible types: {[wt.value for wt in compatible] if compatible is not None else 'All' if compatible is None else 'None'}")

# Test 6: Greatsword equipped - no more weapons allowed (two-handed)
print("\nTest 6: Greatsword equipped (two-handed)")
equipped = [greatsword]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip another Greatsword? {can_equip_weapon(greatsword, equipped)}")  # Should be False
print(f"  Can equip Shield? {can_equip_weapon(shield, equipped)}")                  # Should be False
compatible = get_compatible_weapon_types(equipped)
print(f"  Compatible types: {[wt.value for wt in compatible] if compatible is not None else 'All' if compatible is None else 'None'}")

# Test 7: Dagger equipped - can equip bow
print("\nTest 7: Dagger equipped")
equipped = [dagger]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip Bow? {can_equip_weapon(bow, equipped)}")          # Should be True
print(f"  Can equip Sword? {can_equip_weapon(sword, equipped)}")      # Should be False
print(f"  Can equip another Dagger? {can_equip_weapon(dagger, equipped)}")  # Should be False
compatible = get_compatible_weapon_types(equipped)
print(f"  Compatible types: {[wt.value for wt in compatible] if compatible else 'All'}")

# Test 8: Wand equipped - can equip another wand
print("\nTest 8: Wand equipped")
equipped = [wand]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip another Wand? {can_equip_weapon(wand, equipped)}")  # Should be True
print(f"  Can equip Sword? {can_equip_weapon(sword, equipped)}")        # Should be False
compatible = get_compatible_weapon_types(equipped)
print(f"  Compatible types: {[wt.value for wt in compatible] if compatible else 'All'}")

# Test 9: Non-weapon cards should always be compatible
print("\nTest 9: Non-weapon cards are always compatible")
armor = Card("Armor", CardType.ARMOR, CardClass.EQUIPMENT, "An armor")
equipped = [sword, shield]
print(f"  Equipped: {', '.join([w.name for w in equipped])}")
print(f"  Can equip Armor? {can_equip_weapon(armor, equipped)}")  # Should be True

print("\n" + "="*60)
print("ALL TESTS COMPLETED")
print("="*60)
