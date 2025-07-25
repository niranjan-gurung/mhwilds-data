from bs4 import BeautifulSoup
import requests
import requests.compat
import time
import re
import json
import config
from utils.dump_json import dump_json
from typing import Optional

from utils.common import (
  build_skills_lookup, 
  get_skill_rank_data, 
  roman_numeral_to_int
)

from utils.get_rarity import get_rarity

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROMAN_TO_INT = {'I': 1, 'V': 5}

"""
Parse charm name to extract base name and level
"""
def parse_charm_name(charm_name: str) -> tuple[str, int]:
  if charm_name == 'Hope Charm':
    return charm_name, 1
  
  match = re.match(r'(.+)\s+([IV]+)', charm_name)
  if match:
    base_name = match.group(1)
    level_roman = match.group(2)
    level = roman_numeral_to_int(level_roman, ROMAN_TO_INT)
    return base_name, level
  
  return charm_name, 1

"""
Extract skills from charm skill info section
"""
def extract_skills(
    skill_info, 
    skills_lookup: dict[str, int], 
    skill_level: int, 
    is_hope_charm: bool = False
  ) -> list[dict]:
  
  skills = []

  try:
    skill_table = skill_info.find('table')   \
                          .find('tbody')    \
                          .find_all('tr')
    
    if is_hope_charm:   # hope charm has 2 skills
      for row in skill_table:
        skill_name = row.find('td').get_text(strip=True)
        skill_id = skills_lookup.get(skill_name)
        if skill_id:
          skill_rank = get_skill_rank_data(skill_id, skill_level)
          if skill_rank:
            skill_reference = {
              "id": skill_rank["id"]  # extract just the rank ID from the full rank object
            }
            skills.append(skill_reference)
        else:
          print(f"Unknown skill: {skill_name}")
    else:   # rest of the charms only contain single skill
      if skill_table:
        skill_name = skill_table[0].find('td').get_text(strip=True)
        skill_id = skills_lookup.get(skill_name)
        if skill_id:
          skill_rank = get_skill_rank_data(skill_id, skill_level)
          if skill_rank:
            skill_reference = {
              "id": skill_rank["id"]
            }
            skills.append(skill_reference)
        else:
          print(f"Unknown skill: {skill_name}")
  except Exception as e:
    print(f"Error extracting charm skills: {e}")

  return skills

"""
Find or create charm object in data list
"""
def find_or_create_charm(data: list[dict], charm_base_name: str) -> dict:
  # search existing charm with same base name
  for charm in data:
    if charm['name'] == charm_base_name:
      return charm
  
  # create new charm if not found
  new_charm = {
    'name': charm_base_name,
    'ranks': []
  }
  data.append(new_charm)
  return new_charm

"""
Parse each charm page
"""
def parse_charm(
    soup: BeautifulSoup, 
    data: list[dict], 
    skills_lookup: dict[str, int]
  ) -> Optional[BeautifulSoup]:

  if not soup:
    print("Error: soup is None. Cannot parse charm.")
    return None
  
  content = soup.find_all(name='div', attrs={'class': 'my-8'})
  if len(content) < 3:
    print("Required content sections not found on page.")
    return None
  
  nav = content[0]
  main = content[1]           # main dev - contains charm name + description
  skill_info = content[2]     # need this to reference from skills data
  
  charm_name = main.find('h2').get_text(strip=True)
  charm_desc = main.find('blockquote').get_text(strip=True)

  print(f"Parsing charm: '{charm_name}'")

  charm_base_name, level = parse_charm_name(charm_name)
  is_hope_charm = charm_name == 'Hope Charm'
  rarity = get_rarity(charm_name, 'charm')

  if isinstance(rarity, dict) and 'error' in rarity:
    print(f'{charm_name} not found in lookup table')
    rarity = 1  # revert to default rarity

  # extract skills
  skills = extract_skills(skill_info, skills_lookup, level, is_hope_charm)

  # find or create charm object
  charm = find_or_create_charm(data, charm_base_name)
  
  # create charm rank object
  charm_rank = {
      'name': charm_name,
      'description': charm_desc,
      'level': level,
      'rarity': rarity,
      'skills': skills
  }

  charm['ranks'].append(charm_rank)

  time.sleep(config.RATE_LIMIT)
  # return next charm link:
  return find_next_charm_url(nav)

