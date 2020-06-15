import requests
import json
from bs4 import BeautifulSoup
import csv

CACHE_FNAME = 'crisis_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def write_to_cache(url, req_text):
    CACHE_DICTION[url] = req_text
    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def make_filename(vol, num):
    # input: The volume and number of the issue of the crisis
    filename = "vol{}no{}.pdf".format(vol, num)
    # returns: string of filename
    return filename

def get_volno(volno_date_string):
    volno_string = volno_date_string[volno_date_string.find("Vol."):volno_date_string.find("(")]
    vol = volno_date_string[volno_date_string.find("Vol.")+5:volno_date_string.find(",")]
    if len(vol)<2:
        vol = '0'+ vol
    no =  volno_date_string[volno_date_string.find("No.")+4:volno_date_string.find("(")-1]
    if len(no)<2:
        no = '0'+ no
    return (volno_string, vol, no)

def get_date(volno_string):
    date_string = volno_string[volno_string.find("(")+1:volno_string.find(")")]
    return date_string
    # <a href="https://modjourn.org/issue/bdr507789/">Vol. 1, No. 1 (1910-11-01)</a>

def get_id(link_with_id):
    # https://modjourn.org/issue/bdr521800/
    return link_with_id.split("/")[-2][3:]

def get_dicts():
    # scrapes https://modjourn.org/journal/crisis/
    url = "https://modjourn.org/journal/crisis/"
    # requests.get()
    if url in CACHE_DICTION:
        print("Getting data from Cache...")
        crisis_resp = CACHE_DICTION[url]
    else:
        crisis_resp = requests.get(url).text
        write_to_cache(url, crisis_resp)
    soup = BeautifulSoup(crisis_resp, 'html.parser')
    ems = soup.find_all('em', class_='title')
    list_of_dicts = []
    for em in ems:
        #gets em elements
        #from href, extract id number
        #from text af em, get vol and no information and date
        volno_date = em.find('a').text
        # print(volno_date)
        volno_tup = get_volno(volno_date)
        date_issued = get_date(volno_date)

        link_with_id = em.find('a')['href']
        issue_id = get_id(link_with_id)
        #make file name based on vol and no
        filename = make_filename(volno_tup[1], volno_tup[2])
        #make dictionary with id, vol & no, date issued string and file name for the pdf
        issue_dict = dict(issue_id=issue_id, date_issued=date_issued, volno_string=volno_tup[0],vol=volno_tup[1], no=volno_tup[2], filename=filename)
        list_of_dicts.append(issue_dict)
    #return: list of dictionaries
    return list_of_dicts


def get_pdf(filename, id):
    #input: id number for an issue of the crisis
    # downloads that pdf in local folder
    file_url = "https://repository.library.brown.edu/studio/item/bdr:{}/PDF/".format(id)

    r = requests.get(file_url, stream = True)
    filename = "./issue_pdfs/" + filename
    with open(filename,"wb") as pdf:
        for chunk in r.iter_content(chunk_size=1024):

             # writing one chunk at a time to pdf file
             if chunk:
                 pdf.write(chunk)
    #returns: nothing

def make_metadata(list_of_dicts):
    #input: a list of dictionaries
    #makes a csv of metadata
    with open("./issue_pdfs/metadata.csv", "w", encoding="utf-8") as fout:
        csvwriter = csv.writer(fout)
        csvwriter.writerow(["filename", "issue_id", "date_issued", "volno_string", "volume", "number"])
        for dict in list_of_dicts:
            row = []
            row.append(dict["filename"])
            row.append(dict["issue_id"])
            row.append(dict["date_issued"])
            row.append(dict["volno_string"])
            row.append(dict["vol"])
            row.append(dict["no"])
            csvwriter.writerow(row)
            print(row[0])


if __name__ == '__main__':
    list_of_dicts = get_dicts()
    for dict in list_of_dicts:
        get_pdf(dict['filename'], dict['issue_id'])

    make_metadata(list_of_dicts)
