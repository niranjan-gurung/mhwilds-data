from bs4 import BeautifulSoup
import requests
import requests.compat

url = 'https://mhwilds.kiranico.com/'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

homepage = soup.find(attrs={'data-sidebar': 'group-content'})
a = homepage.find_all('a')
for item in a:
  if item.text == 'Charms' and 'href' in item.attrs:
    href = item['href']
    ar_list_url = requests.compat.urljoin(url, href)
    new_res = requests.get(ar_list_url)
    new_soup = BeautifulSoup(new_res.text, 'html.parser')
    break

charms_link = new_soup.find('tbody') \
                      .find('tr') \
                      .find('a')
print(charms_link.text)