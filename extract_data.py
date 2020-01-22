import os
import subprocess
from shutil import copyfile
from openpyxl import Workbook
from openpyxl import load_workbook,styles
import requests
from lxml import html
import unicodecsv as csv
import argparse



def search_data(sheet, column, text): # Search the existing data for matches... if found, don't count this as a new listing # Sheet must be an Excel worksheet, Column should be in set {A,B,C,D} and Text should be alphanumeric.

    # Get all cells from specified column
    for cell in sheet[column]:
        if(cell.value is not None): # We need to check that the cell is not empty
            if text in cell.value: # Check if the value of the cell contains the text of the business phone number
                return True # return true then break out of this function
    
    return False # Else (if none found) return false



# Define variables

pages_path = r"/home/webscraper/Documents/Newscrape/Pages/"
results_path = r"/home/webscraper/Documents/Newscrape/Results/"
all_path = results_path + "all_results.xlsx"
new_path = results_path + "new_results.xlsx"
template_path = results_path + "new_results_template.xlsx"


# Make a fresh copy of the new-results template for editing.

print("Copying spreadsheet template...", end="")

copyfile(template_path, new_path)

print(" Done.")


# Load worksheets

print("Loading worksheets...", end="")

book_all = load_workbook(filename = all_path) # Load the workbook
sheet_all = book_all['Sheet1'] # Load the worksheet

book_new = load_workbook(filename = new_path) # Load the workbook
sheet_new = book_new['Sheet1'] # Load the worksheet

print(" Done.")


pages_bytes = os.fsencode(pages_path) # Get the directory thing
for page_bytes in os.listdir(pages_bytes):
    page_file = os.fsdecode(page_bytes)

    print("Parsing " + page_file + "...") # DEBUG
    parser = html.fromstring(page_file) #page_path.text

    # Make links absolute
    base_url = "https://www.yellowpages.com.au"
    parser.make_links_absolute(base_url)

    XPATH_LISTINGS = "//div[@class='search-results search-results-data listing-group']//div[@class='flow-layout outside-gap-large inside-gap inside-gap-large vertical']//div[conatins(@class, 'cell in-area-cell find-show-more-trial']//div[@class='listing listing-search listing-data']//div[contains(@class, 'search-contact-card')]//div[contains(@class, 'search-contact-card-table-div')]" # Get the class containing all the listings from this page
    listings = parser.xpath(XPATH_LISTINGS)

    print(listings)

    for results in listings:

        # For each business on this page, gather their data and check if they have already been identified.

        XPATH_BUSINESS_NAME = ".//table//tbody//tr[@class='search-contact-card-row']//td[@class='search-contact-card-top']//div[contains(@class, 'listing-details')]//div[contains(@class, 'flow-layout')]//div[contains(@class, 'first-cell')]//div[@class='flow-layout outside-gap-large inside-gap inside-gap-medium vertical']//div[@class='cell first-cell last-cell']//div[contains(@class, 'inside-gap-medium vertical')]//div[@class='cell first-cell']//div[contains(@class, 'listing-summary')]//div[@class='body left right']//h2//a[@class='listing-name']//text()" 
        ##XPATH_BUSSINESS_PAGE = ".//a[@class='listing-name']//@href" 
        XPATH_TELEPHONE = ".//a[@class='click-to-call contact contact-preferred contact-phone']//@href"
        XPATH_ADDRESS = ".//a[@class='contact contact-main contact-email']//@data-email"
        ##XPATH_LOCATION = ".//p[@class='listing-address mappable-address']//text()"
        #XPATH_STREET = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='streetAddress']//text()"
        #XPATH_LOCALITY = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='addressLocality']//text()"
        #XPATH_REGION = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='addressRegion']//text()"
        #XPATH_ZIP_CODE = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='postalCode']//text()"
        #XPATH_RANK = ".//div[@class='info']//h2[@class='n']/text()"
        #XPATH_CATEGORIES = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='categories']//text()"
        XPATH_WEBSITE = ".//a[@class='contact contact-main contact-url']//@href"
        #XPATH_RATING = ".//div[@class='info']//div[contains(@class,'info-section')]//div[contains(@class,'result-rating')]//span//text()"

        raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
        raw_business_telephone = results.xpath(XPATH_TELEPHONE)	
        ##raw_business_page = results.xpath(XPATH_BUSSINESS_PAGE)
        #raw_categories = results.xpath(XPATH_CATEGORIES)
        raw_website = results.xpath(XPATH_WEBSITE)
        #raw_rating = results.xpath(XPATH_RATING)
        # address = results.xpath(XPATH_ADDRESS)
        #raw_street = results.xpath(XPATH_STREET)
        #raw_locality = results.xpath(XPATH_LOCALITY)
        #raw_region = results.xpath(XPATH_REGION)
        #raw_zip_code = results.xpath(XPATH_ZIP_CODE)
        #aw_rank = results.xpath(XPATH_RANK)
        raw_address = results.xpath(XPATH_ADDRESS)
        ##raw_location = results.xpath(XPATH_LOCATION)
        
        business_name = ''.join(raw_business_name).strip() if raw_business_name else None
        telephone = ''.join(raw_business_telephone).strip() if raw_business_telephone else None
        ##business_page = ''.join(raw_business_page).strip() if raw_business_page else None
        #rank = ''.join(raw_rank).replace('.\xa0','') if raw_rank else None
        #category = ','.join(raw_categories).strip() if raw_categories else None
        website = ''.join(raw_website).strip() if raw_website else None
        #rating = ''.join(raw_rating).replace("(","").replace(")","").strip() if raw_rating else None
        #street = ''.join(raw_street).strip() if raw_street else None
        #locality = ''.join(raw_locality).replace(',\xa0','').strip() if raw_locality else None
        #region = ''.join(raw_region).strip() if raw_region else None
        #zipcode = ''.join(raw_zip_code).strip() if raw_zip_code else None
        address = ''.join(raw_address).strip() if raw_address else None
        ##location = ''.join(raw_location).strip() if raw_location else None


        # Check if this business listing exists


        #TEST PRINT
        print(business_name + telephone + address + website)