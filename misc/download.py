import requests

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

download_file("https://www.nfl.com/plus/games/bills-at-lions-2022-reg-12/1498772?gig_actions=sso.login&gig_apiKey=3_Qa8TkWpIB8ESCBT8tY2TukbVKgO5F6BJVc7N1oComdwFzI7H2L9NOWdm11i_BY9f")