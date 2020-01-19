#!/bin/bash
# Run save_page_as for every page that requires saving.
# https://github.com/abiyani/automate-save-page-as


# Declare universal variables.
loadwait=12
savewait=12
browser="firefox"

maxpages=5
declare -a addressbase=("https://www.yellowpages.com.au/search/listings?clue=" "&eventType=pagination&openNow=false&pageNumber=" "&referredBy=UNKNOWN&&state=" "&suburb=" "+") # [0], clue, [1], page, [2] state, [3] suburb+state
directory="/home/webscraper/Documents/Newscrape/Pages/" # then add "filename.html"


# Declare search terms
declare -a clues=('electricians+electrical+contractors' 'plumbers+gas+fitters' 'builders+building+contractors')

# Later: cross reference with suburbs of other clues (catagories)
declare -a suburbsNSW=('Dubbo' 'Wagga+Wagga' 'Sydney')
declare -a suburbsVIC=('Melbourne' 'Bendigo' 'Ringwood')
declare -a suburbsQLD=('Cleveland' 'Townsville' 'Cairns')


# Loop through clues
for clue in "${clues[@]}"
do

   # Do each state
   # Loop through suburbs

   for suburb in "${suburbsNSW[@]}" # NSW
   do

      # Loop through pages

      for page in $(seq 1 $maxpages)
      do

         # Construct URL
         address="${addressbase[0]}${clue}${addressbase[1]}${page}${addressbase[2]}NSW${addressbase[3]}${suburb}+NSW"
         destination="${directory}/${clue}-NSW-${suburb}-${page}.html"

         echo $address #debug!!!

         ./save_page_as.sh $address "--browser" $browser "--destination" $destination --load-wait-time $loadwait --save-wait-time $savewait

      done

   done

done