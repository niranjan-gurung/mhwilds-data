from bs4 import BeautifulSoup
import requests
import requests.compat
import json
import config
import time
import os
from utils.dump_json import dump_json
from typing import Optional

import pprint

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from utils.common import (
  build_skills_lookup, 
  get_skill_rank_data
)

"""
weapon object to match in API:

// greatsword example:
{
  "name": "..",
  "description": "..",          // this will remain empty
  "weapontype": "GreatSword",   // this will need to match enum types in API
  "defense": 0 or null,
  "rarity": 1,
  "slots": [],
  "affinity": 15 (0.15 in page source),   // * 100 multiplier 
  "damage": {
    "raw": 15,
    "display": 120
  },
  "element": null,
  "sharpness": {
    "red": 40,
    "orange": 50,
    "yellow": 50,
    "green": 60,
    "blue": 0,
    "white": 0
  },
  "skills": [     // references existing skill rank ids
    {
      "id": 3
    },
    {
      "id": 8
    }
  ]
}
"""

"""
Return potential path for chrome exe,
if defined path is not found, selenium will use default
system path (may break as it might use an older version of chrome)
"""
def get_chrome_binary_path() -> Optional[str]:
  """
  Try to find Chrome binary path automatically
  """
  possible_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  ]
  
  for path in possible_paths:
    if os.path.exists(path):
      return path
  
  # selenium will use system default
  return None

"""
Setup chrome driver
"""
def get_driver(headless: bool = False) -> WebDriver:
  options = Options()

  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('--disable-gpu')
  options.add_argument('--disable-extensions')
  options.add_argument('--disable-logging')
  
  # setup headless mode
  if headless:
    options.add_argument('--headless=new')

  chrome_path = get_chrome_binary_path()
  if chrome_path:
    options.binary_location = chrome_path
    print(f"Using Chrome binary at: {chrome_path}")
  else:
    print("Using system default Chrome installation")
  
  try:
    # auto handle chrome version
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # implicit wait
    driver.implicitly_wait(10)
    
    return driver
      
  except Exception as e:
    print(f"Error creating WebDriver: {e}")
    raise

"""
Get weapons page url from homepage
"""
def find_weapons_page_url() -> Optional[str]:
  res = requests.get(config.BASE_URL_WEAPON)
  soup = BeautifulSoup(res.text, 'html.parser')
  homepage = soup.find(attrs={'class': 'cards-container'})
  if not homepage: 
    return None

  weapon_url = homepage.find('a')

  if weapon_url.get_text(strip=True) == 'Weapons' and 'href' in weapon_url.attrs:
    return requests.compat.urljoin(config.BASE_URL_WEAPON, weapon_url['href'])
    
  return None

"""
Loads into the 'Weapons' page and waits for weapon type links-
to be loaded in dynamically. It then grabs and returns the weapon specific-
link defined by the 'type' variable passed in the method parameter
"""
def load_weapon_type_page(driver: WebDriver, url: str, type: str) -> Optional[str]:
  try:
    # request weapons page url
    print(f'Getting weapon type URL for: {type}')
    driver.get(url)

    WebDriverWait(driver, 10).until(
      EC.presence_of_all_elements_located((By.CLASS_NAME, 'weapons-grid'))
    )

    # wait for dynamic content to load (weapon type links)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # page contains a list of links representing all weapon types
    links = soup.find('section', class_='weapons-grid').find_all('a')

    # get url for specific weapon defined by type
    for item in links:
      if item.get_text(strip=True) == type and 'href' in item.attrs:
        return requests.compat.urljoin(config.BASE_URL_WEAPON, item['href'])
    return None
  
  except Exception as e:
    print(f'Error getting weapon type URL: {e}')
    return None

def load_weapon_type_specific_page(driver: WebDriver, url: str) -> Optional[BeautifulSoup]:
  """
  Scrape weapon page using Selenium
  """
  try:
    print(f'Using Selenium to scrape: {url}')
    driver.get(url)
    
    # wait for the main content to load
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, 'ext-table'))
    )
    
    # wait a bit more for all content to load
    time.sleep(2)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    if soup:
      print(f'Successfully loaded page')
      return soup

  except Exception as e:
    print(f'Error scraping with Selenium: {e}')
    return None

def parse_weapon(soup: BeautifulSoup) -> list[dict]:
  weapons = []
  
  table = soup.find('tbody')
  rows = table.find_all('tr')

  for row in rows:
    cells = row.find_all('td')

    def get_cell_text(index):
      return cells[index].get_text(strip=True)

    try:
      weapon = {
        'name': get_cell_text(0),
        'desc': '',
        'weapontype': 'Great Sword',
        'defense': 0 if get_cell_text(7) == '' else get_cell_text(7),
        'rarity': get_cell_text(3),
        # if slot column is empty, then don't append anything into slot list
        'slots': [
          int(val) for i in [22, 23, 24] if (val := get_cell_text(i)) != ''
        ],
        'affinity': 0 if get_cell_text(6) == '' else int(round(float(get_cell_text(6)) * 100)),
        'damage': {
          'display': int(get_cell_text(4)),
          'raw': int(get_cell_text(5))
        },
      }
      
      ele_text = get_cell_text(8)
      if ele_text and ele_text != '-':
        weapon['element'] = {
          'type': ele_text,
          'display': int(get_cell_text(9)),
          'raw': str(int(get_cell_text(9)) / 10)
        }
      else:
        weapon['element'] = {}

      weapon['sharpness'] = {
        'red': get_cell_text(10),
        'orange': get_cell_text(11),
        'yellow': get_cell_text(12),
        'green': get_cell_text(13),
        'blue': get_cell_text(14),
        'white': get_cell_text(15),
        'purple': 0
      }

      weapon['skills'] = []
      weapons.append(weapon)

    except Exception as e:
      print(f'Error parsing weapons: {e}')

  return weapons

"""
Scrapes weapon data from the website (url2) and builds weapon object,
matches weapon model/schema from API
"""
def get_weapon_data() -> list[dict]:
  # print('building skills lookup...')
  # skills_lookup = build_skills_lookup()
  # if not skills_lookup:
  #   print("Failed to build skills lookup. Check API connection.")
  #   return []
  
  # navigate to the weapon page
  print('finding weapons page...')
  try:
    weapons_page_url = find_weapons_page_url()
    if not weapons_page_url:
      print('Could not find the weapon page link.')
      return []

    driver = get_driver()

    # navigate into the weapons page:
    # get first weapon type (great sword)
    try:
      weapon_type_page = load_weapon_type_page(driver, weapons_page_url, 'Great Sword')
      
      if not weapon_type_page:
        print('Could not find the weapon type link.')
        return []
    
      soup = load_weapon_type_specific_page(driver, weapon_type_page)

      if not soup:
        print('Failed to load weapon page content.')
        return []
    
      weapons = parse_weapon(soup)
      print(weapons)
      return weapons
    
    finally:
      driver.quit()

  except Exception as e:
    print(f'Error in get_weapon_data: {e}')
    return []  

get_weapon_data()

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