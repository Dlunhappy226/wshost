import urllib.request
import sys

command = sys.argv()

fileDownload = {
    "main.py": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/main.py",
    "config.py": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/config.py",
    "html/index.html": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/html/index.html",
    "html/400.html": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/html/400.html",
    "html/404.html": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/html/404.html",
    "html/405.html": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/html/405.html",
    "html/500.html": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/html/500.html"
}

def init():
    print("Initing wshost project.")
    for x in fileDownload:
        data = urllib.request.urlopen(fileDownload[x])
        file = open(x, "wb+")
        file.write(data.read())
        file.close
    print("Finish copying all file.")

if len(command) < 2:
    print("'wshost init' to init a new wshost project.")
elif command == "init":
    init()
elif command == "help":
    print("'wshost init' to init a new wshost project.")
else:
    print(f"Command: '{command}' not found.\n'wshost help' for help.")