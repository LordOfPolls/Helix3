from .bot import Helix
import logging
import os
from time import gmtime, strftime, sleep

log = logging.getLogger(__name__)

logLocation = "data/logs"
fhandler = logging.FileHandler(filename="{}/bot.log".format(logLocation), encoding='utf-8', mode='a')
fhandler.setFormatter(logging.Formatter(
    "[%(levelname)s] %(name)s: %(message)s"))
log.addHandler(fhandler)

del fhandler
del logLocation
