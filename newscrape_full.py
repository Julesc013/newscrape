from shutil import copyfile
from openpyxl import Workbook
from openpyxl import load_workbook,styles
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from math import ceil
from datetime import datetime
import list_data # The file containing the lists of suburbs (in the same directory)


class listing: # Record structure to hold new listings found on each page.
    def __init__(self, business_name, phone_number, email_address, business_website, yellow_pages_link):
        self.business_name = business_name
        self.phone_number = phone_number
        self.email_address = email_address
        self.business_website = business_website
        self.yellow_pages_link = yellow_pages_link


def get_time_now():

    time = datetime.now()
    time_string = "[" + time.strftime("%d/%m/%Y %H:%M:%S") + "]"
    return time_string

def console_action(action, details):
    # E.g. Saving file...
    # No newline, first word yellow, has timestamp.

    print(r"\e[30m" + get_time_now() + r" \e[33m" + action + r" \e[0m" + details + "...", end="")

def console_complete(result, status): # Status is a boolean representing success
    # E.g. Done.
    # Newline, green or red.

    if status == True:
        colour = r" \e[32m" # Green
    else:
        colour = r" \e[31m" # Red

    print(r"\e[30m" + get_time_now() + colour + " " + result + "." + r" \e[0m")

def console_message(message):
    
    # Newline, magenta.
    print(r"\e[30m" + get_time_now() + r" \e[35m" + message + "." + r" \e[0m")


def find_match(sheet, column, text): # Search the existing data for matches... if found, don't count this as a new listing # Sheet must be an Excel worksheet, Column should be in set {A,B,C,D,E} and Text should be alphanumeric. # Returns True if a match is found.

    if text is not None: # Check that the string provided exists

        # Get all cells from specified column
        for cell in sheet[column]:

            if(cell.value is not None): # We need to check that the cell is not empty

                if cell.value == text: # Check if the value of the cell contains the text

                    return True # return true then break out of this function
        
    return False # Else (if none found) return false



# Define variables

browser = webdriver.Firefox()
address_base = ("https://www.yellowpages.com.au/search/listings?clue=", "&eventType=pagination&openNow=false&pageNumber=", "&referredBy=UNKNOWN&&state=", "&suburb=", "+") # [0], clue, [1], page, [2] state, [3] suburb+state)

clues = ('electricians+electrical+contractors', 'plumbers+gas+fitters', 'builders+building+contractors')
states = ('NSW', 'VIC', 'QLD', 'ACT', 'SA', 'WA', 'NT', 'TAS')

#pages_path = r"/home/webscraper/Documents/Newscrape/Pages/"
results_path = r"/home/webscraper/Documents/Newscrape/Results/"

all_path = results_path + "all_results.xlsx"
new_path = results_path + "new_results.xlsx"
template_path = results_path + "new_results_template.xlsx"

# Declare list that will hold listing records.
listings = []

# Get the list of suburbs (as a disctionary of tuples)
suburbs = list_data.get_suburbs()


# BEGIN ACTIONS

# Make a fresh copy of the new-results template for editing.

console_action("Copying spreadsheet template", "")

copyfile(template_path, new_path)

console_complete("Done", True)


# Download and extract data from every page!

# .split()[0]Loop through each, clue, state, suburb, and page.

