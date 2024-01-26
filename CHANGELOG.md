# Justfor.Fans Ripper Changelog

- 1.1.0
    - Updated script to handle current JustForFans HTML payload
    - Fixed script halting on pinned posts, shoutout posts, paid posts, and playlist posts
    - Script now doesn't pause after detecting an existing saved file, so it'll be much faster to resume ripping
    - Image locations are now sampled from multiple places in the returned HTML for redundancy.
    - `yt-dlp` is used for video/audio streams that use m3u8.
    - Saved image and video filenames are now much longer and don't end with an ellipsis (...). The filename length is controlled by a variable in `config.py`. Files saved by the older version of this script (now known as "legacy" filenames) will be detected to avoid re-downloading, and a batch file will be written into the current folder that can rename the legacy filenames to the new, longer ones (no automatic renaming will be performed during ripping; the user should check the batch file themselves and choose whether to run it).
    - Windows-only for now because of `yt-dlp.exe` dependency (PRs welcome!). Renames are not performed automatically.

- ?.?.?
    - Initial version forked from https://github.com/whats-happening-rightnow/justfor.fans.ripper
