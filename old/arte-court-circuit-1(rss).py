# -*- coding: utf-8 -*-

# Script de DL pour Court-Circuit d'Arte
# créer une liste de liens
# Ne fonctionne pas bien !
# ne retrouve pas Tous les liens
#finalement créer un flux rss

from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup
import json
import youtube_dl
import logging
from logging.handlers import RotatingFileHandler
import sys
import datetime
import PyRSS2Gen


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
    ''' for logging the youtube_dl's end '''
    if d['status'] == 'finished':
        logger.info('Done downloading: ' + d['filename'])


def main():
    # Request of Arte
    req_artecou = requests.get(URL_COU)
    logger.debug('request: ' + URL_COU)
    logger.debug('status_code: ' + str(req_artecou.status_code))
    if req_artecou.status_code == 200:
        soup = BeautifulSoup(req_artecou.text)
    else:
        logger.error(req_artecou.raise_for_status())
        logger.debug('end')
        exit()

    # create a empty dict for {'title_cm','url_final'}
    arte_cm = {}
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
    
    # for each link, we have to verify until the final link (for YoutubeDL)

    for lien in liens_cinema:
        # TODO status_code
        req_art = requests.get(URL_BASE + lien)
        soup_art = BeautifulSoup(req_art.text)
        # search: <div class="video-container", take: arte_vp_url="https://api.arte.tv/api...
        if soup_art.find("div", class_="video-container"):
            title_cm = lien[12:]
            logger.debug('title_cm: ' + title_cm)
            lien_video = soup_art.find("div", class_="video-container")['arte_vp_url']
            logger.debug('lien_video: ' + lien_video)
            req_final = requests.get(lien_video)
            # TODO status_code
            # take: "VTR": "http:\/\/www.arte.tv\/guide\/fr\/057397-000\/elena",
            json_final = json.loads(req_final.text)
            url_final = json_final['videoJsonPlayer']['VTR']
            logger.debug('liens_dl: ' + url_final)
            # add to the arte_cm dict
            arte_cm[title_cm] = url_final
    
    # Create RSS file
    rss_items = []
    for k,v in arte_cm.iteritems():
        gen = {'title': k,
               'link': v,
               'description': k,
               'guid': PyRSS2Gen.Guid(v)}
        logger.debug('Adding %s with %s' % (gen['title'], gen['link']))
        rss_items.append(PyRSS2Gen.RSSItem(**gen))
        
    rss = PyRSS2Gen.RSS2(
        title = "Arte Court-Circuit",
        link = URL_COU,
        description = "RSS for Arte Court-Circuit",
        lastBuildDate = datetime.datetime.utcnow(),
        items = rss_items)
    
    # TODO write file
    logger.debug('Create arte-court-circuit.xml')
    rss.write_xml(open("arte-court-circuit.xml", "w"),encoding='utf-8')

    return
    exit()    

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
