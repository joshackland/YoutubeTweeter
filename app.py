import json
from googleapiclient.discovery import build
import tweepy
import os
from datetime import datetime, timedelta, timezone
import pathlib

script_directory = str(pathlib.Path(__file__).parent.resolve())
api_twitter_json_path = script_directory+"/api/twitter.json"
api_youtube_json_path = script_directory+"/api/youtube.json"
video_json_path = script_directory+"/videos.json"

def tweet(title, link):
    with open(api_twitter_json_path, "r") as f:
        twitter_creds = json.load(f)

    consumer_key = twitter_creds["API_Key"]
    consumer_secret = twitter_creds["API_Key_Secret"]
    access_token = twitter_creds["Access_Token"]
    access_token_secret = twitter_creds["Access_Token_Secret"]


    client = tweepy.Client(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret
    )
    
    text = f"I have just uploaded a new YouTube video!\n{title}\n{link}"
    response = client.create_tweet(
        text=text
    )


youtube_id = "UCMZ_dijAFd4Hc2yrLmfrMHQ" #replace this with your own channel id - https://www.youtube.com/channel/UCMZ_dijAFd4Hc2yrLmfrMHQ
youtube_video_url = "youtu.be/"


video_list_exists = os.path.exists(video_json_path)

if video_list_exists:
    print("videos.json exists")
    with open(video_json_path, "r") as f:
        previous_videos = json.load(f)
else:
    print("videos.json does not exist")
    previous_videos = {}

with open(api_youtube_json_path, "r") as f:
    youtube_creds = json.load(f)

youtube = build("youtube", 'v3', developerKey=youtube_creds["API_Token"])

request = youtube.search().list(
    part="snippet",
    channelId=youtube_id,
    order="date",
    publishedAfter=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
)
response = request.execute()

if len(response["items"]) == 0:
    print("No videos found")
    exit()
else:
    print("Videos uploaded in the past day found")



for video in response["items"]:
    if video["id"]["kind"] != "youtube#video" or video["id"]["videoId"] in previous_videos:
        continue

    previous_videos[video["id"]["videoId"]] = {
        "title": video["snippet"]["title"],
        "url": youtube_video_url+video["id"]["videoId"],
        "date": video["snippet"]["publishedAt"]
    }
    
    print(f"New video ({video['snippet']['title']}), creating tweet.")
    tweet(video["snippet"]["title"], youtube_video_url+video["id"]["videoId"])



with open(video_json_path, "w+") as f:
    previous_videos = json.dump(previous_videos, f, indent=2)