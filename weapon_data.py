from bs4 import BeautifulSoup
import requests
import requests.compat
import json
import config
import time
import os
from utils.dump_json import dump_json
from typing import Optional

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

from entities.weapon_parser import (
  BaseWeapon, 
  GenericMeleeParser
)

from entities.weapons import (
  Gunlance, 
  ChargeBlade,
  SwitchAxe,
  InsectGlaive,
  LightBowgun
)

WEAPON_TYPES = [
  'Great Sword', 
  'Long Sword',
  'Sword and Shield',
  'Dual Blades',
  'Hammer',
  'Hunting Horn',
  'Lance',
  'Gunlance',
  'Switch Axe',
  'Charge Blade',
  'Insect Glaive',
  'Light Bowgun',
  'Heavy Bowgun',
  'Bow'
]

class WeaponParserFactory:
  """Factory to create appropriate parser for each weapon type"""
  
  _parsers = {
    # melee with special fields
    'Gunlance': Gunlance,
    'Charge Blade': ChargeBlade,
    'Switch Axe': SwitchAxe,
    'Insect Glaive': InsectGlaive,
    'Hunting Horn': GenericMeleeParser,   # todo
    
    # ranged weapons
    'Light Bowgun': LightBowgun,
    #'Heavy Bowgun': HeavyBowgun,
    #'Bow': Bow,
    
    # generic melee weapons (no special fields beyond sharpness)
    'Great Sword': GenericMeleeParser,
    'Long Sword': GenericMeleeParser,
    'Sword and Shield': GenericMeleeParser,
    'Dual Blades': GenericMeleeParser,
    'Hammer': GenericMeleeParser,
    'Lance': GenericMeleeParser
  }
  
  @classmethod
  def get_parser(cls, weapon_type: str) -> BaseWeapon:
    """Get appropriate parser for weapon type"""
    parser_class = cls._parsers.get(weapon_type, GenericMeleeParser)
    return parser_class(weapon_type)
  
  @classmethod
  def is_ranged_weapon(cls, weapon_type: str) -> bool:
    """Check if weapon type is ranged"""
    ranged_weapons = ['Light Bowgun', 'Heavy Bowgun', 'Bow']
    return weapon_type in ranged_weapons

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
to be loaded in dynamically. It then grabs all weapon specific links
"""
def get_all_weapon_type_urls(driver: WebDriver, url: str) -> list[tuple[str, str]]:
  try:
    # request weapons page url
    print(f'Getting all weapon type URLs')
    driver.get(url)

    WebDriverWait(driver, 10).until(
      EC.presence_of_all_elements_located((By.CLASS_NAME, 'weapons-grid'))
    )

    # wait for dynamic content to load (weapon type links)
    time.sleep(config.RATE_LIMIT)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # page contains a list of links representing all weapon types
    links = soup.find('section', class_='weapons-grid').find_all('a')

    weapon_urls: list[tuple[str, str]] = []
    # get url for specific weapon defined by type
    for item in links:
      weapon_type = item.get_text(strip=True)
      if weapon_type in WEAPON_TYPES and 'href' in item.attrs:
        weapon_url = requests.compat.urljoin(config.BASE_URL_WEAPON, item['href'])
        weapon_urls.append((weapon_type, weapon_url))

    print(f'Successfully found {len(weapon_urls)} weapon types')
    return weapon_urls
  
  except Exception as e:
    print(f'Error getting weapon type URL: {e}')
    return None

def load_weapon_type_specific_page(driver: WebDriver, url: str) -> Optional[BeautifulSoup]:
  """
  Load and scrape specific weapon page
  """
  try:
    print(f'Loading page: {url}')
    driver.get(url)
    
    # wait for the main content to load
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, 'ext-table'))
    )
    
    # wait a bit more for all content to load
    time.sleep(config.RATE_LIMIT)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    if soup:
      print(f'Successfully loaded page')
      return soup

  except Exception as e:
    print(f'Error scraping with Selenium: {e}')
    return None

def parse_weapon(soup: BeautifulSoup, type: str) -> list[dict]:
  weapons = []
  
  parser = WeaponParserFactory.get_parser(type)

  table = soup.find('tbody')
  rows = table.find_all('tr')

  for row in rows:
    cells = row.find_all('td')

    try:
      weapon = parser.create_weapon(cells)
      weapons.append(weapon)

      print(f'Successfully parsed {len(weapons)} {type} weapons')

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
    weapons = []

    # navigate into the weapons page:
    # get first weapon type (great sword)
    try:
      weapon_type_urls = get_all_weapon_type_urls(driver, weapons_page_url)
      
      if not weapon_type_urls:
        print('Could not find the weapon type link.')
        return []

      for weapon_type, weapon_url in weapon_type_urls:
        print(f'\n\t---scraping {weapon_type} ---')

        # load specific weapon type page
        soup = load_weapon_type_specific_page(driver, weapon_url)

        if soup:
          # get all weapons from its specific type page 
          weapon_types = parse_weapon(soup, weapon_type)

          # concat all weapons (including all types) into a single list
          weapons.extend(weapon_types)
          print(f"Added {len(weapon_types)} {weapon_type} weapons (Total: {len(weapons)})")
        else:
          print('Failed to load weapon page content.')

        time.sleep(config.RATE_LIMIT)

      print('\n\t--- Scraping finished! ---')
      print(f"Total weapons scraped: {len(weapons)}")
      return weapons
    
    finally:
      driver.quit()

  except Exception as e:
    print(f'Error in get_weapon_data: {e}')
    return []  

# testing
weapon_data = get_weapon_data()
dump_json('weapons', weapon_data)

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