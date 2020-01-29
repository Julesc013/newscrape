#!/usr/bin/env bash

# This program calls the python script once for each clue so that they run simultaneously.
# Basically, it starts the whole system.

# In future, make this program loop forever.
# Maybe use a list of clues and a for loop instead (unless it ruins the parallel processing).


# Declare array of sert terms/clues
declare -a clues=("electricians+electrical+contractors" "plumbers+gas+fitters" "builders+building+contractors")

# Start a process for each clue
for clue in "${clues[@]}"
do

    echo "Starting new newscrape process (${clue})..."

    # Start a Python process in parallel
    python3 newscrape.py ${clue} &

done