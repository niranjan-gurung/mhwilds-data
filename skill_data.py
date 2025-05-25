from bs4 import BeautifulSoup
import requests
import requests.compat
import time

import pprint

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

def get_weapon_skills(weapon_skills):
  weapon_skills_data: list = []
  
  for row in weapon_skills:
    skill_info = row.find_all('td')
    skill_link = row.find('td').find('a')

    skill_name = skill_info[0].get_text(strip=True)
    skill_desc = skill_info[1].get_text(strip=True)

    time.sleep(1)

    try:
      href = skill_link['href']
      skill_details = requests.compat.urljoin(url, href)
      new_res = requests.get(skill_details)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')

      ranks: list = []
      rank_info = new_soup.find('tbody').find_all('tr')

      for tds in rank_info:
        td = tds.find_all('td')
        skill_level = td[0].get_text(strip=True)
        skill_rank_desc = td[2].get_text(strip=True)

        ranks.append({
          'level': int(skill_level[2:]),
          'description': skill_rank_desc
        })

      weapon_skills_data.append({
        'name': skill_name,
        'type': 'Weapon',
        'description': skill_desc,
        'ranks': ranks
      })
      print(f'Process next weapon skill link: {href}')
    except Exception as e:
      print(f"Error processing {href}: {e}")
    
  return weapon_skills_data

def get_armour_skills(armour_skills):
  armour_skills_data: list = []
  for row in armour_skills:
    skill_info = row.find_all('td')
    skill_link = row.find('td').find('a')

    skill_name = skill_info[0].get_text(strip=True)
    skill_desc = skill_info[1].get_text(strip=True)

    time.sleep(1)

    try:
      href = skill_link['href']
      skill_details = requests.compat.urljoin(url, href)
      new_res = requests.get(skill_details)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')

      ranks: list = []
      rank_info = new_soup.find('tbody').find_all('tr')

      for tds in rank_info:
        td = tds.find_all('td')
        skill_level = td[0].get_text(strip=True)
        skill_rank_desc = td[2].get_text(strip=True)

        ranks.append({
          'level': int(skill_level[2:]),
          'description': skill_rank_desc
        })

      armour_skills_data.append({
        'name': skill_name,
        'type': 'Armour',
        'description': skill_desc,
        'ranks': ranks
      })
      print(f'Process next armour skill link: {href}')
    except Exception as e:
      print(f"Error processing {href}: {e}")

  return armour_skills_data

def get_skill_data() -> list:
  """
  homepage -> skills page
  """
  homepage = soup.find(attrs={'data-sidebar': 'group-content'})
  a = homepage.find_all('a')
  for item in a:
    if item.text == 'Skills' and 'href' in item.attrs:
      href = item['href']
      ar_list_url = requests.compat.urljoin(url, href)
      new_res = requests.get(ar_list_url)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')
      break

  tables = new_soup.find_all('tbody')
  t1 = tables[0]  # weapon skills
  t2 = tables[1]  # armour skills
  t3 = tables[2]  # group skill/bonus
  t4 = tables[3]  # set bonus

  weapon_skills = t1.find_all('tr')
  armour_skills = t2.find_all('tr')

  skill_data: list = []
  
  wp_sk = get_weapon_skills(weapon_skills)
  ar_sk = get_armour_skills(armour_skills)

  skill_data.extend(wp_sk)
  skill_data.extend(ar_sk)

  return skill_data

# sd = get_skill_data()
# pprint.pprint(sd)