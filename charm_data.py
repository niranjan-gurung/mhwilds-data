from bs4 import BeautifulSoup
import requests
import requests.compat
import time
import re

import pprint

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

"""
Helper method - roman numeral to int
"""
def roman_numeral_to_int(roman):
  result = 0
  prev_value = 0
  for char in reversed(roman):
    value = roman_to_int[char]
    if value < prev_value:
      result -= value
    else:
      result += value
    prev_value = value
  return result

"""
Builds a dictionary mapping skill names to their IDs from the API
"""
def build_skills_lookup(api_base_url='http://localhost:5000/api'):
  skills_lookup = {}
  try:
    response = requests.get(f"{api_base_url}/skills")
    if response.status_code == 200:
      skills = response.json()
      for skill in skills:
        skills_lookup[skill['name']] = skill['id']
    return skills_lookup
  except Exception as e:
    print(f"Error building skills lookup: {e}")
    return {}
  
"""
Retrieves the skill rank for a given skill ID and level
"""
def get_skill_rank_data(skill_id, skill_level, api_base_url='http://localhost:5000/api'):
  try:
    response = requests.get(f"{api_base_url}/skills/{skill_id}")
    if response.status_code == 200:
      skill_data = response.json()
      for rank in skill_data.get('ranks', []):
        if rank['level'] == skill_level:
          return rank   # from ranks list: get rank object that matches 'skill_level'
    return None
  except Exception as e:
    print(f"Error getting skill rank data: {e}")
    return None
  

skills_lookup = build_skills_lookup()
if not skills_lookup:
  print("Failed to build skills lookup. Check API connection.")

homepage = soup.find(attrs={'data-sidebar': 'group-content'})
a = homepage.find_all('a')

for item in a:
  if item.text == 'Charms' and 'href' in item.attrs:
    href = item['href']
    ar_list_url = requests.compat.urljoin(url, href)
    new_res = requests.get(ar_list_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
    break

# get first charm link:
first_charm_link = new_soup.find('tbody') \
                      .find('tr') \
                      .find('a')

if first_charm_link.text == 'Marathon Charm I' and 'href' in first_charm_link.attrs:
  href = first_charm_link['href']
  charm_url = requests.compat.urljoin(url, href)
  new_res = requests.get(charm_url)
  new_soup = BeautifulSoup(new_res.text, 'html.parser')
else:
  print("First armour link is not Hope or does not have href attribute.")
  #return []

#counter = 0
data: list = []

while True:
  # all div sections that contains necessary charm info:
  content = new_soup.find_all(name='div', attrs={'class': 'my-8'})
  nav = content[0]
  main = content[1]           # main dev - contains charm name + description
  skill_info = content[2]     # need this to reference from skills data
  #nav_copy = content[3]       # same as nav - redundant

  charm_name = main.find('h2').get_text(strip=True)
  charm_desc = main.find('blockquote').get_text(strip=True)

  time.sleep(1)

  match = re.match(r'(.+)\s+([IV]+)', charm_name)

  if match:
    name = match.group(1)
    level_roman = match.group(2)
    roman_to_int = {'I': 1, 'V': 5}
    level = roman_numeral_to_int(level_roman)

  skill_name = skill_info.find('table')   \
                        .find('tbody')   \
                        .find('tr')      \
                        .find('td')      \
                        .get_text(strip=True)
  skill_level = level
  
  charm = next((item for item in data if item['name'] == name), None)

  # if charm doesn't exist, create a new charm object
  if charm is None:
    charm = {
      'name': name,
      'rank': []  # empty list for ranks, will fill it below
    }
    data.append(charm)  # add new charm to data

  charm_rank = {
    'name': charm_name,
    'desc': charm_desc,
    'level': level,
    'rarity': 1,
    'skills': []
  }

  print(f"Parsing charm: '{charm_name}'")
  skill_id = skills_lookup.get(skill_name)

  # get skill rank/level based on id: 
  skill_rank = get_skill_rank_data(skill_id, skill_level)
  # append skill rank info to skill object:
  charm_rank['skills'] = skill_rank
  charm['rank'].append(charm_rank)

  # navigate to next charm link:
  next_charm = nav.find('ul') \
                  .find_all('li')[1] \
                  .find('a')

  if next_charm and 'href' in next_charm.attrs:
    href = next_charm['href']
    next_charm_url = requests.compat.urljoin(url, href)
    new_res = requests.get(next_charm_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
  else:
    print("No next armour link found, ending scrape.")
    break
  #counter += 1

pprint.pprint(data)