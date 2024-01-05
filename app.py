import os
import shutil
import sys
import json
import time
import random
import unicodedata
import re
import pathlib
import urllib.parse
import logging

import config
import requests

from bs4 import BeautifulSoup

from Class.JFFPost import JFFPost

# thanks to https://www.programcreek.com/python/?code=NelisW%2Fpyradi%2Fpyradi-master%2Fpyradi%2Fryfiles.py
def cleanFilename(sourcestring,  removestring ="\/:*?\"<>|"):
    """Clean a string by removing selected characters.

    Creates a legal and 'clean' source string from a string by removing some 
    clutter and  characters not allowed in filenames.
    A default set is given but the user can override the default string.

    Args:
        | sourcestring (string): the string to be cleaned.
        | removestring (string): remove all these characters from the string (optional).

    Returns:
        | (string): A cleaned-up string.

    Raises:
        | No exception is raised.
    """
    # remove the undesireable characters
    return ''.join([c for c in sourcestring if c not in removestring])

def create_folder(tpost):
    fpath = os.path.join(config.save_path, tpost.name, tpost.type)

    if not os.path.exists(fpath):
        os.makedirs(fpath)
    
    return fpath

def append_to_legacy_rename_script_file(folder, file_path_legacy, file_path):
    # todo: this should detect the host os and write the appropriate script type instead of windows batch
    if config.write_legacy_rename_script and file_path_legacy != file_path:
        header = ''
        try:
            legacy_rename_script_file_path = os.path.join(folder, 'legacy_rename_script.bat')
            try:
                size = os.path.getsize(legacy_rename_script_file_path)
                # file exists but is empty
                if size == 0:
                    header = 'chcp 65001'
            except Exception as e:
                # file doesn't exist
                header = 'chcp 65001'
            legacy_rename_script_file = open(legacy_rename_script_file_path, "a", encoding='utf-8')
            legacy_rename_script_file.write(header + '\r\nmove /-Y ' + '"' + os.path.basename(file_path_legacy) + '" "' + os.path.basename(file_path) + '"')
            legacy_rename_script_file.close()
            print('Added legacy rename script for "' + os.path.basename(file_path_legacy) + '"', flush=True)
        except Exception as e:
            print(e, flush=True)
            print(logging.traceback.format_exc(), flush=True)


