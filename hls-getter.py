#!/usr/bin/env python

#Запрашиваем основной URL
#парсим json и ищем там ссылку на плейлист.
#Запрашиваем m3u8 из json, парсим его, ищем нужное качество.
#Запрашиваем m3u8 с нужным качеством, если 401 - начинаем заново с запроса основного URL
#Парсим m3u8 с качеством, ищем ссылки на ts-ки
#Качаем ts-ки, раскладываем их по папочкам, если 401 - начинаем заново с запроса основного URL
import requests
import simplejson as json
import m3u8
import sys

URL = sys.argv[1]
BANDWIDTH=2170880

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
        print "Error!"

def get_and_parse_m3u8(url):
    """Getting and parsing m3u8 playlist.
    In case of root playlist returns URL of playlist with choosen bandwidth.
    I case of playlist returns dict of URLs of *.ts"""
    m3u8_obj = m3u8.load(url)
    if m3u8_obj.is_variant:
        for playlist in m3u8_obj.playlists:
            if playlist.stream_info.bandwidth > BANDWIDTH-100 and playlist.stream_info.bandwidth < BANDWIDTH+100:
                return m3u8_obj._base_uri+'/'+playlist.uri
    else:
        ts = {}
        for segm in m3u8_obj.segments:
            ts[segm.uri] = segm.absolute_uri
        return ts


root_playlist_url = get_channel_json(URL)
#root_playlist = get_m3u8(root_playlist_url)
#print parse_m3u8(root_playlist)
playlist_url = get_and_parse_m3u8(root_playlist_url)
ts = get_and_parse_m3u8(playlist_url)
print ts.keys()


