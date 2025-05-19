# import requests
# import re

# """
# Builds a dictionary mapping skill names to their IDs from the API
# """
# def build_skills_lookup(api_base_url='http://localhost:5000/api'):
#   skills_lookup = {}
#   try:
#     response = requests.get(f"{api_base_url}/skills")
#     if response.status_code == 200:
#       skills = response.json()
#       for skill in skills:
#         skills_lookup[skill['name']] = skill['id']
#     return skills_lookup
#   except Exception as e:
#     print(f"Error building skills lookup: {e}")
#     return {}
  
# """
# Retrieves the skill rank for a given skill ID and level
# """
# def get_skill_rank_data(skill_id, skill_level, api_base_url='http://localhost:5000/api'):
#   try:
#     response = requests.get(f"{api_base_url}/skills/{skill_id}")
#     if response.status_code == 200:
#       skill_data = response.json()
#       for rank in skill_data.get('ranks', []):
#         if rank['level'] == skill_level:
#           return rank   # from ranks list: get rank object that matches 'skill_level'
#     return None
#   except Exception as e:
#     print(f"Error getting skill rank data: {e}")
#     return None

# def parse_skill(skill_string) -> tuple:
#   match = re.match(r'(.+)\s\+(\d+)', skill_string)
#   if match:
#     skill_name = match.group(1)         # extract skill name (str)
#     skill_level = int(match.group(2))   # extract skill level (int)
#     return skill_name, skill_level
#   return None, None

# """
# Helper method - roman numeral to int
# """
# def roman_numeral_to_int(roman, roman_to_int):
#   result = 0
#   prev_value = 0
#   for char in reversed(roman):
#     value = roman_to_int[char]
#     if value < prev_value:
#       result -= value
#     else:
#       result += value
#     prev_value = value
#   return result
