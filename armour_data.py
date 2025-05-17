from bs4 import BeautifulSoup
import requests
import requests.compat
import re
import json

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

"""
Builds a dictionary mapping skill names to their IDs from the API
"""
def build_skills_lookup(api_base_url='http://localhost:5000/api'):
  skills_lookup = {}
  try:
    response = requests.get(f"{api_base_url}/skills")
    if response.status_code == 200:
      skills = response.json()
      for skill in skills:
        skills_lookup[skill['name']] = skill['id']
    return skills_lookup
  except Exception as e:
    print(f"Error building skills lookup: {e}")
    return {}
  
"""
Retrieves the skill rank for a given skill ID and level
"""
def get_skill_rank_data(skill_id, skill_level, api_base_url='http://localhost:5000/api'):
  try:
    response = requests.get(f"{api_base_url}/skills/{skill_id}")
    if response.status_code == 200:
      skill_data = response.json()
      for rank in skill_data.get('ranks', []):
        if rank['level'] == skill_level:
          return rank   # from ranks list: get rank object that matches 'skill_level'
    return None
  except Exception as e:
    print(f"Error getting skill rank data: {e}")
    return None

def parse_skill(skill_string) -> tuple:
  match = re.match(r'(.+)\s\+(\d+)', skill_string)
  if match:
    skill_name = match.group(1)         # extract skill name (str)
    skill_level = int(match.group(2))   # extract skill level (int)
    return skill_name, skill_level
  return None, None

"""
Build armour piece object from webpage,
needs to match armour model/schema from API 
"""
def get_armour_data():
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
    first_armour_link = new_soup.find('tr')
    if not first_armour_link:
      print("Could not find first armour link.")
      return []
    
    first_armour_link = first_armour_link.find('td')
    if not first_armour_link:
      print("Could not find first armour link td.")
      return []
        
    first_armour_link = first_armour_link.find('a')
    if not first_armour_link:
      print("Could not find first armour link a.")
      return []

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

    # process each armour set page
    while True:
      tables = new_soup.find_all('tbody')
      if len(tables) < 3:
        print("Required tables not found on page.")
        break
        
      t2 = tables[1]    # piece type + resistances
      t3 = tables[2]    # piece slot info

      # extract basic armour data from tables
      data = []
      rows = t2.find_all('tr')[1:]

      for row in rows:
        td = row.find_all('td')
        if len(td) < 8:
          print("Row doesn't have enough cells, skipping.")
          continue
            
        type = td[0].get_text(strip=True)
        name = td[1].get_text(strip=True)
        
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

            #print(f'skill rank: {skill_rank}')

            # append skill rank info to armour piece:
            data[i]['skills'].append(skill_rank)

      all_armour_data.extend(data)

      # find link to next armour set
      nav = new_soup.find(name='nav', attrs={'role': 'navigation'})
      if not nav:
        print("Navigation element not found, ending scrape.")
        break
          
      nav_list = nav.find('ul')
      if not nav_list:
        print("Navigation list not found, ending scrape.")
        break
          
      nav_items = nav_list.find_all('li')
      if not nav_items or len(nav_items) < 1:
        print("Navigation items not found, ending scrape.")
        break
          
      next_armour = nav_items[-1].find('a')
      
      if next_armour and 'href' in next_armour.attrs:
        href = next_armour['href']
        next_armour_url = requests.compat.urljoin(url, href)
        new_res = requests.get(next_armour_url)
        new_soup = BeautifulSoup(new_res.text, 'html.parser')
      else:
        print("No next armour link found, ending scrape.")
        break
            
    return all_armour_data

def post_armour_data(api_base_url='http://localhost:5000/api'):
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
      headers=headers
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