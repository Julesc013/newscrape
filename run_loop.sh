#!/bin/bash

# Reset variables
SECONDS=0
runs=0

while [ true ]
do

    duration=$SECONDS # Get time since start
    runs=$((runs + 1)) # Get run number

    # Print console debug stuff
    echo "Running Newscrape (${runs}th time)."
    echo "Uptime: $(($duration / 60))m $(($duration % 60))s ($(($duration / 60 /60 / 24)) days)"

    python3 newscrape.py # Start Newscrape again

done