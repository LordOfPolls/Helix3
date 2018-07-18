from __future__ import print_function

import colorlog
import logging
import os
import sys
import tempfile
import importlib
from time import gmtime, strftime, sleep

restart = False


# logging utility
tmpfile = tempfile.TemporaryFile('w+', encoding='utf8')
log = logging.getLogger('bootScript')
log.setLevel(logging.DEBUG)

# StreamHandler init
sh = logging.StreamHandler(stream=sys.stdout)

fmt = "%(log_color)s[%(levelname)s] %(name)s: %(message)s"
date_format = '%Y-%m-%d %H:%M:%S'
fmt = colorlog.ColoredFormatter(fmt, date_format,
                                log_colors={'DEBUG': 'cyan', 'INFO': 'reset',
                                            'WARNING': 'bold_yellow', 'ERROR': 'bold_red',
                                            'CRITICAL': 'bold_red'})

sh.setFormatter(fmt)
sh.setLevel(logging.DEBUG)
log.addHandler(sh)

tfh = logging.StreamHandler(stream=tmpfile)
tfh.setFormatter(logging.Formatter(
    fmt="[%(levelname)s] %(name)s: %(message)s"
))
tfh.setLevel(logging.DEBUG)
log.addHandler(tfh)


def finalize_logging():
    pass

    # defines log location
    logLocation = "data/logs"

    # archive old logs
    log.debug("Attempting to archive old log")
    # checks if data dir exists
    if not os.path.exists("data"):
        log.warning("No data folder... creating")
        os.mkdir("data")
    # checks if logLocation dir exists
    if not os.path.exists(logLocation):
        # technically should never happen, but error handling
        log.warning("Logging folder somehow doesnt exist... creating")
        os.mkdir(logLocation)
    # checks if old logs exist
    if os.path.isfile("{}/bot.log".format(logLocation)):
        log.debug("Moving old bot log")
        # renaming old archive files + logging archive
        try:
            # creates "archive" folder if not existent
            if not os.path.exists("{}/archive".format(logLocation)):
                log.warning("Archive folder doesnt exist... creating")
                os.mkdir("{}/archive".format(logLocation))
            # i know what youre thinking, urmergurd Dan, just use an else statement
            # but trust me, this way prevents errors in the future
            if os.path.exists("{}/archive".format(logLocation)):
                name = "{}/archive/{}.log".format(logLocation, str(strftime("%Y-%m-%d  %H%M%S", gmtime())))
                sleep(1)
                # tries creating the log file
                try:
                    # renames old log file to new name (current time)
                    os.rename("{}/bot.log".format(logLocation), name)
                    log.debug("Log successfully archived")
                except Exception as e:
                    fmt = 'Failed to archive old bot.log: \n{}: {}\n'
                    log.critical((fmt.format(type(e).__name__, e)))

        except Exception as e:
            fmt = 'Logging archive failed: \n{}: {}\n'
            log.critical((fmt.format(type(e).__name__, e)))

    # opens log file with writing permission
    with open("{}/bot.log".format(logLocation), 'w', encoding='utf8') as f:
        # position tmpfile at first position
        tmpfile.seek(0)

        # writes content of tempfile into log
        f.write(tmpfile.read())

        # close tempfile stream
        tmpfile.close()

        # formatting
        f.write("\n")

    # get the temp file handler from global
    global tfh
    # remove it
    log.removeHandler(tfh)
    del tfh

    # init file handler, output to dir, only append permissions
    fh = logging.FileHandler("data/logs/bot.log", mode='a')

    fh.setFormatter(logging.Formatter( # format the file handlers log output
        fmt="[%(levelname)s] %(name)s: %(message)s"
        # levelname = what level of log it is (i.e debug, info, warning, etc.)
        # name = the file that threw the log message
        # message = the message sent via the log
    ))
    fh.setLevel(logging.DEBUG) # https://docs.python.org/2/library/logging.html#logging.Logger.setLevel
    log.addHandler(fh) # add file handler (fh) to the active log, so it gets used when someone uses logging

    dlog = logging.getLogger('discord') # get discords logger
    dlog.setLevel(logging.WARNING) # set it to only show warnings and higher
    dlh = logging.StreamHandler(stream=sys.stdout) # set its output to the scripts stream
    dlh.terminator = ''
    dlh.setFormatter(logging.Formatter(  #sets discord's logs format
        fmt="[%(levelname)s] %(name)s: %(message)s"
    ))
    dlog.addHandler(dlh) # adds this handler to discords logging
    log.debug("Log setup complete")

def restartCall():
    global restart
    restart = True
    main()


def main():
    global restart
    if len(logging.getLogger(__package__).handlers) == 0:
        finalize_logging()
    if not restart:
        log.info("STARTING BOT PROCESS".center(20, "="))
    else:
        log.info("RESTARTING BOT PROCESS".center(20, "="))
    try:
        del code
    except:
        pass
    from code import Helix
    Helix()


if __name__ == '__main__':
    try:
        ver = os.popen(r'git show -s HEAD --format="%cr|%s|%h"')
        ver = str(ver.read().split('|')[2]).strip()
        log.info("HELIX3 {}".format(ver))
    except:
        log.info("HELIX3")
    log.info("By DNA, Murrax2, Orange, Semmoragge, WatchMiltan")
    # try:
    main()
    # except Exception as e:
    #     log.fatal("Bot runtime has been terminated")
    #     log.fatal(e)
    #     os.execl(sys.executable, sys.executable, *sys.argv)