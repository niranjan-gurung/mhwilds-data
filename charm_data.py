from bs4 import BeautifulSoup
import requests
import requests.compat
import time
import re
import pprint
import json

from util import build_skills_lookup, get_skill_rank_data, roman_numeral_to_int
from util import lookup

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

roman_to_int = {'I': 1, 'V': 5}

def get_rarity(charm_name):
  if charm_name in lookup:
    return lookup[charm_name]
  else:
    return None

def parse_charm(new_soup, data, skills_lookup, is_hope_charm=False):
  if not new_soup:
    print("Error: new_soup is None. Cannot parse charm.")
    return None
  
  content = new_soup.find_all(name='div', attrs={'class': 'my-8'})
  nav = content[0]
  main = content[1]           # main dev - contains charm name + description
  skill_info = content[2]     # need this to reference from skills data
  
  charm_name = main.find('h2').get_text(strip=True)
  charm_desc = main.find('blockquote').get_text(strip=True)

  if charm_name == 'Hope Charm': 
    is_hope_charm = True

  rarity = get_rarity(charm_name)

  if rarity is None:
    print(f'{charm_name} not found in lookup table')

  name = charm_name
  level = 1

  time.sleep(1)

  if is_hope_charm:
    skill_name = skill_info.find('table')   \
                           .find('tbody')   \
                           .find_all('tr')

    skill1 = skill_name[0].find('td').get_text(strip=True)
    skill2 = skill_name[1].find('td').get_text(strip=True)
    skills = [skill1, skill2]
    skill_level = level
  else:
    match = re.match(r'(.+)\s+([IV]+)', charm_name)

    if match:
      name = match.group(1)
      level_roman = match.group(2)
      level = roman_numeral_to_int(level_roman, roman_to_int)

    skill_name = skill_info.find('table')   \
                           .find('tbody')   \
                           .find('tr')      \
                           .find('td')      \
                           .get_text(strip=True)
    skills = [skill_name]
    skill_level = level

  charm = next((item for item in data if item['name'] == name), None)

  # if charm doesn't exist, create a new charm object
  if charm is None:
    charm = {
      'name': name,
      'ranks': []  # empty list for ranks, will fill it below
    }
    data.append(charm)  # add new charm to data

  charm_rank = {
    'name': charm_name,
    'desc': charm_desc,
    'level': level,
    'rarity': rarity,
    'skills': []
  }

  print(f"Parsing charm: '{charm_name}'")

  for skill in skills:
    skill_id = skills_lookup.get(skill)
    if skill_id:
      # get skill rank/level based on id: 
      skill_rank = get_skill_rank_data(skill_id, skill_level)
      if skill_rank:
        # append skill rank info to skill object:
        charm_rank['skills'].append(skill_rank)

  charm['ranks'].append(charm_rank)

  # navigate to next charm link:
  next_charm = nav.find('ul') \
                  .find_all('li')[1] \
                  .find('a')

  if next_charm and 'href' in next_charm.attrs:
    href = next_charm['href']
    next_charm_url = requests.compat.urljoin(url, href)
    new_res = requests.get(next_charm_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
    return new_soup
  else:
    print("No next armour link found, ending scrape.")
    return None

counter = 0
def get_charm_data() -> list:
  data: list = []
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
  first_charm_link = new_soup.find('tbody')   \
                             .find('tr')      \
                             .find('a')

  if first_charm_link.text == 'Marathon Charm I' and 'href' in first_charm_link.attrs:
    href = first_charm_link['href']
    charm_url = requests.compat.urljoin(url, href)
    new_res = requests.get(charm_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
  else:
    print("First charm link is not Marathon Charm I or does not have href attribute.")
    return []
  
  # parse charm data: 
  while True:
    new_soup = parse_charm(new_soup, data, skills_lookup, is_hope_charm=False)
    if not new_soup:
      break
  
  return data

def post_charm_data(api_base_url='http://localhost:5000/api'):
  """
  Posts the scraped charm data to the API
  """
  charm_data = get_charm_data()
  if not charm_data:
    print("No charm data to post.")
    return
      
  print(f"Found {len(charm_data)} charms to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/charms",
      data=json.dumps(charm_data),
      headers=headers
    )
    
    if response.status_code in (200, 201, 207):
      print("Successfully posted charm data!")
      result = response.json()
      if 'errors' in result and result['errors']:
        print(f"Warning: Some items had errors: {result['errors']}")
      return True
    else:
      print(f"Failed to post charm data. Status code: {response.status_code}")
      print(f"Response: {response.text}")
      return False
  except Exception as e:
    print(f"Error posting charm data: {e}")
    return False