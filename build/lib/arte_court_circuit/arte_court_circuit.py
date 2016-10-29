# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup
import json
import youtube_dl
import sys
import datetime
# https://github.com/scrapinghub/dateparser
import dateparser
from urlparse import urlparse, parse_qs
import log
import begin
import os
from os.path import expanduser

# Ce script DL la page
# http://cinema.arte.tv/fr/magazine/court-circuit/emissions
# 'fr' uniquement
# 'de' voir : http://cinema.arte.tv/de/magazin/kurzschluss
# http://cinema.arte.tv/de/magazin/kurzschluss/sendungen-0
#
# trouve la page de la dernière emission téléchargeable
# Sur la page : liste les "métrage" et les DL
#
# vers le début fev maj de ytdl avec arte cinema (à suivre)
#
# m.a.j : 14 juin 2016
#
# notes:
# quality = 'HTTP_EQ_1/HTTP_MP4_EQ_1/best'  # mp4 720x406 VOA-STF, VOSTF 1500k OR best
# voir qualities_for_ytdl.txt
# with YAML windows path escape \

URL_BASE_COU = 'http://cinema.arte.tv/fr/magazine/court-circuit/emissions'
URL_BASE_CINEMA = 'http://cinema.arte.tv'


# FUNCTIONS ####################################################################
def dl_page_for_soup(url):
    ''' Fait une requête sur 'url' renvoie :
    -OK (0|1) selon le status du dl
    -soup objet BS4 contenant le texte de la page'''
    result = []
    reqpage = requests.get(url)

    if reqpage.status_code == 200:
        ok = 1
        soup = BeautifulSoup(reqpage.text, "html.parser")
    else:
        ok = 0
        soup = ''
    result = (ok, soup)
    return result


def correct_date(datelue):
    ''' datelue est un string, à priori une date
    cette date est testée jusqu'à donner une datetime.datetime correcte.
    - on peut trouver 'Vendredi 15 janvier à 00h20'
    mais on peut trouver autre chose... ex: '8 janvier 2016 autour de minuit'
    - return None si pas de date de trouvée'''

    list = datelue.split()
    while list != []:
        adate = ' '.join(list)
        # print adate
        ladate = dateparser.parse(adate, languages=['fr'])
        if ladate is not None:
            return ladate
        else:
            list.pop()


def directory_dl(adir):
    ''' renvoie le répertoire de téléchargement
    si default=HOME -> user
    sinon celui passé en ligne de cmd
    '''
    if adir == '~':
        return expanduser("~")
    else:
        return adir


# MAIN #########################################################################
@begin.start
def main(dirdl='~', quality='HTTP_EQ_1/HTTP_MP4_EQ_1/best', download=True, debug=False):

    ''' arte_court_circuit est un script qui télécharge automatique les derniers
    court-métrages de l'émission 'court-circuit' sur Arte 'fr'. '''

    lvl_log_console = 'INFO'
    if debug:
        lvl_log_console = 'DEBUG'
    dirdl = directory_dl(dirdl)
    logger = log.a_logger('arte-court-circuit', lvl_log_console, dirdl)
    logger.info('download directory: ' + dirdl)

    # let's go !
    success, soup = dl_page_for_soup(URL_BASE_COU)
    if not success:
        logger.debug('no base Arte page')
        exit()

    # liste emissions, récupération date et lien
    divartlist = soup.find("div", class_="article-list")
    divart = divartlist.select("article.node-article")
    linkemission = ''
    for elt in divart:
        dateheure_arte = elt.find("div", class_="field-section").string.strip()
        logger.debug('dateheure_arte:' + dateheure_arte)
        datetimeemission = correct_date(dateheure_arte)
        # logger.debug('datetimeemission:' + datetimeemission)
        if datetimeemission is None:
            logger.debug('No date (dateparser=>None)')
            exit()
        if ((datetime.datetime.now() - datetimeemission).days > 30):
            logger.debug('so far in time')
            break
        if ((datetimeemission < datetime.datetime.today())
                and ((datetime.datetime.now() - datetimeemission).days < 8)):
            logger.debug('OK' + ' --> ' + elt['about'])
            linkemission = URL_BASE_CINEMA + elt["about"]
            logger.info(linkemission + ' (' + datetimeemission.strftime('%d %b %Y') + ')')
            break
        else:
            logger.debug('NO')

    # ICI, on pourrait (ou pas) mettre une verif dans un fichier 'historique'

    if linkemission == '':
        logger.info('Date seems OK, but non link')
        exit()

    # Requete de la page de l'émission
    success, soup = dl_page_for_soup(linkemission)
    if not success:
        exit()

    arte_cm = {}
    # il peut y avoir plusieurs div secondary-list
    div = soup.find_all("div", class_="secondary-list")
    for elt in div:
        divpages = elt.select("article.node-article")
        for elt1 in divpages:
            logger.debug('about:' + elt1['about'])
            fieldsection = elt1.find("div", class_="field-section").string.strip()
            titreh2 = elt1.find("h2").string.strip()
            logger.debug(' fieldsection:' + fieldsection + ' h2:'+ titreh2)
            if ('métrage' in fieldsection) or ('Disponible' in fieldsection) or ('«' in titreh2):
                # on ne garde que <span class=icon-play"> et non 'icon-tv-programm'
                span_icon = elt1.find("span")['class']
                logger.debug(' OK span_icon:' + ' '.join(span_icon))
                if 'icon-play' in span_icon:
                    # ça doit suffir pout YTDL
                    liens_cm = URL_BASE_CINEMA + elt1['about']
                    logger.info(liens_cm)
                    title_cm = liens_cm[33:]
                    arte_cm[title_cm] = liens_cm

    if not download:
        logger.debug('NO download')
        exit()

    # hook for ytdl
    def my_hook(d):
        ''' for logging the youtube_dl's end '''
        if d['status'] == 'finished':
            logger.info('Done downloading: ' + d['filename'])

    logger.debug('---- DL: ' + str(len(arte_cm)) + ' ----')
    for title, link in arte_cm.iteritems():
        # here youtube-dl !!
        logger.debug('launch ytdl for : ' + title)
        ydl_opts = {
            # 'simulate': 'True',
            'format': quality,
            'noprogress': 'True',
            # 'nooverwrites': 'True',
            'outtmpl': dirdl + os.sep + '%(upload_date)s ' + title + '.%(ext)s',
            'logger': logger,
            'progress_hooks': [my_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([link])
            except Exception as e:
                # logger.info(e)
                sys.exc_clear()
