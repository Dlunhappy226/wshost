import urllib.request
import sys
import os


command = sys.argv

file_download = {
    "main.py": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/main.py",
    "config.py": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/config.py",
    "html/index.html": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/html/index.html",
}

def init():
    print("Initing wshost project.")
    if not os.path.exists("html"):
        os.makedirs("html")
    for x in file_download:
        data = urllib.request.urlopen(file_download[x])
        file = open(x, "wb+")
        file.write(data.read())
        file.close
    print("Finish copying all file.")

def main():
    if len(command) < 2:
        print("'wshost init' to init a new wshost project.")
    elif command[1] == "init":
        init()
    elif command[1] == "help":
        print("'wshost init' to init a new wshost project.")
    else:
        print(f"Command: '{command}' not found.\n'wshost help' for help.")
