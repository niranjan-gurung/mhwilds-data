from bs4 import BeautifulSoup
import requests
import requests.compat
import time
import json
import config
from utils.dump_json import dump_json
from typing import Optional

"""
Get skills for both weapon and armour type,
based on which type is passed as string
"""
def get_skills_by_type(skill_rows: list, skill_type: str) -> list[dict]:
  skills_data: list[dict] = []
  
  for row in skill_rows:
    skill_info = row.find_all('td')
    skill_link = row.find('td').find('a')

    skill_name = skill_info[0].get_text(strip=True)
    skill_desc = skill_info[1].get_text(strip=True)

    try:
      href = skill_link['href']
      skill_details = requests.compat.urljoin(config.BASE_URL, href)
      res = requests.get(skill_details).content
      soup = BeautifulSoup(res, 'html.parser')

      ranks = extract_skill_ranks(soup)

      skills_data.append({
        'name': skill_name,
        'type': skill_type,
        'description': skill_desc,
        'ranks': ranks
      })

      print(f'Process next weapon skill link: {href}')
      time.sleep(config.RATE_LIMIT) # rate limit

    except KeyError:
      print(f'No href found for skill: {skill_name}')
    except Exception as e:
      print(f"Error processing {href}: {e}")
    
  return skills_data

"""
Extract all skill ranks from details page
"""
def extract_skill_ranks(soup: BeautifulSoup) -> list[dict]:
  ranks: list = []
  rank_rows = soup.find('tbody').find_all('tr')

  for row in rank_rows:
    tds = row.find_all('td')
    skill_level = tds[0].get_text(strip=True)
    skill_rank_desc = tds[2].get_text(strip=True)

    try:
      level = int(skill_level[2:]) if skill_level.startswith('Lv') else int(skill_level)
      ranks.append({
        'level': level,
        'description': skill_rank_desc
      })
    except ValueError:
      print(f'could not parse skill level: {skill_level}')

  return ranks

"""
Get skills page url from homepage
"""
def find_skills_page_url() -> Optional[str]:
  res = requests.get(config.BASE_URL).content
  soup = BeautifulSoup(res, 'html.parser')
  homepage = soup.find(attrs={'data-sidebar': 'group-content'})
  if not homepage: 
    return None
  
  links = homepage.find_all('a')

  for item in links:
    if item.text == 'Skills' and 'href' in item.attrs:
      return requests.compat.urljoin(config.BASE_URL, item['href'])
  
  return None

"""
Get all weapon + armour skills and,
consolidate into single list[dict].

TODO: 
- group skills 
- set bonus
"""
def get_skill_data() -> list[dict]:
  """
  homepage -> skills page
  """
  try:
    skills_page_url = find_skills_page_url()
    if not skills_page_url:
      print("could not find skills page url")
      return []
    
    res = requests.get(skills_page_url).content
    soup = BeautifulSoup(res, 'html.parser')

  except Exception as e:
    print(f'Error in get_skill_data: {e}')
    return []

  tables = soup.find_all('tbody')
  weapon_skills_table = tables[0]  # weapon skills
  armour_skills_table = tables[1]  # armour skills

  # todo in the future:
  group_skills_table  = tables[2]  # group skill/bonus
  set_bonus_table     = tables[3]  # set bonus

  weapon_skills = weapon_skills_table.find_all('tr')
  armour_skills = armour_skills_table.find_all('tr')

  skill_data: list[dict] = []
  
  wp_sk = get_skills_by_type(weapon_skills, 'Weapon')
  ar_sk = get_skills_by_type(armour_skills, 'Armour')

  skill_data.extend(wp_sk)
  skill_data.extend(ar_sk)

  return skill_data

"""
Posts the scraped skills data to the API
"""
def post_skill_data(api_base_url: str = config.API_BASE_URL) -> bool:
  print('starting skill data scraping...')
  skill_data = get_skill_data()

  if not skill_data:
    print("No skills data to post.")
    return
  
  print(f"Found {len(skill_data)} skills to post.")

  # POST: to the API endpoint
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{api_base_url}/skills/range",
      data=skill_data,
      headers=headers,
      verify=False,
      timeout=30
    )

    response.raise_for_status()
    
    print("Successfully posted armour data!")

    # dump json to file:
    dump_json('skills', skill_data)

    result = response.json()
    if 'errors' in result and result['errors']:
      print(f"Warning: Some items had errors: {result['errors']}")
    return True

  except requests.exceptions.RequestException as e:
    print(f"HTTP error posting skill data: {e}")
    return False
  except json.JSONDecodeError as e:
    print(f"Error parsing API response: {e}")
    return False
  except Exception as e:
    print(f"Unexpected error posting skill data: {e}")
    return False