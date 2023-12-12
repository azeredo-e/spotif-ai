
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from threading import Thread
from dotenv import load_dotenv
import random
import requests
import os


USER_LAST = 'Duazeredo'
load_dotenv()


def uri_top(last_shortTerm_top, sp):
    global uri_shortTerm_top
    uri_shortTerm_top = [sp.search(f'artist: "{i[0]}" track: "{i[1]}"')['tracks']['items'][0]['uri'] for i in last_shortTerm_top]
    return uri_shortTerm_top

def uri_mid(last_shortTerm_mid, sp):
    global uri_shortTerm_mid
    uri_shortTerm_mid = [sp.search(f'artist: "{i[0]}" track: "{i[1]}"')['tracks']['items'][0]['uri'] for i in last_shortTerm_mid]
    return uri_shortTerm_mid


def main():
    headers = {
            "user-agent": os.getenv("USER_LAST") 
    }

    payload = {
        'api_key': os.getenv("ID_LAST"),
        'user': USER_LAST,
        'method': 'user.getTopTracks',
        'limit': 1000,
        'period': '1month',
        'format': 'json'
    }

    r = requests.get(os.getenv("URL_LAST"), headers=headers, params=payload)
    
    if r.status_code == 200:
        pass
    else:
        raise Exception(f"ERRO. Last.fm status code: {r.status_code}")
     
    last_shortTerm = []

    for i in range(len(r.json()["toptracks"]["track"])):
        last_shortTerm.append((r.json()["toptracks"]["track"][i]["artist"]["name"], 
                               r.json()["toptracks"]["track"][i]["name"],
                               r.json()["toptracks"]["track"][i]["playcount"]))

    q75_last_shortTerm = int(len(last_shortTerm) * 0.25)
    q25_last_shortTerm = int(len(last_shortTerm) * 0.75)

    print(q75_last_shortTerm, q25_last_shortTerm)

    last_shortTerm_top = (last_shortTerm[ : q75_last_shortTerm])
    last_shortTerm_mid = (last_shortTerm[q75_last_shortTerm + 1 : q25_last_shortTerm - 1])
    last_shortTerm_bot = (last_shortTerm[q25_last_shortTerm : ])

    random.shuffle(last_shortTerm_top)
    random.shuffle(last_shortTerm_mid)
    random.shuffle(last_shortTerm_bot)

    last_shortTerm_top = random.sample(last_shortTerm_top, 23)
    last_shortTerm_mid = random.sample(last_shortTerm_mid, 17)
    last_shortTerm_bot = random.sample(last_shortTerm_bot, 10)


    scope = 'user-library-read, playlist-modify-private, playlist-modify-public, user-read-playback-position, user-top-read, user-read-recently-played, ugc-image-upload'

    sp = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("ID_SPOT"),
                client_secret=os.getenv("SECRET_SPOT"),
                redirect_uri='https://localhost', 
                scope=scope,
                open_browser=False
            )
        )



    t1 = Thread(target=uri_top, kwargs={"last_shortTerm_top": last_shortTerm_top, "sp": sp})
    t1.start()
    t2 = Thread(target=uri_mid, kwargs={"last_shortTerm_mid": last_shortTerm_mid, "sp": sp})
    t2.start()

    uri_shortTerm_bot = [sp.search(f'artist: "{i[0]}" track: "{i[1]}"')['tracks']['items'][0]['uri'] for i in last_shortTerm_bot]


    try:
        t1.join()
    except:
        pass

    try:
        t2.join()
    except:
        pass

    uri_shortTerm = uri_shortTerm_top + uri_shortTerm_mid + uri_shortTerm_bot

    random.shuffle(uri_shortTerm)

    playlist = sp.user_playlist_create('eduardoazeredo', 'Hello, Spotify. This is Python from NeoVim', description='Funcionou desgraça!!!!')
    # sp.playlist_upload_cover_image(playlist['id'], image_b64)
    sp.playlist_add_items(playlist['id'], uri_shortTerm)

    print(uri_shortTerm)

if __name__ == "__main__":
    main()
