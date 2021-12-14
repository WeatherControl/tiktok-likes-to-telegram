from time import sleep
from TikTokApi import TikTokApi
import telebot
from redis import Redis
import requests
from io import BytesIO
import traceback
from os import getenv
from http.cookies import SimpleCookie

BOT_TOKEN = getenv('BOT_TOKEN')
USER_ID = getenv('USER_ID')
SEC_ID = getenv('SEC_ID')
CHANNEL_ID = getenv('CHANNEL_ID')

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Range": "bytes=0-"
}
api = TikTokApi.get_instance()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
redis = Redis(host='redis')


def already_posted(v_id):
    return not redis.sismember('posted_videos', v_id)


def save_posted(v_id):
    return redis.sadd('posted_videos', v_id)


def poll_likes():
    while True:
        try:
            likes = api.user_liked(USER_ID, SEC_ID, count=10)
            print(f'got {len(likes)} likes')
            for video in likes:
                v_id = video['id']
                v_url = video['video']['playAddr']
                if already_posted(v_id):
                    print(f'skipping {v_id}')
                    continue
                print(f'posting video {v_id}')
                req_headers = {"Referer": v_url, **DEFAULT_HEADERS}
                video_bytes = requests.get(v_url, headers=req_headers).content
                if len(video_bytes) < 1000:
                    raise Exception('error getting the video')
                bot.send_video(CHANNEL_ID, BytesIO(video_bytes))
                save_posted(v_id)
        except Exception as exc:
            traceback.print_exc()
        sleep(60)


if __name__ == '__main__':
    poll_likes()
