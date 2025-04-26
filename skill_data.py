from bs4 import BeautifulSoup
import requests
import requests.compat
import time

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

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

  armour_skills = t2.find_all('tr')

  skill_data: list = []

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
          'desc': skill_rank_desc
        })

      skill_data.append({
        'name': skill_name,
        'type': 'Armour',
        'desc': skill_desc,
        'ranks': ranks
      })
      print(f'proceed {href}')
    except Exception as e:
      print(f"Error processing {href}: {e}")

  return skill_data