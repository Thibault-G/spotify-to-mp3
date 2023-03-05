# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 11:28:00 2020

@author: Thibault
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials #To access authorised Spotify data
import time
import os
from youtubesearchpython import VideosSearch
from tqdm import tqdm
import json

### PARAMETERS ###

with open('credentials.json') as jf:
    credentials = json.load(jf)

root = os.getcwd()
username = credentials['username']
client_id = credentials['client_id']
client_secret = credentials['client_secret']

##################

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

token = spotipy.util.prompt_for_user_token(username,
                            scope='playlist-read-private',
                            client_id=client_id,
                            client_secret=client_secret,
                            redirect_uri='http://localhost:8888/callback/')

sp = spotipy.Spotify(auth=token) #spotify object to access API

def print_playlists(username=username):
    playlists = sp.user_playlists(username)
    
    print("\n----------- PLAYLISTS NAMES -----------")
    for i,item in enumerate(playlists['items']):
        print(str(i)+'. '+item['name'])
    print("---------------------------------------\n")

def get_mp3(playlist_index, path):
    playlists = sp.user_playlists(username)
    playlist_id = playlists['items'][playlist_index]['id']
    playlist = sp.playlist(playlist_id,fields="tracks,next")
    
    #Collecting the track names
    
    tracks_names = []
    
    tracks = playlist['tracks']
    for track in tracks['items']:
              tracks_names.append((track['track']['artists'][0]['name'],
                            track['track']['name']))
    while tracks['next']:
        tracks = sp.next(tracks)
        for track in tracks['items']:
              tracks_names.append((track['track']['artists'][0]['name'],
                            track['track']['name']))   

    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        already_dl = os.listdir(path)
        skipped = 0
        new_tracks_names = []
        for track_name in tracks_names:
            if track_name[1]+' - '+track_name[0]+'.mp3' not in already_dl:
                new_tracks_names.append(track_name)
            else:
                skipped+=1
        tracks_names = new_tracks_names
        
        if skipped>0: print('\nSkipped {} tracks already downloaded'.format(skipped))
        
    # Collecting the youtube URL's corresponding to these tracks 
    print("\nCollecting tracks' URLs ...")
    URLs = []
    
    start = time.time()

    for track_name in tracks_names:
        search = VideosSearch(track_name[0]+' '+track_name[1], limit=1).result()
        url = search['result'][0].get('link')
        URLs.append(url)

    print('\nURLs collection done in : {} s'.format(time.time()-start))
    
    print('\nDownloading MP3s ...\n')

    os.chdir(path)
    
    for name,url in tqdm(zip(tracks_names,URLs),total=len(URLs)):
        command = 'yt-dlp -x -q --audio-format mp3 -o "'+name[1]+' - '+name[0]+'.%(ext)s" '+url
        os.system(command)

if __name__ == "__main__":
    print(print_playlists())
    print('\n')
    index = input('Quelle playlist télécharger ?\n')
    print('\n')
    folder_name = input('Sous quel nom de dossier ?\n')
    inp_path = root+'\\'+folder_name
    get_mp3(int(index), path=inp_path)
