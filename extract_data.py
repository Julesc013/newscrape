import os
import subprocess
from shutil import copyfile
from openpyxl import Workbook
from openpyxl import load_workbook,styles
import requests
from lxml import html
from bs4 import BeautifulSoup
import unicodecsv as csv
import argparse
from requests_testadapter import Resp

class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        with open(file_path, 'rb') as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff)
            r = self.build_response(request, resp)

            return r

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):

        return self.build_response_from_file(request)


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


####################################https://www.pluralsight.com/guides/extracting-data-html-beautifulsoup

pages_bytes = os.fsencode(pages_path) # Get the directory link
for page_bytes in os.listdir(pages_bytes):

    # Get file name and path
    page_file = os.fsdecode(page_bytes)
    page_path = pages_path + page_file

    print("Parsing " + page_file + "...", end="") # DEBUG
    
    requests_session = requests.session()
    requests_session.mount('file://', LocalFileAdapter())
    response = requests_session.get('file://' + page_path)

    # Check that the page parsed correctly before processing the data.
    if response.status_code==200:

        print(" Success.")

        soup = BeautifulSoup(response.text, 'html.parser')


        # Gather all listings' data and check if they have already been identified.

        XPATH_BUSINESS_NAME = "//a[@class='listing-name']//text()"
        XPATH_TELEPHONE = "//a[@class='click-to-call contact contact-preferred contact-phone']//@href"
        XPATH_ADDRESS = "//a[@class='contact contact-main contact-email']//@data-email"
        XPATH_WEBSITE = "//a[@class='contact contact-main contact-url']//@href"

        raw_business_names = soup.xpath(XPATH_BUSINESS_NAME)
        raw_business_telephones = soup.xpath(XPATH_TELEPHONE)
        raw_websites = soup.xpath(XPATH_WEBSITE)
        raw_addresses = soup.xpath(XPATH_ADDRESS)
        

        #TEST PRINT DEBUG
        print(raw_business_names)


        # Check if this business listing exists


    else:
        print(" Failed. Error code: " + response.status_code)
        