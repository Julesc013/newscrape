#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import csv

print('Enter a city to search and what to find there.',
'\nExample:\nWhere do you want to search? manchester nh',
'\nWhat are you looking for? pawn shops',
'\nHow many pages of results? 2\n')

# get input from the user
# spaces are replaced by dashes for use in the url
location = input('Where do you want to search? ').replace(' ', '-')
thing = input('What are you looking for? ').replace(' ', '-')
pages = int(input('How many pages of results? '))
print('Finding...\n')

# set the base url
url = 'http://www.yellowpages.com/{0}/{1}'.format(location, thing)

# iterate over the requested number of pages
for page in range(pages):
	
    # set the page number by appending the url
    next_page = url + '?page={}'.format(page+1)
	
    # request the page
    r = requests.get(next_page)
	
    # create the beautiful soup content
    soup = BeautifulSoup(r.content, 'lxml')

    # find all the div tags with class "info" and put them in data
    data = soup.find_all('div', {'class': 'info'})

    # iterate over the entries in data
    for business in data:

        # find all occurrences of the desired info
        # get the text and write it to a file
        try:
            with open('info.csv', 'a') as file:
                writer = csv.writer(file)

                # convert beautiful soup objects into strings
                name = str(business.contents[0].find_all('a', {'class': 'business-name'})[0].text)
                address = str(business.contents[1].find_all('span', {'itemprop': 'streetAddress'})[0].text)
                locality = str(business.contents[1].find_all('span', {'itemprop': 'addressLocality'})[0].text.replace(',','')).rstrip()
                region = str(business.contents[1].find_all('span', {'itemprop': 'addressRegion'})[0].text)
                postal_code = str(business.contents[1].find_all('span', {'itemprop': 'postalCode'})[0].text)
                primary = str(business.contents[1].find_all('div', {'class': 'primary'})[0].text)

                # write to the file
                writer.writerow([name, address, locality, region, "\'" + postal_code, primary])

        except:
            pass

print('Done.')
