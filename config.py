overwrite_existing = False
save_path = r""
save_full_text = True
# changing this will cause existing downloaded files to not be detected and they'll be downloaded again.
# Note too that this is not the maximum filename length as additional placeholders in file_name_format below
# may be added.
desc_long_max_length = 120
# if any existing download is detected with a legacy filename, outputs a script file to rename it to the
# new format
write_legacy_rename_script = True

# AVAILABLE FIELDS
#  name
#  post_date
#  post_id
#  desc
#  photo_seq (do not change this)
#  ext (do not change this)

file_name_format = '{post_date}_{desc}{photo_seq}.{ext}'

# PROBABLY DON'T NEED TO CHANGE THIS
api_url = 'https://justfor.fans/ajax/getPosts.php?UserID={userid}&Type=One&PosterID={posterid}&StartAt={seq}&Source=Home&UserHash4={hash}'
