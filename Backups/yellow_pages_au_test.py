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
    print(">> retrieving ",url)

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
            print(">> got page")
            #print(response.text)
            #page.write('response.html')

            print(">> parsing page now")
            print(">> status code:", response.status_code)
            if response.status_code==200:

                parser = html.fromstring(response.text)
                print(">> got html from response string")
                #making links absolute
                base_url = "https://www.yellowpages.com.au"
                parser.make_links_absolute(base_url)
                print(">> made links absolute")

                XPATH_LISTINGS = "//div[@class='flow-layout outside-gap-large inside-gap inside-gap-large vertical']//div[@class='v-card']" 
                listings = parser.xpath(XPATH_LISTINGS)
                scraped_results = []

                print(">> getting individual results from listings")
                for results in listings:
                    XPATH_BUSINESS_NAME = ".//a[@class='listing-name']//text()" 
                    XPATH_TELEPHONE = ".//span[@class='contact-text']//text()" 
                    XPATH_BUSSINESS_PAGE = ".//a[@class='listing-name']//@href" 
                    print(">> xpath done")

                    raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
                    raw_business_telephone = results.xpath(XPATH_TELEPHONE)	
                    raw_business_page = results.xpath(XPATH_BUSSINESS_PAGE)
                    print(">> raw done")

                    business_name = ''.join(raw_business_name).strip() if raw_business_name else None
                    telephone = ''.join(raw_business_telephone).strip() if raw_business_telephone else None
                    business_page = ''.join(raw_business_page).strip() if raw_business_page else None
                    print(">> join done")

                    business_details = {
                                        'business_name':business_name,
                                        'telephone':telephone,
                                        'business_page':business_page
                    }
                    scraped_results.append(business_details)
                    print(">> appended results record to file")

                print(">> returning scraped results")
                return scraped_results

            elif response.status_code==404:
                print("> Could not find a location matching",place)
                #no need to retry for non existing page
                break
            else:
                print("> Failed to process page")
                return []
                
        except:
            print("> Failed to process page")
            return []


if __name__=="__main__":
    
    print(">> entered main")

    argparser = argparse.ArgumentParser()
    argparser.add_argument('keyword',help = 'Search Keyword')
    argparser.add_argument('page',help = 'Page Number')
    
    print(">> got arguments")

    args = argparser.parse_args()
    keyword = args.keyword
    page = args.page
    scraped_data = parse_listing(keyword,page)	
    
    if scraped_data:
        print("> Writing scraped data to %s-%s-yellowpages-scraped-data.csv"%(keyword,page))
        with open('%s-%s-yellowpages-scraped-data.csv'%(keyword,page),'wb') as csvfile:
            #fieldnames = ['rank','business_name','telephone','business_page','category','website','rating','street','locality','region','zipcode','listing_url']
            fieldnames = ['business_name','telephone','business_page']
            writer = csv.DictWriter(csvfile,fieldnames = fieldnames,quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_data:
                writer.writerow(data)
