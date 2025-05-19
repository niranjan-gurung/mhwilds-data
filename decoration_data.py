from bs4 import BeautifulSoup
import requests
import requests.compat
import time
import re
import pprint
import json

from utils.common import build_skills_lookup, get_skill_rank_data
from utils.get_rarity import get_rarity

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
  
  print(deco_name)

  if deco_name == 'Defense Jewel [1]':
    type = 'Armour'

  if '/' in deco_name:
    is_dual_skill = True

  #name = deco_name
  level = 1
  rarity = get_rarity(deco_name, 'deco')

  if rarity is None:
    print(f'{deco_name} not found in lookup table')

  time.sleep(1)

  skill_name = skill_info.find('table')   \
                         .find('tbody')   \
                         .find_all('tr')

  match = re.search(r'\[(\d+)\]', deco_name)
  if match:
    #name = deco_name  # Keep the full string for name
    level = int(match.group(1))

  if not is_dual_skill:
    skills = [skill_name[0].find('td').get_text(strip=True)]
    skill_level = level
  else:
    skill1 = skill_name[0].find('td').get_text(strip=True)
    skill2 = skill_name[1].find('td').get_text(strip=True)
    skills = [skill1, skill2]
    skill_level = level

  decorations = {
    'name': deco_name,
    'desc': deco_desc,
    'type': type,
    'rarity': rarity,
    'slot': level,
    'skills': []
  }

  print(f"Parsing charm: '{deco_name}'")

  for skill in skills:
    if is_dual_skill:
      # dual skills needs separate levels for each skill
      pass
    skill_id = skills_lookup.get(skill)
    #print(f'skill id: {skill_id}')
    if skill_id:
      # get skill rank/level based on id: 
      skill_rank = get_skill_rank_data(skill_id, skill_level)
      #print(f'skill rank: {skill_rank}')
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
  counter = 0
  # parse charm data: 
  while counter < 15:
    new_soup = parse_deco(new_soup, data, type, skills_lookup, is_dual_skill=False)
    if not new_soup:
      break
    counter += 1
  
  return data

d = get_deco_data()
pprint.pprint(d)

def post_deco_data(api_base_url='http://localhost:5000/api'):
  """
  Posts the scraped decoration data to the API
  """
  deco_data = get_deco_data()
  if not deco_data:
    print("No decoration data to post.")
    return
      
  print(f"Found {len(deco_data)} decorations to post.")
  
  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/charms",
      data=json.dumps(deco_data),
      headers=headers
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