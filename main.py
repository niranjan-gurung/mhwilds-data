from armour_data import post_armour_data
from skill_data import get_skill_data
from charm_data import post_charm_data
from decoration_data import post_deco_data
import requests
import json

# skill_data = get_skill_data()
# headers = {'Content-Type': 'application/json'}
# res = requests.post(
#   'https://localhost:5001/api/skills',
#   headers=headers,
#   json=skill_data,
#   verify=False
# )

# try:
#   if res.status_code in (200, 201, 207):
#     print("Successfully posted skill data!")
#     result = res.json()
#     if 'errors' in result and result['errors']:
#       print(f"Warning: Some items had errors: {result['errors']}")
#     #return True
#   else:
#     print(f"Failed to post skill data. Status code: {res.status_code}")
#     print(f"Response: {res.text}")
#     #return False
# except Exception as e:
#   print(f"Error posting skill data: {e}")
#   #return False

#post_armour_data()
#post_charm_data()
post_deco_data()