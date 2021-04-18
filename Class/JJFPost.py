import config
import datetime
import re

from dateutil.parser import parse

class JJFPost:

    def __init__(self):
        self.name = ''
        self.post_date_str = ''
        self.post_date = ''
        self.post_id = ''
        self.desc = ''
        self.ext = ''
        self.full_text = ''
        self.title = ''
        self.type = ''
        self.photo_seq = -1

        self.url_vid = ''
        self.url_photo = []

        self.post_soup = {}

    def prepdata(self):

        self.post_date = parse(self.post_date_str).strftime("%Y-%m-%d")
        self.desc = self.full_text[0:50].strip() + ('...' if len(self.full_text) > 45 else '')
        self.desc = re.sub(r'["|/|\:|?|$|!|<|>|~|`|(|)|@|#|$|%|^|&|*|\n|\t|\r]', r'', self.desc)
        
        self.title = config.file_name_format \
            .replace('{name}', self.name) \
            .replace('{post_date}', self.post_date) \
            .replace('{post_id}', self.post_id[-5:]) \
            .replace('{desc}', self.desc) \
            .replace('{ext}', self.ext)
        
        self.title = self.title.replace('{photo_seq}', '.' + str(self.photo_seq).zfill(2)) if self.photo_seq > -1 else self.title.replace('{photo_seq}', '')
