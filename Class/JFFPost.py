import config
import datetime
import re

from dateutil.parser import parse

class JFFPost:

    def __init__(self):
        self.name = ''
        self.post_date_str = ''
        self.post_date = ''
        self.post_id = ''
        self.desc_legacy = ''
        self.desc = ''
        self.ext = ''
        self.full_text = ''
        self.title_legacy = ''
        self.title = ''
        self.type = ''
        self.photo_seq = -1

        self.url_vid = ''
        self.url_photo = []

        self.post_soup = {}

    def prepdata(self):

        self.post_date = parse(self.post_date_str).strftime("%Y-%m-%d")
        # sampled within legacy filename below. Changing this will break compatibility because any existing
        # downloads will not be detected and they'll be downloaded again. Note that because trimming is
        # done before replacement of special characters some filenames end up being a lot shorter.
        self.desc_legacy = self.full_text[0:50].strip() + ('...' if len(self.full_text) > 45 else '')
        self.desc_legacy = re.sub(r'["|/|\:|?|$|!|<|>|~|`|(|)|@|#|$|%|^|&|*|\n|\t|\r]', r'', self.desc_legacy)

        # new longer description used in title below. Note that this format doesn't use an ellipsis.
        self.desc = self.full_text
        self.desc = re.sub(r'["|/|\:|?|$|!|<|>|~|`|(|)|@|#|$|%|^|&|*|\n|\t|\r]', r'', self.desc)
        self.desc = self.desc[0:config.desc_long_max_length].strip()

        # sampled as legacy filename
        self.title_legacy = config.file_name_format \
            .replace('{name}', self.name) \
            .replace('{post_date}', self.post_date) \
            .replace('{post_id}', self.post_id[-5:]) \
            .replace('{desc}', self.desc_legacy) \
            .replace('{ext}', self.ext)
        
        self.title = config.file_name_format \
            .replace('{name}', self.name) \
            .replace('{post_date}', self.post_date) \
            .replace('{post_id}', self.post_id[-5:]) \
            .replace('{desc}', self.desc) \
            .replace('{ext}', self.ext)
        
        # if it's not a photo, remove the photo sequence number placeholder
        self.title_legacy = self.title_legacy.replace(
            '{photo_seq}',
            '.' + str(self.photo_seq).zfill(2)) if self.photo_seq > -1 else self.title_legacy.replace('{photo_seq}', ''
        )
        self.title = self.title.replace(
            '{photo_seq}',
            '.' + str(self.photo_seq).zfill(2)) if self.photo_seq > -1 else self.title.replace('{photo_seq}', ''
        )
