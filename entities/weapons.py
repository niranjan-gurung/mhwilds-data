from typing import Any
from .weapon_parser import MeleeWeaponParser, RangedWeaponParser

"""
Parse gunlance specific data from table row
"""
class Gunlance(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['shell'] = {
      'type': '',
      'power': 1
    }
    return base_fields
  
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)

    parsed_data['shell'] = {
      'type': get_cell_text(25),
      'power': int(get_cell_text(26))
    }
    return parsed_data
  
"""
Parse chargeblade specific data from table row
"""
class ChargeBlade(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['phial'] = ''
    return base_fields
  
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    # value type is optional for chargeblade (needs to be defined in API model/dto)
    parsed_data['phial'] = {
      'type': get_cell_text(25).removesuffix(' Phial')
    }
    return parsed_data

"""
Parse switchaxe specific data from table row
"""
class SwitchAxe(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['phial'] = ''
    return base_fields
  
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    parsed_data['phial'] = {
      'type': get_cell_text(25).removesuffix(' Phial'),
      'value': None if get_cell_text(26) == '' else int(get_cell_text(26))
    }
    return parsed_data

"""
Parse insect glaive specific data from table row
"""
class InsectGlaive(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['kinsectLevel'] = ''
    return base_fields
  
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    parsed_data['kinsectLevel'] = int(get_cell_text(25))
    return parsed_data

"""
Parse light bowgun specific data from table row
"""
class LightBowgun(RangedWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields.update({
      'ammo': [],
      'specialAmmo': ''
    })
    return base_fields
  
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    parsed_data = self.parse_common_ranged_fields(cells, headers)

    def get_cell_text(index) -> str:
      return cells[index].get_text(strip=True)
    
    parsed_data['ammo'] = self._parse_ammo_data(cells)
    parsed_data['specialAmmo'] = get_cell_text(18).replace('?', '')
    return parsed_data
  
"""
Parse heavy bowgun specific data from table row
"""
class HeavyBowgun(RangedWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['ammo'] = []
    return base_fields
  
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    parsed_data = self.parse_common_ranged_fields(cells, headers)
    parsed_data['ammo'] = self._parse_ammo_data(cells)
    return parsed_data
  
"""
Parse bow specific data from table row
"""
class Bow(RangedWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['coating'] = []
    return base_fields
  
  def parse_weapon_from_row(self, cells: list, headers: list) -> dict[str, Any]:
    parsed_data = self.parse_common_ranged_fields(cells, headers)
    parsed_data['coating'] = self._parse_coating_data(cells)
    return parsed_data