from typing import Any
from .weapon_parser import MeleeWeaponParser

class Gunlance(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['shell'] = {
      'type': '',
      'power': 1
    }
    return base_fields
  
  def parse_weapon_from_row(self, cells: list) -> dict[str, Any]:
    """Parse gunlance-specific data from table row"""
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    parsed_data['shell'] = {
      'type': get_cell_text(25),
      'power': int(get_cell_text(26))
    }
    return parsed_data
  
class ChargeBlade(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['phial'] = ''
    return base_fields
  
  def parse_weapon_from_row(self, cells: list) -> dict[str, Any]:
    """Parse gunlance-specific data from table row"""
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    # value type is optional for chargeblade (needs to be defined in API model/dto)
    parsed_data['phial'] = {
      'type': get_cell_text(25)
    }
    return parsed_data

class SwitchAxe(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['phial'] = ''
    return base_fields
  
  def parse_weapon_from_row(self, cells: list) -> dict[str, Any]:
    """Parse gunlance-specific data from table row"""
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    parsed_data['phial'] = {
      'type': get_cell_text(25),
      'value': None if get_cell_text(26) == '' else int(get_cell_text(26))
    }
    return parsed_data
  
class InsectGlaive(MeleeWeaponParser):
  def get_weapon_specific_fields(self) -> dict[str, Any]:
    base_fields = super().get_weapon_specific_fields()
    base_fields['kinsectLevel'] = ''
    return base_fields
  
  def parse_weapon_from_row(self, cells: list) -> dict[str, Any]:
    """Parse gunlance-specific data from table row"""
    parsed_data = self.parse_common_melee_fields(cells)

    def get_cell_text(index):
      return cells[index].get_text(strip=True)
    
    parsed_data['kinsectLevel'] = int(get_cell_text(25))
    return parsed_data