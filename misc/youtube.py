# importing the module
import os

from pytube import YouTube

# where to save
SAVE_PATH = "B:\\Footbawwll\\Downloads"  # to_do

def downloadYouTube(videourl, path):

    yt = YouTube(videourl)
    yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    yt.download(SAVE_PATH)

downloadYouTube("https://www.youtube.com/watch?v=II7a8BYqg0w", SAVE_PATH)