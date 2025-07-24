from bs4 import BeautifulSoup
import requests
import requests.compat
import time
import json
import config
from utils.dump_json import dump_json
from typing import Optional

from utils.common import (
  build_skills_lookup, 
  get_skill_rank_data
)

from utils.get_rarity import get_rarity

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
Get decorations page url from homepage
"""
def find_decorations_page_url() -> Optional[str]:
  try:
    res = requests.get(config.BASE_URL).content
    soup = BeautifulSoup(res, 'html.parser')
    homepage = soup.find(attrs={'data-sidebar': 'group-content'})
    
    if not homepage:
      return None

    links = homepage.find_all('a')
    for item in links:
      if item.text == 'Decorations' and 'href' in item.attrs:
        return requests.compat.urljoin(config.BASE_URL, item['href'])
    
    return None
  except Exception as e:
    print(f"Error finding decorations page URL: {e}")
    return None

"""
Determine decoration type based on decoration name
"""
def get_decoration_type(deco_name: str, current_type: str) -> str:
  # transition from weapon to armour type
  if deco_name == 'Defense Jewel [1]':
    return 'Armour'
  return current_type

"""
Find the next decoration URL from navigation
"""
def find_next_decoration_url(nav) -> Optional[str]:
  try:
    nav_items = nav.find('ul').find_all('li')
    if len(nav_items) > 1:
      next_deco = nav_items[1].find('a')
      if next_deco and 'href' in next_deco.attrs:
        return requests.compat.urljoin(config.BASE_URL, next_deco['href'])
      
    return None
  except Exception as e:
    print(f"Error finding next decoration URL: {e}")
    return None

"""
Get the first decoration URL from the decorations listing page
"""
def get_first_decoration_url(soup: BeautifulSoup) -> Optional[str]:
  try:
    link = soup.find('tbody').find('tr').find('a')
      
    if link.text == 'Attack Jewel [1]' and 'href' in link.attrs:
      return requests.compat.urljoin(config.BASE_URL, link['href'])
      
    print("First decoration link is not Attack Jewel [1] or does not have href attribute.")
    return None
  except Exception as e:
    print(f"Error getting first decoration URL: {e}")
    return None
    
"""
Extract slot level from decoration skill info
"""
def extract_slot_level(skill_info) -> int:
  try:
    skill_level_rows = skill_info.find_all('tr')
    if skill_level_rows:
      skill_level_cell = skill_level_rows[0].find_all('td')[1]
      skill_level_text = skill_level_cell.get_text(strip=True)
      return int(skill_level_text[2])     # extract number from "Lv1", "Lv2", etc.
  except (IndexError, ValueError, AttributeError) as e:
    print(f"Error extracting slot level: {e}")
  return 1  # default slot level

"""
Extract skills from decoration skill info section
"""
def extract_skills(
    skill_info, 
    skills_lookup: 
    dict[str, int], 
    is_dual_skill: bool = False
  ) -> list[dict]:

  skills = []
  
  try:
    skill_table = skill_info.find('table').find('tbody').find_all('tr')
    skill_level_rows = skill_info.find_all('tr')
    
    if is_dual_skill and len(skill_table) >= 2 and len(skill_level_rows) >= 2:
      # dual skill decoration
      skill1_name = skill_table[0].find('td').get_text(strip=True)
      skill2_name = skill_table[1].find('td').get_text(strip=True)
      
      skill1_level = int(skill_level_rows[0].find_all('td')[1].get_text(strip=True)[2])
      skill2_level = int(skill_level_rows[1].find_all('td')[1].get_text(strip=True)[2])
      
      # process first skill
      skill1_id = skills_lookup.get(skill1_name)
      if skill1_id:
        skill1_rank = get_skill_rank_data(skill1_id, skill1_level)
        if skill1_rank:
          skills.append(skill1_rank)
      else:
        print(f"Unknown skill: {skill1_name}")
      
      # process second skill
      skill2_id = skills_lookup.get(skill2_name)
      if skill2_id:
        skill2_rank = get_skill_rank_data(skill2_id, skill2_level)
        if skill2_rank:
          skills.append(skill2_rank)
      else:
        print(f"Unknown skill: {skill2_name}")
            
    elif skill_table:
      # single skill decoration
      skill_name = skill_table[0].find('td').get_text(strip=True)
      skill_level = extract_slot_level(skill_info)
      
      skill_id = skills_lookup.get(skill_name)
      if skill_id:
        skill_rank = get_skill_rank_data(skill_id, skill_level)
        if skill_rank:
          skills.append(skill_rank)
      else:
        print(f"Unknown skill: {skill_name}")
  
  except Exception as e:
    print(f"Error extracting decoration skills: {e}")
  
  return skills

"""
Parse a single decoration page and extract decoration data
"""
def parse_decoration_page(
    soup: BeautifulSoup, 
    data: list[dict], 
    decoration_type: str, 
    skills_lookup: dict[str, int]
  ) -> tuple[Optional[BeautifulSoup], str]:

  if not soup:
    print("Error: soup is None. Cannot parse decoration.")
    return None, decoration_type
  
  content = soup.find_all(name='div', attrs={'class': 'my-8'})
  if len(content) < 3:
    print("Required content sections not found on page.")
    return None, decoration_type
  
  nav = content[0]
  main = content[1]           # main dev - contains deco name + description
  skill_info = content[2]     # need this to reference from skills data
  
  deco_name = main.find('h2').get_text(strip=True)
  deco_desc = main.find('blockquote').get_text(strip=True)
  
  print(f"Parsing decoration: '{deco_name}'")
        
  # update decoration type
  decoration_type = get_decoration_type(deco_name, decoration_type)

  # check if it's a dual skill decoration (contains '/')
  is_dual_skill = '/' in deco_name

  # extract slot level
  slot_level = extract_slot_level(skill_info)
  rarity = get_rarity(deco_name, 'deco')

  if isinstance(rarity, dict) and 'error' in rarity:
    print(f'{deco_name} not found in lookup table')
    rarity = 1

  # extract skills
  skills = extract_skills(skill_info, skills_lookup, is_dual_skill)
  
  # create decoration object
  decoration = {
    'name': deco_name,
    'description': deco_desc,
    'type': decoration_type,
    'rarity': rarity,
    'slot': slot_level,
    'skills': skills
  }
        
  data.append(decoration)

  time.sleep(config.RATE_LIMIT)
  next_url = find_next_decoration_url(nav)

  return next_url, decoration_type

"""
Scrape all decoration data from the website
"""  
def get_deco_data() -> list[dict]:
  print("building skills lookup...")
  skills_lookup = build_skills_lookup()
  if not skills_lookup:
    print("Failed to build skills lookup. Check API connection.")

  print("finding decorations page...")
  try:
    decorations_page_url = find_decorations_page_url()
    if not decorations_page_url:
      print("Could not find the decorations page link.")
      return []
    
    res = requests.get(decorations_page_url).content
    soup = BeautifulSoup(res, 'html.parser')
    
    first_decoration_url = get_first_decoration_url(soup)
    if not first_decoration_url:
      return []
          
  except Exception as e:
    print(f'Error in get_decoration_data: {e}')
    return []

  print("Starting decoration scraping...")
  data = []
  decoration_type = 'Weapon'  # start with weapon type
  current_url = first_decoration_url
  
  while current_url:
    try:
      print(f"Fetching: {current_url}")
      res = requests.get(current_url)
      soup = BeautifulSoup(res.text, 'html.parser')
      
      next_url, decoration_type = parse_decoration_page(soup, data, decoration_type, skills_lookup)
      if not next_url:
        break
          
      # update to next decoration page url
      current_url = next_url
            
    except Exception as e:
      print(f"Error processing decoration URL {current_url}: {e}")
      break

  print(f"Scraping completed. Found {len(data)} decorations.")
  return data

"""
Posts the scraped decoration data to the API
"""
def post_deco_data(api_base_url: str = config.API_BASE_URL) -> bool:
  deco_data = get_deco_data()
  if not deco_data:
    print("No decoration data to post.")
    return
  
  print(f"Found {len(deco_data)} decorations to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/decorations/range",
      data=deco_data,
      headers=headers,
      verify=False,
      timeout=30
    )
    
    response.raise_for_status()
        
    print("Successfully posted decoration data!")
    
    # dump json to file:
    dump_json('decorations', deco_data)
    
    result = response.json()
    if result.get('errors'):
      print(f"Warning: Some items had errors: {result['errors']}")
    return True
        
  except requests.exceptions.RequestException as e:
    print(f"HTTP error posting decoration data: {e}")
    return False
  except json.JSONDecodeError as e:
    print(f"Error parsing API response: {e}")
    return False
  except Exception as e:
    print(f"Unexpected error posting decoration data: {e}")
    return False