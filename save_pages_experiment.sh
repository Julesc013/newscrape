#!/bin/bash
# Run save_page_as for every page that requires saving.
# https://github.com/abiyani/automate-save-page-as


printf "\e[33mSaving all pages...\n\e[0m">&2

# Declare universal variables.
loadwait=6
savewait=2
browser="firefox"

#pagesmax=6 # Put this into the pagesnumber text file before it is populated with an actual result.
declare -a addressbase=("https://www.yellowpages.com.au/search/listings?clue=" "&eventType=pagination&openNow=false&pageNumber=" "&referredBy=UNKNOWN&&state=" "&suburb=" "+") # [0], clue, [1], page, [2] state, [3] suburb+state
directory="/home/webscraper/Documents/Newscrape/Pages/" # then add "filename.html"


# Declare search terms
declare -a clues=('electricians+electrical+contractors' 'plumbers+gas+fitters' 'builders+building+contractors')

# Later: cross reference with suburbs of other clues (catagories)
declare -a suburbsNSW=('Dubbo' 'Wagga+Wagga' 'Sydney')
declare -a suburbsVIC=('Melbourne' 'Bendigo' 'Ringwood')
declare -a suburbsQLD=('Cleveland' 'Townsville' 'Cairns')


# Remove existing pages (from the last scrape)
printf "\e[33mRemoving existing pages...\e[0m">&2
rm ~/Documents/Newscrape/Pages/*
printf "\e[32m Done.\n\e[0m">&2

# Loop through clues
for clue in "${clues[@]}"
do

   # Do each state
   # Loop through suburbs

   # For each suburb, reset the pages number file.
   rm ~/Documents/Newscrape/Binaries/pagesnumber.txt
   echo "-1" >> ~/Documents/Newscrape/Binaries/pagesnumber.txt
   for suburb in "${suburbsNSW[@]}" # NSW
   do

      # Get number of results
      pagesnumber=$(cat ~/Documents/Newscrape/Binaries/pagesnumber.txt) # An integer usually less than 5.

      # Loop through pages

      page=1 # Page number counter
      while [ "$page" -le "$pagesnumber" -o "$pagesnumber" = "-1" ]
      do

         printf "\e[33;2mGetting '${clue}-NSW-${suburb}-${page}'...\n\e[0m">&2

         # Construct URL
         address="${addressbase[0]}${clue}${addressbase[1]}${page}${addressbase[2]}NSW${addressbase[3]}${suburb}+NSW"
         destination="${directory}/${clue}-NSW-${suburb}-${page}.html"

         # Get the first page (and get the number of pages if required).
         ./save_page_as.sh $address "--browser" $browser "--destination" $destination --load-wait-time $loadwait --save-wait-time $savewait

         # If the number of pages hasn't been retrieved already, retrieve it.
         if [ "$pagesnumber" = "-1" ]
         then

            # Update this number after the first scrape of each new suburb.
            pagesnumber=$(cat ~/Documents/Newscrape/Binaries/pagesnumber.txt) 

         fi

         ((page++)) # Increment page counter.

         #printf "\e[32mSaved.\n\e[0m">&2

      done

   done

done

printf "\e[32mSaved all pages.\n\e[0m">&2
