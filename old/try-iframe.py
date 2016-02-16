# -*- coding: utf-8 -*-
import re
from urlparse import urljoin
from urlparse import urlparse, parse_qs

from bs4 import BeautifulSoup
import requests


BASE_URL = 'http://cinema.arte.tv/fr/magazine/court-circuit/emissions'
URL = "http://cinema.arte.tv/fr/article/zero-de-david-gesslbauer-et-michael-lange"
BASE_ACCESS_URL = 'http://daccess-ods.un.org'

# start session
session = requests.Session()
response = session.get(URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})

# get frame links
soup = BeautifulSoup(response.text)
#~ frames = soup.find_all('frame')
iframe = soup.find("div", class_="has-iframe")
#~ header_link, document_link = [urljoin(BASE_URL, frame.get('src')) for frame in frames]
document_link = iframe.find("iframe")['src']

parse_url = parse_qs(urlparse(document_link).query)
url_final = parse_url['json_url'][0]
url_final_new = url_final.replace("EXTRAIT", "PLUS7")

print url_final_new
print type(url_final_new)

exit()
 #~ et ici on tombe sur un json comme une video classique




    

# get header
session.get(header_link, headers={'Referer': URL})

# get document html url
response = session.get(document_link, headers={'Referer': URL})
soup = BeautifulSoup(response.text)

content = soup.find('meta', content=re.compile('URL='))['content']
document_html_link = re.search('URL=(.*)', content).group(1)
document_html_link = urljoin(BASE_ACCESS_URL, document_html_link)

# follow html link and get the pdf link
response = session.get(document_html_link)
soup = BeautifulSoup(response.text)

# get the real document link
content = soup.find('meta', content=re.compile('URL='))['content']
document_link = re.search('URL=(.*)', content).group(1)
document_link = urljoin(BASE_ACCESS_URL, document_link)
print document_link

# follow the frame link with login and password first - would set the important cookie
auth_link = soup.find('frame', {'name': 'footer'})['src']
session.get(auth_link)

# download file
with open('document.pdf', 'wb') as handle:
    response = session.get(document_link, stream=True)

    for block in response.iter_content(1024):
        if not block:
            break

        handle.write(block)