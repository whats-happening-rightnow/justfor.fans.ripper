import os
import shutil
import sys
import json
import config
import requests
import urllib.request
import re
from pySmartDL import SmartDL

from bs4 import BeautifulSoup

from Class.JJFPost import JJFPost

def create_folder(tpost):
    fpath = os.path.join(config.save_path, tpost.name, tpost.type)
    # fpath = os.path.join(config.save_path, re.sub('\W', '', tpost.name), tpost.type)

    if not os.path.exists(fpath):
        os.makedirs(fpath)
    
    return fpath

def photo_save(ppost):
    ii = 1
    photos_url = []

    photos_img = ppost.post_soup.select('div.imageGallery.galleryLarge img.expandable')

    if len(photos_img) == 0:
        ii = -1
        photos_img.append(ppost.post_soup.select('img.expandable')[0])

    for img in photos_img:

        imgsrc = img.attrs['src']
        ext = imgsrc.split('.')[-1]
        
        ppost.photo_seq = ii
        ppost.ext = ext
        ppost.prepdata()

        folder = create_folder(ppost)
        ppath = os.path.join(folder, ppost.title)

        if not config.overwrite_existing and os.path.exists(ppath):
            print(f'p: <<exists skip>>: {ppath}')
            ii += 1
            continue

        photos_url.append([
            ppath, imgsrc
        ])

        ii += 1
    
    for img in photos_url:
        print(f'p: {img[0]}')
        print(img[1])
        # urllib.request.urlretrieve(img[1], img[0])

        # obj = SmartDL(img[1], img[0])
        # obj.start()
        # print("Done: " + obj.get_dest())

        response = requests.get(img[1], stream=True)
        with open(img[0], 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


def video_save(vpost):
    vpost.ext = 'mp4'
    vpost.prepdata()

    folder = create_folder(vpost)
    vpath = os.path.join(folder, vpost.title)

    if not config.overwrite_existing and os.path.exists(vpath):
        print(f'v: <<exists skip>>: {vpath}')
        return

    # print(vpost.post_soup)
    try:
        vidurljumble = vpost.post_soup.select('div.videoBlock a')[0].attrs['onclick']
        vidurl = json.loads(vidurljumble.split(', ')[1])

        vpost.url_vid = vidurl.get('1080p', '')
        vpost.url_vid = vidurl.get('540p', '') if vpost.url_vid == '' else vpost.url_vid

        print(f'v: {vpath}')
        print(vpost.url_vid)
        # urllib.request.urlretrieve(vpost.url_vid, vpath)

        # obj = SmartDL(vpost.url_vid, vpath)
        # obj.start()
        # print("Done: " + obj.get_dest())

        response = requests.get(vpost.url_vid, stream=True)
        with open(vpath, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    except Exception as e:
        print(e)

def text_save(tpost):
    tpost.ext = 'txt'
    tpost.prepdata()

    folder = create_folder(tpost)
    tpath = os.path.join(folder, tpost.title)

    print(f't: {tpath}')

    text_file = open(tpath, "w", encoding='utf-8')
    text_file.write(tpost.full_text)
    text_file.close()

def parse_and_get(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # name
    # name = soup.select('h5.mbsc-card-title.mbsc-bold span')[0].text
    # print(name)
    # print(soup.select('h5.mbsc-card-title.mbsc-bold span')[0].get("onclick").lstrip("location.href='/").rstrip("'"))
    # # date
    # post_date = soup.select('div.mbsc-card-subtitle')[0].text.strip()
    # print("post_date: " + post_date)

    for pp in soup.select('div.mbsc-card.jffPostClass'):

        # print("date")
        # print(pp.select('div.mbsc-card-subtitle')[0].text.strip())

        ptext = pp.select('div.fr-view')

        thispost = JJFPost()
        thispost.post_soup = pp
        thispost.name = pp.select('h5.mbsc-card-title.mbsc-bold span')[0].get("onclick").lstrip("location.href='/").rstrip("'")
        thispost.post_date_str = pp.select('div.mbsc-card-subtitle')[0].text.strip().strip()
        thispost.post_id = pp.attrs['id']
        thispost.full_text = ptext[0].text.strip() if ptext else ''
        thispost.prepdata()

        print(thispost.name)
        print(thispost.post_date_str)

        classvals = pp.attrs['class']
        
        if 'video' in classvals:
            thispost.type = 'video'
            video_save(thispost)

            if config.save_full_text:
                #thispost.type = 'text'
                text_save(thispost)

        elif 'photo' in classvals:
            thispost.type = 'photo'
            photo_save(thispost)

            if config.save_full_text:
                #thispost.type = 'text'
                text_save(thispost)
                
        elif 'text' in classvals:
            if config.save_full_text:
                thispost.type = 'text'
                text_save(thispost)

if __name__ == "__main__":


    uid = sys.argv[1]
    hsh = sys.argv[2]

    api_url = config.api_url

    loopit = True
    loopct = 0
    while loopit:

        geturl = api_url.format(userid=uid, seq=loopct, hash=hsh)
        print(geturl)
        html_text = requests.get(geturl).text

        if 'as sad as you are' in html_text:
            loopit = False
        else:
            parse_and_get(html_text)
            loopct += 10


