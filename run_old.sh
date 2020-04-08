#!/bin/bash

systemd-inhibit --why="Running Newscrape loop process" python3 newscrape_old.py
