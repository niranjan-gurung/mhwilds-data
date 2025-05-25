from bs4 import BeautifulSoup
import requests
import requests.compat
import re
import json
import pprint
import time
from utils.common import (
  build_skills_lookup, 
  get_skill_rank_data, 
  parse_skill
)

import urllib3

# Suppress only the InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

def parse_armour(new_soup, all_armour_data, rank, rarity, skills_lookup):
  data: list = []

  if not new_soup:
    print("Error: new_soup is None. Cannot parse charm.")
    return None, rank, rarity
  
  nav = new_soup.find(name='nav', attrs={'role': 'navigation'})
  tables = new_soup.find_all('tbody')
  if len(tables) < 3:
    print("Required tables not found on page.")
    return []
    
  t2 = tables[1]    # piece type + resistances
  t3 = tables[2]    # piece slot info

  # extract basic armour data from tables
  rows = t2.find_all('tr')[1:]

  time.sleep(1)

  for row in rows:
    td = row.find_all('td')
    if len(td) < 8:
      print("Row doesn't have enough cells, skipping.")
      continue
        
    type = td[0].get_text(strip=True)
    name = td[1].get_text(strip=True)

    print(f"Parsing armour: '{name}'")
    
    # parse defense as an integer
    defense = int(td[2].get_text(strip=True))
    
    # parse resistance as integers
    resistances = {
      "fire": int(td[3].get_text(strip=True)),
      "water": int(td[4].get_text(strip=True)),
      "ice": int(td[5].get_text(strip=True)),
      "thunder": int(td[6].get_text(strip=True)),
      "dragon": int(td[7].get_text(strip=True))
    }

    # determine rank and rarity based on armor name
    if name == 'Conga Helm':
      rarity = 2
    elif name == 'Ingot Helm':
      rarity = 3
    elif name == 'G. Seikret Coil':
      rarity = 4
    elif name == 'Hope Mask \u03b1':
      rank = 'high'
      rarity = 5
    elif name == 'Ingot Helm \u03b1':
      rarity = 6
    elif name == 'Dober Helm \u03b1':
      rarity = 7
    elif name == 'Arkvulcan Helm \u03b1':
      rarity = 8

    # create the armour data structure
    armour_piece = {
      'name': name,
      'slug': name.lower().replace(' ', '-').replace('.', ''),
      'type': type.lower(),
      'rank': rank,
      'rarity': rarity,
      'defense': defense,
      'resistances': resistances,
      'slots': [],
      'skills': []  
    }
    
    data.append(armour_piece)

  # extract slots and skills information
  rows = t3.find_all('tr')[1:]

  for i, row in enumerate(rows):
    if i >= len(data):
      print(f"Index {i} out of range for data (length: {len(data)})")
      continue
        
    td = row.find_all('td')
    if len(td) < 3:
      print(f"Not enough cells in row {i}, skipping.")
      continue
        
    # extract slot information
    slot_text = td[2].get_text(strip=True)
    slot_values = re.findall(r'\[(\d+)\]', slot_text)
    slots = [{'level': int(slot)} for slot in slot_values if int(slot) != 0]
    data[i]['slots'] = slots

    # extract skill information
    if len(td) > 3 and td[3].get_text(strip=True):
      skills = td[3].find_all('div')

      for skill in skills:
        skill_name_level = skill.get_text(strip=True)
        print(f"Parsing skill: '{skill_name_level}'")
        skill_name, skill_level = parse_skill(skill_name_level)
        skill_id = skills_lookup.get(skill_name)
        if not skill_id:
          print(f"Unknown skill: {skill_name}")
          continue

        # get skill rank/level based on id: 
        skill_rank = get_skill_rank_data(skill_id, skill_level)
        if not skill_rank:
          print(f"Could not find rank ID for skill: {skill_name} level {skill_level}")
          continue

        # append skill rank info to armour piece:
        data[i]['skills'].append(skill_rank)

  all_armour_data.extend(data)

  # find link to next armour set
  next_armour = nav.find('ul') \
                   .find_all('li')[-1] \
                   .find('a')

  if next_armour and 'href' in next_armour.attrs:
    href = next_armour['href']
    next_armour_url = requests.compat.urljoin(url, href)
    new_res = requests.get(next_armour_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
    return new_soup, rank, rarity
  else:
    print("No next armour link found, ending scrape.")
    return None, rank, rarity

"""
Build armour piece object from webpage,
needs to match armour model/schema from API 
"""
def get_armour_data() -> list:
  """
  Scrapes armour data from the website and formats it for the API
  """
  skills_lookup = build_skills_lookup()
  if not skills_lookup:
    print("Failed to build skills lookup. Check API connection.")
    return []

  # navigate to the armour page
  homepage = soup.find(attrs={'data-sidebar': 'group-content'})
  a = homepage.find_all('a')
  armour_link = None
  
  for item in a:
    if item.text == 'Armor' and 'href' in item.attrs:
      href = item['href']
      ar_list_url = requests.compat.urljoin(url, href)
      new_res = requests.get(ar_list_url)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')
      armour_link = True
      break
  
  if not armour_link:
    print("Could not find the armour page link.")
    return []

  # get first armour set link (Hope armour)
  first_armour_link = new_soup.find('tr')   \
                              .find('td')   \
                              .find('a')

  all_armour_data = []
  rank = 'low'    # track rank transition
  rarity = 1

  if first_armour_link.text == 'Hope' and 'href' in first_armour_link.attrs:
    href = first_armour_link['href']
    armour_url = requests.compat.urljoin(url, href)
    new_res = requests.get(armour_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
  else:
    print("First armour link is not Hope or does not have href attribute.")
    return []

  #counter = 0
  # process each armour set page
  while True:
    new_soup, rank, rarity = parse_armour(new_soup, all_armour_data, rank, rarity, skills_lookup)
    if not new_soup:
      break
    #counter += 1
  return all_armour_data

# d = get_armour_data()
# pprint.pprint(d)

def post_armour_data(api_base_url='https://localhost:5001/api'):
  """
  Posts the scraped armour data to the API
  """
  armour_data = get_armour_data()
  if not armour_data:
    print("No armour data to post.")
    return
      
  print(f"Found {len(armour_data)} armour pieces to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/armours",
      data=json.dumps(armour_data),
      headers=headers,
      verify=False
    )
    
    if response.status_code == 201 or response.status_code == 207:
      print("Successfully posted armour data!")
      result = response.json()
      if 'errors' in result and result['errors']:
        print(f"Warning: Some items had errors: {result['errors']}")
      return True
    else:
      print(f"Failed to post armour data. Status code: {response.status_code}")
      print(f"Response: {response.text}")
      return False
  except Exception as e:
    print(f"Error posting armour data: {e}")
    return False