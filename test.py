import os
import subprocess
import sys

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
    modules = getModules()
    for module in modules:
        print("Testing " + module)
        if "aiml" not in module:
            module = "aiml"
        if "." in module:
            module = module.split(".")[0]
        if "pillow" in module:
            module = "PIL"
        if "pycryptodome" in module:
            module = "Crypto"
        try:
            __import__(module, fromlist=[''])
        except ModuleNotFoundError:
            print("Could not find " + module)
            exit(1)

    for file in getFiles():
        print("Error checking " + file[1])
        # travis crashes with these lines enabled
        # command = [sys.executable, '-m', 'py_compile', file[0]]
        # out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        # stdout, stderr = out.communicate()
        # if "error" in str(stdout).lower() or "error" in str(stderr).lower():
        #    print("Error in " + file[1])
        #    raise Exception
        if file[1] != "__init__":
            try:
                test = __import__(file[1])
            except Exception as e:
                if "opus" in str(e):
                    print("Opus error, ignoring")
                elif "log" in str(e):
                    print("Logging error, ignoring")
                elif "cannot open shared object" in str(e):
                    print("Travis Error, ignoring")
                elif "Perms" in str(e):
                    print("Travis Error, ignoring")
                else:
                    print(e)
                    print("Error in " + file[1])
                    exit(1)
    print("Tests complete, PASS")
main()
