#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from lxml import html
import unicodecsv as csv
import argparse

def parse_listing(keyword,page):
	"""
	
	Function to process yellowpage listing page 
	: param keyword: search query
    : param page : results page number

	"""
	# Sample URL: https://www.yellowpages.com.au/search/listings?clue=Electricians+%26+Electrical+Contractors&pageNumber=5&referredBy=www.yellowpages.com.au&&eventType=pagination
	url = "https://www.yellowpages.com.au/search/listings?clue={0}&pageNumber={1}&referredBy=www.yellowpages.com.au&&eventType=pagination".format(keyword,page)
	print("retrieving ",url)

	headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
				'Accept-Encoding':'gzip, deflate, br',
				'Accept-Language':'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
				'Cache-Control':'max-age=0',
				'Connection':'keep-alive',
				'Host':'www.yellowpages.com.au',
				'Upgrade-Insecure-Requests':'1',
				'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
			}
	# Adding retries
	for retry in range(10):
		try:
			response = requests.get(url,verify=False, headers = headers )
			print("parsing page")
			if response.status_code==200:
				parser = html.fromstring(response.text)
				#making links absolute
				base_url = "https://www.yellowpages.com.au"
				parser.make_links_absolute(base_url)

				XPATH_LISTINGS = "//div[@class='flow-layout outside-gap-large inside-gap inside-gap-large vertical']//div[@class='v-card']" 
				listings = parser.xpath(XPATH_LISTINGS)
				scraped_results = []

				for results in listings:
					XPATH_BUSINESS_NAME = ".//a[@class='listing-name']//text()" 
					XPATH_TELEPHONE = ".//span[@class='contact-text']//text()" 
					XPATH_BUSSINESS_PAGE = ".//a[@class='listing-name']//@href" 

					raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
					raw_business_telephone = results.xpath(XPATH_TELEPHONE)	
					raw_business_page = results.xpath(XPATH_BUSSINESS_PAGE)
					
					business_name = ''.join(raw_business_name).strip() if raw_business_name else None
					telephone = ''.join(raw_business_telephone).strip() if raw_business_telephone else None
					business_page = ''.join(raw_business_page).strip() if raw_business_page else None


					business_details = {
										'business_name':business_name,
										'telephone':telephone,
										'business_page':business_page
					}
					scraped_results.append(business_details)


				return scraped_results

			elif response.status_code==404:
				print("Could not find a location matching",place)
				#no need to retry for non existing page
				break
			else:
				print("Failed to process page")
				return []
				
		except:
			print("Failed to process page")
			return []


if __name__=="__main__":
	
	argparser = argparse.ArgumentParser()
	argparser.add_argument('keyword',help = 'Search Keyword')
	argparser.add_argument('page',help = 'Page Number')
	
	args = argparser.parse_args()
	keyword = args.keyword
	page = args.page
	scraped_data =  parse_listing(keyword,page)	
	
	if scraped_data:
		print("Writing scraped data to %s-%s-yellowpages-scraped-data.csv"%(keyword,page))
		with open('%s-%s-yellowpages-scraped-data.csv'%(keyword,page),'wb') as csvfile:
			#fieldnames = ['rank','business_name','telephone','business_page','category','website','rating','street','locality','region','zipcode','listing_url']
			fieldnames = ['business_name','telephone','business_page']
			writer = csv.DictWriter(csvfile,fieldnames = fieldnames,quoting=csv.QUOTE_ALL)
			writer.writeheader()
			for data in scraped_data:
				writer.writerow(data)