"""
Get charms page url from homepage
"""
def find_charms_page_url() -> Optional[str]:  
  try:
    res = requests.get(config.BASE_URL_OTHER).content
    soup = BeautifulSoup(res, 'html.parser')
    homepage = soup.find(attrs={'data-sidebar': 'group-content'})
    if not homepage: 
      return None

    links = homepage.find_all('a')

    for item in links:
      if item.text == 'Charms' and 'href' in item.attrs:
        return requests.compat.urljoin(config.BASE_URL_OTHER, item['href'])
    return None
  except Exception as e:
    print(f"Error finding charms page URL: {e}")
    return None

"""
Find link to first charm
"""
def get_first_charm_url(soup: BeautifulSoup) -> Optional[str]:
  try:
    link = soup.find('tbody')   \
               .find('tr')      \
               .find('a')

    if link.text == 'Marathon Charm I' and 'href' in link.attrs:
      return requests.compat.urljoin(config.BASE_URL_OTHER, link['href'])
    
    print("First charm link is not Marathon Charm I or does not have href attribute.")
    return None
  except Exception as e:
    print(f'Error getting first charm URL: {e}')
    return None

"""
Find link to next charm
"""
def find_next_charm_url(soup: BeautifulSoup) -> Optional[str]:
  try:
    next_charm = soup.find('ul') \
                    .find_all('li')[1] \
                    .find('a')

    if next_charm and 'href' in next_charm.attrs:
      return requests.compat.urljoin(config.BASE_URL_OTHER, next_charm['href'])
    return None
  except Exception as e:
    print(f'Error finding next charm URL: {e}')
    return None

"""
Scrapes charm data from the website and builds charm object,
matches charm model/schema from API
"""
def get_charm_data() -> list[dict]:
  print('building skills lookup...')
  skills_lookup = build_skills_lookup()
  if not skills_lookup:
    print("Failed to build skills lookup. Check API connection.")
    return []

  try:
    charms_page_url = find_charms_page_url()
    if not charms_page_url:
      print("Could not find the charm page link.")
      return []
    
    res = requests.get(charms_page_url).content
    soup = BeautifulSoup(res, 'html.parser')

    # get first charm link
    first_charm_url = get_first_charm_url(soup)
    if not first_charm_url:
      return []
    
  except Exception as e:
    print(f'Error in get_charm_data: {e}')
    return []  
  
  print('start charm scraping...')
  all_charm_data = []
  current_url = first_charm_url
  
  # process each charm page: 
  while current_url:
    try:
      print(f"fetching: {current_url}")
      res = requests.get(current_url)
      soup = BeautifulSoup(res.text, 'html.parser')
      
      next_url = parse_charm(soup, all_charm_data, skills_lookup)
      if not next_url:
        print("No more charms found, ending scrape.")
        break
      
      # update to next charm page url
      current_url = next_url
            
    except Exception as e:
      print(f"Error processing charm URL {current_url}: {e}")
      break
  
  return all_charm_data

"""
Posts the scraped charm data to the API
"""
def post_charm_data(api_base_url: str = config.API_BASE_URL) -> bool:
  charm_data = get_charm_data()
  if not charm_data:
    print("No charm data to post.")
    return False
      
  print(f"Found {len(charm_data)} charms to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/charms/range",
      json=charm_data,
      headers=headers,
      verify=False,
      timeout=30
    )
    
    response.raise_for_status()
        
    print("Successfully posted charm data!")
    
    # dump json to file:
    dump_json('charms', charm_data)
    
    # handle both list and dict responses from API
    try:
      result = response.json()
      if isinstance(result, dict) and result.get('errors'):
        print(f"Warning: Some items had errors: {result['errors']}")
      elif isinstance(result, list):
        print(f"Successfully created {len(result)} charms in the database.")
      else:
        print("Charms posted successfully!")
    except json.JSONDecodeError:
      print("Charms posted successfully (no response data)!")

    return True
  
  except requests.exceptions.RequestException as e:
    print(f"HTTP error posting charm data: {e}")
    return False
  except json.JSONDecodeError as e:
    print(f"Error parsing API response: {e}")
    return False
  except Exception as e:
    print(f"Unexpected error posting charm data: {e}")
    return False