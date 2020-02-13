import os
from shutil import copyfile
from openpyxl import Workbook
from openpyxl import load_workbook,styles
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from math import ceil
from time import time, sleep
from datetime import datetime, date, time, timedelta
import list_data # The file containing the lists of suburbs (in the same directory)
import smtplib


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

def format_time_seconds(time_seconds):

    # Take in the time in seconds and return the HMS format string
    minutes, seconds = divmod(time_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{int(hours):d}:{int(minutes):02d}:{int(seconds):02d}'


def write_to_log(output):
    with open(log_file_path, 'a') as log_file:
        log_file.write(output)

def console_action(action, details):
    # E.g. Saving file...
    # No newline, first word yellow, has timestamp.

    if details != "":
        output = get_time_now() + " " + action + " " + details + "..."
    else:
        output = get_time_now() + " " + action + "..."

    print(output, end="")
    write_to_log(output)

def console_complete(result, status): # Status is a boolean representing success
    # E.g. Done.
    # Newline, green or red.

    output = " " + result + "."
    print(output)
    write_to_log(output + "\n")

def console_message(message):
    
    # Newline, magenta.
    output = get_time_now() + " " + message + "."
    print(output)
    write_to_log(output + "\n")


def find_match(sheet, column, text): # Search the existing data for matches... if found, don't count this as a new listing # Sheet must be an Excel worksheet, Column should be in set {A,B,C,D,E} and Text should be alphanumeric. # Returns True if a match is found.

    if text is not None: # Check that the string provided exists

        # Get all cells from specified column
        for cell in sheet[column]:

            if(cell.value is not None): # We need to check that the cell is not empty

                if cell.value == text: # Check if the value of the cell contains the text

                    return True # return true then break out of this function
        
    return False # Else (if none found) return false


# Define variables

version = "1.3.0"

time_atm = datetime.now() # Get time stamp for output files
time_atm_string = time_atm.strftime("%d%m%Y_%H%M%S")

# Email details
email_sender = 'newscrape.listings@gmail.com'
email_password = 'lettuce5'
email_recipient = 'newscrape.listings@gmail.com'


# Set capabilities of the firefox driver (specifically that it is allowed to ignore SSL/insecurity warnings)
browser_capabilities = DesiredCapabilities.FIREFOX.copy()
browser_capabilities['accept_untrusted_certs'] = True

address_base = ("https://www.yellowpages.com.au/search/listings?clue=", "&eventType=pagination&openNow=false&pageNumber=", "&referredBy=UNKNOWN&&state=", "&suburb=", "+") # [0], clue, [1], page, [2] state, [3] suburb+state)

clues = list_data.get_clues() # Clues (as a tuple)
states = list_data.get_states() # States (as a tuple)
suburbs = list_data.get_suburbs() # Suburbs (as a disctionary of tuples)

logs_path = r"/home/webscraper/Documents/Newscrape/Logs/"
results_path = r"/home/webscraper/Documents/Newscrape/Results/"

all_path = results_path + "all_results.xlsx"
all_backup_path = results_path + "all_results_" + time_atm_string + ".xlsx.bak"
new_path = results_path + "new_results_" + time_atm_string + ".xlsx"
template_path = results_path + "new_results_template.xlsx"

# Declare lists that will hold listing records.
listings = []
#new_listings = []



# BEGIN ACTIONS


print("NEWSCRAPE – Yellow Pages Web-Scraper", \
    "Jules Carboni, Copyright 2020, Version " + version, \
    sep="\n")

# Make a new log file for this session

if not os.path.exists(logs_path): # Create the directories if they don't exist
    os.makedirs(logs_path)

# Make filename and path
log_file_name = "newscrape_" + time_atm_string + ".log"
log_file_path = os.path.join(logs_path, log_file_name)

with open(log_file_path, 'w') as log_file:
    log_file.write('Newscrape Console Log ' + get_time_now() + " (Jules Carboni, Copyright 2020, Version " + version + ")\n") # Write the header

console_message("Created new log file " + log_file_name)



# Count total pages to search through

total_clues = len(clues)
pages_multiplier = 1.0185 # Add 1.85% (derived from test data)
time_per_search = 11.8041 # Experimental value from first actual run
time_per_check = 1.0673 # NOT A REAL VALUE, ONLY AN ESTIMATE, REPLACE LATER
time_per_rank = 0 #TEMPVAR (ASIC RANKING) # CURRENTLY 0 BECAUSE NOT IMPLEMENTED

total_suburbs = 0
for state in states:
    total_suburbs += len(suburbs[state]) # Add up all the suburbs
total_searches = total_suburbs * total_clues # Multiply by the number of times we have to fetch from each suburb
expected_searches = total_searches * pages_multiplier # Multiply to get add the amount of pages we expect to be in total
checks_per_clue = 4.273 * total_suburbs * pages_multiplier # A really rough average
ranks_per_clue = 0.05 * total_suburbs * pages_multiplier #TEMPVAR (ASIC RANKING)
total_checks = checks_per_clue * total_clues
total_ranks = ranks_per_clue * total_clues

expected_duration = expected_searches * time_per_search + total_checks * time_per_check + total_ranks * time_per_rank # Calculate the expected total duration of the program
expected_duration_timedelta = timedelta(seconds=expected_duration)

start_time = datetime.now()

# Print this information and time estimates

console_message("Calculated expected results..." + "\n" \
    "Total suburbs to search: " + str(total_suburbs) + "\n" \
    "Total searches to do: " + str(total_searches) + "\n" \
    "Expected total pages to search: " + str(int(expected_searches)) + "\n" \
    "Expected run duration: " + format_time_seconds(expected_duration) + " (" + str(expected_duration_timedelta.days) + " days)" + "\n" \
    "Expected time of completion: " + str(start_time + expected_duration_timedelta) \
    )



# Make a fresh copy of the new-results template for editing.
console_action("Making new spreadsheets", "")
copyfile(template_path, new_path) # Create new blank sheet for new listings
copyfile(all_path, all_backup_path) # Create a backup of the current sheet of all listings
console_complete("Done", True)



# Initialise the selenium webdriver
browser = webdriver.Firefox(capabilities=browser_capabilities)
webdriver.Firefox.quit


# Download and extract data from every page!

# Initialise counting variables
suburbs_counter = 0
pages_counter = 0

# Loop through each, clue, state, suburb, and page.

try:

    for clue in clues:

        for state in states:

            for suburb in suburbs[state]: # Only the suburbs in this state

                suburbs_counter += 1

                # Reset page numbers file
                pages_number = -1

                # Loop through all pages
                page = 1
                while ( (page <= pages_number or pages_number == -1) and page <= 8):
                    
                    print() # Add an empty line (to the terminal printout only) to make it more readable at a glance # DEBUG

                    pages_counter += 1


                    # Construct the url
                    web_address = address_base[0] + clue + address_base[1] + str(page) + address_base[2] + state + address_base[3] + suburb + address_base[4] + state


                    # Get the html for this page
                    while True: # Loop forever until successful
                        try:
                            
                            # Get time values for the console display
                            percentage_complete = (suburbs_counter / total_searches) * 100
                            time_remaining = expected_duration - (suburbs_counter * time_per_search)
                            #time_remaining_timedelta = timedelta(seconds=time_remaining)

                            progress_stamp = "[" + str(round(percentage_complete, 2)) + "% T-" + format_time_seconds(time_remaining) + "] "
                            console_action(progress_stamp + "Getting", web_address)
                    
                            browser.get(web_address) # Get the webpage from the Internet
                            #WebDriverWait(driver, 30).until(readystate_complete) # Wait until the page is fully loaded

                            html_source = browser.page_source # Get the source from the browser driver

                            console_complete("Done", True)
                            break

                        except KeyboardInterrupt:

                            console_complete("Skipped", False)
                            #IN FUTURE MAKE IT SO: Stop trying to download this page and skip the rest of this iteration (return to top of outer while loop)

                            exit() # Exit the entire program as a ^C normally would

                        except Exception as ex:

                            console_complete("Failed (" + str(ex) + ")", False) # Display error message (details)


                            # Reinitialise the selenium webdriver to circumvent certificate errors
                            console_action("Restarting web driver", "")

                            browser.quit() # Gracefully quit driver
                            browser = webdriver.Firefox(capabilities=browser_capabilities) # Restart the driver
                            
                            console_complete("Done", True)


                            # Wait ten seconds before retrying
                            #sleep(10)



                    console_action("Parsing and extracting HTML code", "")

                    soup = BeautifulSoup(html_source, 'html.parser')
                    listings_html = soup.find_all("div", attrs={"class": "listing listing-search listing-data"})

                    console_complete("Done", True)

                    # If the number of pages hasn't been retrieved, get it from the page just downloaded
                    if pages_number == -1:

                        console_action("Finding number of pages", "")

                        try:
                                
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
                            
                        except:

                            pages_number = 0

                            console_complete("Failed (assuming zero results)", False)


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

except Exception as ex:

    # If any shit hits the fan, stop searching and move onto checking so that we at least don't lose the listings we have

    console_message("Searching interrupted unexpectedly (" + str(ex) + ")")


browser.quit() # Gracefully quit driver, all done getting pages (ALWAYS DO THIS)


time_searching_done = datetime.now() # The time at which all the downloading and searching was completed



# Check if each business listing already exists in our local database

try:

    # Load all-results worksheet

    console_action("Loading worksheets", "")

    book_all = load_workbook(filename = all_path) # Load the workbook
    sheet_all = book_all['Sheet1'] # Load the worksheet

    book_new = load_workbook(filename = new_path) # Load the workbook
    sheet_new = book_new['Sheet1'] # Load the worksheet

    console_complete("Done", True)


    # Get the last row in the sheet
    final_row_all = sheet_all.max_row
    final_row_new = 1 #sheet_new.max_row # Always start at the top of the sheet


    # Calculate the expected time remaining
    expected_duration_remaining = expected_duration - (expected_searches * time_per_search)


    # Loop through each newly retrieved record

    index = 0
    # Use seperate indexes for sheets so that no rows are skipped in the spreadsheet
    sheet_index_all = final_row_all
    sheet_index_new = final_row_new

    listings_count = len(listings) # For each listing gathered
    while index <= listings_count - 1:

        business = listings[index]

        # Get time values for the console display
        percentage_complete = (index / listings_count) * 100
        time_remaining = expected_duration_remaining - (index * time_per_check)

        progress_stamp = "[" + str(round(percentage_complete, 2)) + "% T-" + format_time_seconds(time_remaining) + "] "
        console_action(progress_stamp + "Checking", business.business_name)

        this_name = business.business_name
        this_phone = business.phone_number
        this_email = business.email_address
        this_website = business.business_website
        this_yellow_page = business.yellow_pages_link

        # Search the sheet of all listings to see if it already exists
        #this_name_exists = find_match(sheet_all, "A", this_name)
        this_name_exists = False # ALWAYS RETURN FALSE, WE WANT TO IGNORE THIS CHECK
        this_phone_exists = find_match(sheet_all, "B", this_phone)
        this_email_exists = find_match(sheet_all, "C", this_email)
        this_website_exists = find_match(sheet_all, "D", this_website)
        this_yellow_page_exists = find_match(sheet_all, "E", this_yellow_page)

        if this_name_exists or this_phone_exists or this_email_exists or this_website_exists or this_yellow_page_exists: # If any of the searches returned a True result for existence

            console_complete("Already exists", False)

            # Keep sheet indexes the same

        else:

            console_complete("Found new listing", True)

            # Add the new listing to all-results spreadsheet

            # Using the old max row as a base get the next row number to write to
            # AKA Increment the indexes for this new row
            sheet_index_all += 1
            sheet_index_new += 1

            console_action("Adding", business.business_name + " to spreadsheets")


            # Add to all listings sheet
            sheet_all.cell(row=sheet_index_all, column=1).value = this_name # Name
            sheet_all.cell(row=sheet_index_all, column=2).value = this_phone # Phone
            sheet_all.cell(row=sheet_index_all, column=3).value = this_email # Email
            sheet_all.cell(row=sheet_index_all, column=4).value = this_website # Website
            sheet_all.cell(row=sheet_index_all, column=5).value = this_yellow_page # Yellow Page


            ##console_action("Getting ASIC data for", business.business_name)

            ####### GET ASIC DATA!!!!!!!!!!!!!!!!!!
            # GET ASIC (ABN/ACN) DETAILS and SORT NEW LISTINGS BASED ON IF THEY HAVE A WEBSITE/ABN/ACN ((SEE ABOVE--GOES INSIDE FOR LOOP)).
            # ADD ASIC RANKING TO TIME CALCULATIONS
            #### Use the data in an algorithm to produce a ranking!!!


            # Add to new listings sheet
            sheet_new.cell(row=sheet_index_new, column=1).value = this_name # Name
            sheet_new.cell(row=sheet_index_new, column=2).value = this_phone # Phone
            sheet_new.cell(row=sheet_index_new, column=3).value = this_email # Email
            sheet_new.cell(row=sheet_index_new, column=4).value = this_website # Website
            sheet_new.cell(row=sheet_index_new, column=5).value = this_yellow_page # Yellow Page


            # Save the changes to the files
            book_all.save(all_path)
            book_new.save(new_path)


            console_complete("Done", True)


        index += 1 # Increment index (b/c not using a for loop)


except Exception as ex:

    # If any shit hits the fan, stop checking and move onto emailing so that we at least don't lose the listings we have

    console_message("Checking interrupted unexpectedly (" + str(ex) + ")")


# Save all changes
console_action("Saving spreadsheets", "") # ALWAYS DO THIS

# Save the changes to the files
book_all.save(all_path)
book_new.save(new_path)

book_all.close()

console_complete("Done", True)


time_checking_done = datetime.now() # The time at which all the checking was completed (incl. writing to the all-spreadsheet)

#time_ranking_done = datetime.now() # The time at which all the ranking (with ASIC) was completed (incl. writing to the new spreadsheet)



# EMAIL THE SHEETS.

# Calculate listings totals
#total_pages_count = pages_counter
total_listings_count = len(listings)
#new_listings_count = len(new_listings)
new_listings_count = sheet_index_new - final_row_new
#all_listings_count = sheet_index_all - final_row_all #same as tot_list_count


console_action("Emailing results", "")

start_time_string = start_time.strftime("%d %B")
emailing_time_string = datetime.date.today().strftime("%d %B")

sent_from = email_sender
to = [email_recipient]
subject = 'New Listings from ' + start_time_string + ' to ' + emailing_time_string
body = 'Number of new listings: ' + str(new_listings_count)

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(email_sender, email_password)
    server.sendmail(sent_from, to, email_text)
    server.close()

    console_complete(True, "Success")

except Exception as ex:

    console_complete(False, "Failed (" + str(ex) + ")")



# Calculate and print statistics
# (Already calulated listings totals)

finish_time = datetime.now()
total_duration = finish_time - start_time
difference_duration = total_duration - expected_duration_timedelta

time_searching_duration = time_searching_done - start_time
time_checking_duration = time_checking_done - time_searching_done
#time_ranking_duration = time_ranking_done - time_checking_done

time_per_search_actual = time_searching_duration / expected_searches
time_per_check_actual = time_checking_duration / total_listings_count
#time_per_rank_actual = time_ranking_duration / new_listings_count

console_message("Calculated actual results..." + "\n" \
    "Total pages: " + str(pages_counter) + "\n" \
    "Total listings: " + str(total_listings_count) + "\n" \
    "Total new listings: " + str(new_listings_count) + "\n" \
    "Duration of searching: " + str(time_searching_duration) + "\n" \
    "Duration of checking: " + str(time_checking_duration) + "\n" \
    #"Duration of ranking: " + str(time_ranking_duration) + "\n" \
    "Total duration: " + str(total_duration) + "\n" \
    "Expected duration: " + str(expected_duration_timedelta) + "\n" \
    "Difference from expected: " + str(difference_duration) + "\n" \
    "Time per search: " + str(time_per_search_actual) + "\n" \
    "Time per check: " + str(time_per_check_actual) \
    #"Time per rank: " + str(time_per_rank_actual) \
    )