from __future__ import print_function
from time import gmtime, strftime
import os
import sys
import time
import logging
import tempfile
import colorlog
import traceback
import subprocess
import discord
from time import sleep

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
        # ??
        tmpfile.seek(0)

        # writes content of tempfile into log
        f.write(tmpfile.read())

        # close tempfile stream
        tmpfile.close()

        # formatting
        f.write("\n")

    # ??
    global tfh
    log.removeHandler(tfh)
    del tfh

    # ??
    fh = logging.FileHandler("data/logs/bot.log", mode='a')

    fh.setFormatter(logging.Formatter(
        fmt="[%(levelname)s] %(name)s: %(message)s"
    ))
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)

    sh.setLevel(logging.INFO)

    dlog = logging.getLogger('discord')
    dlog.setLevel(logging.WARNING)
    dlh = logging.StreamHandler(stream=sys.stdout)
    dlh.terminator = ''
    dlh.setFormatter(logging.Formatter(
        fmt="[%(levelname)s] %(name)s: %(message)s"
    ))
    dlog.addHandler(dlh)
    log.debug("Log setup complete")

def pyexec(pycom, *args, pycom2=None):
    pycom2 = pycom2 or pycom
    os.execlp(pycom, pycom2, *args)


def restart(*args):
    pyexec(sys.executable, *args, *sys.argv, pycom2='python')


def main():
    # calls logging function
    finalize_logging()
    log.info("STARTING BOT PROCESS".center(20, "="))
    from code import Helix
    h = Helix()

if __name__ == '__main__':
    try:
        ver = os.popen(r'git show -s HEAD --format="%cr|%s|%h"')
        ver = str(ver.read().split('|')[2]).strip()
        log.info("HELIX3 {}".format(ver))
    except:
        log.info("HELIX3")
    try:
        main()
    except Exception as e:
        log.fatal("Bot runtime has been terminated")
        log.fatal(e)
        os.execl(sys.executable, sys.executable, *sys.argv)