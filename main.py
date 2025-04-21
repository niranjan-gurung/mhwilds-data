from bs4 import BeautifulSoup
import requests
import requests.compat
import re

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
this block goes from armour page to Hope armour page.
Each individual armour page has link to next or previous armour.
"""
#armour_names = []

first_armour_link = new_soup.find('tr') \
                            .find('td') \
                            .find('a')

if first_armour_link.text == 'Hope' and 'href' in first_armour_link.attrs:
    href = first_armour_link['href']
    armour_url = requests.compat.urljoin(url, href)
    new_res = requests.get(armour_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')

tables = new_soup.find_all('tbody')
t1 = tables[0]    # piece names
t2 = tables[1]    # piece type + resistances
t3 = tables[2]    # piece slot info

"""
removes any excess words connected to 2nd word (starting with uppercase).
ex. 'Hope MaskArmour' -> 'Hope Mask'
One of the necessary fields for ArmourModel + Schema.
"""
armour_pieces = re.findall(r'Hope [A-Z][a-z]+(?=[A-Z])?', t1.text)
# print(armour_pieces)


"""
Link to next armour set
"""
next_armour = new_soup.find(name='nav', attrs={'role': 'navigation'}) \
                      .find('ul') \
                      .find_all('li')[-1].find('a')
href = next_armour['href']
next_armour_url = requests.compat.urljoin(url, href)
new_res = requests.get(next_armour_url)
new_soup = BeautifulSoup(new_res.text, 'html.parser')

h = new_soup.find('h2')
print(h)

"""
old way... redundant now: 
"""
#print(tr_list.text)
# a = tr_list.
# print(a)
# for item in tr_list:
#   armour_links = item.find_all('a')

#   """
#   remove female version as we only want name of armour set.
#   stats, res, def, skills are basically duplicate of male ver.
#   """
#   if item.text != '':
#     armour_name.append(item.text)

#   for armour in armour_links:
#     if armour.text == 'Hope' and 'href' in armour.attrs:
#       href = armour['href']
#       print(href)
#       armour_url = requests.compat.urljoin(url, href)
#       print(armour_url)
#       new_res = requests.get(armour_url)
#       print(new_res)
#       new_soup = BeautifulSoup(new_res.text, 'html.parser')
#       break

# t = new_soup.find('h2')
# print(t)


