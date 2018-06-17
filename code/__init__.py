from .bot import Helix
import logging
import os
from time import gmtime, strftime, sleep

logLocation = "data/logs"
log = logging.getLogger(__name__)

if not os.path.exists(logLocation):
    # technically should never happen, but error handling
    log.warning("Logging folder somehow doesnt exist... creating")
    os.mkdir(logLocation)
if os.path.isfile("{}/bot.log".format(logLocation)):
    log.info("Moving old bot log")
    try:
        if not os.path.exists("{}/archive".format(logLocation)):
            log.warning("Archive folder doesnt exist... creating")
            os.mkdir("{}/archive".format(logLocation))
        if os.path.exists("{}/archive".format(logLocation)):
            # i know what youre thinking, urmergurd Dan, just use an else statement
            # but trust me, this way prevents errors in the future
            name = "{}/archive/{}.log".format(logLocation, str(strftime("%Y-%m-%d  %H%M%S", gmtime())))
        sleep(1)
        os.rename("{}/bot.log".format(logLocation), name)
    except Exception as e:
        log.critical("Unable to perform logging pre-connect")
        log.critical(e)
fhandler = logging.FileHandler(filename="{}/bot.log".format(logLocation), encoding='utf-8', mode='a')
fhandler.setFormatter(logging.Formatter(
    "[%(levelname)s] %(name)s: %(message)s"))
log.addHandler(fhandler)

del fhandler
del logLocation
