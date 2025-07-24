from bs4 import BeautifulSoup
import requests
import requests.compat
import re
import json
import time
import config
from utils.dump_json import dump_json
from typing import Optional

from utils.common import (
  build_skills_lookup, 
  get_skill_rank_data, 
  parse_skill
)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
Get armours page url from homepage
"""
def find_armours_page_url() -> Optional[str]:
  res = requests.get(config.BASE_URL).content
  soup = BeautifulSoup(res, 'html.parser')
  homepage = soup.find(attrs={'data-sidebar': 'group-content'})
  if not homepage: 
    return None

  links = homepage.find_all('a')
  
  for item in links:
    if item.text == 'Armor' and 'href' in item.attrs:
      return requests.compat.urljoin(config.BASE_URL, item['href'])
    
  return None

"""
Rank and rarity lookup table
"""
def get_rank_and_rarity(name: str, current_rank: str, current_rarity: int) -> tuple[str, int]:
  # define rank and rarity transitions based on specific armor pieces
  rank_rarity_map = {
    'Conga Helm': ('low', 2),
    'Ingot Helm': ('low', 3),
    'G. Seikret Coil': ('low', 4),
    'Hope Mask α': ('high', 5),
    'Ingot Helm α': ('high', 6),
    'Dober Helm α': ('high', 7),
    'Arkvulcan Helm α': ('high', 8),
  }
  
  if name in rank_rarity_map:
    return rank_rarity_map[name]
  
  return current_rank, current_rarity

"""
Extract slot information from slot text
"""
def extract_slots(slot_text: str) -> list[int]:
  slot_values = re.findall(r'\[(\d+)\]', slot_text)
  return [int(slot) for slot in slot_values if int(slot) != 0]

"""
Extract skills information from skills lookup
"""
def extract_skills(skill_elements, skills_lookup: dict[str, int]) -> list[dict]:
  skills = []

  for skill in skill_elements:
    skill_name_level = skill.get_text(strip=True)
    print(f"Parsing skill: '{skill_name_level}'")

    skill_name, skill_level = parse_skill(skill_name_level)
    if not skill_name or not skill_level:
      print(f"Could not parse skill: {skill_name_level}")
      continue

    skill_id = skills_lookup.get(skill_name)
    if not skill_id:
      print(f"Unknown skill: {skill_name}")
      continue

    # get skill rank/level based on id: 
    skill_rank = get_skill_rank_data(skill_id, skill_level)
    if not skill_rank:
      print(f"Could not find rank ID for skill: {skill_name} level {skill_level}")
      continue

    skills.append(skill_rank)

  return skills

"""
Parse each armour page
"""
def parse_armour(
    soup: BeautifulSoup, 
    rank: str, 
    rarity: int, 
    skills_lookup: dict[str, int]
  ) -> tuple[list[dict], str, int]:

  if not soup:
    print("Error: soup is None. Cannot parse armour.")
    return [], rank, rarity
  
  tables = soup.find_all('tbody')
  if len(tables) < 3:
    print("Required tables not found on page.")
    return []
    
  t2rows = tables[1].find_all('tr')[1:]   # piece type + resistances
  t3rows = tables[2].find_all('tr')[1:]   # piece slot info

  armour_pieces = []

  for i, (t2rows, t3rows) in enumerate(zip(t2rows, t3rows)):
    try:
      t2cells = t2rows.find_all('td')
      if len(t2cells) < 8:
        print("Row doesn't have enough cells, skipping.")
        continue

      type = t2cells[0].get_text(strip=True)
      name = t2cells[1].get_text(strip=True)

      print(f"Parsing armour: '{name}'")

      # update rank and rarity from lookup table via armour name
      rank, rarity = get_rank_and_rarity(name, rank, rarity)

      # parse defense as an integer
      defense = int(t2cells[2].get_text(strip=True))

      # parse resistance as integers
      resistances = {
        "fire": int(t2cells[3].get_text(strip=True)),
        "water": int(t2cells[4].get_text(strip=True)),
        "ice": int(t2cells[5].get_text(strip=True)),
        "thunder": int(t2cells[6].get_text(strip=True)),
        "dragon": int(t2cells[7].get_text(strip=True))
      }

      t3cells = t3rows.find_all('td')
      if len(t3cells) < 3:
        print("Row doesn't have enough cells, skipping.")
        continue

      # extract slots
      slot_text = t3cells[2].get_text(strip=True)
      slots = extract_slots(slot_text)

      # extract skills
      skills = []
      if len(t3cells) > 3 and t3cells[3].get_text(strip=True):
        skill_elements = t3cells[3].find_all('div')
        skills = extract_skills(skill_elements, skills_lookup)

      # create the armour object
      armour_piece = {
        'name': name,
        'slug': name.lower().replace(' ', '-').replace('.', ''),
        'type': type.lower(),
        'rank': rank,
        'rarity': rarity,
        'defense': defense,
        'resistances': resistances,
        'slots': slots,
        'skills': skills  
      }

      armour_pieces.append(armour_piece)
      
    except (ValueError, IndexError) as e:
      print(f"Error parsing armour piece at index {i}: {e}")
      continue
    except Exception as e:
      print(f"Unexpected error parsing armour piece at index {i}: {e}")
      continue

  time.sleep(config.RATE_LIMIT)
  return armour_pieces, rank, rarity

"""
Find link to first armour set (Hope armour)
"""
def get_first_armour_url(soup: BeautifulSoup) -> Optional[str]:
  try:
    link = soup.find('tr')   \
               .find('td')   \
               .find('a')
    
    if link.text == 'Hope' and 'href' in link.attrs:
      return requests.compat.urljoin(config.BASE_URL, link['href'])
    
    print('first armour link is not Hope or does not contain href attribute')
    return None
  except Exception as e:
    print(f'Error getting first armour URL: {e}')
    return None

"""
Find link to next armour set
"""
def find_next_armour_url(soup: BeautifulSoup) -> Optional[str]:
  try:
    next_armour = soup.find('ul') \
                      .find_all('li')[-1] \
                      .find('a')
    if next_armour and 'href' in next_armour.attrs:
      return requests.compat.urljoin(config.BASE_URL, next_armour['href'])
    return None
  except Exception as e:
    print(f'Error finding next armour URL: {e}')
    return None
    
"""
Scrapes armour data from the website and builds armour object,
matches armour model/schema from API
"""
def get_armour_data() -> list[dict]:
  print('building skills lookup...')
  skills_lookup = build_skills_lookup()
  if not skills_lookup:
    print("Failed to build skills lookup. Check API connection.")
    return []

  # navigate to the armour page
  print('finding armours page...')
  try:
    armours_page_url = find_armours_page_url()
    if not armours_page_url:
      print("Could not find the armour page link.")
      return []
    
    res = requests.get(armours_page_url).content
    soup = BeautifulSoup(res, 'html.parser')

    # get first armour set link (Hope armour)
    first_armour_url = get_first_armour_url(soup)
    if not first_armour_url:
      return []
    
  except Exception as e:
    print(f'Error in get_armour_data: {e}')
    return []  

  print('start armour scraping...')
  all_armour_data = []
  rank = 'low'    # track rank transition
  rarity = 1
  current_url = first_armour_url
  
  # process each armour set page
  while current_url:
    try:
      print(f'fetching: {current_url}')
      res = requests.get(current_url).content
      soup = BeautifulSoup(res, 'html.parser')
      
      armour_pieces, rank, rarity = parse_armour(soup, rank, rarity, skills_lookup)
      all_armour_data.extend(armour_pieces)

      current_url = find_next_armour_url(soup)
      
      if not current_url:
        print('no more armour sets found, ending scraping process.')
        break
    except Exception as e:
      print(f'Error processing armour url {current_url}: {e}')
      break
      
  print(f'scraping finished. Found {len(all_armour_data)} armour pieces.')
  return all_armour_data

"""
Posts the scraped armour data to the API
"""
def post_armour_data(api_base_url: str = config.API_BASE_URL) -> bool:
  armour_data = get_armour_data()
  if not armour_data:
    print("No armour data to post.")
    return
      
  print(f"Found {len(armour_data)} armour pieces to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/armours/range",
      data=armour_data,
      headers=headers,
      verify=False,
      timeout=30
    )
    
    response.raise_for_status()
        
    print("Successfully posted armour data!")
    
    # dump json to file:
    dump_json('armours', armour_data)
    
    result = response.json()
    if 'errors' in result and result['errors']:
      print(f"Warning: Some items had errors: {result['errors']}")
    return True
  
  except requests.exceptions.RequestException as e:
    print(f"HTTP error posting armour data: {e}")
    return False
  except json.JSONDecodeError as e:
    print(f"Error parsing API response: {e}")
    return False
  except Exception as e:
    print(f"Unexpected error posting armour data: {e}")
    return False