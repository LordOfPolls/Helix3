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
        extraInfo = ""
        try:
            import pip
            self.pipWorking = True
            extraInfo = "normally"
        except ImportError:
            self.pipWorking = False
            self.installPIP()
            if os.name != "nt" and self.python_m("--version") is None:
                try:
                    print("\033[41mI will install it dammit >:(\033[0m")
                    print("Updating apt...")
                    subprocess.run("apt-get update", shell=True)
                    print("\033[42mAttempting to install pip ^-^\033[0m")
                    subprocess.run("apt-get install python3-pip", shell=True)
                    if self.python_m("--version") is None:
                        raise Exception
                    return
                except:
                    clear()
                    print("Im sorry, i cant install pip myself ;-;")
                    print("Please google how to install pip on your OS")
                    time.sleep(10)
                    exit()
            else:
                try:
                    import pip
                    self.pipWorking = True
                except:
                    self.pipWorking = False
                    print("Unable to use pip module, testing python -m pip")
                    if self.python_m("--version") is None:
                        print("PIP is not working on this machine, sorry")
                        print("Try installing it manually")
                        time.sleep(10)
                        exit()
                    else:
                        extraInfo = "via command line only"
        sys.stdout.write("PIP is working " + extraInfo + "\n")
        return True


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
        subprocess.run(sys.executable + " get-pip.py", shell=True)
        clear()
        os.unlink("get-pip.py")

    @staticmethod
    def python_m(*args, **kwargs):
        try:
            return str(subprocess.check_output([sys.executable, '-m', 'pip'] + list(args)))
        except subprocess.CalledProcessError:
            return None
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
    checkGit()
    PIP().checkPIP()
    if not gitWorking:
        print("Unable to use git, please install git shell")
        print("https://git-scm.com/book/en/v2/Getting-Started-Installing-Git")

    if not os.path.exists("code"):
        requirementsDir = "Helix3/requirements.txt"
        pull = False
    else:
        pull = True
        requirementsDir = "requirements.txt"

    clear()
    if gitWorking:
        if not pull:
            if os.path.exists("Helix3"):
                print("Error, helix3 directory already exists, please run Installer.py from that location")
                time.sleep(3)
            else:
                print("Downloading Helix")
                subprocess.run("git clone https://github.com/LordOfPolls/Helix3.git")
        else:
            print("Updating Helix")
            y_n = input("Would you like to overwrite any local changes?")
            if "y" in y_n.lower():
                subprocess.run("git fetch --all", shell=True)
                subprocess.run("git reset --hard", shell=True)
            else:
                subprocess.run("git pull", shell=True)
    clear()
    requirements = PIP.getRequirements(requirementsDir)
    print("Installing {} modules from {}\nMSG from the dev: This can take a **really** long time\n i suggest brewing a nice cup of tea\n\n".format(len(requirements), requirementsDir))
    for module in requirements:
        clear()
        print(
            "Installing {} modules from {}\nMSG from the dev: This can take a **really** long time\n i suggest brewing a nice cup of tea\n\n".format(
                len(requirements), requirementsDir))
        print("Installing {}".format(module))
        try:
            subprocess.call("pip install {} --no-cache-dir --upgrade".format(module), shell=True)
        except subprocess.CalledProcessError as e:
            print("Unable to install {}\n{}".format(module, e.returncode))
            time.sleep(10)
            exit()
    clear()
    print("All modules installed")
    print("Helix should now be usable")
    print("Press any 'enter' to quit")
    input()

if __name__ == '__main__':
    main()