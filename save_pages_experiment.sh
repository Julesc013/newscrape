#!/bin/bash
# Run save_page_as for every page that requires saving.
# https://github.com/abiyani/automate-save-page-as


printf "SAVER: Saving all pages...\n">&2

# Declare universal variables.
loadwait=12
savewait=4
browser="firefox"

pagesmax=5
declare -a addressbase=("https://www.yellowpages.com.au/search/listings?clue=" "&eventType=pagination&openNow=false&pageNumber=" "&referredBy=UNKNOWN&&state=" "&suburb=" "+") # [0], clue, [1], page, [2] state, [3] suburb+state
directory="/home/webscraper/Documents/Newscrape/Pages/" # then add "filename.html"


# Declare search terms
declare -a clues=('electricians+electrical+contractors' 'plumbers+gas+fitters' 'builders+building+contractors')

# Later: cross reference with suburbs of other clues (catagories)
declare -a suburbsNSW=('Dubbo' 'Wagga+Wagga' 'Sydney')
declare -a suburbsVIC=('Melbourne' 'Bendigo' 'Ringwood')
declare -a suburbsQLD=('Cleveland' 'Townsville' 'Cairns')


# Remove existing pages (from the last scrape)
printf "SAVER: Removing existing pages...">&2
rm ~/Documents/Newscrape/Pages/*.html
printf " Done.\n">&2

# Loop through clues
for clue in "${clues[@]}"
do

   # Do each state
   # Loop through suburbs

   pagesmax >> ~/Documents/Newscrape/Binaries/pagesnumber.txt
   for suburb in "${suburbsNSW[@]}" # NSW
   do

      # Get number of results
      pagesnumber=$(cat ~/Documents/Newscrape/Binaries/pagesnumber.txt) # An integer usually less than 5.

      # Loop through pages

      page=1 # Page number counter
      while [ $page -le $pagesnumber ]
      do

         printf "SAVER: Saving '${clue}-NSW-${suburb}-${page}'...">&2

         # Construct URL
         address="${addressbase[0]}${clue}${addressbase[1]}${page}${addressbase[2]}NSW${addressbase[3]}${suburb}+NSW"
         destination="${directory}/${clue}-NSW-${suburb}-${page}.html"

         ./save_page_as.sh $address "--browser" $browser "--destination" $destination --load-wait-time $loadwait --save-wait-time $savewait

         pagesnumber=$(cat ~/Documents/Newscrape/Binaries/pagesnumber.txt) # Update this number after the first scrape of each new suburb.

         ((page++)) # Increment page counter

         printf " Done.">&2

      done

   done

done