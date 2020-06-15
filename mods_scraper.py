import requests
import json
from bs4 import BeautifulSoup
import csv
from pdf_scraper import get_dicts
import pymods

AUTHOR_CACHENAME = "author_pagecount.json"

MODS_CACHENAME = "mods_cache.json"

list_of_dicts = get_dicts()

try:
    author_cache_file = open(AUTHOR_CACHENAME, 'r')
    author_cache_contents = author_cache_file.read()
    AUTHOR_CACHE = json.loads(author_cache_contents)
    author_cache_file.close()
except:
    AUTHOR_CACHE = {}

try:
    mods_cache_file = open(MODS_CACHENAME, 'r')
    mods_cache_contents = mods_cache_file.read()
    MODS_CACHE = json.loads(mods_cache_contents)
    mods_cache_file.close()
except:
    MODS_CACHE = {}

def update_author(author_name, page_start, page_end):
    pass
    #input: the name of the author taken from MODS record and the two page numbers when their article starts and ends
    #calculate the number of pages the aricle takes
    pages_written = int(page_end) - int(page_start)
    if pages_written == 0:
        pages_written = 1
    # if author already in dictionary, add the page number to the total
    if author_name in AUTHOR_CACHE.keys():
        AUTHOR_CACHE[author_name] += pages_written
    #else, create new dictionary entry for the author
    else:
        AUTHOR_CACHE[author_name] = pages_written
    #update the cache file
    dumped_json_cache = json.dumps(AUTHOR_CACHE)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def scrape_mods(issue_id):
    pass
    #input: id of one issue of the crisis
