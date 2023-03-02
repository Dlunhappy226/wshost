from setuptools import setup, find_packages

VERSION = 1.0
DESCRIPTION = "A python based web server including custom python route."

with open("README.md") as file:
    README = file

setup(
    name="wshost",
    version=VERSION,
    author="Dlunhappy226",
    author_email="dlun@dlun.tk",
    description= DESCRIPTION,
    long_description=README,
    url="https://github.com/Dlunhappy226/wshost",
    keywords=["web", "http", "server"],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only"
    ]
)