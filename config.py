overwrite_existing = False
save_path = r""
save_full_text = True

# AVAILABLE FIELDS
#  name
#  post_date
#  post_id
#  desc
#  photo_seq (do not change this)
#  ext (do not change this)

file_name_format = '{post_date}_{desc}{photo_seq}.{ext}'

# PROBABLY DON'T NEED TO CHANGE THIS
api_url = 'https://justfor.fans/ajax/getPosts.php?UserID={userid}&Type=All&StartAt={seq}&Source=Home&UserHash4={hash}'
