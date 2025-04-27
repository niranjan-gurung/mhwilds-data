from bs4 import BeautifulSoup
import requests
import requests.compat
import re

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

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
    return e
  
def get_skill_rank_data(skill_id, skill_level, api_base_url='http://localhost:5000/api'):
  try:
    response = requests.get(f"{api_base_url}/skills/{skill_id}")
    if response.status_code == 200:
      skill_data = response.json()
      for rank in skill_data.get('ranks', []):
        if rank['level'] == skill_level:
          return rank['id']
    return None
  except Exception as e:
    return e

def get_armour_data():
  skills_lookup = build_skills_lookup()

  """
  homepage -> armour page
  """
  homepage = soup.find(attrs={'data-sidebar': 'group-content'})
  a = homepage.find_all('a')
  for item in a:
    if item.text == 'Armor' and 'href' in item.attrs:
      href = item['href']
      ar_list_url = requests.compat.urljoin(url, href)
      new_res = requests.get(ar_list_url)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')
      break


  """
  armour page -> first armour page (Hope armour).
  Each individual armour page has link to next or previous armour.
  """
  first_armour_link = new_soup.find('tr') \
                              .find('td') \
                              .find('a')

  all_armour_data = []
  rank = 'low'    # track rank transition
  rarity = 1

  if first_armour_link.text == 'Hope' and 'href' in first_armour_link.attrs:
    href = first_armour_link['href']
    armour_url = requests.compat.urljoin(url, href)
    new_res = requests.get(armour_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')

  while True:
    tables = new_soup.find_all('tbody')
    t2 = tables[1]    # piece type + resistances
    t3 = tables[2]    # piece slot info

    """
    uses 2nd and 3rd table structures to extract appropriate data:
    - name
    - type
    - defense
    - resistances
    - slots

    builds a armour piece dict object using the above info
    """
    data = []
    rows = t2.find_all('tr')[1:]

    for row in rows:
      td = row.find_all('td')
      type = td[0].get_text(strip=True)
      name = td[1].get_text(strip=True)
      defense = td[2].get_text(strip=True)
      resistances = {
        "fire": td[3].get_text(strip=True),
        "water": td[4].get_text(strip=True),
        "ice": td[5].get_text(strip=True),
        "thunder": td[6].get_text(strip=True),
        "dragon": td[7].get_text(strip=True)
      }

      """
      rank + rarity not listed on website so
      manual change required:
      """
      if name == 'Conga Helm':
        rarity = 2
      if name == 'Ingot Helm':
        rarity = 3
      if name == 'G. Seikret Coil':
        rarity = 4
      if name == 'Hope Mask \u03b1':
        rank = 'high'
        rarity = 5
      if name == 'Ingot Helm \u03b1':
        rarity = 6
      if name == 'Dober Helm \u03b1':
        rarity = 7
      if name == 'Arkvulcan Helm \u03b1':
        rarity = 8

      data.append({
        'name': name,
        'slug': name.lower().replace(' ', '-').replace('.', ''),
        'type': type.lower(),
        'rank': rank,
        'rarity': rarity,
        'defense': defense,
        'resistances': resistances,
        'slots': [],
        'skills': []
      })
      
    """
    this block extracts slots information
    """
    rows = t3.find_all('tr')[1:]

    for i, row in enumerate(rows):
      if i < len(data):
        td = row.find_all('td')
        slot_text = td[2].get_text(strip=True)
        slot_values = re.findall(r'\[(\d+)\]', slot_text)
        slots = [{'level': int(slot)} for slot in slot_values if int(slot) != 0]
        data[i]['slots'] = slots

        if len(td) > 3 and td[3].get_text(strip=True):
          skill_name_level = td[3].get_text(strip=True)

          match = re.match(r'([a-zA-Z\s]+)\s([\+\-]?\d+)$', skill_name_level.strip())

          if match:
            skill_name = match.group(1).strip()
            skill_level = int(match.group(2))

          skill_id = skills_lookup.get(skill_name)

          if skill_id:
            skill_rank_id = get_skill_rank_data(skill_id, skill_level)

            if skill_rank_id:
              response = requests.get(f'http://localhost:5000/api/skills/{skill_id}')
              if response.status_code == 200:
                skill_data = response.json()
                for srank in skill_data['ranks']:
                  if srank['level'] == skill_level:
                    data[i]['skills'].append({
                      'id': srank['id'],
                      'level': srank['level'],
                      'desc': srank['desc'],
                      'skill_id': skill_id
                    })
                  else:
                    print(f"Rank not found for level {skill_level}")
            else:
              print(f"Could not find rank ID for skill: {skill_name} level {skill_level}")
          else:
            print(f"Unknown skill: {skill_name}")

    all_armour_data.extend(data)

    """
    Link to next armour set
    """
    next_armour = new_soup.find(name='nav', attrs={'role': 'navigation'}) \
                          .find('ul') \
                          .find_all('li')[-1].find('a')
    
    if next_armour and 'href' in next_armour.attrs:
      href = next_armour['href']
      next_armour_url = requests.compat.urljoin(url, href)
      new_res = requests.get(next_armour_url)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')
    else:
      break
  return all_armour_data