def photo_save(ppost):
    global skip_next_network_request_delay

    ii = 1
    photos_url = []

    photos_img = ppost.post_soup.select('div.imageGallery.galleryLarge img.expandable')

    if len(photos_img) == 0:
        ii = -1
        # some photo posts may not contain any photos at all
        if len(ppost.post_soup.select('img.expandable')) > 0:
            photos_img.append(ppost.post_soup.select('img.expandable')[0])
        else:
            print('p: no photos found in post', flush=True)

    for img in photos_img:

        if 'src' in img.attrs:
            imgsrc = img.attrs['src']
        elif 'data-lazy' in img.attrs:
            imgsrc = img.attrs['data-lazy']
        ext = imgsrc.split('.')[-1]
        
        ppost.photo_seq = ii
        ppost.ext = ext
        ppost.prepdata()

        folder = create_folder(ppost)
        ppath_legacy = os.path.join(folder, cleanFilename(ppost.title_legacy))
        ppath = os.path.join(folder, cleanFilename(ppost.title))

        if not config.overwrite_existing and os.path.exists(ppath_legacy):
            print(f'p: <<exists skip (legacy filename)>>: {ppath_legacy}', flush=True)
            ii += 1
            append_to_legacy_rename_script_file(folder, ppath_legacy, ppath)
            skip_next_network_request_delay = True
            continue

        if not config.overwrite_existing and os.path.exists(ppath):
            print(f'p: <<exists skip>>: {ppath}', flush=True)
            ii += 1
            skip_next_network_request_delay = True
            continue

        photos_url.append([
            ppath_legacy, imgsrc
        ])

        ii += 1
    
    for img in photos_url:
        print(f'p: {img[0]}', flush=True)

        try:
            # always delay between picture download calls
            time.sleep(random.randint(1, 2))            

            response = requests.get(img[1], stream=True)
            with open(img[0], 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            skip_next_network_request_delay = False
        except Exception as e:
            print(e, flush=True)
            print(logging.traceback.format_exc(), flush=True)


def video_save(vpost):
    global skip_next_network_request_delay

    vpost.ext = 'mp4'
    vpost.prepdata()

    folder = create_folder(vpost)
    vpath_legacy = os.path.join(folder, cleanFilename(vpost.title_legacy))
    vpath = os.path.join(folder, cleanFilename(vpost.title))

    if not config.overwrite_existing and os.path.exists(vpath_legacy):
        print(f'v: <<exists skip (legacy filename)>>: {vpath_legacy}', flush=True)
        append_to_legacy_rename_script_file(folder, vpath_legacy, vpath)
        skip_next_network_request_delay = True
        return
    
    if not config.overwrite_existing and os.path.exists(vpath):
        print(f'v: <<exists skip>>: {vpath}', flush=True)
        skip_next_network_request_delay = True
        return

    try:
        skip_next_network_request_delay = False
        vidurljumble = vpost.post_soup.select('div.videoBlock a')[0].attrs['onclick']
        vidurl = json.loads(vidurljumble.split(', ')[1])

        vpost.url_vid = vidurl.get('1080p', '')
        vpost.url_vid = vidurl.get('540p', '') if vpost.url_vid == '' else vpost.url_vid

        print(f'v: {vpath}', flush=True)

        response = requests.head(vpost.url_vid)

        if response.headers['content-type'].startswith('application/x-mpegurl'):
            # handle as a gzip'ed m3u8 file to be downloaded via yt-dlp
            print('Got gzip\'ed m3u8 file, passing to yt-dlp to save stream:', flush=True)
            response_m3u8 = requests.get(vpost.url_vid, stream=True)
            m3u8_path = vpath + '.m3u8'
            m3u8_file = open(m3u8_path, "wb")
            m3u8_file.write(response_m3u8.content)
            m3u8_file.close()

            # generate a file protocol path we can use for yt-dlp. It allows file protocol paths, but only absolute
            # ones, except if it's on a window drive because the drive letter breaks it, so it has to be absolute to
            # the current drive, sigh. The actual usuable value is something like `file:///downloads/blah%2Ething.m3u8`
            full_dir_path = os.path.dirname(pathlib.Path.cwd().joinpath(vpath))
            file_protocol_path = 'file://' + urllib.parse.quote(str(pathlib.Path(full_dir_path).relative_to(pathlib.Path.cwd().drive)).replace('\\', '/') + '/' + pathlib.Path(m3u8_path).parts[-1])

            cmd = 'yt-dlp.exe -o "' + full_dir_path + '/%(title)s" --retries "infinite" --fragment-retries "infinite" --windows-filenames --no-overwrites --enable-file-urls "' + file_protocol_path + '"'
            os.system(cmd)

            print('m3u8 file removed: ' + m3u8_path, flush=True)
            os.remove(m3u8_path)
            del response_m3u8
        else:
            response_mp4 = requests.get(vpost.url_vid, stream=True)
            with open(vpath, 'wb') as out_file:
                shutil.copyfileobj(response_mp4.raw, out_file)
            del response_mp4
        del response

    except Exception as e:
        print(e, flush=True)
        print(logging.traceback.format_exc(), flush=True)

def text_save(tpost):
    tpost.ext = 'txt'
    tpost.prepdata()

    folder = create_folder(tpost)
    tpath_legacy = os.path.join(folder, cleanFilename(tpost.title_legacy))
    tpath = os.path.join(folder, cleanFilename(tpost.title))

    if not config.overwrite_existing and os.path.exists(tpath_legacy):
        print(f'v: <<exists skip (legacy filename)>>: {tpath_legacy}', flush=True)
        append_to_legacy_rename_script_file(folder, tpath_legacy, tpath)
        return
    
    if not config.overwrite_existing and os.path.exists(tpath):
        print(f'v: <<exists skip>>: {tpath}', flush=True)
        return

    text_file = open(tpath, "w", encoding='utf-8')
    text_file.write(tpost.full_text)
    text_file.close()

def parse_and_get(html_text):
    global skip_next_network_request_delay

    soup = BeautifulSoup(html_text, 'html.parser')

    for pp in soup.select('div.mbsc-card.jffPostClass'):

        # we can skip the network request day if the last post processor indicated it didn't use the network
        if skip_next_network_request_delay == False:
            time.sleep(random.randint(1, 2))

        # reset the delay back to default
        skip_next_network_request_delay = False

        # ignore playlist posts but they're just duplicates of other content
        if "playlist" in pp['class']:
            print("parse_and_get: skipping playlist post", flush=True)
            continue

        # ignore pinned posts but they're just duplicates of other content (and their HTML follows a slightly different format)
        if len(pp.select('.pinnedNotice')) > 0:
            print("parse_and_get: skipping pinned post", flush=True)
            continue

        # ignore shoutout posts because they're someone else's content
        if len(pp.select('.shoutoutNotice')) > 0:
            print("parse_and_get: skipping pinned post", flush=True)
            continue

        ptext = pp.select('div.fr-view')

        thispost = JFFPost()
        thispost.post_soup = pp

        namespan = pp.select('h5.mbsc-card-title.mbsc-bold span')
        if len(namespan) == 0:
            continue
        
        thispost.name = namespan[0].get("onclick").removeprefix("location.href='/").removesuffix("'")

        thispost.post_date_str = pp.select('div.mbsc-card-subtitle')[0].text
        # remove random junk after the date
        thispost.post_date_str = re.sub('This post.*$', '', thispost.post_date_str)
        thispost.post_date_str = thispost.post_date_str.strip().strip()
        thispost.post_id = pp.attrs['id']
        thispost.full_text = ptext[0].text.strip() if ptext else ''
        thispost.prepdata()

        classvals = pp.attrs['class']
        
        if 'video' in classvals:
            thispost.type = 'video'
            video_save(thispost)

            if config.save_full_text:
                text_save(thispost)

        elif 'photo' in classvals:
            thispost.type = 'photo'
            photo_save(thispost)

            if config.save_full_text:
                text_save(thispost)
                
        elif 'text' in classvals:
            if config.save_full_text:
                thispost.type = 'text'
                text_save(thispost)

if __name__ == "__main__":


    uid = sys.argv[1]
    pid = sys.argv[2]
    hsh = sys.argv[3]

    api_url = config.api_url

    skip_next_network_request_delay = False

    loopit = True
    loopct = 0
    if (len(sys.argv) >= 5):
        loopct = int(sys.argv[4])    

    while loopit:
        geturl = api_url.format(userid=uid, posterid=pid, seq=loopct, hash=hsh)

        # always delay between pagination calls
        time.sleep(random.randint(1, 2))

        html_text = requests.get(geturl).text

        print("Fetching posts " + str(loopct + 1) + " to " + str(loopct + 10) + " from " + geturl, flush=True)

        if 'as sad as you are' in html_text:
            loopit = False
        else:
            parse_and_get(html_text)
            loopct += 10
