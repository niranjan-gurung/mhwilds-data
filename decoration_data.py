from bs4 import BeautifulSoup
import requests
import requests.compat
import time
import re
import pprint
import json

from utils.common import build_skills_lookup, get_skill_rank_data
from utils.get_rarity import get_rarity

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

def parse_deco(new_soup, data, type, skills_lookup, is_dual_skill=False):
  if not new_soup:
    print("Error: new_soup is None. Cannot parse decoration.")
    return None
  
  content = new_soup.find_all(name='div', attrs={'class': 'my-8'})
  nav = content[0]
  main = content[1]           # main dev - contains deco name + description
  skill_info = content[2]     # need this to reference from skills data
  
  deco_name = main.find('h2').get_text(strip=True)
  deco_desc = main.find('blockquote').get_text(strip=True)
  deco_skill_level = skill_info.find_all('tr')
  
  if deco_name == 'Defense Jewel [1]':
    type = 'Armour'

  if '/' in deco_name:
    is_dual_skill = True

  skill_level = int(deco_skill_level[0]     \
                  .find_all('td')[1]        \
                  .get_text(strip=True)[2])
  rarity = get_rarity(deco_name, 'deco')

  if rarity is None:
    print(f'{deco_name} not found in lookup table')

  time.sleep(1)

  skill_name = skill_info.find('table')   \
                         .find('tbody')   \
                         .find_all('tr')

  if not is_dual_skill:
    skill = skill_name[0].find('td').get_text(strip=True)
  else:
    skill1 = skill_name[0].find('td').get_text(strip=True)
    skill2 = skill_name[1].find('td').get_text(strip=True)
    skill_level1 = skill_level
    skill_level2 = int(deco_skill_level[1]    \
                  .find_all('td')[1]          \
                  .get_text(strip=True)[2])

  decorations = {
    'name': deco_name,
    'description': deco_desc,
    'type': type,
    'rarity': rarity,
    'slot': skill_level,
    'skills': []
  }

  print(f"Parsing decoration: '{deco_name}'")

  if is_dual_skill:
    skill1_id = skills_lookup.get(skill1)
    skill2_id = skills_lookup.get(skill2)
    if skill1_id and skill2_id:
      skill1_rank = get_skill_rank_data(skill1_id, skill_level1)
      skill2_rank = get_skill_rank_data(skill2_id, skill_level2)
      if skill1_rank and skill2_rank:
        # append skill rank info to skill object:
        decorations['skills'].append(skill1_rank)
        decorations['skills'].append(skill2_rank)
  else:
    skill_id = skills_lookup.get(skill)
    if skill_id:
      # get skill rank/level based on id: 
      skill_rank = get_skill_rank_data(skill_id, skill_level)
      if skill_rank:
        # append skill rank info to skill object:
        decorations['skills'].append(skill_rank)

  data.append(decorations)

  # navigate to next deco link:
  next_deco = nav.find('ul') \
                 .find_all('li')[1] \
                 .find('a')

  if next_deco and 'href' in next_deco.attrs:
    href = next_deco['href']
    next_deco_url = requests.compat.urljoin(url, href)
    new_res = requests.get(next_deco_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
    return new_soup
  else:
    print("No next deco link found, ending scrape.")
    return None
  

def get_deco_data() -> list:
  data: list = []
  skills_lookup = build_skills_lookup()
  if not skills_lookup:
    print("Failed to build skills lookup. Check API connection.")

  homepage = soup.find(attrs={'data-sidebar': 'group-content'})
  a = homepage.find_all('a')

  for item in a:
    if item.text == 'Decorations' and 'href' in item.attrs:
      href = item['href']
      ar_list_url = requests.compat.urljoin(url, href)
      new_res = requests.get(ar_list_url)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')
      break

  # get first deco link:
  first_deco_link = new_soup.find('tbody')   \
                             .find('tr')      \
                             .find('a')

  if first_deco_link.text == 'Attack Jewel [1]' and 'href' in first_deco_link.attrs:
    href = first_deco_link['href']
    charm_url = requests.compat.urljoin(url, href)
    new_res = requests.get(charm_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
  else:
    print("First decoration link is not Attack Jewel [1] or does not have href attribute.")
    return []
  
  type = 'Weapon'
  #counter = 0
  # parse charm data: 
  while True:
    new_soup = parse_deco(new_soup, data, type, skills_lookup, is_dual_skill=False)
    if not new_soup:
      break
    #counter += 1
  
  return data

# d = get_deco_data()
# pprint.pprint(d)

def post_deco_data(api_base_url='https://localhost:5001/api'):
  """
  Posts the scraped decoration data to the API
  """
  deco_data = get_deco_data()
  if not deco_data:
    print("No decoration data to post.")
    return
  
  pprint.pprint(deco_data)
  print(f"Found {len(deco_data)} decorations to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/decorations",
      data=json.dumps(deco_data),
      headers=headers,
      verify=False
    )
    
    if response.status_code in (200, 201, 207):
      print("Successfully posted decoration data!")
      result = response.json()
      if 'errors' in result and result['errors']:
        print(f"Warning: Some items had errors: {result['errors']}")
      return True
    else:
      print(f"Failed to post decoration data. Status code: {response.status_code}")
      print(f"Response: {response.text}")
      return False
  except Exception as e:
    print(f"Error posting decoration data: {e}")
    return False