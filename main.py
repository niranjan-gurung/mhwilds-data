from armour_data import get_armour_data
from skill_data import get_skill_data

import requests

headers = {
  'Content-Type': 'application/json'
}

skill_data = get_skill_data()

res = requests.post(
  'http://localhost:5000/api/skills',
  headers=headers,
  json=skill_data
)

if res.status_code in[200, 201]:
  print(f'successfully added data: {res}')
else:
  print(f'error adding data: {res.status_code} - {res.text}')
