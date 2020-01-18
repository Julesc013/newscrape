import subprocess

address = "https://www.yellowpages.com.au/search/listings?clue=electricians+electrical+contractors&locationClue=sydney+cbd+nsw&lat=&lon=&referredBy=www.yellowpages.com.au&selectedViewMode=list&eventType=refinement&openNow=false&sortBy=relevance&suburb=Sydney+NSW"
browser = "firefox"
destination = "/home/webscraper/Documents/Newscrape/Pages/test10.html"

subprocess.call(["./save_page_as", address, "--browser", browser, "--destination", destination])