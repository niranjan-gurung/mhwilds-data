from utils.charm_lookup import charm_lookup
from utils.deco_lookup import deco_lookup

def get_rarity(name: str, id: str) -> dict:
  lookup = {}
  if id == 'charm':
    lookup = charm_lookup
  elif id == 'deco':
    lookup = deco_lookup
  else:
    print('look table not found')
    
  if name in lookup:
    return lookup[name]
  else:
    return {'error': 'no lookup found'}