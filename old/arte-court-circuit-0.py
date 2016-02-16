# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup
import json
import youtube_dl
import logging
from logging.handlers import RotatingFileHandler
import sys


URL_BASE = 'http://cinema.arte.tv'
URL_COU = 'http://cinema.arte.tv/fr/magazine/court-circuit'
QUALITY = 'HTTP_MP4_EQ_1'  # mp4 720x406 VOA-STF, VOSTF 1500k
DIR_DL = 'F:\\--JDL--\\arte\\'
FILE_LOG = 'F:\\--JDL--\\arte\\arte-court-circuit.log'

# pour le logger
logger = logging.getLogger('arte-COU')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                              '%Y-%m-%d %H:%m')
# handler file_handler
file_handler = RotatingFileHandler(FILE_LOG, 'a', 1000000, 1)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# création d'un second handler pour la console (vers le stdout)
steam_handler = logging.StreamHandler(sys.stdout)
steam_handler.setLevel(logging.DEBUG)
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)


def my_hook(d):
    if d['status'] == 'finished':
        logger.info('Done downloading: ' + d['filename'])


def main():
    # C'est parti !
    reqartecou = requests.get(URL_COU)
    logger.debug('request : ' + URL_COU + ' ' + str(reqartecou.status_code))
    if reqartecou.status_code == 200:
        soup = BeautifulSoup(reqartecou.text)
    else:
        logger.error(reqartecou.raise_for_status())
        logger.debug('end')
        exit()

    # <div class="article-list showing-8"> (showing-?)?
    trav = soup.find("div", class_="article-list")
    # search: <article class="node node-article has-image has-video ...
    # if we have "Court-métrage" take: about="/fr/article/...." > in liens_cinema
    liens_cinema = []
    bloc_art_view = trav.select("article.has-image.has-video")
    for elt in bloc_art_view:
        bloc_art_court = elt.find("div", class_="field-section").string.strip()
        if bloc_art_court == "Court-métrage":
            liens_cinema.append(elt['about'])
            logger.debug('liens_cinema: ' + elt['about'])

    liens_video = []
    for lien in liens_cinema:
        r_art = requests.get(URL_BASE + lien)
        soup_art = BeautifulSoup(r_art.text)
        # search: <div class="video-container", take: arte_vp_url="https://api.arte.tv/api...
        liens_video.append(soup_art.find("div", class_="video-container")['arte_vp_url'])     
        logger.debug('liens_video: ' + soup_art.find("div", class_="video-container")['arte_vp_url'])

    # DL json (from lien arte_vp_url)
    liens_finaux = []
    for lien in liens_video:
        r_final = requests.get(lien)
        # take: "VTR": "http:\/\/www.arte.tv\/guide\/fr\/057397-000\/elena",
        json_final = json.loads(r_final.text)
        liens_finaux.append(json_final['videoJsonPlayer']['VTR'])
        logger.debug('liens_dl: ' + json_final['videoJsonPlayer']['VTR'])
        

    # here youtube-dl !!
    logger.debug('launch ytdl')
    ydl_opts = {
        'format': QUALITY,
        'restrictfilenames': 'True',
        'nooverwrites': 'True',
        'outtmpl': DIR_DL + '%(title)s-%(upload_date)s.%(ext)s',
        'logger': logger,
        'progress_hooks': [my_hook],
        }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(liens_finaux)


if __name__ == "__main__":
    main()
