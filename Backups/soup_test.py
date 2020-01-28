# Proof of concept to show that a Pyhton web scraper can work with Yellow Pages.


# import libraries
import urllib.request
from bs4 import BeautifulSoup
import csv
from datetime import datetime


# specify the url to get
page_set = 'https://www.yellowpages.com.au/find/electricians/'


# mimic a popular human browser
headers = {}
headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0"

# query the website and return the html
req = urllib.request.Request(page_set, headers = headers)
print("request sent")
html = urllib.request.urlopen(req).read()
print(html)

# parse the html using beautiful soup and store in variable "soup"
soup = BeautifulSoup(html, 'html.parser')
print("souped up")

# Take out the <div> of name and get its value
listing_name = soup.find('a', attrs={'href': 'https://www.google.com/intl/en/policies/terms/'})
name = listing_name.text.strip() # strip() is used to remove starting and trailing
print(name)


# open a csv file with append, so old data will not be erased
with open('index.csv', 'a') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([name, datetime.now()])