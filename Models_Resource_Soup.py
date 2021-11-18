from urllib.parse import urljoin

import bpy
import os
import pathlib
import requests
import sys
import zipfile
from bs4 import BeautifulSoup as BS


def update_progress(job_title, progress):
    length = 30 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()


def normalize_string(s):
    """Turns string into valid filename"""
    return "".join(x for x in s if x.isalnum())

def create_folder(dir):
    """creates directory dir"""
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

def dir_to_list(mypath):
    """returns list of files in mypath, no full paths, filenames only"""
    return [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

def extract_archive(archive_file, the_path):
    new_path = os.path.join(the_path, archive_file[:-4])
    if not os.path.exists(new_path):
        create_folder(new_path)
        with zipfile.ZipFile(archive_file, 'r') as zip_ref:
            zip_ref.extractall(new_path)
        return True
    else:
        return False

def getListOfFiles(dirName):
    """get list of all files in directory dirName with full paths, searches recursively"""
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles
    
    
def save_file(url, output_file,  overwrite=False, debug=False):
    """Download file from url, saves it in output_file"""
    if not (os.path.exists(output_file) and not overwrite):
        if debug: print(f'Downloading file {output_file} from link {url}')
        r = requests.get(url, allow_redirects=True)
        if r:
            with open(output_file, 'wb') as f:
                f.write(r.content)


def get_list(url, section, filter, recursive=False):
    """Generic function, gets list from url"""
    res = {}
    if not url or url == 'None': return {"" : "None"}
    r  = requests.get(url).content
    soup = BS(r,'html.parser')
    #pl = soup.find("div", {"id": ID})
    pl = soup.find(section,filter)
    if not pl: return res
    children =pl.findChildren("a" , recursive=recursive)
    for child in children:
        #print(child.string, urljoin(url, child.get('href')))
        res[child.string] = urljoin(url, child.get('href'))
    del r
    del soup
    return res

def get_list_try(url, section, filter, recursive=False):
    """Same as above but returns empty dict if there is an error"""
    try: return get_list(url, section, filter, recursive=False)
    except: return {"": "None"}

def get_platforms(url):
    """Get list of platforms"""
    return get_list(url,  "div", {"id": 'leftnav-consoles'})

def get_letters(url):
    """Get list of platforms"""
    return get_list(url,  "div", {"id": 'letters'})

def get_letters_thread(self, context):
    """gets letters for current platform"""
    wm = context.window_manager
    try: url = context.scene.platforms_dynamic
    except: url = ''
    if not url or url == 'None': return
    try:
        data = get_letters(url)
    except:
        data = {'ALL': url}
    for e in list(context.scene.letters_collection): del context.scene.letters_collection[e]
    if 'ALL' in data or not data: 
        context.scene.letters_collection['ALL'] = bpy.context.scene.platforms_dynamic
    else: 
        for e in data:
            context.scene.letters_collection[e] = data[e]
    wm.Label = 'Letters updated'
        

def get_platforms_thread(self, context):
    wm = context.window_manager
    data = get_platforms(wm.url)
    for e in list(context.scene.platforms_collection): del context.scene.platforms_collection[e]
    for e in data:
        context.scene.platforms_collection[e] = data[e]
    wm.Label = 'Platforms updated'

    
def get_games(url):
    """get games from url"""
    res = {}
    if not url or url == 'None': return {"" : "None"}
    r  = requests.get(url).content
    soup = BS(r,'html.parser')
    pl = soup.find("div", {"id": 'content'})
    children =pl.findChildren("div" , recursive=False)
    games = None
    for child in children:
        if 'text-align: center' in str(child.get('style')):
            games = child
            break
    children =games.findChildren("a" , recursive=False)
    for x in children:
        link = urljoin(url, x.get('href'))
        name = 'None'
        """Getting name"""
        for elem in x.findChildren("span" , recursive=True):
            if elem.get('class')[0] == 'gameiconheadertext':
                name = elem.string
                break
        """Getting image preview"""
        try:
            img_src = x.findChildren("img" , recursive=True)[0].get('src')
        except:
            img_src = 'None'
        res[name] = {
            "name" : normalize_string(name),
            "link" : link,
            "img_src" : urljoin(url, img_src)
        }
    return res


def get_models_by_sections(rawdata, debug=False):
    """sorts models into sections, rawdata can be either string or soup"""
    res = {}
    if isinstance(rawdata, str):
        r = requests.get(rawdata).content
        soup = BS(r, 'html.parser')
    else:
        soup = rawdata
    pl = soup.find_all()
    current_section = ''
    for tag in pl:
        if tag.get('class'):
            if tag.get('class')[0] == 'sect-name':
                if debug: print(f'Section {tag.string}')
                if not tag.string in res:
                    current_section = tag.string
            elif tag.get('class')[0] == 'iconheadertext':
                if debug: print(f'    Model: {tag.string}')
                res[tag.string] = current_section
    return res


def get_models(url):
    """get all models from url"""
    res = {}
    r = requests.get(url).content
    soup = BS(r, 'html.parser')
    sections = get_models_by_sections(soup)
    pl = soup.find("div", {"id": 'content'})
    models = [model for model in pl.findChildren("a", recursive=True) if 'text-decoration: none;' in str(model.get('style'))]
    #print(len(models))
    for i in range(len(models)):
        model = models[i]
        link = urljoin(url, model.get('href'))
        name = model.find("span", {"class" : "iconheadertext"}).string
        if not name: continue
        img_src = model.find("img").get('src')
        try: section = sections[name]
        except: section = 'unknown'
        res[name] = {
            "name" : normalize_string(name),
            "link" : link,
            "section" : section,
            "img_src" : urljoin(url,img_src),
            #"archive" : urljoin(url, get_zip_url(link))
            "archive" : ""
        }
    return res

def get_zip_url(url):
    r = requests.get(url).content
    soup = BS(r, 'html.parser')
    zip = [link.get('href') for link in soup.find_all('a') if link.get('href').startswith('/download')][0]
    rowheader = soup.find('tr', {'class': 'rowheader'})
    name = [link.string for link in rowheader.findChildren("div", recursive=True) if link.string][0]
    return zip, name

