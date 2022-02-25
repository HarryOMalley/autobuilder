
#   Author:     Harry O'Malley
#   Date:       22/02/2022
#   File:       helpers.py
#
#   Helper library with frequently used functions for use with the autobuilder

from pathlib import Path
import json
import os
from termcolor import colored as c


# print boolean as red or green
def bprint(i):
    if i == False:
        return red("False", True)
    return green("True", True)


def grey(string, bold=False):
    return c(string, attrs=["dark", ("bold"if bold else None)])


def purple(string, bold=False):
    return c(string, color="magenta", attrs=[("bold")] if bold else None)


def blue(string, bold=False):
    return c(string, color="blue", attrs=[("bold")] if bold else None)


def cyan(string, bold=False):
    return c(string, color="cyan", attrs=[("bold")] if bold else None)


def green(string, bold=False):
    return c(string, color="green", attrs=[("bold")] if bold else None)


def yellow(string, bold=False):
    return c(string, color="yellow", attrs=[("bold")] if bold else None)


def red(string, bold=False):
    return c(string, color="red", attrs=[("bold")] if bold else None)


def bold(string):
    return c(string, attrs=[("bold")])


def saveJson(dir, filename, data):
    Path(dir).mkdir(parents=True, exist_ok=True)
    with open(f'{dir}/{filename}.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True)
        return


def renameFile(oldFile, newFile):
    try:
        os.rename(oldFile, newFile)
    except:
        print("Failed to rename the file")
        return 1


def appendJson(dir, filename, data):
    Path(dir).mkdir(parents=True, exist_ok=True)
    existing = loadJson(f'{dir}/{filename}.json')
    if(not existing):
        output = [data]
    else:
        existing.append(data)
        output = existing

    saveJson(dir, filename, output)


def saveBytes(dir, filename, data):
    Path(dir).mkdir(parents=True, exist_ok=True)
    with open(f'{dir}/{filename}.json', 'wb') as outfile:
        outfile.write(data)
        return


def loadJson(filename):
    try:
        with open(filename) as jsonFile:
            input = json.load(jsonFile)
            return input
    except:
        print(f"Failed loading json: {filename}")
        return None


def clearTerminal():
    os.system('cls||clear')
    return
