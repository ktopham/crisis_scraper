import requests
import json
import csv
from pdf_scraper import get_dicts
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

## Initiate Caches
AUTHOR_CACHENAME = "author_pagecount.json"

MODS_CACHENAME = "mods_cache.json"

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

def write_to_cache(url, req_text):
    MODS_CACHE[url] = req_text
    dumped_json_cache = json.dumps(MODS_CACHE)
    fw = open(MODS_CACHENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

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
    #input: id of one issue of the crisis
    url = "https://repository.library.brown.edu/storage/bdr:{}/MODS/".format(issue_id)

    mods_resp = requests.get(url)
    filename = "./mods_records/" + issue_id + "_mods.xml"
    with open(filename,"w") as xml:
        xml.write(mods_resp.text)
    outfilename = "./mods_records/" + issue_id + "_mods_edited.xml"
    with open(filename, "r") as fin:
        fileh = fin.readlines()
        for line in fileh:
            line = line.replace("mods:", "")
            # print(line)
            with open(outfilename, 'a') as ouf:
                ouf.write(line)



def parseXML(issue_id, issues_dict):

    filename = "./mods_records/{}_mods_edited.xml".format(issue_id)
    # create element tree object
    tree = ET.parse(filename)

    # get root element
    root = tree.getroot()

    # create empty list for news items
    article_dicts = []

    for item in root.findall('./relatedItem'):
        if item.attrib['type'] == "constituent":
            article_dict = {}

            for child in item:
                # print(child.tag)
                if child.tag == "name":
                    article_dict['author'] = ""
                    for namechild in child:
                        if namechild.tag == "namePart":
                            article_dict['author'] += namechild.text + " "
                elif child.tag == 'titleInfo':
                    title = ""
                    for titlechild in child:
                        # print(titlechild.tag)
                        if titlechild.tag == "nonSort":
                            title += titlechild.text + " "
                        else: title += titlechild.text
                    article_dict['title'] = title
                elif child.tag == 'genre':
                    article_dict['genre'] = child.text
                elif child.tag == "part":
                    extent = None
                    start = None
                    end = None
                    for extenttag in child:
                        for extentch in extenttag:
                            if extentch.tag == "start":
                                start = extentch.text
                            elif extentch.tag == "end":
                                end = extentch.text
                    try:
                        extent = int(end) - int(start)
                        if extent <= 0:
                            extent = 1
                        article_dict['extent'] = extent
                    except:
                        print("Error: Something wrong with extent")
                        article_dict['extent'] = None
            for k in ['extent', 'title', 'author', 'genre']:
                if k not in list(article_dict.keys()):
                    article_dict[k] = ""
            article_dict['issue_id'] = issue_id
            article_dict['date_issued'] = issues_dict[issue_id]['date_issued']
            article_dict['volno_string'] = issues_dict[issue_id]['volno_string']
                # print(list(article_dict.keys()))
            article_dicts.append(article_dict)
    return article_dicts

def make_artice_metadata(list_of_dicts):
    #input: a list of dictionaries
    #makes a csv of metadata
    with open("article_metadata.csv", "w", encoding="utf-8") as fout:
        csvwriter = csv.writer(fout)
        csvwriter.writerow(["title", "author", "genre", "extent", "issue_id", "date_issued", "volno_string"])
        for dict in list_of_dicts:
            row = []
            row.append(dict["title"])
            row.append(dict["author"])
            row.append(dict["genre"])
            row.append(dict["extent"])
            row.append(dict["issue_id"])
            row.append(dict["date_issued"])
            row.append(dict["volno_string"])
            csvwriter.writerow(row)
            print(row[0])


if __name__ == '__main__':
    issue_dict_list = get_dicts()
    issues_dict = {}
    for dictionary in issue_dict_list:
        issues_dict[dictionary['issue_id']] = dict(date_issued=dictionary['date_issued'], volno_string=dictionary['volno_string'],vol=dictionary['vol'], no=dictionary['vol'])

    all_articles = []
    welcome_string = "What would you like to do? \nXML files must be generated before parsing XML and creating metadata. \nXML must always be parsed before metadata is created.\n"
    welcome_string += "Available commands:\n"
    welcome_string += "\tscrape_mods \n\t\t- scrapes the Crisis collection for MODS records.\n"
    welcome_string += "\tparse_xml \n\t\t- parses the XML records and stores the article metadata in a dictionary.\n"
    welcome_string += "\tcreate_metadata \n\t\t- outputs the data created by parse_xml into a csv.\n"
    while True:
        proceed = input(welcome_string)
        if proceed == "scrape_mods":
            for k in issues_dict.keys():
                scrape_mods(k)

        if proceed == "parse_xml":
            for k in issues_dict.keys():
                issue_articles = parseXML(k, issues_dict)
                all_articles += issue_articles

        if proceed == "create_metadata":
            make_artice_metadata(all_articles)
        proceed = input("continue?[Y/N] ")
        if proceed.lower() == "n" or proceed.lower() == "no":
            break
