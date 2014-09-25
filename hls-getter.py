#!/usr/bin/env python

import requests
import simplejson as json
import m3u8
import sys
import urlparse
import time

URL = sys.argv[1]
BANDWIDTH=2170880
DONE=[]
#CH_PATH=sys.argv[2]
CH_PATH="/tmp/live/1.stream/"

def get_channel_json(url):
    """Get spbtv channel json and return channel url"""
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()['stream']['url']
    else:
        print "Error!"


def get_m3u8(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        print "Rerun!"
        run()

def extract_url_base(url):
    u = urlparse.urlparse(url)
    a = u.path
    b = a.rfind("/")
    return u.scheme+"://"+u.hostname+a[0:b]

def get_and_parse_m3u8(url):
    """Getting and parsing m3u8 playlist.
    In case of root playlist returns URL of playlist with choosen bandwidth.
    I case of playlist returns dict of URLs of *.ts and playlist itself"""
    #m3u8_obj = m3u8.load(url)
    base_url = extract_url_base(url)
    playlist = get_m3u8(url)
    m3u8_obj = m3u8.loads(playlist)
    m3u8_obj.base_url = base_url
    if m3u8_obj.is_variant:
        for playlist in m3u8_obj.playlists:
            if playlist.stream_info.bandwidth > BANDWIDTH-100 and playlist.stream_info.bandwidth < BANDWIDTH+100:
                return m3u8_obj.base_url+'/'+playlist.uri
    else:
        m3u8_obj.base_uri = base_url
        ts = {}
        for segm in m3u8_obj.segments:
            ts[segm.uri] = segm.absolute_uri
        return ts,playlist

def get_and_save_ts(ts_dict):
    """Getting mpeg-ts files and save it"""
    for ts_name in ts_dict.keys():
        if ts_name not in DONE:
            r = requests.get(ts_dict[ts_name])
            if r.status_code == 200:
                try:
                    ts_file=open(CH_PATH+ts_name,'w')
                    ts_file.write(r.content)
                    ts_file.close()
                    DONE.append(ts_name)
                except:
                    print "error saving", ts_name
def save_playlist(playlist):
    """Save playlist as hi.m3u8"""
    playlist_file=open(CH_PATH+"hi.m3u8",'w')
    playlist_file.write(playlist)
    playlist_file.close()

def done_list_cleanup():
    global DONE
    if len(DONE) > 100:
        DONE = DONE[-100:]

def run():
    root_playlist_url = get_channel_json(URL)
    playlist_url = get_and_parse_m3u8(root_playlist_url)
    
    while True:
        ts,playlist = get_and_parse_m3u8(playlist_url)
        get_and_save_ts(ts)
        save_playlist(playlist)
        time.sleep(5)
        done_list_cleanup()

run()