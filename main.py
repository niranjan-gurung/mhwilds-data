from bs4 import BeautifulSoup
import requests
import requests.compat

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

"""
Starting to work... kinda
"""

"""
this block goes from homepage to armour page
"""
data = soup.find(attrs={'data-sidebar': 'group-content'})
a = data.find_all('a')
for item in a:
  if item.text == 'Armor' and 'href' in item.attrs:
    href = item['href']
    ar_list_url = requests.compat.urljoin(url, href)
    new_res = requests.get(ar_list_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
    break


"""
this block goes from armour page to specific armour page.

- need a way to dynamically compare armour name:
  - append names to list and use that list instead of hard code. 
"""
armour_name = []
tr_list = new_soup.find_all('tr')
for item in tr_list:
  armour_links = item.find_all('a')

  """
  remove female version as we only want name of armour set.
  stats, res, def, skills are basically duplicate of male ver.
  """
  if item.text != '':
    armour_name.append(item.text)

  for armour in armour_links:
    if armour.text == 'Hope' and 'href' in armour.attrs:
      href = armour['href']
      print(href)
      armour_url = requests.compat.urljoin(url, href)
      print(armour_url)
      new_res = requests.get(armour_url)
      print(new_res)
      new_soup = BeautifulSoup(new_res.text, 'html.parser')
      break

t = new_soup.find('h2')
print(t)

#armours = []

# for item in tbody.contents:
#   if item.text == '': continue
#   print(item.get_text())
  # armours.append(item.text)
  #print(item.find_next())

#print(armours)

# armour_name = data[0]
# armour_type = data[1]   # do some filter / ignore name + resistances + th
# restances = data[1]     # do some filter / ignore type + name + th
# slots = data[2]         # ignore type, name, skills
# skills = data[2]        # ignore type, name, slots

# for item in data[1].contents:
#   print(item.text)

# for item in data[2].contents:
#   print(item.text)


#print(data[1].prettify())
#print(ul.prettify())



