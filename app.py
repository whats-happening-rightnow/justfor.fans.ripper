import sys
import os
import shutil
import requests
import time
import random
import json
import subprocess
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
from pathlib import Path


import config
from Class.JJFPost import JJFPost

def create_directory_for_post(post):
    """
    This function creates a directory structure where to save the downloaded content.
    """
    folder_path = os.path.join(config.save_path, post.name, post.type)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path

def save_photo(post):
    """
    This function is responsible for downloading and saving the photos.
    """
    photo_counter = 1
    photo_urls = []

    photos = post.post_soup.select('div.imageGallery.galleryLarge img.expandable')

    if len(photos) == 0:
        photo_counter = -1
        photos.append(post.post_soup.select('img.expandable')[0])

    for img in photos:
        img_source = img.attrs.get('src', img.attrs.get('data-lazy', None))

        if img_source is None:
            print("no image source, skipping")
            continue

        extension = img_source.split('.')[-1]

        post.photo_seq = photo_counter
        post.ext = extension
        post.prepdata()

        folder = create_directory_for_post(post)
        file_path = os.path.join(folder, post.title)

        if not config.overwrite_existing and os.path.exists(file_path):
            print(f'Photo: <<exists skip>>: {file_path}')
            photo_counter += 1
            continue

        photo_urls.append([file_path, img_source])

        photo_counter += 1

    for img in photo_urls:
        download_file(img[0], img[1])  # Use a function to download the file, for better code readability

def add_metadata_to_video(video_path, title, artist, date, description):
    print(f'Adding metadata to: {video_path}')
    metadata_command = [
        'ffmpeg',
        '-i', video_path,  # input file
        '-metadata', f'title={title}',
        '-metadata', f'artist={artist}',
        '-metadata', f'date={date}',
        '-metadata', f'description={description}',
        '-codec', 'copy',  # don't re-encode video or audio
        video_path+'.tmp.mp4'  # output file
    ]
    subprocess.run(metadata_command)
    os.remove(video_path)
    os.rename(video_path+'.tmp.mp4', video_path)

def download_file(file_path, url):
    """
    This function downloads a file and saves it to the specified location.
    """
    print(f'Downloading: {file_path}')
    print(f'From: {url}')

    try:
        response = requests.get(url, stream=True)
        with open(file_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    except Exception as e:
        print(e)

def save_video(post):
    """
    This function is responsible for downloading and saving the videos.
    """
    post.ext = 'mp4'
    post.prepdata()

    folder = create_directory_for_post(post)
    file_path = os.path.join(folder, post.title)


    if not config.overwrite_existing and os.path.exists(file_path):
        print(f'Video: <<exists skip>>: {file_path}')

        return

    try:
        video_url_data = post.post_soup.select('div.videoBlock a')[0].attrs['onclick']
        video_url = json.loads(video_url_data.split(', ')[1])

        post.url_vid = video_url.get('1080p', video_url.get('540p', ''))

        ydl_opts = {
            'outtmpl': file_path,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([post.url_vid])  # download() expects a list of URLs.

    except Exception as e:
        print(e)


def save_text(post):
    """
    This function is responsible for saving the text of the post.
    """
    post.ext = 'txt'
    post.prepdata()

    folder = create_directory_for_post(post)
    file_path = os.path.join(folder, post.title)

    print(f'Text: {file_path}')

    with open(file_path, "w", encoding='utf-8') as text_file:  # Use a with statement to handle the file open/close.
        text_file.write(post.full_text)

def parse_and_save_content(html_content):
    """
    This function parses the HTML content, extracts the information of the post and downloads/saves the related content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    for post_element in soup.select('div.mbsc-card.jffPostClass'):
        time.sleep(random.randint(1, 2))  # Random delay to prevent being flagged as a bot.

        post = JJFPost()
        post.post_soup = post_element
        post.name = post_element.select('h5.mbsc-card-title.mbsc-bold span')[0].get("onclick").lstrip("location.href='/").rstrip("'")
        post.post_date_str = post_element.select('div.mbsc-card-subtitle')[0].text.strip()
        post.post_id = post_element.attrs['id']
        post.full_text = post_element.select('div.fr-view')[0].text.strip() if post_element.select('div.fr-view') else ''
        post.prepdata()

        print(post.name)
        print(post.post_date_str)

        class_values = post_element.attrs['class']

        if 'video' in class_values:
            post.type = 'video'
            save_video(post)
            folder = create_directory_for_post(post)
            file_path = os.path.join(folder, post.title)
            add_metadata_to_video(file_path, post.title, post.name, post.post_date, post.full_text)

            if config.save_full_text:
                save_text(post)
        elif 'photo' in class_values:
            post.type = 'photo'
            save_photo(post)
            if config.save_full_text:
                save_text(post)
        elif 'text' in class_values:
            if config.save_full_text:
                post.type = 'text'
                save_text(post)

if __name__ == "__main__":
    user_id = sys.argv[1]
    hash_value = sys.argv[2]

    api_url = config.api_url

    loop_count = 0
    while True:
        formatted_url = api_url.format(userid=user_id, seq=loop_count, hash=hash_value)
        html_content = requests.get(formatted_url).text

        if 'as sad as you are' in html_content:
            break
        else:
            parse_and_save_content(html_content)
            loop_count += 10
