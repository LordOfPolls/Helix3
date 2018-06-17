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

tmpfile = tempfile.TemporaryFile('w+', encoding='utf8')
log = logging.getLogger('launcher')
log.setLevel(logging.DEBUG)

sh = logging.StreamHandler(stream=sys.stdout)
sh.setFormatter(logging.Formatter(
    fmt="[%(levelname)s] %(name)s: %(message)s"
))

sh.setLevel(logging.INFO)
log.addHandler(sh)

tfh = logging.StreamHandler(stream=tmpfile)
tfh.setFormatter(logging.Formatter(
    fmt="[%(levelname)s] %(name)s: %(message)s"
))
tfh.setLevel(logging.DEBUG)
log.addHandler(tfh)


def finalize_logging():
    pass

    with open("logs/bot.log", 'w', encoding='utf8') as f:
        tmpfile.seek(0)
        f.write(tmpfile.read())
        tmpfile.close()

        f.write('\n')
        f.write(" PRE-RUN SANITY CHECKS PASSED ".center(80, '#'))
        f.write('\n\n\n')

    global tfh
    log.removeHandler(tfh)
    del tfh

    fh = logging.FileHandler("logs/bot.log", mode='a')
    fh.setFormatter(logging.Formatter(
        fmt="[%(levelname)s]: %(message)s"
    ))
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)

    sh.setLevel(logging.INFO)

    dlog = logging.getLogger('discord')
    dlog.setLevel(logging.WARNING)
    dlh = logging.StreamHandler(stream=sys.stdout)
    dlh.terminator = ''
    dlh.setFormatter(logging.Formatter('.'))
    dlog.addHandler(dlh)


def pyexec(pycom, *args, pycom2=None):
    pycom2 = pycom2 or pycom
    os.execlp(pycom, pycom2, *args)


def restart(*args):
    pyexec(sys.executable, *args, *sys.argv, pycom2='python')


def main():
    from code import Helix
    log.info("=======STARTING BOT PROCESS=======\n")
    h = Helix()

if __name__ == '__main__':
    # try:
    main()
    # except Exception as e:
    #     log.fatal("Bot runtime has been terminated")
    #     log.fatal(e)
        #os.execl(sys.executable, sys.executable, *sys.argv)