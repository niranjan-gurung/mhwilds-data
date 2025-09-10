from typing import Any
from abc import ABC, abstractmethod
import re

class BaseWeapon(ABC):
  def __init__(self, weapon_type: str):
    self.weapon_type = weapon_type
  
  """ 
  Base structure for all weapons
  """
  def get_base_weapon_structure(self) -> dict[str, Any]:
    return {
      "name": "",
      "description": "",
      "weaponType": self.weapon_type,
      "defense": 0,
      "rarity": 1,
      "slot": [],
      "affinity": 0,
      "damage": {
        "raw": 0,
        "display": 0
      },
      "element": {},
      "skills": []
    }

  @abstractmethod
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    """Get weapon-specific fields that extend the base structure"""
    pass

  @abstractmethod
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    """Parse a weapon from table row data"""
    pass

  def create_weapon(self, cells: list, headers: list) -> dict[str, Any]:
    weapon = self.get_base_weapon_structure()
    weapon.update(self.get_weapon_specific_fields())

    parsed_data = self.parse_weapon_from_row(cells, headers)
    weapon.update(parsed_data)

    return weapon

class MeleeWeaponParser(BaseWeapon):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    return {
      "sharpness": {
        "red": 0,
        "orange": 0,
        "yellow": 0,
        "green": 0,
        "blue": 0,
        "white": 0,
        "purple": 0
      }
    }
      
  def parse_common_melee_fields(self, cells: list) -> dict[str, Any]:
    def get_cell_text(index):
      return cells[index].get_text(strip=True)

    return {
      'name': get_cell_text(0),
      'defense': 0 if get_cell_text(7) == '' else int(get_cell_text(7)),
      'rarity': int(get_cell_text(3)),
      # if slot column is empty, then don't append anything into slot list
      'slot': [
        int(val) for i in [22, 23, 24] if (val := get_cell_text(i)) != ''
      ],
      'affinity': 0 if get_cell_text(6) == '' else int(round(float(get_cell_text(6)) * 100)),
      'damage': {
        'raw': int(get_cell_text(5)),
        'display': int(get_cell_text(4))
      },
      'element': self._parse_element(get_cell_text(8), get_cell_text(9)),
      'sharpness': {
        'red': int(get_cell_text(10)),
        'orange': int(get_cell_text(11)),
        'yellow': int(get_cell_text(12)),
        'green': 0 if get_cell_text(13) == '' else int(get_cell_text(13)),
        'blue': 0 if get_cell_text(14) == '' else int(get_cell_text(14)),
        'white': 0 if get_cell_text(15) == '' else int(get_cell_text(15)),
        'purple': 0
      }
    }
  
  # helper method
  def _parse_element(self, element: str, value: str) -> dict:
    if element and element != '-':
      return {
        'type': element,
        'raw': round(int(value) / 10),
        'display': int(value)
      }
    else:
      return {}

class GenericMeleeParser(MeleeWeaponParser):
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    return self.parse_common_melee_fields(cells)
  
class RangedWeaponParser(BaseWeapon):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    return {}
  
  def parse_common_ranged_fields(self, cells: list, headers: list) -> dict[str, Any]:
    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    return {
        'name': get_cell_text(0),
        'defense': 0 if get_cell_text(7) == '' else int(get_cell_text(7)),
        'rarity': int(get_cell_text(3)),
        # if slot column is empty, then don't append anything into slot list
        'slot': [
          int(val) for i in [9, 10, 11] if (val := get_cell_text(i)) != ''
        ],
        'affinity': 0 if get_cell_text(6) == '' else int(round(float(get_cell_text(6)) * 100)),
        'damage': {
          'raw': int(get_cell_text(5)),
          'display': int(get_cell_text(4))
        },
        'element':
          self._parse_element(get_cell_text(8), get_cell_text(9)) 
          if headers[9] == 'Element Attack'
          else {}
      }
    
  # helper methods
  def _parse_element(self, element: str, value: str) -> dict:
    if element and element != '-':
      return {
        'type': element,
        'raw': round(int(value) / 10),
        'display': int(value)
      }
    else:
      return {}
  
  def _parse_ammo_data(self, cells: list) -> list[dict]:
    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    types_raw = get_cell_text(12)
    levels_raw = get_cell_text(13)
    capacities_raw = get_cell_text(14)
    # rapids_raw = False

    types = [ammo_type.strip() for ammo_type in types_raw.split(',')]
    levels = list(map(int, re.findall(r'\d+', levels_raw)))
    capacities = list(map(int, re.findall(r'\d+', capacities_raw)))

    ammos = []

    # website ensures all types, levels, capacities have the same length
    for i in range(len(types)):
      try:
        ammo = {
          'type': types[i],
          'level': levels[i],
          'capacity': capacities[i],
          'rapid': False
        }
        ammos.append(ammo)
 
      except (ValueError, IndexError) as e:
        print(f"Warning: Failed to parse ammo data at index {i}: {e}")
        continue

    return ammos
  
  def _parse_coating_data(self, cells: list) -> list[dict]:
    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    coatings_raw = get_cell_text(16)
    coatings = [coating.replace('Coating', '').strip() for coating in coatings_raw.split(',')]
    return coatings
