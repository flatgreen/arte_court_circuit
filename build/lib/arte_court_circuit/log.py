# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from logging.handlers import RotatingFileHandler
import os
import sys


class SingleLevelFilter(logging.Filter):
    def __init__(self, passlevel, reject):
        self.passlevel = passlevel
        self.reject = reject

    def filter(self, record):
        if self.reject:
            return (record.levelno != self.passlevel)
        else:
            return (record.levelno == self.passlevel)


def a_logger(name, lvlconsole, logdir=''):
    
    if not lvlconsole in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        lvlconsole = 'DEBUG'
    level = logging.getLevelName(lvlconsole)
    
    logFileName = os.path.join(logdir, "%s.log" % name)
    # logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                                  '%Y-%m-%d %H:%M')

    # handler: file_handler level: INFO
    file_handler = RotatingFileHandler(logFileName, 'a', 1000000, 1)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # Second handler: console level: DEBUG
    # ne s'interesse qu'a logging.INFO !
    # f1 = SingleLevelFilter(logging.INFO, False)
    steam_handler = logging.StreamHandler(sys.stdout)
    # steam_handler.addFilter(f1)
    steam_handler.setLevel(level)
    steam_handler.setFormatter(formatter)
    logger.addHandler(steam_handler)
    
    return logger
    

