# Justfor.Fans Ripper

## Overview

Thing to download all content from someone's JustFor.Fans. Please note that you _do_ need to be subscribed to their account, and unless their account is free then that means paying for it.

Please do not contact any developers about downloading content without paying or attempting to circumvent payment.

Written in Python 3.8 and working against JustFor.Fans as 20231224.

## Install

1. Install requirements: `pip install -r requirements.txt`
2. Download `yt-dlp.exe` from https://github.com/yt-dlp/yt-dlp (see their releases page) and put that file in the same folder as `app.py`.
    - If you're running on a different platform, you'll need to update `app.py` to use your binary instead of `yt-dlp.exe`. Compatibility with other platforms has not been checked.
3. Optional: set configuration (defaults are fine)
    1. `overwrite_existing` - will skip download if file exists
    2. `save_path` - destination folder - will save to same location as script folder if none provided
    3. `save_full_text` - will save text file with full description
    4. `file_name_format` - filename format, following values are available:
        - `name`
        - `post_date`
        - `post_id`
        - `desc`
    5. `desc_long_max_length` - set the maximum length of filenames generated from the post description
    6. `write_legacy_rename_script` - if you've saved files with the older version of this script (which uses short filenames) the script will detect them and write a shell script/batch file that you can use to rename those files to the longer format. No renaming will be performed automatically.

## How to use

Make sure you've performed the steps in Install above.

You'll need the UserID, PostedID, and UserHash4 values from your JustFor.Fans account to run this tool:

1. Log into your JustFor.Fans account
2. Open the performer's main page
3. Open the browser's Developer tools (on Windows typically the `F12` key, on Mac Chrome `Command+Option+I`, and for Safari follow the steps at https://www.howtogeek.com/721416/how-to-turn-on-the-develop-menu-in-safari-on-mac/)
4. Hit the Network tab, then refresh the page
5. Locate the `getPost.php` call and copy the `UserID`, `PosterID`, and `UserHash4` values (in yellow)
    - If you want to start ripping from a specific post number instead of the most recent, copy the number from the call above as well and use it as `StartAt` in the next step
6. Pass those numbers in as params when running the script:
    - `python app.py [UserID] [PosterID] [UserHash4] [StartAt]`

![image](https://user-images.githubusercontent.com/12958294/115130004-859a5580-9fa0-11eb-9275-235d4ec51967.png)

## Notes and troubleshooting

* Existing files will be skipped (so if you've had to stop ripping, you can resume without downloading everything again)
* An older version of this script saved to shorter filenames, but this version will attempt to write longer ones. If you already have the file with a shorter name it'll be detected, and a shell script/batch file will be written to the same folder to allow you to rename it to the longer version. No renaming will be performed automatically.
* Pinned posts (posts also showing at the top of a user's feed), shoutout posts (other people's content being promoted), and paid posts (Pay-Per-View content) will be skipped.

## Warranty

Absolutely no warranty is given for this code and you run it at your own risk... or better, learn the basics of Python, validate the code yourself, and fix any bugs or complete features from `TODO.md` :)
