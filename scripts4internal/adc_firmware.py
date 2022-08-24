import re
import requests
from bs4 import BeautifulSoup

adc_url_in = 'https://www.citrix.com/en-in/downloads/citrix-adc/'

html_text = requests.get(adc_url_in).text
soup = BeautifulSoup(html_text, 'html.parser')
for i in [header.get_text(strip=False) for header in soup.find_all("td")]:
    print(i)
