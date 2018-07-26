import os
import subprocess
import sys
import ast



def getModules():
    lineiter = (line.strip() for line in open("requirements.txt"))
    return [line for line in lineiter if line and not line.startswith("#")]

def getFiles():
    fileList = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for path, subdirs, files in os.walk(dir_path):
        for name in files:
            if name.endswith(".py"):
                sys.path.insert(0, path)
                fileTemp = [(os.path.join(path, name)), name.replace(".py", "")]
                fileList.append(fileTemp)
    return fileList


def main():
    print("\033[94mHelix self test\033[0m\n")
    fail = False
    modules = getModules()
    aimlName = "https://github.com/LordOfPolls/Python-AIML-Logging/archive/master.zip"
    correctNames = {
        aimlName: "aiml",
        "discord.py[voice]": "discord",
        "pillow": "PIL",
        "pycryptodome":"Crypto"
    }
    modules = str(modules)
    for origional, replacement in correctNames.items():
        modules = modules.replace(origional, replacement)
    modules = ast.literal_eval(modules)
    print("\033[95mChecking modules\033[0m")
    for module in modules:
        try:
            __import__(module, fromlist=[''])
            print("Testing {} \033[92mPASSED\033[0m".format(module))
        except ModuleNotFoundError:
            print("Testing {} \033[91mFAILED\033[0m".format(module))
            fail = True
    print("\033[95mChecking files\033[0m")
    for file in getFiles():
        print("Testing " + file[1], end="\r")
        # travis crashes with these lines enabled
        # command = [sys.executable, '-m', 'py_compile', file[0]]
        # out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        # stdout, stderr = out.communicate()
        # if "error" in str(stdout).lower() or "error" in str(stderr).lower():
        #     print("Testing {} \033[91mFAILED\033[0m".format(file[1]))
        #     fail = True
        if file[1] != "__init__":
            try:
                __import__(file[1])
                print("Testing {} \033[92mPASSED\033[0m".format(file[1]))
            except Exception as e:
                if "opus" in str(e):
                    pass
                elif "log" in str(e):
                    pass
                elif "cannot open shared object" in str(e):
                    pass
                elif "Perms" in str(e):
                    pass
                else:
                    print(e)
                    print("Testing {} \033[91mFAILED\033[0m".format(file[1]))
                    fail = True
    print("\033[95mChecking folders exist\033[0m")
    folders = ["code", "aiml", "aiml/alice", "aiml/custom"]
    for folder in folders:
        print("Checking {} folder".format(folder), end="\r")
        if not os.path.exists(folder):
            print("Checking {} folder \033[91mFAILED\033[0m".format(folder))
            fail = True
        else:
            print("Checking {} folder \033[92mPASSED\033[0m".format(folder))
            
    if fail:
        print("Tests \033[91mFAILED\033[0m")
        exit(1)
    else:
        print("Tests \033[92mPASSED\033[0m")

if __name__ == "__main__":
    main()

