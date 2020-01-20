#!/bin/bash
# Run save_page_as for every page that requires saving.
# https://github.com/abiyani/automate-save-page-as


printf "SAVER: Saving all pages...\n">&2

# Declare universal variables.
loadwait=12
savewait=4
browser="firefox"

pagesmax=6 # Put this into the pagesnumber text file before it is populated with an actual result.
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

   rm ~/Documents/Newscrape/Binaries/pagesnumber.txt
   echo $pagesmax >> ~/Documents/Newscrape/Binaries/pagesnumber.txt
   for suburb in "${suburbsNSW[@]}" # NSW
   do

      # Get number of results
      pagesnumber=$(cat ~/Documents/Newscrape/Binaries/pagesnumber.txt) # An integer usually less than 5.

      # Loop through pages

      page=1 # Page number counter
      while [ "$page" -le "$pagesnumber" ]
      do

         printf "SAVER: Saving '${clue}-NSW-${suburb}-${page}'...\n">&2

         # Construct URL
         address="${addressbase[0]}${clue}${addressbase[1]}${page}${addressbase[2]}NSW${addressbase[3]}${suburb}+NSW"
         destination="${directory}/${clue}-NSW-${suburb}-${page}.html"

         # If the number of pages hasn't been gota already, get it.
         if [ "$pagesnumber" = "$pagesmax" ]
         then

            # Get the first page (and get the number of pages).
            ./save_page_as.sh $address "--browser" $browser "--destination" $destination --load-wait-time $loadwait --save-wait-time $savewait --get-pages-number

            # Update this number after the first scrape of each new suburb.
            pagesnumber=$(cat ~/Documents/Newscrape/Binaries/pagesnumber.txt) 

         else

            # Get the next page (but don't need to update the number of pages).
            ./save_page_as.sh $address "--browser" $browser "--destination" $destination --load-wait-time $loadwait --save-wait-time $savewait

         fi

         ((page++)) # Increment page counter.

         printf "SAVER: Saved.\n">&2

      done

   done

done