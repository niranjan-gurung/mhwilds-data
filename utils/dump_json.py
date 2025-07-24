import json

"""
Save list of skill dicts as json for reference
"""
def dump_json(filename: str, data_obj: list[dict]):
  with open(f'data/{filename}.json', 'w') as f:
    json.dump(data_obj, f, indent=2)
  print(f'success: {filename} data saved as json')