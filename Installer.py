from __future__ import print_function

import os
import sys
import time
import traceback
import subprocess
from shutil import disk_usage, rmtree
from base64 import b64decode

pipWorking = False
gitWorking = False

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def checkGit():
    global gitWorking
    try:
        gitWorking = bool(subprocess.check_output('git --version', shell=True))
    except:
        gitWorking = False

class PIP():
    def __init__(self):
        global pipWorking
        global gitWorking
        self.pipWorking = pipWorking
        self.gitWorking = gitWorking

    def checkPIP(self):
        try:
            import pip
            self.pipWorking = True
        except ImportError:
            self.pipWorking = False
            self.installPIP()

    def installPIP(self):
        clear()
        sys.stderr.write("PIP isnt installed, installing\n")
        try:
            import urllib.request
        except ImportError:
            sys.stderr.write("Unable to download pip\nPlease follow this guide: https://www.makeuseof.com/tag/install-pip-for-python/\n")
            time.sleep(10)
            exit()
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
        subprocess.run([sys.executable, 'get-pip.py'], shell=True)
        clear()
        os.unlink("get-pip.py""")
        self.checkPIP()
        if not self.pipWorking:
            sys.stderr.write("Unable to install pip, try installing it manually")
            time.sleep(5)
            exit()
        else:
            sys.stdout.write("PIP successfully installed")

    @staticmethod
    def python_m(*args, **kwargs):
        return subprocess.check_output([sys.executable, '-m', 'pip'] + list(args))

    def install(self, module):
        command = "install %s" % module
        self.python_m(*command.split())

    @staticmethod
    def getRequirements(file="requirements.txt"):
        lineiter = (line.strip() for line in open(file))
        return [line for line in lineiter if line and not line.startswith("#")]

def main():
    print("Making sure python is running at the correct version")
    if sys.version_info < (3, 5):
        print("Helix doesnt support any version of python below 3.5, please use that 3.5 or higher")
        time.sleep(5)
        exit()
    print("Helix3 installer")
    checkGit()
    PIP().checkPIP()
    if not gitWorking:
        print("Unable to use git, please install git shell")
        print("https://git-scm.com/book/en/v2/Getting-Started-Installing-Git")
    if not pipWorking:
        print("Unable to use pip, please install it manually")

    if not os.path.exists("code"):
        requirementsDir = "Helix3/requirements.txt"
        pull = False
    else:
        pull = True
        requirementsDir = "requirements.txt"

    clear()
    if not gitWorking:
        if not pull:
            if os.path.exists("Helix3"):
                print("Error, helix3 directory already exists, please run Installer.py from that location")
                time.sleep(3)
            else:
                print("Downloading Helix")
                subprocess.run("git clone https://github.com/LordOfPolls/Helix3.git")
        else:
            print("Updating Helix")
            subprocess.run("git fetch --all")
            subprocess.run("git reset --hard")

    clear()
    requirements = PIP.getRequirements(requirementsDir)
    print("Installing {} modules from {}".format(len(requirements), requirementsDir))
    for module in requirements:
        print("Installing {}".format(module))
        try:
            subprocess.call("pip install {} --no-cache-dir --upgrade -q".format(module))
        except subprocess.CalledProcessError as e:
            print("Unable to install {}\n{}".format(module, e.returncode))
            time.sleep(10)
            exit()
    clear()
    print("All modules installed")
    print("Helix should now be usable")

main()