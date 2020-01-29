#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests

print('Enter a city to search and what to find there.',
'\nExample:\nWhere do you want to search? manchester nh',
'\nWhat are you looking for? pawn shops',
'\nHow many pages of results? 2\n')

# spaces are replaced by dashes for use in the url
location = input('Where do you want to search? ').replace(' ', '-')
thing = input('What are you looking for? ').replace(' ', '-')
pages = int(input('How many pages of results? '))
print('Finding...\n')

url = 'http://www.yellowpages.com/{0}/{1}'.format(location, thing)

for page in range(pages):
	
	next_page = url + '?page={}'.format(page+1)

	r = requests.get(next_page)
	
	soup = BeautifulSoup(r.content, "lxml")

	data = soup.find_all('div', {'class': 'info'})

	for business in data:
		print('\n', end='')

		try:
			print(business.contents[0].find_all('a', {'class': 'business-name'})[0].text)
			print(business.contents[1].find_all('span', {'itemprop': 'streetAddress'})[0].text)
			print(business.contents[1].find_all('span', {'itemprop': 'addressLocality'})[0].text.replace(',',''))
			print(business.contents[1].find_all('span', {'itemprop': 'addressRegion'})[0].text)
			print(business.contents[1].find_all('span', {'itemprop': 'postalCode'})[0].text)
			print(business.contents[1].find_all('div', {'class': 'primary'})[0].text)
		except:
			pass
