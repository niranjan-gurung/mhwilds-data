from bs4 import BeautifulSoup
import requests
import requests.compat

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

def get_armour_data():
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

  if first_armour_link.text == 'Hope' and 'href' in first_armour_link.attrs:
    href = first_armour_link['href']
    armour_url = requests.compat.urljoin(url, href)
    new_res = requests.get(armour_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')

  tables = new_soup.find_all('tbody')
  #tables = soup.find_all('tbody')
  #t1 = tables[0]    # piece names
  t2 = tables[1]    # piece type + resistances
  t3 = tables[2]    # piece slot info

  # """
  # removes any excess words connected to 2nd word (starting with uppercase).
  # ex. 'Hope MaskArmour' -> 'Hope Mask'
  # One of the necessary fields for ArmourModel + Schema.
  # """
  #armour_pieces = re.findall(r'Hope [A-Z][a-z]+(?=[A-Z])?', t1.text)
  #print(armour_pieces)


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
    this block extracts slots information
    """
    rows = t3.find_all('tr')[1:]
    for row in rows:
      td = row.find_all('td')
      slot_row = td[2].get_text(strip=True) \
                      .strip('[]')          \
                      .split('][')
      slots = [{'level': int(slot)} for slot in slot_row if int(slot) != 0]

    data.append({
      'name': name,
      'slug': name.lower().replace(' ', '-'),
      'type': type.lower(),
      'rank': 'low',
      'rarity': 1,
      'defense': defense,
      'resistances': resistances,
      'slots': slots
    })

  return data
  #print(data)

  """
  Link to next armour set
  """
  # next_armour = new_soup.find(name='nav', attrs={'role': 'navigation'}) \
  #                       .find('ul') \
  #                       .find_all('li')[-1].find('a')
  # href = next_armour['href']
  # next_armour_url = requests.compat.urljoin(url, href)
  # new_res = requests.get(next_armour_url)
  # new_soup = BeautifulSoup(new_res.text, 'html.parser')

  # h = new_soup.find('h2')
  # print(h)