for clue in clues:

    for state in states:

        for suburb in suburbs[state]: # Only the suburbs in this state

            # Reset page numbers file
            pages_number = -1

            # Loop through all pages
            page = 1
            while ( (page <= pages_number or pages_number == -1) and page <= 30):

                # Construct the url
                web_address = address_base[0] + clue + address_base[1] + str(page) + address_base[2] + state + address_base[3] + suburb + address_base[4] + state

                console_action("Getting", clue + "-" + state + "+" + suburb + "+" + page)
                
                # Get the html for this page
                browser.get(web_address)
                html_source = browser.page_source

                console_complete("Done", True)
                console_action("Parsing and extracting HTML code", "")

                soup = BeautifulSoup(html_source, 'html.parser')
                listings_html = soup.find_all("div", attrs={"class": "listing listing-search listing-data"})

                console_complete("Done", True)

                # If the number of pages hasn't been retrieved, get it from the page just downloaded
                if pages_number == -1:

                    console_action("Finding number of pages", "")

                    # Extract the number of results
                    results_number_parent = soup.find("div", attrs={"class": "cell search-message first-cell"})
                    results_number_html = results_number_parent.find("span", attrs={"class": "emphasise"})
                    results_number = int(results_number_html.text.split()[0])

                    # Do the math
                    if results_number >= 1 and results_number <= 1500:

                        pages_number = int(ceil(results_number / 35.0))

                        console_complete("Done", True)
                        
                    else:

                        pages_number = -1

                        console_complete("Unreasonable result", False)


                # Gather all listings' data and check if they have already been identified.

                for listing_html in listings_html:

                    console_action("Extracting listing", listing_html.get('data-listing-name'))

                    ## Make links absolute
                    base_url = "https://www.yellowpages.com.au"
                    #listing_html.make_links_absolute(base_url)


                    # Reset variables
                    business_name_html = None
                    phone_number_html = None
                    email_address_html = None
                    business_website_html = None
                    name = None
                    phone = None
                    email = None
                    website = None
                    yellow_page = None

                    # Get the html data of each match.
                    business_name_html = listing_html.find("a", attrs={"class": "listing-name"})
                    #phone_number_html = listing_html.find("a", attrs={"class": "click-to-call contact contact-preferred contact-phone"})
                    phone_number_html = listing_html.find("a", attrs={"class": lambda x: x and 'click-to-call contact contact-preferred' in x})
                    email_address_html = listing_html.find("a", attrs={"class": "contact contact-main contact-email"})
                    business_website_html = listing_html.find("a", attrs={"class": "contact contact-main contact-url"})


                    # Extract the appropriate sections of each html element.

                    # Get sections (only if they exist)
                    if business_name_html is not None:
                        name = business_name_html.text
                    if phone_number_html is not None:
                        phone = phone_number_html.get('href')
                    if email_address_html is not None:
                        email = email_address_html.get('data-email')
                    if business_website_html is not None:
                        website = business_website_html.get('href')
                    if business_name_html is not None:
                        yellow_page = business_name_html.get('href') # Link to the Yellow Pages listing.

                    # Add sections to a record
                    record = listing(name, phone, email, website, base_url + yellow_page)
                    #record = listing(name, phone, email, base_url + yellow_page) # Use the YP listing instead of the actual website temporarily.
                    # Append this record to the list of listings
                    listings.append(record)

                    console_complete("Done", True)


                page += 1 # Increment page number


# Check if each business listing already exists in our local database


# Load worksheets

console_action("Loading worksheets", "")

book_all = load_workbook(filename = all_path) # Load the workbook
sheet_all = book_all['Sheet1'] # Load the worksheet

book_new = load_workbook(filename = new_path) # Load the workbook
sheet_new = book_new['Sheet1'] # Load the worksheet

console_complete("Done", True)


# Get the last row in the sheet
final_row_all = sheet_all.max_row
final_row_new = 1 #sheet_new.max_row # Always start at the top of the sheet


# Loop through each newly retrieved record

index = 0
sheet_index = 0 # This is used so that no rows are skipped in the spreadsheet
listings_count = len(listings)
while index <= listings_count - 1:

    business = listings[index]

    console_action("Checking", business.business_name)

    this_name = business.business_name
    this_phone = business.phone_number
    this_email = business.email_address
    this_website = business.business_website
    this_yellow_page = business.yellow_pages_link

    # Search the sheet of all listings to see if it already exists
    this_name_exists = find_match(sheet_all, "A", this_name)
    this_phone_exists = find_match(sheet_all, "B", this_phone)
    this_email_exists = find_match(sheet_all, "C", this_email)
    this_website_exists = find_match(sheet_all, "D", this_website)
    this_yellow_page_exists = find_match(sheet_all, "E", this_yellow_page)

    if this_name_exists or this_phone_exists or this_email_exists or this_website_exists or this_yellow_page_exists: # If any of the searches returned a True result for existence

        console_complete("Already exists", False)

        # Keep sheet_index the same

    else:

        console_complete("Found new listing", True)

        # Add the new listing to both spreadsheets

        # Using the old max row as a base get the next row number to write to
        this_row_all = final_row_all + sheet_index + 1
        this_row_new = final_row_new + sheet_index + 1 # Start at the top

        console_action("Adding", business.business_name + " to spreadsheets")

        # Add to all listings sheet
        sheet_all.cell(row=this_row_all, column=1).value = this_name # Name
        sheet_all.cell(row=this_row_all, column=2).value = this_phone # Phone
        sheet_all.cell(row=this_row_all, column=3).value = this_email # Email
        sheet_all.cell(row=this_row_all, column=4).value = this_website # Website
        sheet_all.cell(row=this_row_all, column=5).value = this_yellow_page # Yellow Page

        # Add to new listings sheet
        sheet_new.cell(row=this_row_new, column=1).value = this_name # Name
        sheet_new.cell(row=this_row_new, column=2).value = this_phone # Phone
        sheet_new.cell(row=this_row_new, column=3).value = this_email # Email
        sheet_new.cell(row=this_row_new, column=4).value = this_website # Website
        sheet_new.cell(row=this_row_new, column=5).value = this_yellow_page # Yellow Page


        console_complete("Done", True)

        sheet_index += 1


    index += 1 # Increment index (b/c not using a for loop)

console_action("Saving all spreadsheets")

# Save the changes to the files
book_all.save(all_path)
book_new.save(new_path)

console_complete("Done", True)


# GET ASIC (ABN/ACN) DETAILS and SORT NEW LISTINGS BASED ON IF THEY HAVE A WEBSITE/ABN/ACN.
# EMAIL THE SHEETS.