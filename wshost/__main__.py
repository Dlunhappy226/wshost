import urllib.request
import sys
import os


USAGE = """Usage: wshost <command>
init:    Create a new WSHost project in the current directory.
help:    Show this page.
"""

files = {
    "main.py": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/main.py",
    "config.py": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/config.py",
    "route.py": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/route.py",
    "requirements.txt": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/requirements.txt",
    "html/index.html": "https://raw.githubusercontent.com/Dlunhappy226/wshost/main/html/index.html"
}


def cli():
    args = sys.argv

    if len(args) < 2:
        print(USAGE)
    
    elif args[1].lower() == "init":
        init()

    elif args[1].lower() == "help":
        print(USAGE)

    else:
        print(f"Error: command {args[1]} not found.")


def init():
    print("Creating a new WSHost project in the current directory.")

    if not os.path.exists("html"):
        os.makedirs("html")

    for filename in files:
        print(f"Downloading {filename} ({list(files).index(filename) + 1}/{len(files)})")
        request = urllib.request.urlopen(files[filename])
        
        with open(filename, "wb") as f:
            f.write(request.read())
            f.close()
