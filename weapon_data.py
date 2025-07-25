from bs4 import BeautifulSoup
import requests
import requests.compat
import json
import config
from utils.dump_json import dump_json
from typing import Optional

from utils.common import (
  build_skills_lookup, 
  get_skill_rank_data
)

res = requests.get(config.BASE_URL_WEAPON)
soup = BeautifulSoup(res.text, 'html.parser')

# main homepage
homepage = soup.find(attrs={'class': 'cards-container'})
if not homepage: 
  print('homepage not found')

# weapon link
weapon_url = homepage.find('a')
if weapon_url.get_text(strip=True) == 'Weapons' and 'href' in weapon_url.attrs:
  # build weapon link url
  link = requests.compat.urljoin(config.BASE_URL_WEAPON, weapon_url['href'])
  print(f'link: {link}')

# go to weapon page
res = requests.get(link)
soup = BeautifulSoup(res.text, 'html.parser')

# hero section
print(f'h1:   {soup.find('h1').text}')
print(f'p:    {soup.find('p').text}')

"""
Scrapes weapon data from the website (url2) and builds weapon object,
matches weapon model/schema from API
"""
def get_weapon_data() -> list[dict]:
  print('building skills lookup...')
  skills_lookup = build_skills_lookup()
  if not skills_lookup:
    print("Failed to build skills lookup. Check API connection.")
    return []
  
"""
Posts the scraped weapon data to the API
"""
def post_weapon_data(api_base_url: str = config.API_BASE_URL) -> bool:
  weapon_data = get_weapon_data()
  if not weapon_data:
    print("No weapon data to post.")
    return False
      
  print(f"Found {len(weapon_data)} weapons to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/weapons/range",
      json=weapon_data,
      headers=headers,
      verify=False,
      timeout=30
    )
    
    response.raise_for_status()
        
    print("Successfully posted weapon data!")
    
    # dump json to file:
    dump_json('weapons', weapon_data)
    
    # handle both list and dict responses from API
    try:
      result = response.json()
      if isinstance(result, dict) and result.get('errors'):
        print(f"Warning: Some items had errors: {result['errors']}")
      elif isinstance(result, list):
        print(f"Successfully created {len(result)} weapons in the database.")
      else:
        print("Weapons posted successfully!")
    except json.JSONDecodeError:
      print("Weapons posted successfully (no response data)!")
      
    return True
  
  except requests.exceptions.RequestException as e:
    print(f"HTTP error posting weapon data: {e}")
    return False
  except json.JSONDecodeError as e:
    print(f"Error parsing API response: {e}")
    return False
  except Exception as e:
    print(f"Unexpected error posting weapon data: {e}")
    return False